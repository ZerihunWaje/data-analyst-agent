from pathlib import Path

KNOWLEDGE_DIR = Path("knowledge")


def load_documents() -> list[dict]:
    docs = []

    # Tables and metrics: one file = one chunk
    for folder in ["tables", "metrics"]:
        for path in sorted((KNOWLEDGE_DIR / folder).glob("*.md")):
            docs.append({
                "id": f"{folder}/{path.stem}",
                "text": path.read_text(encoding="utf-8"),
                "type": folder,
            })

    # Examples: split one file into one chunk per question
    text = (KNOWLEDGE_DIR / "examples" / "examples.md").read_text(encoding="utf-8")
    for i, chunk in enumerate(text.split("## Question:")[1:], 1):
        docs.append({
            "id": f"examples/{i}",
            "text": "## Question:" + chunk.rstrip(),
            "type": "examples",
        })

    if not docs:
        raise ValueError("No knowledge documents found")
    return docs

import chromadb
import ollama

CHROMA_DIR = "chroma_db"
COLLECTION = "knowledge"
EMBED_MODEL = "nomic-embed-text"


def embed(texts: list[str], prefix: str) -> list[list[float]]:
    inputs = [prefix + t for t in texts]
    return ollama.embed(model=EMBED_MODEL, input=inputs)["embeddings"]


def build_index() -> chromadb.Collection:
    docs = load_documents()
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Rebuild from scratch every time (idempotent)
    client.get_or_create_collection(COLLECTION)
    client.delete_collection(COLLECTION)
    collection = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    collection.add(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        embeddings=embed([d["text"] for d in docs], prefix="search_document: "),
        metadatas=[{"type": d["type"]} for d in docs],
    )
    return collection

def retrieve(question: str, k: int = 4) -> list[dict]:
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION)
    query_vec = embed([question], prefix="search_query: ")
    res = collection.query(query_embeddings=query_vec, n_results=k)
    return [
        {"id": i, "text": t, "distance": round(d, 3)}
        for i, t, d in zip(res["ids"][0], res["documents"][0], res["distances"][0])
    ]


if __name__ == "__main__":
    collection = build_index()
    print(f"Indexed {collection.count()} chunks into '{COLLECTION}'")