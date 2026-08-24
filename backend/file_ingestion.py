"""
File Ingestion Module — Large Dataset Support
Handles CSV/Excel files of any size using chunked reading.
Supports files up to 500MB with 1M+ rows.
"""

import os
import re
import io
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./querygenie_dev.db")
UPLOAD_TABLE_PREFIX = "uploaded_"
CHUNK_SIZE = 10_000       # rows per chunk for large file ingestion
SAMPLE_SIZE = 5_000       # rows to sample for schema description
MAX_FILE_SIZE_MB = 500


def sanitize_column_name(col: str) -> str:
    col = str(col).strip().lower()
    col = re.sub(r"[^a-z0-9_]", "_", col)
    col = re.sub(r"_+", "_", col)
    col = col.strip("_")
    if not col or col[0].isdigit():
        col = "col_" + col
    return col


def sanitize_table_name(filename: str) -> str:
    name = os.path.splitext(filename)[0]
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")
    return UPLOAD_TABLE_PREFIX + name[:40]  # cap table name length


def get_file_info(file_bytes: bytes, filename: str) -> dict:
    """
    Quick scan of file to get row count and columns
    without loading everything into memory.
    """
    ext = os.path.splitext(filename)[1].lower()
    size_mb = len(file_bytes) / (1024 * 1024)

    if ext == ".csv":
        # Count rows efficiently
        content = file_bytes.decode("utf-8", errors="replace")
        lines = content.count("\n")
        # Get columns from first line
        first_line = content.split("\n")[0]
        col_count = len(first_line.split(","))
        return {"rows": lines, "columns": col_count, "size_mb": round(size_mb, 2)}
    else:
        # For Excel, read just the first sheet header
        df_head = pd.read_excel(io.BytesIO(file_bytes), nrows=0)
        return {"rows": "unknown", "columns": len(df_head.columns), "size_mb": round(size_mb, 2)}


def ingest_file(file_bytes: bytes, filename: str, progress_callback=None) -> dict:
    """
    Reads a CSV or Excel file using chunked processing for large files.
    Returns metadata about the created table.
    """
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File too large ({size_mb:.0f}MB). Maximum is {MAX_FILE_SIZE_MB}MB.")

    ext = os.path.splitext(filename)[1].lower()
    table_name = sanitize_table_name(filename)
    engine = create_engine(DATABASE_URL)

    total_rows = 0
    clean_cols = None
    original_cols = None
    sample_df = None  # keep first SAMPLE_SIZE rows for schema description

    if ext == ".csv":
        # ── Chunked CSV ingestion ──────────────────────────────────────────
        chunks = pd.read_csv(
            io.BytesIO(file_bytes),
            chunksize=CHUNK_SIZE,
            low_memory=False,
            encoding="utf-8",
            encoding_errors="replace",
        )

        for i, chunk in enumerate(chunks):
            if i == 0:
                original_cols = chunk.columns.tolist()
                chunk.columns = [sanitize_column_name(c) for c in chunk.columns]
                clean_cols = chunk.columns.tolist()
                sample_df = chunk.head(SAMPLE_SIZE).copy()
                chunk.to_sql(table_name, engine, if_exists="replace", index=False)
            else:
                chunk.columns = clean_cols
                if sample_df is not None and len(sample_df) < SAMPLE_SIZE:
                    sample_df = pd.concat([sample_df, chunk]).head(SAMPLE_SIZE)
                chunk.to_sql(table_name, engine, if_exists="append", index=False)

            total_rows += len(chunk)
            if progress_callback:
                progress_callback(total_rows)

    elif ext in (".xlsx", ".xls"):
        # ── Excel ingestion (chunked via row batching) ─────────────────────
        df_full = pd.read_excel(io.BytesIO(file_bytes), dtype=str)
        original_cols = df_full.columns.tolist()
        df_full.columns = [sanitize_column_name(c) for c in df_full.columns]
        clean_cols = df_full.columns.tolist()
        sample_df = df_full.head(SAMPLE_SIZE).copy()
        total_rows = len(df_full)

        # Write in chunks to avoid SQLite lock issues on large files
        for start in range(0, total_rows, CHUNK_SIZE):
            chunk = df_full.iloc[start:start + CHUNK_SIZE]
            mode = "replace" if start == 0 else "append"
            chunk.to_sql(table_name, engine, if_exists=mode, index=False)
            if progress_callback:
                progress_callback(start + len(chunk))
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use CSV, XLSX, or XLS.")

    # Build sample values from the sample_df
    sample_values = {}
    for col in clean_cols[:8]:
        try:
            vals = sample_df[col].dropna().unique()[:3].tolist()
            sample_values[col] = [str(v)[:50] for v in vals]
        except Exception:
            sample_values[col] = []

    metadata = {
        "table_name": table_name,
        "original_filename": filename,
        "row_count": total_rows,
        "size_mb": round(size_mb, 2),
        "columns": clean_cols,
        "original_columns": original_cols,
        "sample_values": sample_values,
    }

    print(f"Ingested '{filename}' → '{table_name}' ({total_rows:,} rows, {len(clean_cols)} cols, {size_mb:.1f}MB)")
    return metadata


def build_schema_description(metadata: dict) -> str:
    cols = metadata["columns"]
    samples = metadata["sample_values"]
    filename = metadata["original_filename"]

    sample_text = ""
    for col, vals in list(samples.items())[:6]:
        if vals:
            sample_text += f"'{col}' (e.g. {', '.join(vals[:2])}), "

    description = (
        f"Table: {metadata['table_name']}. "
        f"Uploaded from file: {filename}. "
        f"Contains {metadata['row_count']:,} rows and {len(cols)} columns. "
        f"Columns: {', '.join(cols[:20])}{'...' if len(cols) > 20 else ''}. "
        f"Sample values — {sample_text.rstrip(', ')}."
    )
    return description


def index_uploaded_schema(metadata: dict):
    """Embeds the uploaded table's schema into Qdrant."""
    from sentence_transformers import SentenceTransformer
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
    import hashlib

    qdrant_url = os.environ.get("QDRANT_URL", "")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY", "")
    qdrant_path = "./qdrant_storage"
    collection_name = "schema_index"

    if qdrant_url and qdrant_api_key:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    else:
        client = QdrantClient(path=qdrant_path)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    description = build_schema_description(metadata)
    vector = model.encode(description).tolist()

    point_id = int(hashlib.md5(metadata["table_name"].encode()).hexdigest()[:8], 16)

    client.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "table": metadata["table_name"],
                    "columns": metadata["columns"],
                    "description": description,
                    "is_uploaded": True,
                    "original_filename": metadata["original_filename"],
                    "row_count": metadata["row_count"],
                },
            )
        ],
    )
    print(f"Schema for '{metadata['table_name']}' indexed into Qdrant.")


def list_uploaded_tables() -> list[dict]:
    """Returns all currently uploaded tables from the DB."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'uploaded_%'")
        )
        tables = [row[0] for row in result]

    info = []
    for table in tables:
        with engine.connect() as conn:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                cols_result = conn.execute(text(f"PRAGMA table_info({table})"))
                cols = [row[1] for row in cols_result]
                info.append({"table": table, "rows": count, "columns": cols})
            except Exception:
                pass
    return info
