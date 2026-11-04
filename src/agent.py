import re

import duckdb
import ollama

from db import DB_PATH, get_schema
from retriever import retrieve

SYSTEM_PROMPT = """You are a data analyst writing DuckDB SQL for an e-commerce database.
Rules:
- Use only tables and columns from the schema. Use exact column names.
- Follow the business definitions in the context.
- Return exactly one SQL query inside a ```sql code block. No explanation.
- Only SELECT or WITH queries. Never modify data."""


def build_prompt(question: str, schema: str, use_rag: bool = True) -> str:
    parts = [f"Database schema:\n{schema}"]
    if use_rag:
        hits = retrieve(question)
        context = "\n\n".join(hit["text"] for hit in hits)
        parts.append(f"Business context and examples:\n{context}")
    parts.append(f"Question: {question}")
    return "\n\n".join(parts)

LLM_MODEL = "qwen2.5-coder:7b"


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
MAX_RETRIES = 2


def ask(question: str, con, schema: str, use_rag: bool = True) -> dict:
    sql = generate_sql(question, schema, use_rag)
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            df = con.execute(sql).df()
            return {"sql": sql, "result": df, "attempts": attempt, "error": None}
        except duckdb.Error as e:
            if attempt > MAX_RETRIES:
                return {"sql": sql, "result": None, "attempts": attempt, "error": str(e)}
            sql = generate_sql(question, schema, use_rag, previous_sql=sql, error=str(e))

if __name__ == "__main__":
    con = duckdb.connect(DB_PATH, read_only=True)
    schema = get_schema(con)
    question = "What is the revenue per seller?"

    for use_rag in [False, True]:
        result = ask(question, con, schema, use_rag)
        print(f"\n===== RAG = {use_rag} =====")
        print(f"SQL: {result['sql']}")
        if result['error']:
            print(f"Error: {result['error']}")
        else:
            print(f"Result:\n{result['result'].head()}")

if __name__ == "__main__":
    con = duckdb.connect(DB_PATH, read_only=True)
    schema = get_schema(con)
    question = "What is the revenue per seller?"

    for use_rag in [False, True]:
        out = ask(question, con, schema, use_rag)
        print(f"\n===== RAG = {use_rag} | attempts: {out['attempts']} =====")
        print(out["sql"])
        if out["error"]:
            print("FAILED:", out["error"])
        else:
            print(out["result"].head())