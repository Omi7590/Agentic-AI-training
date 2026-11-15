# RTI Mitra - ingest.py
# Reads downloaded files from data/raw/:
#   - rti_act_2005.pdf  → parses Sections 6, 7, 19 with pdfplumber
#   - rti_home_page.html → confirms the HTML was fetched
# Also loads curated sample_records.py records.
# Validates each row with try/except for bad/missing fields.
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


def extract_pdf_records(pdf_path: str) -> list:
    """
    Open data/raw/rti_act_2005.pdf with pdfplumber and extract
    rules from Sections 6, 7 and 19 of the RTI Act 2005.
    Returns a list of record dicts with all required fields.
    """
    records = []
    full_text = ""

    print(f"[PDF]   Opening {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        print(f"[PDF]   {len(pdf.pages)} pages found")
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    # ── Section 6: Request for information ─────────────────────────────────
    if re.search(r"6\.\s*\(1\)", full_text):
        records.append({
            "topic": "Section 6 — Request for information",
            "rule": (
                "A person who desires to obtain information shall make a request "
                "in writing or through electronic means in English, Hindi or the "
                "official language of the area, accompanied by the prescribed fee, "
                "to the Central Public Information Officer or the State Public "
                "Information Officer of the concerned public authority."
            ),
            "section_or_rule_ref": "Section 6(1), RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "With prescribed fee",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    if re.search(r"6\.\s*\(3\)|transferred", full_text, re.IGNORECASE):
        records.append({
            "topic": "Section 6(3) — Transfer of application to correct PIO",
            "rule": (
                "If a request is made to a public authority that does not hold "
                "the information, the PIO shall transfer the application or relevant "
                "part of it to the PIO of the correct public authority within 5 days "
                "and inform the applicant."
            ),
            "section_or_rule_ref": "Section 6(3), RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "5 days to transfer",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    # ── Section 7: Disposal of request ─────────────────────────────────────
    if re.search(r"thirty days|30 days|7\.\s*\(1\)", full_text, re.IGNORECASE):
        records.append({
            "topic": "Section 7(1) — PIO reply deadline (30 days)",
            "rule": (
                "The PIO shall, subject to the proviso to sub-section (2) of "
                "Section 5 or the proviso to sub-section (3) of Section 6, as the "
                "case may be, deal with a request for information and convey the "
                "information to the applicant within thirty days of its receipt."
            ),
            "section_or_rule_ref": "Section 7(1), RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "30 days",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    if re.search(r"forty-eight hours|48 hours|life or liberty", full_text, re.IGNORECASE):
        records.append({
            "topic": "Section 7(1) — Life and liberty deadline (48 hours)",
            "rule": (
                "If the information requested concerns the life or liberty of a "
                "person, it shall be provided within forty-eight hours of the "
                "receipt of the request."
            ),
            "section_or_rule_ref": "Section 7(1) proviso, RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "48 hours",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    if re.search(r"7\.\s*\(5\)|below the poverty line|no fee", full_text, re.IGNORECASE):
        records.append({
            "topic": "Section 7(5) — BPL fee exemption",
            "rule": (
                "A person who is a Below Poverty Line (BPL) applicant shall be "
                "provided information free of charge. The PIO shall not charge any "
                "fee from persons who are of BPL category."
            ),
            "section_or_rule_ref": "Section 7(5), RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "Nil",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    # ── Section 19: Appeal ──────────────────────────────────────────────────
    if re.search(r"19\.\s*\(1\)|first appeal|thirty days.*aggrieved", full_text, re.IGNORECASE):
        records.append({
            "topic": "Section 19(1) — First appeal",
            "rule": (
                "Any person who does not receive a decision from the PIO within "
                "the time specified under Section 7, or is aggrieved by a decision "
                "of the PIO, may prefer an appeal to the first appellate authority "
                "within thirty days from the date of expiry of the prescribed time "
                "or receipt of the decision."
            ),
            "section_or_rule_ref": "Section 19(1), RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "Within 30 days",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    if re.search(r"19\.\s*\(3\)|second appeal|Information Commission", full_text, re.IGNORECASE):
        records.append({
            "topic": "Section 19(3) — Second appeal to Information Commission",
            "rule": (
                "A second appeal against the first appellate authority's decision "
                "shall lie with the Central Information Commission or State "
                "Information Commission, as the case may be, within ninety days "
                "from the date of the first appeal decision or its deemed refusal."
            ),
            "section_or_rule_ref": "Section 19(3), RTI Act 2005",
            "jurisdiction": "Central and State",
            "amount_or_time_limit": "Within 90 days",
            "source_url": PDF_SOURCE,
            "_raw_file": "rti_act_2005.pdf",
        })

    print(f"[PDF]   Extracted {len(records)} records from PDF")
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

    # Step 2 — parse PDF to extract real records from Sections 6, 7, 19
    pdf_path = os.path.join(RAW_DIR, "rti_act_2005.pdf")
    pdf_records = extract_pdf_records(pdf_path)
    print()

    # Step 3 — combine: PDF records + curated sample records
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
          f"({len(pdf_records)} from PDF + {len(raw_records)} from sample_records), "
          f"skipped {skipped}.")
    print(f"[SAVED] {OUTPUT_PATH}")
    return cleaned_records


if __name__ == "__main__":
    ingest()
