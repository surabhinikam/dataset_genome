import type { NextConfig } from "next";

/**
 * next.config.ts — Next.js configuration for Dataset Genome frontend.
 */
const nextConfig: NextConfig = {
  // Strict mode helps catch React issues early in development
  reactStrictMode: true,

  // Allow the app to be embedded in iframes from the same origin (useful for dashboards)
  // headers: async () => [...],
};

export default nextConfig;
