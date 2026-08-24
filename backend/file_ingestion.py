"""
File Ingestion Module
Handles CSV/Excel file uploads, creates SQLite tables dynamically,
and indexes the schema into Qdrant for the agent to use.
"""

import os
import re
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./querygenie_dev.db")
UPLOAD_TABLE_PREFIX = "uploaded_"


def sanitize_column_name(col: str) -> str:
    """Convert column names to safe SQL identifiers."""
    col = col.strip().lower()
    col = re.sub(r"[^a-z0-9_]", "_", col)
    col = re.sub(r"_+", "_", col)
    col = col.strip("_")
    if col[0].isdigit():
        col = "col_" + col
    return col


def sanitize_table_name(filename: str) -> str:
    """Convert filename to a safe SQL table name."""
    name = os.path.splitext(filename)[0]
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")
    return UPLOAD_TABLE_PREFIX + name


def ingest_file(file_bytes: bytes, filename: str) -> dict:
    """
    Reads a CSV or Excel file, creates a SQLite table from it,
    and returns metadata about the table for schema indexing.
    """
    # Read file into DataFrame
    if filename.endswith(".csv"):
        import io
        df = pd.read_csv(io.BytesIO(file_bytes))
    elif filename.endswith((".xlsx", ".xls")):
        import io
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        raise ValueError(f"Unsupported file type: {filename}. Use CSV or Excel.")

    # Sanitize column names
    original_cols = df.columns.tolist()
    df.columns = [sanitize_column_name(str(c)) for c in df.columns]
    clean_cols = df.columns.tolist()

    # Create table name
    table_name = sanitize_table_name(filename)

    # Write to SQLite
    engine = create_engine(DATABASE_URL)
    df.to_sql(table_name, engine, if_exists="replace", index=False)

    # Build metadata for schema indexing
    col_info = []
    for orig, clean in zip(original_cols, clean_cols):
        col_info.append({"original": str(orig), "clean": clean})

    sample_values = {}
    for col in clean_cols[:5]:  # sample first 5 columns
        vals = df[col].dropna().unique()[:3].tolist()
        sample_values[col] = [str(v) for v in vals]

    metadata = {
        "table_name": table_name,
        "original_filename": filename,
        "row_count": len(df),
        "columns": clean_cols,
        "column_info": col_info,
        "sample_values": sample_values,
    }

    print(f"Ingested '{filename}' → table '{table_name}' ({len(df)} rows, {len(clean_cols)} columns)")
    return metadata


def build_schema_description(metadata: dict) -> str:
    """
    Builds a natural-language description of the uploaded table
    for embedding into Qdrant.
    """
    cols = metadata["columns"]
    samples = metadata["sample_values"]
    filename = metadata["original_filename"]

    sample_text = ""
    for col, vals in samples.items():
        if vals:
            sample_text += f"'{col}' (e.g. {', '.join(vals)}), "

    description = (
        f"Table: {metadata['table_name']}. "
        f"Uploaded from file: {filename}. "
        f"Contains {metadata['row_count']} rows and {len(cols)} columns. "
        f"Columns: {', '.join(cols)}. "
        f"Sample values — {sample_text.rstrip(', ')}."
    )
    return description


def index_uploaded_schema(metadata: dict):
    """
    Embeds the uploaded table's schema description into Qdrant
    so the Schema Retriever Agent can find it.
    """
    from sentence_transformers import SentenceTransformer
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct

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

    # Use a large ID to avoid colliding with the 5 base tables (IDs 0-4)
    import hashlib
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
                },
            )
        ],
    )
    print(f"Schema for '{metadata['table_name']}' indexed into Qdrant.")
