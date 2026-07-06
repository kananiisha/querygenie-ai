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

MODEL = "llama-3.3-70b-versatile"

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
"""


def explain_result(question: str, sql: str, results: list[dict]) -> str:
    """
    Takes the question, SQL, and raw DB results and returns
    a plain-English explanation.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

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

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()


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
