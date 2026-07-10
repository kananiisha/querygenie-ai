"""
Embeds each table's description and stores it in Qdrant.
Supports both local mode (dev) and Qdrant Cloud (production).

Run: python -m backend.schema_indexer.index_schema
"""

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from .schema_metadata import SCHEMA_METADATA

load_dotenv()

COLLECTION_NAME = "schema_index"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
QDRANT_PATH = "./qdrant_storage"


def get_qdrant_client() -> QdrantClient:
    """
    Returns Qdrant Cloud client if QDRANT_URL and QDRANT_API_KEY are set,
    otherwise falls back to local file-based storage for dev.
    """
    qdrant_url = os.environ.get("QDRANT_URL", "")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY", "")

    if qdrant_url and qdrant_api_key:
        print(f"Connecting to Qdrant Cloud: {qdrant_url}")
        return QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    else:
        print(f"Using local Qdrant storage: {QDRANT_PATH}")
        return QdrantClient(path=QDRANT_PATH)


def build_schema_index():
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = get_qdrant_client()

    vector_size = model.get_embedding_dimension()

    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    points = []
    for idx, entry in enumerate(SCHEMA_METADATA):
        text = f"{entry['description']} Columns: {', '.join(entry['columns'])}."
        vector = model.encode(text).tolist()
        points.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload={
                    "table": entry["table"],
                    "columns": entry["columns"],
                    "description": entry["description"],
                },
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Indexed {len(points)} tables into Qdrant collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    build_schema_index()
