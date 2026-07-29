import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Dataset Genome | AI Research Dashboard",
  description:
    "Dataset Genome — Sprint 1 Foundation. Upload CSV datasets and explore structural metadata powered by AI research tooling.",
  keywords: ["dataset", "CSV", "AI research", "data analysis", "genome"],
  authors: [{ name: "Dataset Genome Team" }],
  openGraph: {
    title: "Dataset Genome",
    description: "AI-powered dataset analysis dashboard",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
