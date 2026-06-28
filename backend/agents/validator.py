"""
Validator / Safety Agent: checks that generated SQL is safe to execute
before it ever touches the real database. Blocks destructive or
multi-statement queries, and retries the SQL Generator with feedback
if a query fails validation.
"""

import re

from backend.agents.sql_generator import generate_sql

FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE", "MERGE",
]


class UnsafeQueryError(Exception):
    """Raised when no safe SQL query could be generated after retries."""
    pass


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Returns (is_valid, reason). reason is "" if valid, otherwise
    explains why the query was rejected.
    """
    if not sql or not sql.strip():
        return False, "Empty query."

    cleaned = sql.strip().rstrip(";")

    # Block multiple statements (stacked queries / injection attempt)
    if ";" in cleaned:
        return False, "Multiple statements detected \u2014 only one query is allowed."

    # Must start with SELECT
    first_word = cleaned.split()[0].upper()
    if first_word != "SELECT":
        return False, f"Query must start with SELECT, found '{first_word}'."

    # Block destructive/forbidden keywords anywhere in the query
    upper_sql = cleaned.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            return False, f"Forbidden keyword detected: {keyword}."

    return True, ""


def generate_safe_sql(question: str, schema_context: list[dict], max_retries: int = 2) -> str:
    """
    Calls the SQL Generator, validates the result, and retries WITH
    FEEDBACK if the query fails validation. Raises UnsafeQueryError if
    no safe query is produced within max_retries attempts.
    """
    feedback = None
    last_reason = ""

    for attempt in range(max_retries + 1):
        sql = generate_sql(question, schema_context, feedback=feedback)
        is_valid, reason = validate_sql(sql)
        if is_valid:
            return sql
        last_reason = reason
        feedback = (
            f"Your previous query was rejected: {reason} "
            f"Please write a corrected SELECT-only query."
        )

    raise UnsafeQueryError(
        f"Could not generate a safe query after {max_retries + 1} attempts. "
        f"Last rejection reason: {last_reason}"
    )


if __name__ == "__main__":
    from backend.schema_indexer.retrieve_schema import get_relevant_tables

    test_question = "Which customers are from Mumbai?"
    context = get_relevant_tables(test_question, top_k=2)
    safe_sql = generate_safe_sql(test_question, context)
    print(f"Question: {test_question}")
    print(f"Safe SQL:\n{safe_sql}")

    print("\n--- Validator self-tests ---")
    test_cases = [
        "SELECT * FROM customers",
        "DROP TABLE customers",
        "SELECT * FROM customers; DROP TABLE customers;",
        "DELETE FROM orders WHERE order_id = 1",
        "UPDATE customers SET city = 'Delhi'",
    ]
    for case in test_cases:
        valid, reason = validate_sql(case)
        status = "VALID  " if valid else "BLOCKED"
        print(f"{status} | {case!r} | {reason}")
