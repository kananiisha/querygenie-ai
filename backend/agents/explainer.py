"""
Explainer Agent: takes the original question, the generated SQL,
and the raw query result (list of dicts) and returns a plain-English
answer using the Groq LLM.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are a helpful data analyst assistant.
You will be given:
1. A business question asked by a non-technical user
2. The SQL query that was run to answer it
3. The raw results from the database

Your job is to write a clear, concise plain-English answer (2-4 sentences max).
- Use simple language, no SQL jargon
- Include specific numbers/names from the results
- If results are empty, say so clearly
- Never make up data not present in the results
- Prefer concise natural statements like 'There are 350 customers from USA.'
"""


def fallback_explain_result(question: str, sql: str, results: list[dict]) -> str:
    """Return a natural-language answer when LLM access is unavailable or fails."""
    if not results:
        return "No matching records were found for that question."

    q = (question or "").lower()
    first = results[0]

    if "how many" in q or "count" in q or "total" in q:
        # If the row already exposes a count/total, use it directly.
        for key in ["count", "total", "total_count", "customer_count", "order_count"]:
            if key in first:
                value = first[key]
                country = first.get("country") or first.get("city") or first.get("region")
                if country:
                    return f"There are {value} customers from {country}."
                return f"There are {value} matching records for your question."

        if len(results) == 1:
            for key, value in first.items():
                if isinstance(value, (int, float)) and key.lower() not in {"id", "customer_id", "order_id"}:
                    country = first.get("country") or first.get("city") or first.get("region")
                    if country:
                        return f"There are {value} customers from {country}."
                    return f"There are {value} {key.replace('_', ' ')} records."

        return f"There are {len(results)} matching records for your question."

    if len(results) == 1:
        row = first
        if "country" in row and isinstance(row.get("country"), str):
            return f"There are {len(results)} matching records from {row['country']}."
        if "city" in row and isinstance(row.get("city"), str):
            return f"There are {len(results)} matching records in {row['city']}."
        return f"The result shows {row} for your question."

    if len(results) <= 5:
        return f"The query returned {len(results)} matching records: {results[:3]}."

    return f"The query returned {len(results)} matching records. Here are the first few: {results[:3]}."


def explain_result(question: str, sql: str, results: list[dict]) -> str:
    """
    Takes the question, SQL, and raw DB results and returns
    a plain-English explanation.
    """
    if not results:
        return fallback_explain_result(question, sql, results)

    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    except Exception:
        return fallback_explain_result(question, sql, results)

    if not results:
        results_text = "The query returned no results."
    else:
        results_text = json.dumps(results[:10], indent=2, default=str)

    user_prompt = (
        f"Question: {question}\n\n"
        f"SQL query that was run:\n{sql}\n\n"
        f"Database results:\n{results_text}\n\n"
        f"Write a plain-English answer to the question based on these results."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=300,
        )
        answer = response.choices[0].message.content.strip()
        if answer:
            return answer
    except Exception:
        pass

    return fallback_explain_result(question, sql, results)


if __name__ == "__main__":
    # Quick manual test with fake results
    test_question = "Which customers are from Mumbai?"
    test_sql = "SELECT customer_id, name, email FROM customers WHERE city = 'Mumbai'"
    test_results = [
        {"customer_id": 2, "name": "Rohan Mehta", "email": "rohan.mehta@mail.com"},
    ]

    answer = explain_result(test_question, test_sql, test_results)
    print(f"Question: {test_question}")
    print(f"Answer: {answer}")
