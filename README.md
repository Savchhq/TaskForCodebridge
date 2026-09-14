# Commercial Offer PDF Comparator
> **Codebridge AI-First Product Builder Test Task**  
> AI service for comparing two commercial offers in text-based PDF format with deterministic arithmetic validation, dual source location citations, and certainty classification.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF.svg)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3-38B2AC.svg)](https://tailwindcss.com)
[![Tests](https://img.shields.io/badge/pytest-86%20passed-success.svg)](https://pytest.org)
[![E2E Suite](https://img.shields.io/badge/E2E%20Acceptance-100%25%20PASS-brightgreen.svg)](test_fixtures/ACCEPTANCE_REPORT.md)

---

## Overview

When evaluating commercial offers (original vs. revised), decision-makers face renamed line items, reordered rows, altered quantities, sneaky unit price changes, and human arithmetic errors.

This prototype provides an **end-to-end, reproducible solution**:
1. **Zero Manual Entry**: Users upload two text-based PDFs (up to 3 pages each, 1 currency, up to 10 items).
2. **Substantive Change Detection**: Identifies added, removed, renamed, quantity, unit price, total, and delivery date changes.
3. **Dual Source References**: Every detected change explicitly references **both** source locations (`page_number` and verbatim `source_snippet`).
4. **Deterministic Math Auditor**: Pure Python recalculation of `qty * unit_price == total` and document subtotals. Discrepancies are flagged without altering original document figures.
5. **Formatting Exemption**: Changes in layout, fonts, or whitespace yield **strictly 0 commercial changes**.
6. **Certainty Classification**: Clear distinction between `CONFIRMED` changes and ambiguous matches flagged as `UNCERTAIN` for human review.
7. **Performance & Variable Cost Tracking**: Measures latency (`processing_time_ms`) and token expenditures (`estimated_cost_usd`).

---

## Architecture & Multi-Agent Workflow

The project was coordinated and built using a multi-agent architecture where specialized AI agents operated in distinct roles with dedicated `.ai/` governance:
* **Master Agent**: Central coordinator and quality auditor.
* **Architect Agent**: Data contracts (Pydantic v2 domain schemas & TypeScript mirrors).
* **Backend Agent**: FastAPI, PDF text extractor (`pdfplumber`), deterministic math auditor, and diff engine.
* **AI Agent**: Structured LLM extraction prompts, semantic matcher, and provider abstraction (`GeminiFlashProvider` & `MockAIProvider`).
* **Frontend Agent**: Interactive React + Vite + Tailwind dashboard with 1-click test scenario presets.
* **QA Agent**: Reproducible test PDF generator (`reportlab`) and automated E2E acceptance runner.

---

## Reproducible Test Suite & Benchmark Results

The repository includes deterministic test generators in `test_fixtures/generate_test_pdfs.py` producing 4 benchmark documents:

| Scenario | Description | Expected Commercial Changes | Detected Changes | False Positives | Dual Source References | Math Audit | Latency | Est. Cost (USD) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Scenario 1** | Main Commercial Pair (Substantive + Math Error) | 7 | 7 | 0 | 100% | Flagged ($1,000 $\neq$ $1,200) | ~1.6 ms | $0.00030 | **PASS (100%)** |
| **Scenario 2** | Formatting-Only Variant (Layout/Font Shift) | 0 | 0 | 0 | 100% | Valid (0 errors) | ~0.6 ms | $0.00030 | **PASS (100%)** |
| **Scenario 3** | Ambiguity & Clarification (Vague Description) | 3 | 3 | 0 | 100% | Flagged `UNCERTAIN` | ~1.1 ms | $0.00030 | **PASS (100%)** |

*Complete benchmark details are available in [`test_fixtures/ACCEPTANCE_REPORT.md`](test_fixtures/ACCEPTANCE_REPORT.md).*

---

## Quickstart Guide

### Prerequisites
* **Python 3.10+** (tested on 3.12)
* **Node.js 18+** & npm

### 1. Backend Setup
```powershell
# From project root:
cd backend

# Create virtual environment and install dependencies:
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# (Optional) Add your Gemini API key:
cp .env.example .env
# Edit .env and set: GEMINI_API_KEY=your_key_here

# Run backend tests (86 unit tests):
.\.venv\Scripts\pytest

# Start FastAPI server:
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```
* Backend interactive OpenAPI docs: `http://localhost:8000/api/docs`
* Health check: `http://localhost:8000/health`

### 2. Frontend Setup
```powershell
# In a new terminal, from project root:
cd frontend

# Install packages:
npm install

# Start development server:
npm run dev
```
* Open browser: **`http://localhost:5173`**

### 3. Run E2E Acceptance Test Suite
```powershell
# From project root:
.\backend\.venv\Scripts\python test_fixtures/run_acceptance_tests.py
```

---

## Testing Scenarios in the Web UI

The web interface features **1-Click Test Scenario Presets**:
1. Click **1-click test scenario presets** dropdown in the UI.
2. Select **Scenario 1** to inspect the 7 substantive changes, math error warning, and dual source citations.
3. Select **Scenario 2** to observe the 0-changes formatting exemption.
4. Select **Scenario 3** to review the `UNCERTAIN` status warning requiring human confirmation.
5. Or drag-and-drop your own text-based PDF files!

---

## Delivery Notes & Pricing Model

* **AI Provider**: Google Gemini 2.5 Flash (`gemini-2.5-flash`).
* **Pricing Assumptions**:
  * Input tokens: $0.075 per 1M tokens ($0.000075 / 1k).
  * Output tokens: $0.30 per 1M tokens ($0.00030 / 1k).
  * Average token usage per comparison: ~2,000 tokens $\approx$ **$0.00030 USD per document pair**.
* **Offline Mock Provider**: Included for 100% deterministic, instant testing with zero external API calls or API key dependencies.
