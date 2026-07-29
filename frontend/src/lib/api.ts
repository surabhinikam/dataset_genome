/**
 * lib/api.ts — Typed API client for the Dataset Genome backend.
 *
 * Centralises all HTTP calls so the rest of the app never hardcodes URLs
 * or fetch logic. Swap BASE_URL via the NEXT_PUBLIC_API_URL env variable.
 */

import type { DatasetMetadata, HealthResponse } from "@/types/dataset";
import type { GenomeReport } from "@/types/intelligence";

/** Backend base URL — override via .env.local: NEXT_PUBLIC_API_URL=http://... */
const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Generic request helper
// ---------------------------------------------------------------------------

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, options);

  if (!response.ok) {
    // Attempt to parse a structured FastAPI error detail
    let message = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      message = body?.detail ?? message;
    } catch {
      // Ignore JSON parse failures; surface the HTTP status
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Upload a CSV file and retrieve its structural metadata.
 *
 * @param file - The File object selected by the user.
 * @returns Parsed DatasetMetadata from the backend.
 */
export async function uploadCSV(file: File): Promise<DatasetMetadata> {
  const formData = new FormData();
  formData.append("file", file);

  return request<DatasetMetadata>("/upload", {
    method: "POST",
    body: formData,
    // Do NOT set Content-Type manually — the browser must set the multipart
    // boundary automatically when using FormData.
  });
}

/**
 * Run Dataset Intelligence Engine profilers on an uploaded dataset.
 *
 * @param datasetId - The UUID string of the uploaded dataset.
 * @returns Full GenomeReport JSON from POST /analyze.
 */
export async function analyzeDataset(datasetId: string): Promise<GenomeReport> {
  return request<GenomeReport>("/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ dataset_id: datasetId }),
  });
}

/**
 * Ping the backend health-check endpoint.
 */
export async function checkHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}
