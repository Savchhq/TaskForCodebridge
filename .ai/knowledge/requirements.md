# Requirements & Acceptance Criteria

## 1. Functional Requirements
* **Input Documents**: Two user-uploaded text-based PDF files (`original.pdf` and `revised.pdf`).
* **Header Extraction**:
  * Vendor / Supplier Name
  * Client / Customer Name
  * Document IDs & Dates
  * Delivery Dates / Lead Times
  * Currency
* **Line Items Extraction**:
  * Item identifier / code (if present)
  * Item title & description
  * Quantity & unit of measure
  * Unit price
  * Line total price
* **Matching**:
  * Same item reordered -> MATCH
  * Same item renamed (e.g. "Widget A Pro" -> "Pro Widget A (v2)") -> MATCH with semantic reasoning
  * Item present in original only -> REMOVED
  * Item present in revised only -> ADDED
* **Change Classification**:
  * Substantive changes: Added, Removed, Renamed, Quantity Changed, Unit Price Changed, Total Changed, Delivery Date Changed.
  * Formatting-only changes (font, layout, spacing, casing) must be ignored.
* **Deterministic Calculations & Auditing**:
  * Recalculate: `expected_line_total = quantity * unit_price`
  * Recalculate: `expected_subtotal = sum(line_totals)`
  * Compare with printed values in document; if mismatch, flag as arithmetic error.
  * Never overwrite the source values.
* **Source Attribution**:
  * Every extracted field and detected change must reference the `page_number` and the verbatim `source_snippet`.
* **Certainty Status**:
  * `CONFIRMED`: unambiguous match / change.
  * `UNCERTAIN`: ambiguous match / low semantic confidence / partial description alignment.
