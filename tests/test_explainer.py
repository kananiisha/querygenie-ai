from unittest.mock import patch, MagicMock
from backend.agents.explainer import explain_result


@patch("backend.agents.explainer.Groq")
def test_explain_result_with_data(mock_groq_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        "There is 1 customer from Mumbai: Rohan Mehta."
    )
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client

    answer = explain_result(
        question="Which customers are from Mumbai?",
        sql="SELECT name FROM customers WHERE city = 'Mumbai'",
        results=[{"name": "Rohan Mehta"}],
    )

    assert "Rohan Mehta" in answer or len(answer) > 0


@patch("backend.agents.explainer.Groq")
def test_explain_result_empty_results(mock_groq_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        "There are no customers from the specified city."
    )
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client

    answer = explain_result(
        question="Which customers are from Paris?",
        sql="SELECT name FROM customers WHERE city = 'Paris'",
        results=[],
    )

    assert len(answer) > 0
