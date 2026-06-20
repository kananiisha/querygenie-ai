"""
Embeds each table's description (from schema_metadata.py) and stores it
in a local Qdrant collection so it can be semantically searched later.

Run standalone:
    python -m backend.schema_indexer.index_schema
"""

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from .schema_metadata import SCHEMA_METADATA

COLLECTION_NAME = "schema_index"
QDRANT_PATH = "./qdrant_storage"  # local file-based Qdrant, no Docker needed for dev
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # small, free, runs locally


def build_schema_index():
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = QdrantClient(path=QDRANT_PATH)

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
