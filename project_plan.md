# Data Analyst AI Agent – Project Plan

## Goal
Answer business questions in plain English on a real e-commerce database, using RAG to ground SQL generation. Show measurable accuracy improvement with RAG vs without.

## Steps
1. Setup: Ollama + models, venv, packages, test LLM call  [X]
2. Data: load Olist CSVs into DuckDB, explore tables and joins  [X]
3. Knowledge base: write table docs, column meanings, metric definitions, 10–15 example question->SQL pairs  [X]
4. Retriever: embed knowledge base with nomic-embed-text, store in ChromaDB, test retrieval quality  [X]
5. SQL generation: prompt design, LLM writes SQL, run in DuckDB, handle errors (retry with error message)  [ ]
6. Answer explanation: LLM summarizes result table into a business insight  [ ]
7. Evaluation: 20–30 test questions with expected answers; compare no-RAG vs RAG accuracy  [ ]
8. Streamlit UI: question box, show retrieved context, SQL, result table, explanation  [ ]
9. GitHub: clean repo, README with architecture diagram, results table, lessons learned  [ ]

## Folder structure
```
data-analyst-agent/
  data/            Olist CSVs
  knowledge/       markdown docs for the knowledge base
  src/             db.py, retriever.py, agent.py, evaluate.py
  app.py           Streamlit UI
  eval/            test questions + results
  README.md
```

## Progress log
- 2026-11-02: project started, architecture chosen
