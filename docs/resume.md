# RTI Mitra — Resume Bullets

**Om Jarhad · 2124UCSM2012 · CYBER · Sanjivani College of Engineering**

---

## 3 Resume Bullets

**1. Built a production RAG system for RTI Act compliance**
Designed and deployed RTI Mitra, a Retrieval-Augmented Generation (RAG) assistant that answers Right to Information Act queries grounded in official documents (RTI Act 2005, Maharashtra RTI Rules 2005). Chunked and indexed 24 RTI rule records into a persistent Chroma vector store, achieving semantic search with avg latency of 1,057ms and avg 624 tokens per request using Groq's qwen/qwen3.8-27b model.

**2. Engineered a dual-jurisdiction RTI rule engine with LangGraph agents**
Built a hand-written agent loop and a LangGraph agent (with MemorySaver memory and interrupt-based approval step) that correctly picks between central RTI Rules 2012/2019 and Maharashtra RTI Rules 2005 based on the public authority type. Implemented the `draft_rti_application` tool that computes reply deadlines (30 days / +5 via APIO / 48 hrs life & liberty) and word limits (150 words for Maharashtra) using Python `datetime` — not left to the LLM.

**3. Delivered a full MLOps pipeline with CI/CD, Docker and live deployment**
Wrote 28 pytest tests (including fake-LLM monkeypatching and prompt-injection defence), passed ruff linting, containerised the app with Docker and docker-compose, set up GitHub Actions CI (ruff + pytest + docker build) with a green badge, and deployed the FastAPI service live on Render at https://rti-mitra-mq86.onrender.com with UptimeRobot monitoring (100% uptime, 0 incidents).
