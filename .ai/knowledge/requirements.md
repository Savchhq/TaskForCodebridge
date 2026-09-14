# Official Requirements & Acceptance Criteria

## 1. Core Problem & Product Scope
* **Input**: User uploads original and revised versions of a commercial offer in text-based PDF format.
* **Document Constraints**:
  * Up to **3 pages** each.
  * **One currency**.
  * Up to **10 line items**.
  * No legal advice, no handwritten/scanned OCR required.
* **No Manual Data Entry**: Do not ask the user to re-type or re-enter line items into a form.

## 2. Substantive Change Detection & Matching
* **Substantive Change Categories**:
  * Scope: Added items, Removed items
  * Renamed items (matched semantically despite wording differences)
  * Reordered rows (matched regardless of row order)
  * Quantity changes
  * Unit price changes
  * Totals changes (subtotals, discounts, grand totals)
  * Delivery date changes
* **Formatting Exemption**: Formatting-only changes (whitespace, layout shifts, font, capitalization) **must NOT** appear as commercial changes.
* **Certainty Differentiation**: Distinctly separate `CONFIRMED` changes from `UNCERTAIN` matches (e.g. low semantic confidence, ambiguous scope).

## 3. Dual Source Location References
* **CRITICAL REQUIREMENT**: **Every change must reference both source locations** (original document page & verbatim snippet AND revised document page & verbatim snippet).
  * For Added items: revised source reference is required (original is N/A).
  * For Removed items: original source reference is required (revised is N/A).
  * For Modified / Renamed / Qty / Price / Date / Total changes: **BOTH** original and revised source references are mandatory.

## 4. Deterministic Arithmetic Auditing
* Recalculate totals deterministically (`quantity * unit_price == total`, `sum(line items) == grand total`).
* Detect and display arithmetic discrepancies in source documents.
* **Strict Integrity Rule**: Do NOT silently replace or overwrite what the source document states. Display both the printed value and the calculated value.

## 5. Required Test Sets & Fixtures
The prototype must include a reproducible, scripted test set:
1. **Primary Test Pair (Original & Revised)** containing:
   * 1 renamed item
   * Reordered rows
   * 1 quantity change
   * 1 price change
   * 1 removed item
   * 1 changed delivery date
   * 1 intentionally incorrect total (arithmetic error)
   * Formatting changes without changing meaning
2. **Formatting-Only Variant**:
   * A revision with altered layout/fonts/whitespace that produces **zero substantive changes**.
3. **Clarification / Ambiguity Pair**:
   * An input on which the product marks matches as `UNCERTAIN`, asks for clarification, or declines to conclude.
4. **Generalization**:
   * Must process completely new, user-uploaded PDFs dynamically (no hardcoded responses).

## 6. Performance & Cost Reporting
* The application must measure and report:
  * **Processing Time** (seconds / ms to useful result).
  * **Estimated Variable Cost per Document Pair** (token usage breakdown: input/output, model pricing assumptions, e.g. Gemini Flash rates).
* Output must remain concise enough for a decision-maker evaluating whether to approve the revised offer.

## 7. Submission Checklist
* Working browser demo (React + Vite).
* Repository with setup instructions.
* Video walkthrough plan (up to 3 minutes).
* Delivery notes: sample inputs, expected vs actual results, what failed, time spent, AI tools/models with verification example, measured speed & cost.
