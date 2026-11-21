# RTI Mitra - vectorstore.py
# Indexes all RTI chunks into a persistent Chroma collection.
# Uses Chroma's built-in default embedding function (onnxruntime based)
# so sentence-transformers/torch are NOT loaded at startup — keeps
# memory low enough for Render free tier (512 MB).
# Powers GET /search/semantic?q=

import os

import chromadb
from chromadb.utils import embedding_functions

from app.chunking import chunk_records

CHROMA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "chroma"
)

COLLECTION_NAME = "rti_mitra"

_collection = None


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        ef = embedding_functions.DefaultEmbeddingFunction()
        _collection = client.get_or_create_collection(
            COLLECTION_NAME,
            embedding_function=ef,
        )
    return _collection


def build_index():
    """Index all chunks into Chroma. Safe to call multiple times (upsert)."""
    collection = get_collection()
    chunks = chunk_records()

    print(f"Indexing {len(chunks)} chunks into Chroma...")

    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "title": c["title"],
            "page": c["page"],
            "jurisdiction": c["jurisdiction"],
        }
        for c in chunks
    ]

    # Chroma's default embedding function handles encoding automatically
    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"[DONE] Indexed {len(chunks)} chunks into '{COLLECTION_NAME}'")
    return len(chunks)


def semantic_search(query: str, top_k: int = 5) -> list:
    """Search the Chroma collection with a query string."""
    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "score": round(1 - results["distances"][0][i], 4),
            "title": results["metadatas"][0][i]["title"],
            "source": results["metadatas"][0][i]["source"],
            "jurisdiction": results["metadatas"][0][i]["jurisdiction"],
        })

    return hits


if __name__ == "__main__":
    build_index()
    print("\nTest search: 'RTI fee Maharashtra'")
    results = semantic_search("RTI fee Maharashtra", top_k=3)
    for r in results:
        print(f"  [{r['score']}] {r['title']} — {r['source']}")
