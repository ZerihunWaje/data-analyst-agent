import datetime
import math
import re
from decimal import Decimal
from pathlib import Path

import duckdb
import pandas as pd

from agent import ask
from db import DB_PATH, get_schema

QUESTIONS_FILE = Path("eval/questions.md")
RESULTS_FILE = Path("eval/results.csv")


def load_questions() -> list[dict]:
    text = QUESTIONS_FILE.read_text(encoding="utf-8")
    items = []
    for chunk in text.split("## Question:")[1:]:
        question = chunk.strip().splitlines()[0].strip()
        match = re.search(r"```sql\s*\n(.*?)```", chunk, re.DOTALL | re.IGNORECASE)
        items.append({"question": question, "gold_sql": match.group(1).strip()})
    if not items:
        raise ValueError(f"No questions found in {QUESTIONS_FILE}")
    return items


def normalize(value):
    if isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, datetime.date):
        return str(value)[:10]  # compare dates only: 2017-11-01
    return str(value)


def column_values(series: pd.Series) -> list:
    values = [normalize(v) for v in series.tolist()]
    return sorted(values, key=lambda v: (isinstance(v, str), v))


def values_equal(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float):
        return math.isclose(a, b, rel_tol=0.01)
    return a == b


def results_match(pred: pd.DataFrame | None, gold: pd.DataFrame) -> bool:
    if pred is None or len(pred) != len(gold):
        return False
    pred_cols = [column_values(pred.iloc[:, i]) for i in range(pred.shape[1])]
    for i in range(gold.shape[1]):
        gold_col = column_values(gold.iloc[:, i])
        if not any(all(values_equal(g, p) for g, p in zip(gold_col, pc)) for pc in pred_cols):
            return False
    return True


def main() -> None:
    con = duckdb.connect(DB_PATH, read_only=True)
    schema = get_schema(con)
    questions = load_questions()
    rows = []

    for use_rag in [False, True]:
        label = "RAG " if use_rag else "BASE"
        for i, item in enumerate(questions, 1):
            gold = con.execute(item["gold_sql"]).df()
            out = ask(item["question"], con, schema, use_rag, explain=False)
            correct = results_match(out["result"], gold)
            rows.append({
                "use_rag": use_rag, "id": i, "question": item["question"],
                "correct": correct, "attempts": out["attempts"],
                "error": out["error"], "sql": out["sql"],
            })
            print(f"[{label}] Q{i:02d} {'PASS' if correct else 'FAIL'}  {item['question']}")

    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_FILE, index=False)
    summary = df.groupby("use_rag").agg(
        accuracy=("correct", "mean"),
        avg_attempts=("attempts", "mean"),
        failed_sql=("error", lambda s: s.notna().sum()),
    )
    print("\n", summary)
    con.close()


if __name__ == "__main__":
    main()