# Testing Strategy & Test Scenarios

## Test Strategy
1. **Unit Tests (Backend)**:
   * PDF text and layout extraction.
   * Deterministic arithmetic auditor (valid math, line item mismatch, subtotal mismatch, rounding errors).
   * Change classifier rules.
2. **AI Provider & Mocking**:
   * Mock AI provider for offline, deterministic CI/CD testing without API keys.
   * Integration tests with live Gemini Flash provider when API key is available.
3. **Reproducible Test PDF Suite**:
   * Scripted PDF generator using `reportlab`.
   * Standardized test pairs:
     * **Pair 1 (Baseline)**: Identical documents (expect 0 changes).
     * **Pair 2 (Standard Commercial Changes)**: 1 added, 1 removed, 1 qty change, 1 price change, updated delivery date.
     * **Pair 3 (Renamed & Reordered)**: Items swapped in order with minor renaming ("Cloud Server Tier 1" -> "Tier-1 Cloud Compute").
     * **Pair 4 (Source Math Error)**: Original PDF has a deliberate calculation mistake ($100 * 2 = $250 printed). Auditor must flag this discrepancy.
     * **Pair 5 (Uncertain / Ambiguous)**: An item with ambiguous description where confidence is marked UNCERTAIN.
