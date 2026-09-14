/**
 * Domain types and data contracts for commercial offer comparison.
 * Mirrors backend Pydantic models in backend/app/models/schemas.py.
 */

export enum ChangeType {
  ADDED = "ADDED",
  REMOVED = "REMOVED",
  RENAMED = "RENAMED",
  QUANTITY_CHANGED = "QUANTITY_CHANGED",
  UNIT_PRICE_CHANGED = "UNIT_PRICE_CHANGED",
  TOTAL_CHANGED = "TOTAL_CHANGED",
  DELIVERY_DATE_CHANGED = "DELIVERY_DATE_CHANGED",
}

export enum ConfidenceLevel {
  CONFIRMED = "CONFIRMED",
  UNCERTAIN = "UNCERTAIN",
}

export interface SourceReference {
  page_number: number;
  snippet: string;
}

export interface LineItem {
  item_id?: string | null;
  name: string;
  description?: string | null;
  quantity?: number | null;
  unit?: string | null;
  unit_price?: number | null;
  total_price?: number | null;
  source_ref?: SourceReference | null;
}

export interface OfferDocument {
  vendor_name?: string | null;
  client_name?: string | null;
  offer_id?: string | null;
  offer_date?: string | null;
  delivery_date?: string | null;
  currency?: string | null;
  items: LineItem[];
  subtotal?: number | null;
  tax?: number | null;
  grand_total?: number | null;
}

export interface MathDiscrepancy {
  location: string;
  expected_value: number;
  actual_value: number;
  message: string;
}

export interface AuditReport {
  document_name: string;
  is_valid: boolean;
  discrepancies: MathDiscrepancy[];
}

export interface DetectedChange {
  change_type: ChangeType;
  item_name_original?: string | null;
  item_name_revised?: string | null;
  original_value?: unknown;
  revised_value?: unknown;
  confidence: ConfidenceLevel;
  explanation: string;
  original_source_ref?: SourceReference | null;
  revised_source_ref?: SourceReference | null;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
}

export interface ComparisonSummary {
  total_changes?: number;
  added_items_count?: number;
  removed_items_count?: number;
  modified_items_count?: number;
  has_arithmetic_errors?: boolean;
  price_difference?: number | null;
  original_grand_total?: number | null;
  revised_grand_total?: number | null;
  currency?: string | null;
  processing_time_ms?: number | null;
  token_usage?: TokenUsage | null;
  estimated_cost_usd?: number | null;
  [key: string]: unknown;
}

export interface ComparisonReport {
  original_document?: OfferDocument | null;
  revised_document?: OfferDocument | null;
  original_audit: AuditReport;
  revised_audit: AuditReport;
  changes: DetectedChange[];
  summary: ComparisonSummary;
  processing_time_ms?: number | null;
  token_usage?: TokenUsage | null;
  estimated_cost_usd?: number | null;
}

export interface PageContent {
  page_number: number;
  raw_text: string;
  lines: string[];
}

export interface ItemMatch {
  original_item?: LineItem | null;
  revised_item?: LineItem | null;
  confidence_score: number;
  confidence_level: ConfidenceLevel;
  rationale?: string | null;
}
