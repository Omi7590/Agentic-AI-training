# RTI Mitra - tests/test_all_days.py
# 25 pytest tests covering:
#   - records (load, search, count_by, get_by_id)
#   - smart search (TF-IDF)
#   - FastAPI endpoints (/health, /records, /records/{id} 404, /search)
#   - /ask with a fake LLM (monkeypatched)
#   - draft_rti_application tool (word count, fee, dates, BPL, APIO)

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app
from app.records import count_by, get_by_id, load_records, search
from app.smart_search import smart_search
from app.tools import draft_rti_application

# ── Records tests ─────────────────────────────────────────────────────────────

def test_load_records_returns_list():
    records = load_records()
    assert isinstance(records, list)
    assert len(records) >= 20


def test_records_have_required_fields():
    required = {"topic", "rule", "section_or_rule_ref",
                "jurisdiction", "amount_or_time_limit", "source_url"}
    for r in load_records():
        for field in required:
            assert field in r, f"Missing field '{field}' in record: {r.get('topic')}"


def test_search_returns_results():
    results = search("fee")
    assert len(results) >= 1
    assert all("fee" in r["topic"].lower() or "fee" in r["rule"].lower()
               for r in results)


def test_search_no_match_returns_empty():
    results = search("zzzznonexistent999")
    assert results == []


def test_count_by_jurisdiction():
    counts = count_by("jurisdiction")
    assert isinstance(counts, dict)
    assert len(counts) >= 2
    assert sum(counts.values()) >= 20


def test_get_by_id_valid():
    record = get_by_id(0)
    assert record is not None
    assert "topic" in record


def test_get_by_id_out_of_range():
    assert get_by_id(99999) is None


# ── Smart search test ─────────────────────────────────────────────────────────

def test_smart_search_returns_ranked_results():
    results = smart_search("RTI fee Maharashtra", top_k=3)
    assert len(results) >= 1
    assert "score" in results[0]
    assert results[0]["score"] > 0


# ── FastAPI endpoint tests ────────────────────────────────────────────────────

@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "RTI Mitra"


def test_records_endpoint_default_limit(client):
    resp = client.get("/records")
    assert resp.status_code == 200
    data = resp.json()
    assert "records" in data
    assert len(data["records"]) <= 10


def test_records_endpoint_custom_limit(client):
    resp = client.get("/records?limit=5")
    assert resp.status_code == 200
    assert len(resp.json()["records"]) <= 5


def test_records_by_id_valid(client):
    resp = client.get("/records/1")
    assert resp.status_code == 200
    assert "topic" in resp.json()


def test_records_by_id_not_found(client):
    resp = client.get("/records/99999")
    assert resp.status_code == 404


def test_search_endpoint(client):
    resp = client.get("/search?q=fee")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert data["total"] >= 1


# ── /ask with fake LLM ────────────────────────────────────────────────────────

def test_ask_endpoint_with_fake_llm(client, monkeypatch):
    """Test /ask with a monkeypatched RAG function — no real API call made."""
    fake_result = {
        "answer": "The RTI fee in Maharashtra is Rs 10.",
        "citations": [{"title": "Application fee - Maharashtra",
                       "source": "https://rti.gov.in/", "score": 0.9}],
        "chunks_used": 1,
    }

    def fake_rag_ask(question, top_k=5):
        return fake_result

    monkeypatch.setattr("app.rag.ask", fake_rag_ask)
    monkeypatch.setattr(main_module, "rag_ask", fake_rag_ask)

    resp = client.post("/ask", json={"question": "What is the RTI fee?", "top_k": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "citations" in data


# ── draft_rti_application tool tests ─────────────────────────────────────────

def test_draft_tool_word_count_within_limit():
    info = "Please provide the 2026 road-repair work order for Kopargaon village."
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Maharashtra",
        authority_name="Kopargaon Panchayat Samiti",
        authority_address="Kopargaon - 423601",
        information_sought=info,
        jurisdiction="Maharashtra",
    )
    assert result["word_count"] <= 150
    assert result["word_limit_ok"] is True


def test_draft_tool_word_count_exceeds_limit():
    info = " ".join(["word"] * 160)
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Maharashtra",
        authority_name="Kopargaon Panchayat Samiti",
        authority_address="Kopargaon - 423601",
        information_sought=info,
        jurisdiction="Maharashtra",
    )
    assert result["word_count"] == 160
    assert result["word_limit_ok"] is False


def test_draft_tool_bpl_fee():
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Maharashtra",
        authority_name="Kopargaon Panchayat Samiti",
        authority_address="Kopargaon - 423601",
        information_sought="Please provide information.",
        jurisdiction="Maharashtra",
        is_bpl=True,
    )
    assert "Nil" in result["fee"]
    assert "BPL" in result["fee"]


def test_draft_tool_standard_fee():
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Maharashtra",
        authority_name="Kopargaon Panchayat Samiti",
        authority_address="Kopargaon - 423601",
        information_sought="Please provide information.",
        jurisdiction="Maharashtra",
        is_bpl=False,
    )
    assert result["fee"] == "Rs 10"


def test_draft_tool_reply_date_30_days():
    today = datetime.now()
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Maharashtra",
        authority_name="Kopargaon Panchayat Samiti",
        authority_address="Kopargaon - 423601",
        information_sought="Please provide information.",
        jurisdiction="Maharashtra",
        via_apio=False,
    )
    expected = (today + timedelta(days=30)).strftime("%d %B %Y")
    assert result["reply_due"] == expected


def test_draft_tool_reply_date_via_apio_35_days():
    today = datetime.now()
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Maharashtra",
        authority_name="Kopargaon Panchayat Samiti",
        authority_address="Kopargaon - 423601",
        information_sought="Please provide information.",
        jurisdiction="Maharashtra",
        via_apio=True,
    )
    expected = (today + timedelta(days=35)).strftime("%d %B %Y")
    assert result["reply_due"] == expected


def test_draft_tool_appeal_date_30_days_after_reply():
    today = datetime.now()
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Maharashtra",
        authority_name="Kopargaon Panchayat Samiti",
        authority_address="Kopargaon - 423601",
        information_sought="Please provide information.",
        jurisdiction="Maharashtra",
        via_apio=False,
    )
    expected_appeal = (today + timedelta(days=60)).strftime("%d %B %Y")
    assert result["appeal_due"] == expected_appeal


def test_draft_tool_central_no_word_limit():
    info = " ".join(["word"] * 200)
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Maharashtra",
        authority_name="Central Ministry",
        authority_address="New Delhi",
        information_sought=info,
        jurisdiction="Central",
    )
    assert result["word_limit"] is None
    assert result["word_limit_ok"] is True


def test_draft_contains_applicant_name():
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Maharashtra",
        authority_name="Kopargaon Panchayat Samiti",
        authority_address="Kopargaon - 423601",
        information_sought="Please provide information.",
        jurisdiction="Maharashtra",
    )
    assert "Om Jarhad" in result["draft"]


def test_draft_contains_legal_disclaimer():
    result = draft_rti_application(
        applicant_name="Om Jarhad",
        applicant_address="Kopargaon, Maharashtra",
        authority_name="Kopargaon Panchayat Samiti",
        authority_address="Kopargaon - 423601",
        information_sought="Please provide information.",
        jurisdiction="Maharashtra",
    )
    assert "not legal advice" in result["draft"].lower()
