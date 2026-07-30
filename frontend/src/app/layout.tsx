import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dataset Genome | AI Dataset Intelligence & Optimization Platform",
  description:
    "Dataset Genome — An AI-powered platform that analyzes, evolves, optimizes, trains, and publishes benchmark datasets.",
  keywords: ["Dataset Genome", "AI Dataset Intelligence", "Dataset Evolution", "AutoScientist", "Adaptive Data", "ML Benchmark"],
  authors: [{ name: "Dataset Genome Core Team" }],
  openGraph: {
    title: "Dataset Genome — AI Dataset Intelligence Platform",
    description: "Analyze, evolve, optimize, train, and publish ML datasets automatically.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased font-sans text-[#F9FAFB] bg-[#0B1220] selection:bg-[#3B82F6]/30 selection:text-[#3B82F6]">
        {children}
      </body>
    </html>
  );
}
