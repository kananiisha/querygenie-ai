"""
Given a natural-language question, finds the most relevant table(s)
from the indexed schema. This is what the Schema Retriever Agent
calls before the SQL Generator Agent writes a query.
"""

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

from .index_schema import COLLECTION_NAME, QDRANT_PATH, EMBEDDING_MODEL

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
        _client = QdrantClient(path=QDRANT_PATH)
    return _client


def get_relevant_tables(question: str, top_k: int = 2) -> list[dict]:
    """
    Returns the top_k most relevant tables (with columns + description)
    for a given natural-language question.
    """
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
    # Quick manual test
    test_question = "Which customers are from Mumbai?"
    matches = get_relevant_tables(test_question)
    for m in matches:
        print(f"{m['table']} (score={m['score']:.3f}) -> {m['columns']}")
