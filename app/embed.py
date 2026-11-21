# RTI Mitra - embed.py
# Embeds RTI chunks using sentence-transformers and runs
# semantic search for the 10 user questions.
# Records hits in eval/search_results.md

import os

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.chunking import chunk_records

MODEL_NAME = "all-MiniLM-L6-v2"

QUESTIONS = [
    "What is the RTI application fee in Maharashtra?",
    "Within how many days must the PIO reply to an RTI?",
    "Can I ask for information about my own panchayat in Marathi?",
    "Draft an RTI to Kopargaon Panchayat Samiti for the 2026 road-repair work order and payment status.",
    "What is the difference between filing RTI to a central ministry online and to a Maharashtra department online?",
    "What did the PIO of Kopargaon municipal council reply to RTIs filed last month?",
    "Am I exempt from paying the RTI fee if I am below the poverty line?",
    "What happens if the PIO does not reply within 30 days?",
    "Can I file an RTI through an APIO at my nearest post office, and does that change the reply deadline?",
    "What information is exempt from RTI disclosure under Section 8?",
]

RESULTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "eval", "search_results.md"
)


def build_index(chunks: list, model: SentenceTransformer) -> np.ndarray:
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings


def semantic_search(query: str, chunks: list, embeddings: np.ndarray,
                    model: SentenceTransformer, top_k: int = 3) -> list:
    query_vec = model.encode([query])
    scores = cosine_similarity(query_vec, embeddings).flatten()
    top_indices = scores.argsort()[::-1][:top_k]
    results = []
    for idx in top_indices:
        results.append({
            "score": round(float(scores[idx]), 4),
            "title": chunks[idx]["title"],
            "source": chunks[idx]["source"],
            "text": chunks[idx]["text"][:200],
        })
    return results


def run_and_save():
    print("Loading model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Chunking records...")
    chunks = chunk_records()
    print(f"Total chunks: {len(chunks)}")

    print("Building embeddings...")
    embeddings = build_index(chunks, model)

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)

    lines = [
        "# Semantic Search Results — RTI Mitra\n\n",
        f"Model: `{MODEL_NAME}`  |  Chunks: {len(chunks)}\n\n---\n\n",
    ]

    for i, question in enumerate(QUESTIONS, 1):
        results = semantic_search(question, chunks, embeddings, model, top_k=3)
        lines.append(f"## Q{i}: {question}\n\n")
        for j, r in enumerate(results, 1):
            lines.append(f"**Hit {j}** (score: {r['score']})\n\n")
            lines.append(f"- Title: {r['title']}\n")
            lines.append(f"- Source: {r['source']}\n")
            lines.append(f"- Text: {r['text']}...\n\n")
        lines.append("---\n\n")

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n[SAVED] {RESULTS_PATH}")


if __name__ == "__main__":
    run_and_save()
