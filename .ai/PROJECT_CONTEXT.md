# Project Context

## 1. Goal
We are building the Codebridge AI-First Product Builder test task:
**An AI service for comparing two commercial offers in PDF format.**

This is a focused ~8-hour MVP prototype optimized for correctness, clarity, and working end-to-end execution.

## 2. Core Capabilities
* **Input**: Two text-based PDF documents:
  1. `Original Offer`
  2. `Revised Offer`
* **Data Extraction**: Extract commercial header data (vendor, client, offer dates, delivery dates, currency) and line items (name, description, quantity, unit price, total price).
* **Semantic Matching**: Match corresponding items across documents even when renamed or reordered.
* **Substantive Change Detection**:
  * Added and removed items
  * Renamed items
  * Quantity changes
  * Unit price changes
  * Totals and subtotal changes
  * Delivery date / terms changes
  * *Ignore formatting-only and layout changes.*
* **Deterministic Recalculation & Audit**:
  * Verify `quantity * unit_price == total` and line item sum == grand total.
  * Detect and report arithmetic errors present in source documents.
  * Never let AI hallucinate or silently overwrite source numbers.
* **Traceability & Certainty**:
  * Every change must include a source reference (`page` number + verbatim `source snippet`).
  * Distinguish `CONFIRMED` changes from `UNCERTAIN` matches.
* **Evaluation**: Include a reproducible test set with synthetic PDF pairs verifying edge cases.

## 3. Tech Stack
* **Backend**: Python 3.10+, FastAPI, Pydantic, pdfplumber.
* **AI Provider**: Google Gemini Flash via a pluggable provider interface (swappable, API key via `.env`).
* **Frontend**: React + Vite + Tailwind CSS.
* **Infrastructure**: No database, no user authentication, in-memory/ephemeral processing.
