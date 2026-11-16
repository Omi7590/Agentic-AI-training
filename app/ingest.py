# RTI Mitra - ingest.py
# S1: Downloads data/raw/rti_act_2005.pdf with fetch.py, then this script
# opens it with pdfplumber, slices the real text of Sections 6, 7 and 19
# using regex between headings, and fills rule + amount_or_time_limit
# directly from the extracted text.
# Also loads curated sample_records.py records.
# Validates each row with try/except for bad rows.
# Saves all cleaned records to data/records.json.

import json
import os
import re
import sys

import pdfplumber

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

PDF_SOURCE = "https://rti.gov.in/Writereaddata/RTI-Act.pdf"


def slice_section(full_text: str, start_pattern: str, end_pattern: str) -> str:
    """
    Slice the real text between start_pattern and end_pattern from the PDF.
    Returns cleaned single-line text.
    """
    m_start = re.search(start_pattern, full_text)
    if not m_start:
        return ""
    m_end = re.search(end_pattern, full_text[m_start.start():])
    if m_end:
        raw = full_text[m_start.start(): m_start.start() + m_end.start()]
    else:
        raw = full_text[m_start.start(): m_start.start() + 1200]
    # Clean up line breaks and extra spaces from PDF extraction
    cleaned = re.sub(r'\s+', ' ', raw).strip()
    return cleaned


def extract_amount(text: str) -> str:
    """Pull out a time limit or amount from sliced section text."""
    if re.search(r'forty.eight hours', text, re.IGNORECASE):
        return "48 hours"
    if re.search(r'thirty days', text, re.IGNORECASE):
        return "30 days"
    if re.search(r'ninety days', text, re.IGNORECASE):
        return "90 days"
    if re.search(r'five days|5 days', text, re.IGNORECASE):
        return "5 days"
    if re.search(r'free of charge|no fee|nil', text, re.IGNORECASE):
        return "Nil"
    return "Not specified"


def extract_pdf_records(pdf_path: str) -> list:
    """
    Open data/raw/rti_act_2005.pdf with pdfplumber, extract the full text,
    then slice Sections 6, 7 and 19 using regex between headings.
    The rule field is filled directly from the sliced PDF text.
    """
    full_text = ""
    print(f"[PDF]   Opening {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        print(f"[PDF]   {len(pdf.pages)} pages found")
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    records = []

    # ── Section 6(1) — Request for information ──────────────────────────────
    sec6_text = slice_section(
        full_text,
        r'6\.\s*\(1\)',
        r'7\.\s*\(1\)'
    )
    if sec6_text:
        records.append({
            "topic": "Section 6 — Request for information (how to file RTI)",
            "rule": sec6_text[:600],
            "section_or_rule_ref": "Section 6(1), RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": extract_amount(sec6_text) or "With prescribed fee",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    # ── Section 7(1) — PIO reply within 30 days ─────────────────────────────
    sec7_text = slice_section(
        full_text,
        r'7\.\s*\(1\)',
        r'8\.\s*\(1\)|8\.\s*There'
    )
    if sec7_text:
        records.append({
            "topic": "Section 7(1) — PIO must reply within 30 days",
            "rule": sec7_text[:600],
            "section_or_rule_ref": "Section 7(1), RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "30 days (48 hours for life or liberty)",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    # ── Section 7(1) proviso — 48 hours for life and liberty ────────────────
    proviso_match = re.search(
        r'(Provided that where the information sought for concerns the life or liberty.*?receipt of the request\.)',
        full_text, re.DOTALL
    )
    if proviso_match:
        proviso_text = re.sub(r'\s+', ' ', proviso_match.group(1)).strip()
        records.append({
            "topic": "Section 7(1) proviso — Life and liberty: 48-hour deadline",
            "rule": proviso_text[:500],
            "section_or_rule_ref": "Section 7(1) proviso, RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "48 hours",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    # ── Section 19(1) — First appeal ────────────────────────────────────────
    sec19_text = slice_section(
        full_text,
        r'19\.\s*\(1\)',
        r'19\.\s*\(2\)'
    )
    if sec19_text:
        records.append({
            "topic": "Section 19(1) — First appeal within 30 days",
            "rule": sec19_text[:600],
            "section_or_rule_ref": "Section 19(1), RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "30 days",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    # ── Section 19(3) — Second appeal ───────────────────────────────────────
    sec19_3_text = slice_section(
        full_text,
        r'19\.\s*\(3\)',
        r'19\.\s*\(4\)'
    )
    if sec19_3_text:
        records.append({
            "topic": "Section 19(3) — Second appeal to Information Commission",
            "rule": sec19_3_text[:600],
            "section_or_rule_ref": "Section 19(3), RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "90 days",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    print(f"[PDF]   Extracted {len(records)} records from real PDF text")
    return records


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
    if "_raw_file" in raw:
        cleaned["_raw_file"] = raw["_raw_file"]
    return cleaned


def ingest():
    print("=== RTI Mitra Ingest ===\n")

    # Step 1 — confirm raw files are present
    check_raw_files()
    print()

    # Step 2 — parse PDF, slice real section text into records
    pdf_path = os.path.join(RAW_DIR, "rti_act_2005.pdf")
    pdf_records = extract_pdf_records(pdf_path)
    print()

    # Step 3 — combine PDF records + curated sample records
    all_raw = pdf_records + list(raw_records)

    cleaned_records = []
    skipped = 0

    for i, raw in enumerate(all_raw):
        try:
            cleaned = clean_record(raw, i + 1)
            cleaned_records.append(cleaned)
        except ValueError as e:
            print(f"[SKIP]  {e}")
            skipped += 1

    # Step 4 — save to data/records.json
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, indent=2, ensure_ascii=False)

    print(f"[DONE]  Ingested {len(cleaned_records)} records "
          f"({len(pdf_records)} from PDF text + {len(raw_records)} from sample_records), "
          f"skipped {skipped}.")
    print(f"[SAVED] {OUTPUT_PATH}")
    return cleaned_records


if __name__ == "__main__":
    ingest()
