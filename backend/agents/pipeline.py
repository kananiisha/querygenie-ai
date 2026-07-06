"""
Full agent pipeline — ties everything together:
1. Schema Retriever → finds relevant tables
2. SQL Generator → writes the query
3. Validator → checks it's safe, retries if not
4. Executor → runs the query against the DB
5. Explainer → turns results into plain English

This is the single function Mokshi calls from the /query endpoint.
"""

from backend.schema_indexer.retrieve_schema import get_relevant_tables
from backend.agents.validator import generate_safe_sql
from backend.agents.executor import execute_query
from backend.agents.explainer import explain_result


def run_pipeline(question: str) -> dict:
    """
    Runs the full pipeline for a user question.
    Returns a dict with question, sql, results, and answer.
    """
    # Step 1: Retrieve relevant schema context
    schema_context = get_relevant_tables(question, top_k=2)

    # Step 2 + 3: Generate + validate SQL
    sql = generate_safe_sql(question, schema_context)

    # Step 4: Execute query
    results = execute_query(sql)

    # Step 5: Explain results in plain English
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
        "Which product category has the most orders?",
    ]

    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Question: {q}")
        output = run_pipeline(q)
        print(f"SQL: {output['sql']}")
        print(f"Results: {output['results']}")
        print(f"Answer: {output['answer']}")
