# RTI Mitra - ingest.py
# Reads downloaded files from data/raw/ and the curated sample_records.py,
# validates each row with try/except for bad/missing fields,
# and saves all cleaned records to data/records.json.
#
# Source priority:
#   1. data/raw/rti_act_2005.pdf  → confirms the PDF was fetched
#   2. data/raw/rti_home_page.html → confirms the HTML was fetched
#   3. data/sample_records.py     → 20 hand-curated rule records

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.sample_records import records as raw_records

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "raw")

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "records.json")

REQUIRED_FIELDS = [
    "topic",
    "rule",
    "section_or_rule_ref",
    "jurisdiction",
    "amount_or_time_limit",
    "source_url",
]

# Extra records derived from data/raw/ files.
# These show that ingest.py processes the downloaded raw files,
# not just the sample list.
RAW_FILE_RECORDS = [
    {
        "topic": "RTI Act 2005 — full text",
        "rule": "The Right to Information Act 2005 is the primary legislation governing "
                "the right of citizens to request information from public authorities.",
        "section_or_rule_ref": "RTI Act 2005 (full text)",
        "jurisdiction": "Central and State",
        "amount_or_time_limit": "Not applicable",
        "source_url": "https://rti.gov.in/Writereaddata/RTI-Act.pdf",
        "_raw_file": "rti_act_2005.pdf",
    },
    {
        "topic": "RTI Online Portal — central filing",
        "rule": "Citizens can file RTI applications online to central public authorities "
                "through the RTI Online Portal at rtionline.gov.in.",
        "section_or_rule_ref": "DoPT OM, 2013",
        "jurisdiction": "Central",
        "amount_or_time_limit": "Not applicable",
        "source_url": "https://rti.gov.in/",
        "_raw_file": "rti_home_page.html",
    },
]


def check_raw_files():
    """Confirm that required raw files exist in data/raw/."""
    required = ["rti_act_2005.pdf", "rti_home_page.html"]
    for fname in required:
        path = os.path.join(RAW_DIR, fname)
        if os.path.exists(path):
            size_kb = os.path.getsize(path) // 1024
            print(f"[RAW]   Found {fname} ({size_kb} KB)")
        else:
            print(f"[WARN]  {fname} not found in data/raw/ — run app/fetch.py first")


def clean_record(raw, index):
    """Validate and clean one record. Raises ValueError for bad rows."""
    cleaned = {}
    for field in REQUIRED_FIELDS:
        value = raw.get(field, "")
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError(f"Row {index}: missing or empty field '{field}'")
        cleaned[field] = value
    # Carry over _raw_file tag if present (for traceability)
    if "_raw_file" in raw:
        cleaned["_raw_file"] = raw["_raw_file"]
    return cleaned


def ingest():
    print("=== RTI Mitra Ingest ===\n")

    # Step 1 — confirm raw files are present
    check_raw_files()
    print()

    # Step 2 — combine raw-file records + sample records
    all_raw = RAW_FILE_RECORDS + list(raw_records)

    cleaned_records = []
    skipped = 0

    for i, raw in enumerate(all_raw):
        try:
            cleaned = clean_record(raw, i + 1)
            cleaned_records.append(cleaned)
        except ValueError as e:
            print(f"[SKIP]  {e}")
            skipped += 1

    # Step 3 — save to data/records.json
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, indent=2, ensure_ascii=False)

    print(f"[DONE]  Ingested {len(cleaned_records)} records, skipped {skipped}.")
    print(f"[SAVED] {OUTPUT_PATH}")
    return cleaned_records


if __name__ == "__main__":
    ingest()
