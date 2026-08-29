"""
Full agent pipeline with query result caching and confidence scoring.
"""

from backend.schema_indexer.retrieve_schema import get_relevant_tables
from backend.agents.validator import generate_safe_sql
from backend.agents.executor import execute_query
from backend.agents.explainer import explain_result

_query_cache: dict = {}
MAX_CACHE_SIZE = 100


def calculate_confidence(schema_context: list, sql: str, results: list, retry_count: int = 0) -> dict:
    """
    Calculates a confidence score (0-100) based on:
    - Schema retrieval score from Qdrant (how relevant the tables are)
    - Whether SQL passed validation on first try
    - Whether results are non-empty
    """
    scores = {}

    # 1. Schema retrieval confidence (0-40 points)
    if schema_context:
        avg_score = sum(s.get("score", 0) for s in schema_context) / len(schema_context)
        scores["schema"] = round(min(avg_score * 100, 40))
    else:
        scores["schema"] = 0

    # 2. Validation confidence (0-40 points)
    # Full marks if passed first try, deduct for retries
    scores["validation"] = max(40 - (retry_count * 15), 0)

    # 3. Result confidence (0-20 points)
    if results and len(results) > 0:
        scores["results"] = 20
    else:
        scores["results"] = 5  # empty result still valid, just less confident

    total = sum(scores.values())

    # Confidence label
    if total >= 85:
        label = "High"
        color = "green"
    elif total >= 60:
        label = "Medium"
        color = "orange"
    else:
        label = "Low"
        color = "red"

    return {
        "score": total,
        "label": label,
        "color": color,
        "breakdown": scores,
    }


def run_pipeline(question: str, table_hint: str | None = None) -> dict:
    """
    Runs the full 5-agent pipeline with caching and confidence scoring.
    """
    cache_key = f"{question.strip().lower()}::{table_hint or 'demo'}"
    if cache_key in _query_cache:
        print(f"Cache hit: '{question}'")
        cached = _query_cache[cache_key].copy()
        cached["cached"] = True
        return cached

    # Step 1: Retrieve schema
    schema_context = get_relevant_tables(question, top_k=2)

    if table_hint:
        hint_in_context = any(s["table"] == table_hint for s in schema_context)
        if not hint_in_context:
            schema_context = [s for s in schema_context if s["table"] != table_hint][:1]
            schema_context.insert(0, {
                "table": table_hint,
                "columns": [],
                "description": f"User uploaded table: {table_hint}",
                "score": 0.8,
            })

    # Step 2 + 3: Generate + validate SQL (track retries for confidence)
    retry_count = 0
    try:
        from backend.agents.validator import generate_safe_sql as _gen
        # Monkey-patch to count retries
        original_generate = __import__("backend.agents.sql_generator", fromlist=["generate_sql"]).generate_sql
        call_count = [0]
        def counting_generate(q, ctx, feedback=None):
            if feedback:
                call_count[0] += 1
            return original_generate(q, ctx, feedback=feedback)
        import backend.agents.sql_generator as _mod
        _mod.generate_sql = counting_generate
        sql = _gen(question, schema_context)
        _mod.generate_sql = original_generate
        retry_count = call_count[0]
    except Exception:
        sql = generate_safe_sql(question, schema_context)

    # Step 4: Execute
    results = execute_query(sql)

    # Step 5: Explain
    answer = explain_result(question, sql, results)

    # Step 6: Calculate confidence
    confidence = calculate_confidence(schema_context, sql, results, retry_count)

    output = {
        "question": question,
        "sql": sql,
        "results": results,
        "answer": answer,
        "confidence": confidence,
        "cached": False,
    }

    if len(_query_cache) >= MAX_CACHE_SIZE:
        oldest_key = next(iter(_query_cache))
        del _query_cache[oldest_key]
    _query_cache[cache_key] = output.copy()

    return output


def clear_cache():
    _query_cache.clear()
    print("Query cache cleared.")


if __name__ == "__main__":
    out = run_pipeline("Which customers are from Mumbai?")
    print(f"SQL: {out['sql']}")
    print(f"Answer: {out['answer']}")
    print(f"Confidence: {out['confidence']['score']}% ({out['confidence']['label']})")