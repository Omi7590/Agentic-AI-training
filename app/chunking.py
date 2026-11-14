# RTI Mitra - chunking.py
# Chunks RTI rule records into smaller pieces,
# keeping source, page and title metadata for each chunk.

import json
import os

RECORDS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "records.json"
)


def load_records() -> list:
    with open(RECORDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_records(chunk_size: int = 200) -> list:
    """
    Convert each RTI rule record into one or more text chunks.
    Each chunk keeps: id, text, source, title, page, jurisdiction.
    """
    records = load_records()
    chunks = []

    for i, record in enumerate(records):
        full_text = (
            f"Topic: {record['topic']}\n"
            f"Rule: {record['rule']}\n"
            f"Reference: {record['section_or_rule_ref']}\n"
            f"Jurisdiction: {record['jurisdiction']}\n"
            f"Amount or time limit: {record['amount_or_time_limit']}"
        )

        words = full_text.split()
        for j in range(0, len(words), chunk_size):
            chunk_text = " ".join(words[j: j + chunk_size])
            chunks.append({
                "id": f"record_{i}_chunk_{j // chunk_size}",
                "text": chunk_text,
                "source": record["source_url"],
                "title": record["topic"],
                "page": i + 1,
                "jurisdiction": record["jurisdiction"],
            })

    return chunks


if __name__ == "__main__":
    chunks = chunk_records()
    print(f"Total chunks: {len(chunks)}")
    for c in chunks[:3]:
        print(f"\n[{c['id']}] {c['title']}")
        print(f"  Source: {c['source']}")
        print(f"  Text  : {c['text'][:120]}...")
