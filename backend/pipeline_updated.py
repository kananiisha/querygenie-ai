"""
Updated pipeline.py — supports table_hint for uploaded datasets
Replace backend/agents/pipeline.py with this
"""

from backend.schema_indexer.retrieve_schema import get_relevant_tables
from backend.agents.validator import generate_safe_sql
from backend.agents.executor import execute_query
from backend.agents.explainer import explain_result


def run_pipeline(question: str, table_hint: str | None = None) -> dict:
    """
    Runs the full 5-agent pipeline.
    If table_hint is provided (uploaded dataset), prioritizes that table
    in the schema retrieval step.
    """
    # Step 1: Retrieve relevant schema context
    schema_context = get_relevant_tables(question, top_k=2)

    # If a table hint is provided, make sure that table is in context
    if table_hint:
        hint_in_context = any(s["table"] == table_hint for s in schema_context)
        if not hint_in_context:
            # Force the uploaded table into context
            schema_context = [
                s for s in schema_context
                if s["table"] != table_hint
            ][:1]  # keep 1 from search
            # Add hint table info
            schema_context.insert(0, {
                "table": table_hint,
                "columns": [],  # executor will still work
                "description": f"User uploaded table: {table_hint}",
                "score": 1.0,
            })

    # Step 2 + 3: Generate + validate SQL
    sql = generate_safe_sql(question, schema_context)

    # Step 4: Execute query
    results = execute_query(sql)

    # Step 5: Explain results
    answer = explain_result(question, sql, results)

    return {
        "question": question,
        "sql": sql,
        "results": results,
        "answer": answer,
    }


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
