"""
Full agent pipeline with query result caching for speed.
"""

from functools import lru_cache
from backend.schema_indexer.retrieve_schema import get_relevant_tables
from backend.agents.validator import generate_safe_sql
from backend.agents.executor import execute_query
from backend.agents.explainer import explain_result

# Cache stores last 100 unique questions
_query_cache: dict = {}
MAX_CACHE_SIZE = 100


def run_pipeline(question: str, table_hint: str | None = None) -> dict:
    """
    Runs the full 5-agent pipeline.
    Caches results for repeated identical questions.
    """
    # Check cache first
    cache_key = f"{question.strip().lower()}::{table_hint or 'demo'}"
    if cache_key in _query_cache:
        print(f"Cache hit: '{question}'")
        cached = _query_cache[cache_key].copy()
        cached["cached"] = True
        return cached

    # Step 1: Retrieve relevant schema context
    schema_context = get_relevant_tables(question, top_k=2)

    # Force uploaded table into context if hint provided
    if table_hint:
        hint_in_context = any(s["table"] == table_hint for s in schema_context)
        if not hint_in_context:
            schema_context = [s for s in schema_context if s["table"] != table_hint][:1]
            schema_context.insert(0, {
                "table": table_hint,
                "columns": [],
                "description": f"User uploaded table: {table_hint}",
                "score": 1.0,
            })

    # Step 2 + 3: Generate + validate SQL
    sql = generate_safe_sql(question, schema_context)

    # Step 4: Execute query
    results = execute_query(sql)

    # Step 5: Explain results
    answer = explain_result(question, sql, results)

    output = {
        "question": question,
        "sql": sql,
        "results": results,
        "answer": answer,
        "cached": False,
    }

    # Store in cache, evict oldest if full
    if len(_query_cache) >= MAX_CACHE_SIZE:
        oldest_key = next(iter(_query_cache))
        del _query_cache[oldest_key]
    _query_cache[cache_key] = output.copy()

    return output


def clear_cache():
    """Call this when new data is uploaded to invalidate stale results."""
    _query_cache.clear()
    print("Query cache cleared.")


if __name__ == "__main__":
    test_questions = [
        "Which customers are from Mumbai?",
        "What is the total revenue from successful payments?",
    ]
    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        out = run_pipeline(q)
        print(f"SQL: {out['sql']}")
        print(f"Answer: {out['answer']}")
        print(f"Cached: {out['cached']}")