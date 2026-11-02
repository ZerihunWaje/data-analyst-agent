import ollama

#1. LLM call: can the model write SQL?
resp=ollama.chat(
    model="qwen2.5-coder:7b",
    messages=[{"role":"user","content":"Write a SQL query counting rows in a table called orders. only SQL."}],
    options={"temperature":0},
)
print("LLM:", resp["message"]["content"])

#2. Embedding call: text->vector
emb=ollama.embed(model="nomic-embed-text",input="total revenue per month")
vec=emb["embeddings"][0]
print("Embedding dim:",len(vec),"| first values:",vec[:3])