import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dataset Genome | Bioinformatics Data Lineage Browser",
  description:
    "Dataset Genome — A bioinformatics lab instrument for data engineering. Map dataset ancestry, specimen derivation trees, and Sanger quality traces.",
  keywords: ["Dataset Genome", "Data Lineage", "Bioinformatics", "Data Engineering", "Sanger Chromatogram", "Dataset Specimen"],
  authors: [{ name: "Dataset Genome Core Team" }],
  openGraph: {
    title: "Dataset Genome — Lineage Browser",
    description: "Map dataset ancestry like a genome browser maps DNA.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased font-sans text-[#14171A] bg-[#EEF2EF] selection:bg-[#0F6B5C]/20 selection:text-[#0F6B5C]">
        {children}
      </body>
    </html>
  );
}
