# Architecture Overview

## 1. System Pipeline

```
[User Uploads: Original & Revised PDF]
                  │
                  ▼
       1. PDF Ingestion Engine (pdfplumber)
          - Extracts page text blocks with page indices & snippets
                  │
                  ▼
       2. AI Structured Extraction (Gemini Flash / Provider Interface)
          - Extracts header (vendor, dates, currency) & line items
          - Associates each extracted field with page & verbatim snippet
                  │
                  ▼
       3. Deterministic Arithmetic Auditor (Pure Python)
          - Audits: qty * unit_price == total
          - Audits: sum(line items) + tax/discount == grand_total
          - Flags discrepancies without overwriting raw source figures
                  │
                  ▼
       4. Semantic Matching & Change Classifier (AI + Heuristics)
          - Matches items across versions (handles renamed / reordered)
          - Assigns match confidence (CONFIRMED vs UNCERTAIN)
          - Classifies changes: ADDED, REMOVED, RENAMED, QTY_CHANGED,
            PRICE_CHANGED, TOTAL_CHANGED, DELIVERY_DATE_CHANGED
                  │
                  ▼
       5. Diff Synthesizer & API Response (FastAPI)
          - Packages structured comparison report
                  │
                  ▼
[React + Vite Frontend Dashboard]
  - Upload Dropzone
  - Summary Metrics & Arithmetic Warning Callouts
  - Filterable Item Comparison Table with Diff Badges
  - Source Reference Drawer (Page + Quote)
```

## 2. Pluggable AI Provider Interface

Located in `backend/app/services/ai/base.py`:
```python
class BaseAIProvider(ABC):
    @abstractmethod
    async def extract_offer_data(self, pages: list[PageContent]) -> OfferDocument:
        """Extract structured commercial data with source snippet mapping."""
        pass

    @abstractmethod
    async def match_line_items(
        self, 
        original_items: list[LineItem], 
        revised_items: list[LineItem]
    ) -> list[ItemMatch]:
        """Match items semantically, detecting renames with confidence scoring."""
        pass
```
* Default implementation: `GeminiFlashProvider` (`google-genai` SDK or `google-generativeai`).
* Fallback/mock provider for offline/deterministic testing: `MockAIProvider`.

## 3. Domain Data Contracts & Schemas

The system relies on strict Pydantic v2 schemas in `backend/app/models/schemas.py` and mirrored TypeScript types in `frontend/src/types/index.ts`:

* **`SourceReference`**: Citation containing 1-indexed `page_number` and verbatim `snippet`.
* **`LineItem`**: Product/service item with `name`, `description`, `quantity`, `unit`, `unit_price`, `total_price`, and `source_ref`.
* **`OfferDocument`**: Extracted offer metadata (`vendor_name`, `client_name`, `offer_id`, `offer_date`, `delivery_date`, `currency`), `items: list[LineItem]`, `subtotal`, `tax`, and `grand_total`.
* **`MathDiscrepancy` & `AuditReport`**: Deterministic arithmetic audit results (`expected_value`, `actual_value`, `location`, `message`, `is_valid`).
* **`ChangeType`**: Enum with `ADDED`, `REMOVED`, `RENAMED`, `QUANTITY_CHANGED`, `UNIT_PRICE_CHANGED`, `TOTAL_CHANGED`, `DELIVERY_DATE_CHANGED`.
* **`ConfidenceLevel`**: Enum with `CONFIRMED` and `UNCERTAIN`.
* **`DetectedChange`**: Substantive diff record with change type, original/revised values, confidence level, explanation, and source references.
* **`ComparisonSummary` & `ComparisonReport`**: Comprehensive comparison output encapsulating audits, diff items, and metrics.
* **`PageContent` & `ItemMatch`**: Auxiliary schemas for PDF text extraction and semantic item matching.

## 4. Directory Layout

```
TaskForCodebridge/
├── .ai/                    # Single source of truth for AI agents
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI application entrypoint
│   │   ├── api/            # API endpoints (/api/compare, /api/health)
│   │   ├── core/           # Config (.env settings), logging
│   │   ├── models/         # Pydantic schemas (Offer, Item, Diff, Audit)
│   │   └── services/       # pdf_extractor, auditor, ai_provider, matcher
│   ├── tests/              # Pytest suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/     # Upload, DiffTable, AuditAlerts, SourceRefModal
│   │   ├── types/          # TypeScript interfaces matching backend models
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── test_fixtures/          # Synthetic PDF generation scripts and samples
└── README.md
```
