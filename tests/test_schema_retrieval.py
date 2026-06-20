from backend.schema_indexer.index_schema import build_schema_index
from backend.schema_indexer.retrieve_schema import get_relevant_tables


def test_retrieves_correct_table_for_customer_question():
    build_schema_index()
    results = get_relevant_tables("Which customers are from Mumbai?", top_k=1)
    assert results[0]["table"] == "customers"


def test_retrieves_correct_table_for_revenue_question():
    results = get_relevant_tables("What is our total revenue?", top_k=1)
    assert results[0]["table"] in ("payments", "order_items")
