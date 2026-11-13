"""
Validator / Safety Agent: checks that generated SQL is safe to execute
before it ever touches the real database. Blocks destructive or
multi-statement queries, restricts which tables can be read on a public
deployment, and retries the SQL Generator with feedback if a query fails
validation.
"""

import os
import re

from backend.agents.sql_generator import generate_sql

FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE", "MERGE",
]

# Tables a visitor may read on the public demo. The app's own tables
# (users, query logs) are deliberately not on this list.
DEMO_TABLES = {"customers", "products", "orders", "order_items", "payments"}

# Always blocked, in every environment: SQLite internals and risky functions.
_SYSTEM_NAMES = re.compile(r"\b(sqlite_\w+|pragma_\w+)", re.IGNORECASE)
_RISKY_FUNCTIONS = re.compile(
    r"\b(load_extension|readfile|writefile|randomblob|zeroblob)\s*\(", re.IGNORECASE
)

_AUTO = object()  # sentinel: "decide the table allowlist from the environment"


def _is_production() -> bool:
    return bool(os.environ.get("RENDER")) or os.environ.get("ENV", "").lower() == "production"


def get_allowed_tables() -> set[str] | None:
    """
    Which tables queries may touch.
    - ALLOWED_TABLES env var (comma separated) wins everywhere.
    - On a deployment (RENDER=true or ENV=production): the demo tables only.
    - Local development: None, meaning no table restriction.
    """
    configured = os.environ.get("ALLOWED_TABLES", "").strip()
    if configured:
        return {t.strip().lower() for t in configured.split(",") if t.strip()}
    if _is_production():
        return set(DEMO_TABLES)
    return None


def normalize_sqlite_sql(sql: str) -> str:
    """Convert common PostgreSQL cast syntax into SQLite-compatible CAST(...) calls."""
    if not sql:
        return ""

    normalized = sql.strip()
    normalized = re.sub(
        r"(?P<expr>NULL|TRUE|FALSE|CURRENT_DATE|CURRENT_TIMESTAMP|[A-Za-z_][A-Za-z0-9_\"\.]*(?:\.[A-Za-z_][A-Za-z0-9_\"\.]*)*|\([^)]*\)|'[^']*')::(?P<type>[A-Za-z_]+(?:\s*\([^)]*\))?)",
        lambda m: f"CAST({m.group('expr')} AS {m.group('type')})",
        normalized,
        flags=re.IGNORECASE,
    )
    return normalized


class UnsafeQueryError(Exception):
    """Raised when no safe SQL query could be generated after retries."""
    pass


def _check_tables(cleaned_sql: str, allowed: set[str]) -> str:
    """
    Parses the query and returns a rejection reason if it reads any table
    outside `allowed`; returns "" if every table is allowed. Fails closed:
    a query that cannot be parsed is rejected.
    """
    try:
        import sqlglot
        from sqlglot import exp

        statements = sqlglot.parse(cleaned_sql, read="sqlite")
    except Exception:
        return "The query could not be parsed safely."

    if len(statements) != 1 or statements[0] is None:
        return "Only one query is allowed."

    tree = statements[0]
    cte_names = {c.alias_or_name.lower() for c in tree.find_all(exp.CTE)}

    for table in tree.find_all(exp.Table):
        if not isinstance(table.this, exp.Identifier):
            return "Table-valued functions are not allowed."
        name = table.name.lower()
        if name in cte_names and not table.args.get("db"):
            continue  # reference to a WITH-defined name; its body is checked separately
        if name not in allowed:
            return (
                f"Table '{table.name}' is not available. "
                f"Use only these tables: {', '.join(sorted(allowed))}."
            )
    return ""


def validate_sql(sql: str, allowed_tables=_AUTO) -> tuple[bool, str]:
    """
    Returns (is_valid, reason). reason is "" if valid, otherwise
    explains why the query was rejected.

    allowed_tables: a set of table names to restrict the query to, None for
    no restriction, or omitted to decide from the environment.
    """
    if not sql or not sql.strip():
        return False, "Empty query."

    normalized = normalize_sqlite_sql(sql)
    cleaned = normalized.strip().rstrip(";")

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

    # SQLite internals and risky functions are never needed for business questions
    if _SYSTEM_NAMES.search(cleaned):
        return False, "Access to database system tables is not allowed."
    if _RISKY_FUNCTIONS.search(cleaned):
        return False, "A function that is not allowed was used."

    # Table allowlist (public deployment)
    if allowed_tables is _AUTO:
        allowed_tables = get_allowed_tables()
    if allowed_tables is not None:
        reason = _check_tables(cleaned, {t.lower() for t in allowed_tables})
        if reason:
            return False, reason

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
        sql = normalize_sqlite_sql(sql)
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
        "SELECT email, hashed_password FROM users",
        "SELECT name FROM sqlite_master",
    ]
    for case in test_cases:
        valid, reason = validate_sql(case, allowed_tables=DEMO_TABLES)
        status = "VALID  " if valid else "BLOCKED"
        print(f"{status} | {case!r} | {reason}")