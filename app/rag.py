# RTI Mitra - rag.py
# Retrieval-Augmented Generation for RTI Mitra.
# POST /ask: retrieves top-k chunks from Chroma, sends them to the LLM
# with citations, and returns a grounded answer.
# Must say "I don't know" for questions about live/case data (e.g. Q6).

import os
from dotenv import load_dotenv
from groq import Groq
from app.vectorstore import semantic_search

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "qwen/qwen3.8-27b"

RAG_SYSTEM_PROMPT = """You are RTI Mitra, an expert assistant on the Right to Information (RTI) Act 2005.

You will be given CONTEXT — a set of RTI rules retrieved from official sources.
Answer the user's question using ONLY the provided context.

Rules:
1. Base your answer strictly on the CONTEXT. Do not add information not present in the context.
2. Always cite the source reference (e.g. Section 7(1), RTI Act 2005) from the context.
3. If the question asks for live data, case outcomes, or specific PIO replies that are not in the context, say exactly: "I don't know — RTI Mitra does not have access to live case records."
4. If the context does not contain enough information to answer, say: "I don't know based on the available RTI rules."
5. Keep answers clear and simple — the user may never have filed an RTI before.
6. End answers that touch on legal strategy with: "This is general information on the RTI Act, not legal advice."
"""


def build_context(chunks: list) -> str:
    """Format retrieved chunks into a numbered context block with citations."""
    lines = []
    for i, chunk in enumerate(chunks, 1):
        lines.append(
            f"[{i}] {chunk['text']}\n"
            f"    Source: {chunk['source']} | Title: {chunk['title']}"
        )
    return "\n\n".join(lines)


def ask(question: str, top_k: int = 5) -> dict:
    """
    Retrieve top_k chunks from Chroma, send to LLM with RAG prompt.
    Returns: { answer, citations, chunks_used }
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set. Add it to your .env file.")

    # Step 1 — retrieve relevant chunks
    chunks = semantic_search(question, top_k=top_k)

    # Step 2 — build context string
    context = build_context(chunks)

    # Step 3 — build citations list
    citations = [
        {"title": c["title"], "source": c["source"], "score": c["score"]}
        for c in chunks
    ]

    # Step 4 — call LLM with context
    client = Groq(api_key=GROQ_API_KEY)
    user_message = f"CONTEXT:\n{context}\n\nQUESTION: {question}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content.strip()

    return {
        "answer": answer,
        "citations": citations,
        "chunks_used": len(chunks),
    }


if __name__ == "__main__":
    questions = [
        "What is the RTI application fee in Maharashtra?",
        "What did the PIO of Kopargaon municipal council reply to RTIs filed last month?",
    ]
    for q in questions:
        print(f"\nQ: {q}")
        result = ask(q, top_k=3)
        print(f"A: {result['answer'][:300]}")
        print(f"Citations: {[c['title'] for c in result['citations']]}")
