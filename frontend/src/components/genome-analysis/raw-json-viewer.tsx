"use client";

/**
 * components/genome-analysis/raw-json-viewer.tsx — Raw Genome JSON Viewer.
 *
 * Syntax-highlighted JSON code block with a one-click copy button.
 */

import { useState } from "react";
import type { GenomeReport } from "@/types/intelligence";

interface RawJsonViewerProps {
  report: GenomeReport;
}

export default function RawJsonViewer({ report }: RawJsonViewerProps) {
  const [copied, setCopied] = useState(false);
  const jsonString = JSON.stringify(report, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">Raw Genome Report JSON</h3>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white/70 transition-all hover:bg-white/10 hover:text-white"
        >
          {copied ? (
            <>
              <svg className="h-4 w-4 text-emerald-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span className="text-emerald-300">Copied!</span>
            </>
          ) : (
            <>
              <svg className="h-4 w-4 text-white/50" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.757c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 011.927-.184" />
              </svg>
              <span>Copy JSON</span>
            </>
          )}
        </button>
      </div>

      <div className="relative rounded-2xl border border-white/10 bg-[#06060e] p-4 shadow-inner">
        <pre className="max-h-[420px] overflow-auto text-xs font-mono text-violet-200/90 leading-relaxed">
          <code>{jsonString}</code>
        </pre>
      </div>
    </div>
  );
}
