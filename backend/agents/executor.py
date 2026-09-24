"""
Query Executor: runs a validated SQL query against the database
and returns results as a list of dicts.
"""

import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Use the same DB as the main app
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./querygenie_dev.db")


def normalize_sqlite_sql(sql: str) -> str:
    """Convert PostgreSQL cast syntax into SQLite-compatible CAST(...) calls."""
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


def execute_query(sql: str) -> list[dict]:
    """
    Executes a SELECT query and returns results as a list of dicts.
    Raises an exception if the query fails.
    """
    safe_sql = normalize_sqlite_sql(sql)
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text(safe_sql))
        columns = list(result.keys())
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]


if __name__ == "__main__":
    test_sql = "SELECT name, city FROM customers WHERE city = 'Mumbai'"
    results = execute_query(test_sql)
    print(f"Results: {results}")
