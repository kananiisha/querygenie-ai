"""
SQL Generator Agent: takes a natural-language question plus the relevant
schema context (from the Retriever agent) and asks an LLM to write a
single safe SELECT query.

Requires GROQ_API_KEY in your .env file (free tier at console.groq.com).
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a SQL generator for a PostgreSQL e-commerce database.
Rules:
- Only write SELECT queries. Never write INSERT, UPDATE, DELETE, DROP, or ALTER.
- Only use the tables and columns provided in the schema context below.
- Return ONLY the raw SQL query. No explanation, no markdown, no backticks.
"""


def _build_schema_context_text(schema_context: list[dict]) -> str:
    lines = []
    for table in schema_context:
        lines.append(f"Table: {table['table']}")
        lines.append(f"Columns: {', '.join(table['columns'])}")
        lines.append(f"Description: {table['description']}")
        lines.append("")
    return "\n".join(lines)


def generate_sql(question: str, schema_context: list[dict]) -> str:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

    schema_text = _build_schema_context_text(schema_context)
    user_prompt = (
        f"Schema context:\n{schema_text}\n\n"
        f"Question: {question}\n\n"
        f"Write a single PostgreSQL SELECT query to answer this question."
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()
    # Defensive cleanup in case the model wraps it in markdown anyway
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


if __name__ == "__main__":
    from backend.schema_indexer.retrieve_schema import get_relevant_tables

    test_question = "Which customers are from Mumbai?"
    context = get_relevant_tables(test_question, top_k=2)
    sql = generate_sql(test_question, context)
    print(f"Question: {test_question}")
    print(f"Generated SQL:\n{sql}")
