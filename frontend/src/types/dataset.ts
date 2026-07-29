/**
 * types/dataset.ts — TypeScript interfaces for Dataset Genome API responses.
 *
 * These mirror the Pydantic models defined in backend/schemas/dataset.py.
 * Any change to the backend schema must be reflected here.
 */

/** Structural metadata returned after a successful CSV upload. */
export interface DatasetMetadata {
  /** UUID identifying this upload session. */
  dataset_id: string;
  /** Original filename as provided by the client. */
  filename: string;
  /** Total number of data rows (header excluded). */
  num_rows: number;
  /** Total number of columns. */
  num_cols: number;
  /** Ordered list of column header names. */
  column_names: string[];
}

/** Response from GET /health */
export interface HealthResponse {
  status: string;
  version: string;
}
