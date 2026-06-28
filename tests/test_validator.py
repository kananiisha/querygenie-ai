import pytest
from unittest.mock import patch

from backend.agents.validator import validate_sql, generate_safe_sql, UnsafeQueryError


def test_valid_select_query():
    is_valid, reason = validate_sql("SELECT * FROM customers")
    assert is_valid
    assert reason == ""


def test_blocks_drop_table():
    is_valid, reason = validate_sql("DROP TABLE customers")
    assert not is_valid


def test_blocks_delete():
    is_valid, reason = validate_sql("DELETE FROM orders WHERE order_id = 1")
    assert not is_valid


def test_blocks_update():
    is_valid, reason = validate_sql("UPDATE customers SET city = 'Delhi'")
    assert not is_valid


def test_blocks_multiple_statements():
    is_valid, reason = validate_sql("SELECT * FROM customers; DROP TABLE customers;")
    assert not is_valid
    assert "Multiple statements" in reason


def test_blocks_empty_query():
    is_valid, reason = validate_sql("")
    assert not is_valid


@patch("backend.agents.validator.generate_sql")
def test_generate_safe_sql_returns_valid_query_on_first_try(mock_generate_sql):
    mock_generate_sql.return_value = "SELECT * FROM customers"
    schema_context = [{"table": "customers", "columns": ["customer_id"], "description": "..."}]

    sql = generate_safe_sql("Show all customers", schema_context)

    assert sql == "SELECT * FROM customers"
    assert mock_generate_sql.call_count == 1


@patch("backend.agents.validator.generate_sql")
def test_generate_safe_sql_retries_with_feedback_then_succeeds(mock_generate_sql):
    # First attempt is unsafe, second attempt (after feedback) is safe
    mock_generate_sql.side_effect = [
        "DROP TABLE customers",
        "SELECT * FROM customers",
    ]
    schema_context = [{"table": "customers", "columns": ["customer_id"], "description": "..."}]

    sql = generate_safe_sql("Show all customers", schema_context, max_retries=2)

    assert sql == "SELECT * FROM customers"
    assert mock_generate_sql.call_count == 2
    # Confirm the second call actually received feedback about the rejection
    second_call_kwargs = mock_generate_sql.call_args_list[1].kwargs
    assert "rejected" in second_call_kwargs.get("feedback", "").lower()


@patch("backend.agents.validator.generate_sql")
def test_generate_safe_sql_raises_after_max_retries(mock_generate_sql):
    mock_generate_sql.return_value = "DROP TABLE customers"
    schema_context = [{"table": "customers", "columns": ["customer_id"], "description": "..."}]

    with pytest.raises(UnsafeQueryError):
        generate_safe_sql("Show all customers", schema_context, max_retries=1)
