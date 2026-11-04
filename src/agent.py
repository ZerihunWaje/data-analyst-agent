import re

import duckdb
import ollama

from db import DB_PATH, get_schema
from retriever import retrieve

LLM_MODEL = "qwen2.5-coder:7b"
MAX_RETRIES = 2
MAX_ROWS = 20

SYSTEM_PROMPT = """You are a data analyst writing DuckDB SQL for an e-commerce database.
Rules:
- Use only tables and columns from the schema. Use exact column names.
- Follow the business definitions in the context.
- Return exactly one SQL query inside a ```sql code block. No explanation.
- Only SELECT or WITH queries. Never modify data."""

EXPLAIN_PROMPT = """You explain SQL query results to a business user.
Rules:
- 2-4 sentences, plain English, no SQL terms.
- Use only numbers that appear in the result. Never invent numbers.
- If only part of the result is shown, do not claim it is the full picture."""


def build_prompt(question: str, schema: str, use_rag: bool = True) -> str:
    parts = [f"Database schema:\n{schema}"]
    if use_rag:
        hits = retrieve(question)
        context = "\n\n".join(hit["text"] for hit in hits)
        parts.append(f"Business context and examples:\n{context}")
    parts.append(f"Question: {question}")
    return "\n\n".join(parts)


def extract_sql(text: str) -> str:
    match = re.search(r"```sql\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    sql = match.group(1) if match else text
    return sql.strip()


def generate_sql(
    question: str,
    schema: str,
    use_rag: bool = True,
    previous_sql: str | None = None,
    error: str | None = None,
) -> str:
    prompt = build_prompt(question, schema, use_rag)
    if error:
        prompt += (
            f"\n\nYour previous SQL failed:\n```sql\n{previous_sql}\n```\n"
            f"Error: {error}\nWrite a corrected query."
        )
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0, "num_ctx": 8192},
    )
    return extract_sql(response["message"]["content"])


def explain_result(question: str, sql: str, df) -> str:
    table = df.head(MAX_ROWS).to_string(index=False)
    prompt = (
        f"Question: {question}\n\n"
        f"SQL used:\n{sql}\n\n"
        f"Result ({len(df)} rows total, first {min(len(df), MAX_ROWS)} shown):\n{table}"
    )
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": EXPLAIN_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0, "num_ctx": 8192},
    )
    return response["message"]["content"].strip()


def ask(question: str, con, schema: str, use_rag: bool = True, explain: bool = True) -> dict:
    sql = generate_sql(question, schema, use_rag)
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            df = con.execute(sql).df()
            explanation = explain_result(question, sql, df) if explain else None
            return {"sql": sql, "result": df, "attempts": attempt,
                    "error": None, "explanation": explanation}
        except duckdb.Error as e:
            if attempt > MAX_RETRIES:
                return {"sql": sql, "result": None, "attempts": attempt,
                        "error": str(e), "explanation": None}
            sql = generate_sql(question, schema, use_rag, previous_sql=sql, error=str(e))


if __name__ == "__main__":
    con = duckdb.connect(DB_PATH, read_only=True)
    schema = get_schema(con)
    question = "What share of delivered orders arrived late?"

    out = ask(question, con, schema, use_rag=True)
    print(out["sql"])
    print(out["result"])
    print("\nEXPLANATION:\n", out["explanation"])