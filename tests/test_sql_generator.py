from unittest.mock import patch, MagicMock

from backend.agents.sql_generator import generate_sql


@patch("backend.agents.sql_generator.Groq")
def test_generate_sql_returns_select_query(mock_groq_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        "SELECT * FROM customers WHERE city = 'Mumbai';"
    )
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client

    schema_context = [
        {
            "table": "customers",
            "columns": ["customer_id", "name", "city"],
            "description": "Stores customer details.",
        }
    ]

    sql = generate_sql("Which customers are from Mumbai?", schema_context)

    assert sql.strip().upper().startswith("SELECT")
    assert "customers" in sql.lower()


@patch("backend.agents.sql_generator.Groq")
def test_generate_sql_strips_markdown_formatting(mock_groq_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        "```sql\nSELECT * FROM customers;\n```"
    )
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client

    schema_context = [{"table": "customers", "columns": ["customer_id"], "description": "..."}]
    sql = generate_sql("Show all customers", schema_context)

    assert "```" not in sql
