/**
 * app/page.tsx — Dataset Genome Bioinformatics Lineage Browser.
 *
 * Implements the premium bioinformatics instrument dashboard mapping dataset ancestry,
 * DNA base-pair operation rungs, Sanger chromatogram quality traces, and specimen inspector.
 */

"use client";

import { LineageBrowserDashboard } from "@/components/genome/LineageBrowserDashboard";

export default function HomePage() {
  return <LineageBrowserDashboard />;
}
