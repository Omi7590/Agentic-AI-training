# RTI Mitra - smart_search.py
# Ranks RTI rule records using TF-IDF + cosine similarity.
# Powers the /search and /questions endpoints.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.records import load_records

def _build_corpus(records):
    """Combine topic and rule text into one string per record."""
    return [f"{r['topic']} {r['rule']}" for r in records]

def smart_search(query: str, top_k: int = 5) -> list:
    """
    Return the top_k records most similar to the query
    using TF-IDF cosine similarity.
    """
    records = load_records()
    corpus = _build_corpus(records)

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    query_vec = vectorizer.transform([query])

    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Pair each record with its score, sort descending
    ranked = sorted(
        zip(scores, records),
        key=lambda x: x[0],
        reverse=True
    )

    results = []
    for score, record in ranked[:top_k]:
        if score > 0:
            results.append({**record, "score": round(float(score), 4)})

    return results
