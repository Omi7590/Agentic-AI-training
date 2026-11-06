# RTI Mitra ingest.py

import json
import os
import sys

# Allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.sample_records import records as raw_records

REQUIRED_FIELDS = [
    "topic",
    "rule",
    "section_or_rule_ref",
    "jurisdiction",
    "amount_or_time_limit",
    "source_url",
]

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "records.json")

def clean_record(raw, index):
    """Validate and clean one record. Raises ValueError for bad rows."""
    cleaned = {}
    for field in REQUIRED_FIELDS:
        value = raw.get(field, "").strip() if isinstance(raw.get(field), str) else raw.get(field)
        if not value:
            raise ValueError(f"Row {index}: missing or empty field '{field}'")
        cleaned[field] = value
    return cleaned

def ingest():
    cleaned_records = []
    skipped = 0

    for i, raw in enumerate(raw_records):
        try:
            cleaned = clean_record(raw, i + 1)
            cleaned_records.append(cleaned)
        except ValueError as e:
            print(f"[SKIP] {e}")
            skipped += 1

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, indent=2, ensure_ascii=False)

    print(f"\n[DONE] Ingested {len(cleaned_records)} records, skipped {skipped}.")
    print(f"[SAVED] {OUTPUT_PATH}")
    return cleaned_records

if __name__ == "__main__":
    ingest()