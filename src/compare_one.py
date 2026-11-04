import sys

import duckdb
import pandas as pd

from db import DB_PATH
from evaluate import load_questions

qid = int(sys.argv[1])
con = duckdb.connect(DB_PATH, read_only=True)

gold_sql = load_questions()[qid - 1]["gold_sql"]
print(f"===== GOLD Q{qid} =====\n{gold_sql}")
print(con.execute(gold_sql).df())

results = pd.read_csv("eval/results.csv")
for _, row in results[results["id"] == qid].iterrows():
    mode = "RAG" if row["use_rag"] else "BASE"
    print(f"\n===== {mode} (correct={row['correct']}) =====\n{row['sql']}")
    print(con.execute(row["sql"]).df())