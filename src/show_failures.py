import pandas as pd

df = pd.read_csv("eval/results.csv")
failures = df[~df["correct"] & df["id"].isin([17, 7, 19])]

for _, row in failures.iterrows():
    mode = "RAG" if row["use_rag"] else "BASE"
    print(f"\n===== [{mode}] Q{row['id']}: {row['question']} =====")
    print(row["sql"])