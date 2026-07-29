"use client";

/**
 * components/csv-upload.tsx — Drag-and-drop CSV upload component.
 *
 * States:
 *   idle     → user hasn't selected a file yet
 *   selected → file chosen but not uploaded
 *   loading  → upload in progress
 *   success  → upload complete (triggers onSuccess callback)
 *   error    → upload or validation failed (shows error message)
 */

import { useCallback, useRef, useState } from "react";
import { uploadCSV } from "@/lib/api";
import type { DatasetMetadata } from "@/types/dataset";

interface CsvUploadProps {
  onSuccess: (data: DatasetMetadata) => void;
}

type UploadState = "idle" | "selected" | "loading" | "success" | "error";

export default function CsvUpload({ onSuccess }: CsvUploadProps) {
  const [state, setState] = useState<UploadState>("idle");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // ---- Handlers ----

  const handleFile = useCallback((file: File) => {
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setError("Please select a valid CSV file.");
      setState("error");
      return;
    }
    setSelectedFile(file);
    setError(null);
    setState("selected");
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setState("loading");
    setError(null);

    try {
      const metadata = await uploadCSV(selectedFile);
      setState("success");
      onSuccess(metadata);
    } catch (err) {
      setState("error");
      setError(err instanceof Error ? err.message : "Upload failed. Please try again.");
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setError(null);
    setState("idle");
    if (inputRef.current) inputRef.current.value = "";
  };

  // ---- Derived UI ----

  const isLoading = state === "loading";

  return (
    <div className="w-full space-y-4">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !isLoading && inputRef.current?.click()}
        className={`
          group relative flex cursor-pointer flex-col items-center justify-center gap-4
          rounded-2xl border-2 border-dashed p-12 text-center transition-all duration-300
          ${isDragging
            ? "border-violet-400 bg-violet-500/10 scale-[1.01]"
            : state === "selected"
            ? "border-indigo-400/60 bg-indigo-500/5"
            : state === "error"
            ? "border-red-400/60 bg-red-500/5"
            : "border-white/10 bg-white/[0.02] hover:border-violet-400/50 hover:bg-violet-500/5"
          }
        `}
      >
        {/* Icon */}
        <div
          className={`
            flex h-16 w-16 items-center justify-center rounded-2xl transition-all duration-300
            ${isDragging || state === "selected"
              ? "bg-gradient-to-br from-violet-500 to-indigo-600 shadow-lg shadow-violet-500/30"
              : "bg-white/5"
            }
          `}
        >
          {isLoading ? (
            <svg className="h-7 w-7 animate-spin text-violet-400" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : (
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className={`h-7 w-7 transition-colors duration-300 ${
                isDragging || state === "selected" ? "text-white" : "text-white/40 group-hover:text-violet-400"
              }`}
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            </svg>
          )}
        </div>

        {/* Text */}
        {isLoading ? (
          <div className="space-y-1">
            <p className="text-sm font-medium text-violet-300">Analysing dataset…</p>
            <p className="text-xs text-white/40">Please wait while we process your file</p>
          </div>
        ) : state === "selected" && selectedFile ? (
          <div className="space-y-1">
            <p className="text-sm font-semibold text-indigo-300">{selectedFile.name}</p>
            <p className="text-xs text-white/40">
              {(selectedFile.size / 1024).toFixed(1)} KB · Ready to upload
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            <p className="text-sm font-medium text-white/70">
              Drop your CSV here, or{" "}
              <span className="text-violet-400 underline underline-offset-2">browse</span>
            </p>
            <p className="text-xs text-white/30">CSV files only · Max 50 MB</p>
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept=".csv,text/csv"
          className="hidden"
          onChange={handleInputChange}
          disabled={isLoading}
        />
      </div>

      {/* Error message */}
      {state === "error" && error && (
        <div className="flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3">
          <svg className="mt-0.5 h-4 w-4 shrink-0 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
              clipRule="evenodd" />
          </svg>
          <p className="text-sm text-red-300">{error}</p>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3">
        {(state === "selected" || state === "error") && (
          <button
            onClick={handleReset}
            className="flex-1 rounded-xl border border-white/10 bg-white/5 py-3 text-sm font-medium text-white/60 transition-all hover:bg-white/10 hover:text-white/80"
          >
            Clear
          </button>
        )}
        <button
          onClick={state === "success" ? handleReset : handleUpload}
          disabled={state !== "selected" && state !== "error" || isLoading}
          className={`
            flex-1 rounded-xl py-3 text-sm font-semibold transition-all duration-300
            ${state === "success"
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30"
              : state !== "selected"
              ? "cursor-not-allowed bg-white/5 text-white/20"
              : "bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 hover:scale-[1.01] active:scale-[0.99]"
            }
          `}
        >
          {isLoading ? "Uploading…" : state === "success" ? "Upload Another" : "Analyse Dataset"}
        </button>
      </div>
    </div>
  );
}
