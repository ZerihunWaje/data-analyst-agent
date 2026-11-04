import re
from pathlib import Path

import altair as alt
import duckdb
import ollama
import pandas as pd
import streamlit as st

from agent import LLM_MODEL, ask
from db import DB_PATH, get_schema
from retriever import retrieve

ASSETS = Path("assets")
st.set_page_config(
    page_title="Data Analyst Agent", page_icon=str(ASSETS / "icon.png"), layout="wide"
)
st.logo(str(ASSETS / "logo.svg"), icon_image=str(ASSETS / "icon.svg"), size="large")
EXAMPLES = [
    "What was the revenue per month in 2018?",
    "Which 5 states have the most customers?",
    "What share of delivered orders arrived late?",
]
MONEY_COLUMN = re.compile(r"revenue|paid|price|value|freight|payment", re.IGNORECASE)


# ---------- Setup ----------
@st.cache_resource
def get_db():
    con = duckdb.connect(DB_PATH, read_only=True)
    return con, get_schema(con)


def ollama_ready() -> bool:
    try:
        ollama.list()
        return True
    except ConnectionError:
        return False


def queue_example(q: str) -> None:
    st.session_state.pending = q


# ---------- Formatting helpers ----------
def column_config(df: pd.DataFrame) -> dict:
    config = {}
    for col in df.columns:
        label = col.replace("_", " ").title()
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            config[col] = st.column_config.DateColumn(label, format="YYYY-MM-DD")
        elif pd.api.types.is_numeric_dtype(df[col]):
            fmt = "R$ %.2f" if MONEY_COLUMN.search(col) else None
            config[col] = st.column_config.NumberColumn(label, format=fmt)
        else:
            config[col] = st.column_config.TextColumn(label)
    return config


def format_metric(col: str, value) -> str:
    if isinstance(value, (int, float)):
        text = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
        return f"R$ {text}" if MONEY_COLUMN.search(col) else text
    return str(value)


def show_chart(df: pd.DataFrame) -> None:
    dates = df.select_dtypes(include="datetime").columns
    numbers = df.select_dtypes(include="number").columns
    labels = [c for c in df.columns if c not in numbers and c not in dates]

    if len(df) < 2 or len(numbers) == 0:
        st.info("No chart for this result.")
    elif len(dates) > 0:
        st.line_chart(df, x=dates[0], y=numbers[0])
    elif labels and len(df) <= 30:
        chart = alt.Chart(df).mark_bar(color="#0F766E").encode(
            x=alt.X(labels[0], sort="-y", title=labels[0].replace("_", " ")),
            y=alt.Y(numbers[0], title=numbers[0].replace("_", " ")),
            tooltip=list(df.columns),
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Too many rows to chart clearly. See the table.")


# ---------- Render one answer (used for new and past messages) ----------
def render_answer(out: dict, use_rag: bool, hits: list) -> None:
    if out["error"]:
        st.error(f"Could not answer after {out['attempts']} attempts.\n\n{out['error']}")
        st.code(out["sql"], language="sql")
        return

    df = out["result"]
    if df.shape == (1, 1):
        col = df.columns[0]
        st.metric(col.replace("_", " ").title(), format_metric(col, df.iloc[0, 0]))
    st.markdown(out["explanation"].replace("$", "\\$"))

    chart_tab, table_tab, sql_tab, context_tab = st.tabs(
        ["📈 Chart", "📋 Table", "🧾 SQL", "📚 Context"]
    )
    with chart_tab:
        show_chart(df)
    with table_tab:
        st.dataframe(df, column_config=column_config(df), hide_index=True)
        st.caption(f"{len(df)} rows")
    with sql_tab:
        st.code(out["sql"], language="sql")
        st.caption(f"Attempts: {out['attempts']} · RAG: {'on' if use_rag else 'off'}")
    with context_tab:
        if not use_rag:
            st.info("RAG was off: the model saw only the database schema.")
        for hit in hits:
            with st.expander(f"{hit['id']} · distance {hit['distance']}"):
                st.text(hit["text"])


# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    use_rag = st.toggle("Use RAG (business context)", value=True)
    st.caption("Turn RAG off to see how the model does without business knowledge.")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
    st.divider()
    st.subheader("How it works")
    st.markdown(
        "1. **Retrieve** docs and examples (ChromaDB)\n"
        "2. **Generate** SQL with a local LLM\n"
        "3. **Run** on DuckDB (read-only, auto-retry)\n"
        "4. **Explain** the result"
    )
    st.caption("Each question is answered independently (no follow-up memory).")

# ---------- Header ----------
st.title("Ask your data")
st.caption(
    f"Olist e-commerce data (2016–2018) · Model: `{LLM_MODEL}` · "
    f"Eval: **96%** accuracy with RAG vs **40%** without"
)

if not ollama_ready():
    st.error("Ollama is not running. Start the Ollama app, then reload this page.")
    st.stop()

con, schema = get_db()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Empty state: example questions
if not st.session_state.messages:
    st.markdown("#### Try an example")
    for col, q in zip(st.columns(len(EXAMPLES)), EXAMPLES):
        col.button(q, on_click=queue_example, args=(q,))

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            render_answer(**msg["payload"])

# New question
question = st.chat_input("Ask a business question...") or st.session_state.pop("pending", None)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.status("Working on it...") as status:
            hits = []
            if use_rag:
                status.update(label="Searching the knowledge base...")
                hits = retrieve(question)
                st.write("Retrieved: " + ", ".join(h["id"] for h in hits))
            status.update(label="Writing and running SQL...")
            out = ask(question, con.cursor(), schema, use_rag)
            st.write(f"SQL attempts: {out['attempts']}")
            failed = out["error"] is not None
            status.update(
                label="Failed" if failed else "Done",
                state="error" if failed else "complete",
                expanded=False,
            )
        render_answer(out, use_rag, hits)

    st.session_state.messages.append(
        {"role": "assistant", "payload": {"out": out, "use_rag": use_rag, "hits": hits}}
    )