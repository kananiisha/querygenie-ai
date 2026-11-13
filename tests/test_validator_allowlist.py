"""
Tests for the validator's table allowlist and always-on blocks.
These pass allowed_tables explicitly, so they do not depend on environment variables,
except the two tests that check the environment-based default.
"""

import pytest

from backend.agents.validator import DEMO_TABLES, get_allowed_tables, validate_sql


@pytest.mark.parametrize("sql", [
    "SELECT COUNT(*) FROM customers",
    "SELECT name FROM customers WHERE city = 'Mumbai'",
    "SELECT * FROM Customers",
    "SELECT DISTINCT c.name FROM customers c JOIN orders o ON o.customer_id = c.customer_id",
    "SELECT p.category, SUM(oi.quantity * oi.unit_price) FROM order_items oi "
    "JOIN products p ON p.product_id = oi.product_id GROUP BY p.category",
    "SELECT COUNT(*) FROM (SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) > 1) t",
    "SELECT order_id FROM order_items GROUP BY order_id HAVING SUM(quantity * unit_price) > "
    "(SELECT AVG(t) FROM (SELECT SUM(quantity * unit_price) AS t FROM order_items GROUP BY order_id) x)",
    "SELECT substr(signup_date, 1, 4), COUNT(*) FROM customers GROUP BY 1",
    "SELECT * FROM main.customers",
])
def test_demo_table_queries_are_allowed(sql):
    ok, reason = validate_sql(sql, allowed_tables=DEMO_TABLES)
    assert ok, reason


@pytest.mark.parametrize("sql", [
    "SELECT * FROM users",
    'SELECT * FROM "users"',
    "SELECT * FROM [users]",
    "SELECT * FROM `users`",
    "SELECT * FROM main.users",
    "SELECT * FROM query_logs",
    "SELECT email, hashed_password FROM users",
    "SELECT * FROM customers c, users u",
    "SELECT c.name FROM customers c JOIN users u ON u.id = c.customer_id",
    "SELECT (SELECT hashed_password FROM users LIMIT 1) FROM customers",
    "SELECT * FROM customers WHERE name IN (SELECT email FROM users)",
    "SELECT * FROM (SELECT * FROM users) t",
    "SELECT name FROM customers UNION SELECT hashed_password FROM users",
    "SELECT * FROM (WITH x AS (SELECT * FROM users) SELECT * FROM x)",
    "SELECT * FROM json_each('[1,2]')",
    "SELECT * FROM sqlite_master",
    "SELECT * FROM pragma_table_info('users')",
    "SELECT zeroblob(1000000000)",
    "SELECT load_extension('x')",
])
def test_non_demo_tables_and_internals_are_blocked(sql):
    ok, reason = validate_sql(sql, allowed_tables=DEMO_TABLES)
    assert not ok
    assert reason


@pytest.mark.parametrize("sql", [
    "DROP TABLE customers",
    "SELECT * FROM customers; DROP TABLE customers;",
    "DELETE FROM orders WHERE order_id = 1",
    "UPDATE customers SET city = 'Delhi'",
    "SELECT FROM WHERE ((",
])
def test_unsafe_and_unparseable_queries_are_still_blocked(sql):
    ok, _ = validate_sql(sql, allowed_tables=DEMO_TABLES)
    assert not ok


def test_internals_blocked_even_without_allowlist():
    assert not validate_sql("SELECT * FROM sqlite_master", allowed_tables=None)[0]
    assert not validate_sql("SELECT zeroblob(1000000000)", allowed_tables=None)[0]
    assert validate_sql("SELECT * FROM users", allowed_tables=None)[0]  # local dev: no table restriction


def test_default_allowlist_follows_environment(monkeypatch):
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("ALLOWED_TABLES", raising=False)

    monkeypatch.delenv("RENDER", raising=False)
    assert get_allowed_tables() is None
    assert validate_sql("SELECT * FROM users")[0]

    monkeypatch.setenv("RENDER", "true")
    assert get_allowed_tables() == set(DEMO_TABLES)
    assert not validate_sql("SELECT * FROM users")[0]
    assert validate_sql("SELECT COUNT(*) FROM customers")[0]

    monkeypatch.setenv("ALLOWED_TABLES", "customers, my_upload")
    assert get_allowed_tables() == {"customers", "my_upload"}
    assert validate_sql("SELECT * FROM my_upload")[0]
    assert not validate_sql("SELECT * FROM orders")[0]
