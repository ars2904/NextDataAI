# VedaNova AI & NexaData Platform 🌿
> **Holistic Intelligence Platform** — Autonomous Data Analytics, Company PDF RAG, and Dual-Mode Conversational AI.

---

## 🌟 Key Capabilities

### 1. Dual-Mode Conversational AI & PDF RAG Engine
- **🏢 Company Questions Mode**: Strict, zero-hallucination document intelligence grounded in verified company PDF documents (`company_docs/`). Every answer cites exact document names and page numbers.
- **💬 General Questions Mode**: Conversational AI assistant for broad inquiries, programming, and general knowledge.
- **⚡ High-Speed Semantic Retrieval**: In-memory vector retriever running with sub-millisecond search latency.

### 2. High-Performance Analytics Engine
- **⚡ DuckDB Vectorized Execution**: Aggregates and filters 50,000+ records in ~30 milliseconds.
- **🛡️ AST Security Guardrails**: Strict read-only query validator blocking destructive commands (`DROP`, `DELETE`, writes).
- **🔁 Self-Healing Loop**: Automatically corrects query syntax or schema mismatches.
- **📊 Interactive Visualizations**: Automatic chart inference rendering Plotly charts (Bar, Pie, Line, Scatter).
- **📄 Executive PDF & Excel Reports**: C-suite ready landscape A4 reports and multi-tab styled `.xlsx` workbooks.

---

## 🏗️ Architecture & Project Structure

```text
vedanovasolutions/
├── backend/
│   ├── main.py                 # FastAPI application with CORS & REST endpoints
│   ├── models.py               # Pydantic request/response schemas
│   └── orchestrator.py         # Dual-mode message routing & grounding logic
│
├── rag/
│   ├── engine.py               # VedaNova knowledge base orchestrator
│   ├── pdf_loader.py           # Document parser & page extractor (pypdf)
│   ├── chunker.py              # Semantic text chunking with metadata
│   └── retriever.py            # Local semantic vector similarity retriever
│
├── company_docs/               # Verified company PDF repository
│   └── VedaNova_Company_Overview_and_Services.pdf
│
├── core/
│   ├── config.py               # Central configuration & API key management
│   └── security.py             # AST validation & SQL safety guardrails
│
├── connectors/
│   └── loader.py               # Multi-source dataset ingestion (CSV, Excel, Parquet)
│
├── engine/
│   └── query_engine.py         # DuckDB execution pipeline
│
├── visualizer/
│   └── charts.py               # Plotly interactive chart generation
│
├── reporting/
│   ├── pdf_generator.py        # Executive PDF report builder (ReportLab)
│   └── excel_generator.py      # Multi-tab styled Excel builder (OpenPyXL)
│
├── tests/
│   ├── test_rag.py             # RAG knowledge base & semantic retrieval tests
│   ├── test_api.py             # FastAPI REST endpoints integration tests
│   └── test_analytics.py       # DuckDB engine & security guardrail tests
│
├── app.py                      # Full-featured Streamlit analytics application
└── requirements.txt            # Production dependencies
```

---

## 🚀 Quickstart

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run Tests
```bash
python tests/test_rag.py
python tests/test_api.py
python tests/test_analytics.py
```

### 3. Start the FastAPI Backend
```bash
uvicorn backend.main:app --reload --port 8000
```
- API Documentation: `http://localhost:8000/docs`
- Health Probe: `http://localhost:8000/api/health`

### 4. Start the Analytics Dashboard
```bash
streamlit run app.py
```
