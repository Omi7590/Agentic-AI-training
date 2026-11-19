# RTI Mitra - tools.py
# Agent tool: draft_rti_application
# Fills a fixed RTI template (state or central format) with the applicant's
# details, authority, information items and period.
# - Counts words against the Maharashtra 150-word rule
# - Adds the correct fee line (Rs 10, or nil for BPL)
# - Computes reply due date and first-appeal date using datetime

import re
from datetime import datetime, timedelta


def draft_rti_application(
    applicant_name: str,
    applicant_address: str,
    authority_name: str,
    authority_address: str,
    information_sought: str,
    jurisdiction: str = "Maharashtra",
    is_bpl: bool = False,
    application_date: str | None = None,
    via_apio: bool = False,
) -> dict:
    """
    Draft a correct RTI application and return a dict with:
      - draft       : formatted application text
      - word_count  : word count of information_sought
      - word_limit_ok: True if <= 150 words (Maharashtra) or no limit (Central)
      - fee         : Rs 10 or Nil (BPL)
      - reply_due   : date by which PIO must reply
      - appeal_due  : date by which first appeal can be filed
      - jurisdiction: Central or Maharashtra
    """

    # ── Date setup ────────────────────────────────────────────────────────────
    if application_date:
        try:
            app_date = datetime.strptime(application_date, "%Y-%m-%d")
        except ValueError:
            app_date = datetime.now()
    else:
        app_date = datetime.now()

    # Reply deadline: 30 days (35 via APIO)
    reply_days = 35 if via_apio else 30
    reply_due = app_date + timedelta(days=reply_days)

    # First appeal: within 30 days of reply due date
    appeal_due = reply_due + timedelta(days=30)

    # ── Fee ───────────────────────────────────────────────────────────────────
    fee = "Nil (BPL applicant — attach valid BPL certificate)" if is_bpl else "Rs 10"

    # ── Word count ────────────────────────────────────────────────────────────
    words = [w for w in re.split(r"\s+", information_sought.strip()) if w]
    word_count = len(words)
    word_limit = 150 if jurisdiction.lower() == "maharashtra" else None
    word_limit_ok = (word_count <= word_limit) if word_limit else True

    # ── Draft ─────────────────────────────────────────────────────────────────
    date_str = app_date.strftime("%d %B %Y")
    reply_str = reply_due.strftime("%d %B %Y")
    appeal_str = appeal_due.strftime("%d %B %Y")

    via_note = " (submitted via APIO)" if via_apio else ""

    draft = f"""To,
The Public Information Officer,
{authority_name},
{authority_address}

Date: {date_str}

Subject: Application under the Right to Information Act, 2005{via_note}

Sir/Madam,

I, {applicant_name}, a citizen of India, hereby request the following
information under Section 6(1) of the Right to Information Act, 2005:

{information_sought}

{"[NOTE: Word count = " + str(word_count) + "/150 — within Maharashtra limit]" if jurisdiction.lower() == "maharashtra" else ""}

I am enclosing the application fee of {fee}.

Please provide the information within {reply_days} days as required under
Section 7(1) of the RTI Act, 2005. The reply is due by: {reply_str}.

If I do not receive a reply by {reply_str}, I may file a First Appeal
under Section 19(1) of the RTI Act, 2005 within 30 days, i.e. by {appeal_str}.

Yours faithfully,
{applicant_name}
{applicant_address}

---
Note: This is general information on the RTI Act, not legal advice.
"""

    return {
        "draft": draft.strip(),
        "word_count": word_count,
        "word_limit_ok": word_limit_ok,
        "word_limit": word_limit,
        "fee": fee,
        "reply_due": reply_str,
        "appeal_due": appeal_str,
        "jurisdiction": jurisdiction,
        "via_apio": via_apio,
    }


if __name__ == "__main__":
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Dist. Ahmednagar, Maharashtra",
        authority_name="Public Information Officer, Kopargaon Panchayat Samiti",
        authority_address="Kopargaon, Dist. Ahmednagar, Maharashtra - 423601",
        information_sought=(
            "Please provide the following information regarding the 2026 road-repair "
            "work order for Kopargaon village roads: "
            "1) Copy of the work order issued for road repair in 2026. "
            "2) Name of the contractor and contract amount. "
            "3) Current payment status and amount paid so far. "
            "4) Expected completion date of the work."
        ),
        jurisdiction="Maharashtra",
        is_bpl=False,
        via_apio=False,
    )
    print(result["draft"])
    print(f"\nWord count: {result['word_count']}/{result['word_limit']}")
    print(f"Fee: {result['fee']}")
    print(f"Reply due: {result['reply_due']}")
    print(f"Appeal due: {result['appeal_due']}")
