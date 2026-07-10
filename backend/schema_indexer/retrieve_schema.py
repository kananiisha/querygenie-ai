"""
Given a natural-language question, finds the most relevant table(s)
from the indexed schema using Qdrant.
Supports both local and Qdrant Cloud mode.
"""

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

from .index_schema import COLLECTION_NAME, EMBEDDING_MODEL, QDRANT_PATH

load_dotenv()

_model = None
_client = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_client():
    global _client
    if _client is None:
        qdrant_url = os.environ.get("QDRANT_URL", "")
        qdrant_api_key = os.environ.get("QDRANT_API_KEY", "")
        if qdrant_url and qdrant_api_key:
            _client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            _client = QdrantClient(path=QDRANT_PATH)
    return _client


def get_relevant_tables(question: str, top_k: int = 2) -> list[dict]:
    model = _get_model()
    client = _get_client()

    query_vector = model.encode(question).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
    ).points

    return [
        {
            "table": hit.payload["table"],
            "columns": hit.payload["columns"],
            "description": hit.payload["description"],
            "score": hit.score,
        }
        for hit in results
    ]


if __name__ == "__main__":
    test_question = "Which customers are from Mumbai?"
    matches = get_relevant_tables(test_question)
    for m in matches:
        print(f"{m['table']} (score={m['score']:.3f}) -> {m['columns']}")
