/**
 * lib/mock-genome-data.ts — Specimen dataset ancestry graph for Dataset Genome.
 *
 * 9 interconnected specimens with explicit parent-child lineage edges,
 * operation types (MERGE, FILTER, TRANSFORM, ANNOTATE), Sanger chromatogram quality traces,
 * schemas, and version histories.
 */

export type OperationType = "MERGE" | "FILTER" | "TRANSFORM" | "ANNOTATE";

export interface LineageRung {
  id: string;
  sourceId: string;
  targetId: string;
  operation: OperationType;
  baseColor: string; // #3FA66D, #D64545, #D98F3F, #3C6E9C
  baseCode: "A" | "T" | "G" | "C";
  operator: string;
  description: string;
  transformedColumns: string[];
  metricsDelta: string;
}

export interface SchemaField {
  name: string;
  type: "string" | "integer" | "float" | "datetime" | "boolean" | "category";
  nullPercentage: number;
  distinctCount: number;
  qualityStatus: "optimal" | "warn" | "drift";
  description: string;
}

export interface VersionCommit {
  version: string;
  commitHash: string;
  author: string;
  timestamp: string;
  message: string;
  healthDelta: number;
}

export interface DatasetSpecimen {
  id: string;
  locusPath: string; // genome://retail/customers/v3.2
  name: string;
  version: string;
  domain: string;
  rowCount: number;
  columnCount: number;
  sizeBytes: number;
  healthStatus: "healthy" | "warning" | "critical";
  healthScore: number; // 0-100
  owner: string;
  createdAt: string;
  lastUpdated: string;
  description: string;
  tags: string[];
  parentIds: string[];
  childIds: string[];
  schema: SchemaField[];
  qualityTrace: number[]; // Sanger chromatogram wave amplitudes (20 points 0-100)
  qualityTracePeaks: { pos: number; label: string; base: "A" | "T" | "G" | "C"; severity: "low" | "mid" | "high" }[];
  versionHistory: VersionCommit[];
  derivationEvent?: {
    operation: OperationType;
    operator: string;
    description: string;
    parentNames: string[];
  };
}

export const OPERATION_COLOR_MAP: Record<OperationType, { hex: string; base: string; label: string }> = {
  MERGE: { hex: "#3FA66D", base: "A", label: "Merge (Base A)" },
  FILTER: { hex: "#D64545", base: "T", label: "Filter / Drop (Base T)" },
  TRANSFORM: { hex: "#D98F3F", base: "G", label: "Transform (Base G)" },
  ANNOTATE: { hex: "#3C6E9C", base: "C", label: "Annotate / Enrich (Base C)" },
};

export const MOCK_SPECIMENS: Record<string, DatasetSpecimen> = {
  "raw-transactions": {
    id: "raw-transactions",
    locusPath: "genome://retail/raw_transactions/v1.0",
    name: "raw_transactions",
    version: "v1.0",
    domain: "Transactions",
    rowCount: 1450200,
    columnCount: 14,
    sizeBytes: 184500000,
    healthStatus: "warning",
    healthScore: 78.4,
    owner: "data-ingest-bot",
    createdAt: "2026-07-01T08:00:00Z",
    lastUpdated: "2026-07-28T14:20:00Z",
    description: "Raw POS credit card transaction telemetry collected from 480 retail outlets.",
    tags: ["raw", "telemetry", "ingest"],
    parentIds: [],
    childIds: ["user-transactions"],
    schema: [
      { name: "txn_id", type: "string", nullPercentage: 0.0, distinctCount: 1450200, qualityStatus: "optimal", description: "Primary transaction UUID" },
      { name: "user_uuid", type: "string", nullPercentage: 2.1, distinctCount: 245000, qualityStatus: "warn", description: "Customer identity reference" },
      { name: "amount", type: "float", nullPercentage: 0.0, distinctCount: 42100, qualityStatus: "optimal", description: "Transaction value in USD" },
      { name: "merchant_category", type: "category", nullPercentage: 0.5, distinctCount: 38, qualityStatus: "optimal", description: "MCC retail taxonomy code" },
      { name: "timestamp", type: "datetime", nullPercentage: 0.0, distinctCount: 1240000, qualityStatus: "optimal", description: "ISO 8601 transaction timestamp" },
      { name: "device_fingerprint", type: "string", nullPercentage: 8.4, distinctCount: 198000, qualityStatus: "warn", description: "Device hardware signature" },
    ],
    qualityTrace: [65, 72, 80, 55, 42, 68, 75, 82, 90, 60, 48, 52, 70, 78, 62, 55, 80, 85, 74, 60],
    qualityTracePeaks: [
      { pos: 4, label: "Null User UUID Spike", base: "T", severity: "mid" },
      { pos: 10, label: "Device Fingerprint Drop", base: "T", severity: "low" },
    ],
    versionHistory: [
      { version: "v1.0.0", commitHash: "7a8b1c", author: "ingest-pipeline", timestamp: "2026-07-01", message: "Initial S3 streaming batch ingestion", healthDelta: 0.0 },
    ],
  },

  "raw-users": {
    id: "raw-users",
    locusPath: "genome://retail/raw_users/v1.0",
    name: "raw_users",
    version: "v1.0",
    domain: "Identity",
    rowCount: 250000,
    columnCount: 12,
    sizeBytes: 42000000,
    healthStatus: "healthy",
    healthScore: 91.0,
    owner: "user-service",
    createdAt: "2026-07-01T08:30:00Z",
    lastUpdated: "2026-07-27T09:10:00Z",
    description: "Registered user profile records including sign-up demographic parameters.",
    tags: ["raw", "profiles", "identity"],
    parentIds: [],
    childIds: ["filtered-users"],
    schema: [
      { name: "user_uuid", type: "string", nullPercentage: 0.0, distinctCount: 250000, qualityStatus: "optimal", description: "Unique user account ID" },
      { name: "email_domain", type: "string", nullPercentage: 0.1, distinctCount: 840, qualityStatus: "optimal", description: "Normalized email domain" },
      { name: "signup_date", type: "datetime", nullPercentage: 0.0, distinctCount: 1250, qualityStatus: "optimal", description: "Account registration date" },
      { name: "postal_code", type: "string", nullPercentage: 4.8, distinctCount: 18500, qualityStatus: "warn", description: "5-digit postal code" },
    ],
    qualityTrace: [85, 88, 92, 90, 84, 88, 91, 95, 93, 89, 92, 94, 90, 88, 92, 95, 93, 91, 90, 92],
    qualityTracePeaks: [
      { pos: 12, label: "Postal Code Null Warning", base: "G", severity: "low" },
    ],
    versionHistory: [
      { version: "v1.0.0", commitHash: "3f2e1d", author: "user-service-db", timestamp: "2026-07-01", message: "Postgres read replica dump", healthDelta: 0.0 },
    ],
  },

  "filtered-users": {
    id: "filtered-users",
    locusPath: "genome://retail/filtered_users/v1.1",
    name: "filtered_users",
    version: "v1.1",
    domain: "Identity",
    rowCount: 215400,
    columnCount: 12,
    sizeBytes: 36200000,
    healthStatus: "healthy",
    healthScore: 96.5,
    owner: "data-quality-team",
    createdAt: "2026-07-05T11:00:00Z",
    lastUpdated: "2026-07-28T10:00:00Z",
    description: "Filtered user set removing bot signups, unverified emails, and test accounts.",
    tags: ["filtered", "clean", "identity"],
    parentIds: ["raw-users"],
    childIds: ["user-transactions"],
    derivationEvent: {
      operation: "FILTER",
      operator: "DropUnverifiedBotsRule",
      description: "Dropped 34,600 non-human bot signups and unverified email profiles.",
      parentNames: ["raw_users"],
    },
    schema: [
      { name: "user_uuid", type: "string", nullPercentage: 0.0, distinctCount: 215400, qualityStatus: "optimal", description: "Verified user account ID" },
      { name: "email_domain", type: "string", nullPercentage: 0.0, distinctCount: 780, qualityStatus: "optimal", description: "Verified email domain" },
      { name: "signup_date", type: "datetime", nullPercentage: 0.0, distinctCount: 1250, qualityStatus: "optimal", description: "Registration date" },
    ],
    qualityTrace: [92, 94, 96, 95, 93, 96, 97, 98, 96, 95, 97, 98, 96, 97, 98, 99, 96, 97, 95, 96],
    qualityTracePeaks: [],
    versionHistory: [
      { version: "v1.1.0", commitHash: "9c8b7a", author: "surabhicodes", timestamp: "2026-07-05", message: "Applied regex email verification filter", healthDelta: +5.5 },
    ],
  },

  "user-transactions": {
    id: "user-transactions",
    locusPath: "genome://retail/user_transactions/v2.0",
    name: "user_transactions",
    version: "v2.0",
    domain: "Integrated",
    rowCount: 1280000,
    columnCount: 22,
    sizeBytes: 210000000,
    healthStatus: "healthy",
    healthScore: 89.2,
    owner: "analytics-eng",
    createdAt: "2026-07-10T14:30:00Z",
    lastUpdated: "2026-07-28T16:00:00Z",
    description: "Joined purchase history with verified user demographic profile features.",
    tags: ["joined", "transactions", "demographics"],
    parentIds: ["raw-transactions", "filtered-users"],
    childIds: ["cleaned-events"],
    derivationEvent: {
      operation: "MERGE",
      operator: "InnerJoinUserTransactions",
      description: "Inner join raw_transactions with filtered_users on user_uuid key.",
      parentNames: ["raw_transactions", "filtered_users"],
    },
    schema: [
      { name: "txn_id", type: "string", nullPercentage: 0.0, distinctCount: 1280000, qualityStatus: "optimal", description: "Transaction ID" },
      { name: "user_uuid", type: "string", nullPercentage: 0.0, distinctCount: 215400, qualityStatus: "optimal", description: "Verified user identity" },
      { name: "amount", type: "float", nullPercentage: 0.0, distinctCount: 39500, qualityStatus: "optimal", description: "USD value" },
      { name: "postal_code", type: "string", nullPercentage: 3.9, distinctCount: 17200, qualityStatus: "warn", description: "Customer residence ZIP code" },
    ],
    qualityTrace: [82, 85, 88, 76, 80, 86, 90, 88, 85, 82, 86, 89, 91, 87, 85, 88, 90, 86, 84, 88],
    qualityTracePeaks: [
      { pos: 3, label: "Minor Postal Code Null Drift", base: "G", severity: "low" },
    ],
    versionHistory: [
      { version: "v2.0.0", commitHash: "4d5e6f", author: "data-eng", timestamp: "2026-07-10", message: "Spark inner join pipeline executed", healthDelta: +10.8 },
    ],
  },

  "cleaned-events": {
    id: "cleaned-events",
    locusPath: "genome://retail/cleaned_events/v2.1",
    name: "cleaned_events",
    version: "v2.1",
    domain: "Cleaned",
    rowCount: 1280000,
    columnCount: 22,
    sizeBytes: 210000000,
    healthStatus: "healthy",
    healthScore: 94.8,
    owner: "autoscientist-bot",
    createdAt: "2026-07-15T09:00:00Z",
    lastUpdated: "2026-07-28T18:00:00Z",
    description: "KNN imputed missing postal codes and Winsorized outlier transaction amounts.",
    tags: ["imputed", "winsorized", "autoscientist"],
    parentIds: ["user-transactions"],
    childIds: ["enriched-profiles"],
    derivationEvent: {
      operation: "TRANSFORM",
      operator: "KNNImputationTransformation",
      description: "KNN (k=5) missing value imputation on postal_code and 99th percentile Winsorization on amount.",
      parentNames: ["user_transactions"],
    },
    schema: [
      { name: "txn_id", type: "string", nullPercentage: 0.0, distinctCount: 1280000, qualityStatus: "optimal", description: "Transaction UUID" },
      { name: "amount_cleaned", type: "float", nullPercentage: 0.0, distinctCount: 38200, qualityStatus: "optimal", description: "Outlier-capped transaction value" },
      { name: "postal_code_imputed", type: "string", nullPercentage: 0.0, distinctCount: 18100, qualityStatus: "optimal", description: "KNN-imputed postal code" },
    ],
    qualityTrace: [90, 93, 95, 94, 92, 95, 96, 97, 95, 94, 96, 97, 95, 96, 97, 98, 96, 95, 94, 96],
    qualityTracePeaks: [],
    versionHistory: [
      { version: "v2.1.0", commitHash: "1a2b3c", author: "autoscientist", timestamp: "2026-07-15", message: "AutoScientist KNN imputation applied", healthDelta: +5.6 },
    ],
  },

  "enriched-profiles": {
    id: "enriched-profiles",
    locusPath: "genome://retail/enriched_profiles/v3.0",
    name: "enriched_profiles",
    version: "v3.0",
    domain: "Intelligence",
    rowCount: 1280000,
    columnCount: 28,
    sizeBytes: 245000000,
    healthStatus: "healthy",
    healthScore: 97.2,
    owner: "ml-research",
    createdAt: "2026-07-20T16:00:00Z",
    lastUpdated: "2026-07-29T11:00:00Z",
    description: "Annotated dataset enriched with LLM customer sentiment tags and RFM value segmentations.",
    tags: ["annotated", "enriched", "llm-embeddings", "rfm"],
    parentIds: ["cleaned-events"],
    childIds: ["customers", "churn-features"],
    derivationEvent: {
      operation: "ANNOTATE",
      operator: "Gemini25ProAnnotator",
      description: "Attached Gemini 2.5 Pro sentiment embeddings and RFM recency/monetary tiers.",
      parentNames: ["cleaned_events"],
    },
    schema: [
      { name: "rfm_segment", type: "category", nullPercentage: 0.0, distinctCount: 5, qualityStatus: "optimal", description: "Champions, Loyal, At Risk, Lost, Hibernating" },
      { name: "sentiment_score", type: "float", nullPercentage: 0.0, distinctCount: 100, qualityStatus: "optimal", description: "LLM inferred customer sentiment [-1.0, 1.0]" },
      { name: "churn_risk_tier", type: "category", nullPercentage: 0.0, distinctCount: 3, qualityStatus: "optimal", description: "Low, Medium, High" },
    ],
    qualityTrace: [94, 96, 97, 98, 96, 97, 98, 99, 97, 96, 98, 99, 98, 97, 98, 99, 98, 97, 96, 98],
    qualityTracePeaks: [],
    versionHistory: [
      { version: "v3.0.0", commitHash: "8d7e6f", author: "ml-research", timestamp: "2026-07-20", message: "Gemini 2.5 Pro LLM enrichment layer", healthDelta: +2.4 },
    ],
  },

  "customers": {
    id: "customers",
    locusPath: "genome://retail-data/customers/v3.2",
    name: "customers",
    version: "v3.2",
    domain: "Core Specimen",
    rowCount: 450000,
    columnCount: 28,
    sizeBytes: 98000000,
    healthStatus: "healthy",
    healthScore: 98.4,
    owner: "lead-data-scientist",
    createdAt: "2026-07-22T10:00:00Z",
    lastUpdated: "2026-07-29T14:00:00Z",
    description: "High-value active customer specimen filtered for downstream churn modeling and experiment planning.",
    tags: ["core-specimen", "active-users", "benchmark"],
    parentIds: ["enriched-profiles"],
    childIds: ["final-training"],
    derivationEvent: {
      operation: "FILTER",
      operator: "ActiveHighValueCustomerFilter",
      description: "Filtered active accounts with >= 2 transactions in 90-day window.",
      parentNames: ["enriched_profiles"],
    },
    schema: [
      { name: "customer_id", type: "string", nullPercentage: 0.0, distinctCount: 450000, qualityStatus: "optimal", description: "Primary customer UUID" },
      { name: "lifetime_value", type: "float", nullPercentage: 0.0, distinctCount: 38400, qualityStatus: "optimal", description: "90-day aggregated spend" },
      { name: "rfm_segment", type: "category", nullPercentage: 0.0, distinctCount: 4, qualityStatus: "optimal", description: "High value RFM cohort" },
      { name: "sentiment_score", type: "float", nullPercentage: 0.0, distinctCount: 98, qualityStatus: "optimal", description: "Aggregated sentiment score" },
      { name: "postal_code", type: "string", nullPercentage: 0.0, distinctCount: 14200, qualityStatus: "optimal", description: "KNN imputed geography" },
    ],
    qualityTrace: [96, 97, 98, 99, 98, 99, 99, 100, 98, 97, 99, 100, 99, 98, 99, 100, 99, 98, 97, 99],
    qualityTracePeaks: [],
    versionHistory: [
      { version: "v3.2.0", commitHash: "5b4a3c", author: "surabhicodes", timestamp: "2026-07-22", message: "Refined 90-day activity threshold filter", healthDelta: +1.2 },
      { version: "v3.1.0", commitHash: "2c1b0a", author: "surabhicodes", timestamp: "2026-07-21", message: "Initial active cohort selection", healthDelta: +0.0 },
    ],
  },

  "churn-features": {
    id: "churn-features",
    locusPath: "genome://retail/churn_features/v3.3",
    name: "churn_features",
    version: "v3.3",
    domain: "Feature Engineering",
    rowCount: 1280000,
    columnCount: 16,
    sizeBytes: 142000000,
    healthStatus: "healthy",
    healthScore: 93.6,
    owner: "feature-store",
    createdAt: "2026-07-23T12:00:00Z",
    lastUpdated: "2026-07-29T10:00:00Z",
    description: "Calculated 30-day, 60-day, and 90-day recency, frequency, and monetary velocity deltas.",
    tags: ["features", "velocity", "recency"],
    parentIds: ["enriched-profiles"],
    childIds: ["final-training"],
    derivationEvent: {
      operation: "TRANSFORM",
      operator: "VelocityFeatureTransformer",
      description: "Rolling window aggregated velocity calculations across 30d/60d/90d intervals.",
      parentNames: ["enriched_profiles"],
    },
    schema: [
      { name: "recency_days", type: "integer", nullPercentage: 0.0, distinctCount: 90, qualityStatus: "optimal", description: "Days since last transaction" },
      { name: "velocity_30d_vs_90d", type: "float", nullPercentage: 0.0, distinctCount: 12400, qualityStatus: "optimal", description: "Spend acceleration ratio" },
    ],
    qualityTrace: [88, 91, 93, 92, 90, 93, 95, 94, 92, 91, 94, 95, 93, 92, 94, 95, 93, 92, 91, 93],
    qualityTracePeaks: [],
    versionHistory: [
      { version: "v3.3.0", commitHash: "9e8d7c", author: "feature-store", timestamp: "2026-07-23", message: "Added 30d vs 90d spend velocity ratio", healthDelta: +3.6 },
    ],
  },

  "final-training": {
    id: "final-training",
    locusPath: "genome://retail/final_training_v4.0",
    name: "final_training",
    version: "v4.0",
    domain: "Benchmark Ready",
    rowCount: 450000,
    columnCount: 44,
    sizeBytes: 195000000,
    healthStatus: "healthy",
    healthScore: 99.1,
    owner: "autoscientist-lead",
    createdAt: "2026-07-25T15:00:00Z",
    lastUpdated: "2026-07-29T16:00:00Z",
    description: "Merged final training specimen for AutoScientist hypothesis & evaluation benchmark execution.",
    tags: ["final", "benchmark-ready", "autoscientist", "training"],
    parentIds: ["customers", "churn-features"],
    childIds: [],
    derivationEvent: {
      operation: "MERGE",
      operator: "JoinCustomersAndFeatures",
      description: "Left outer join customers specimen with churn_features on user_uuid.",
      parentNames: ["customers", "churn_features"],
    },
    schema: [
      { name: "customer_id", type: "string", nullPercentage: 0.0, distinctCount: 450000, qualityStatus: "optimal", description: "Primary customer key" },
      { name: "target_churned_30d", type: "boolean", nullPercentage: 0.0, distinctCount: 2, qualityStatus: "optimal", description: "Supervised target label" },
      { name: "lifetime_value", type: "float", nullPercentage: 0.0, distinctCount: 38400, qualityStatus: "optimal", description: "Customer lifetime value" },
    ],
    qualityTrace: [97, 98, 99, 100, 99, 100, 100, 100, 99, 98, 100, 100, 99, 98, 99, 100, 99, 98, 99, 100],
    qualityTracePeaks: [],
    versionHistory: [
      { version: "v4.0.0", commitHash: "0f1e2d", author: "autoscientist-lead", timestamp: "2026-07-25", message: "Final benchmark dataset build complete", healthDelta: +0.7 },
    ],
  },
};

export const MOCK_LINEAGE_RUNGS: LineageRung[] = [
  {
    id: "rung-1",
    sourceId: "raw-users",
    targetId: "filtered-users",
    operation: "FILTER",
    baseColor: "#D64545",
    baseCode: "T",
    operator: "DropUnverifiedBotsRule",
    description: "Dropped 34,600 unverified bot signups",
    transformedColumns: ["user_uuid", "email_domain"],
    metricsDelta: "-34,600 rows (Health: 91.0 -> 96.5)",
  },
  {
    id: "rung-2",
    sourceId: "raw-transactions",
    targetId: "user-transactions",
    operation: "MERGE",
    baseColor: "#3FA66D",
    baseCode: "A",
    operator: "InnerJoinUserTransactions",
    description: "Joined transaction telemetry with filtered user profiles",
    transformedColumns: ["user_uuid", "amount", "postal_code"],
    metricsDelta: "+8 feature columns (Health: 78.4 -> 89.2)",
  },
  {
    id: "rung-3",
    sourceId: "filtered-users",
    targetId: "user-transactions",
    operation: "MERGE",
    baseColor: "#3FA66D",
    baseCode: "A",
    operator: "InnerJoinUserTransactions",
    description: "Joined transaction telemetry with filtered user profiles",
    transformedColumns: ["user_uuid", "signup_date"],
    metricsDelta: "Key match rate 98.4%",
  },
  {
    id: "rung-4",
    sourceId: "user-transactions",
    targetId: "cleaned-events",
    operation: "TRANSFORM",
    baseColor: "#D98F3F",
    baseCode: "G",
    operator: "KNNImputationTransformation",
    description: "KNN (k=5) missing postal code imputation & Winsorized outliers",
    transformedColumns: ["postal_code", "amount"],
    metricsDelta: "Null ratio 3.9% -> 0.0% (Health: 89.2 -> 94.8)",
  },
  {
    id: "rung-5",
    sourceId: "cleaned-events",
    targetId: "enriched-profiles",
    operation: "ANNOTATE",
    baseColor: "#3C6E9C",
    baseCode: "C",
    operator: "Gemini25ProAnnotator",
    description: "Attached LLM sentiment embeddings & RFM segmentations",
    transformedColumns: ["rfm_segment", "sentiment_score", "churn_risk_tier"],
    metricsDelta: "+6 enrichment features (Health: 94.8 -> 97.2)",
  },
  {
    id: "rung-6",
    sourceId: "enriched-profiles",
    targetId: "customers",
    operation: "FILTER",
    baseColor: "#D64545",
    baseCode: "T",
    operator: "ActiveHighValueCustomerFilter",
    description: "Filtered active high-value cohort (>= 2 transactions in 90d)",
    transformedColumns: ["customer_id", "lifetime_value"],
    metricsDelta: "-830,000 inactive rows (Health: 97.2 -> 98.4)",
  },
  {
    id: "rung-7",
    sourceId: "enriched-profiles",
    targetId: "churn-features",
    operation: "TRANSFORM",
    baseColor: "#D98F3F",
    baseCode: "G",
    operator: "VelocityFeatureTransformer",
    description: "Calculated 30d/60d/90d velocity acceleration deltas",
    transformedColumns: ["recency_days", "velocity_30d_vs_90d"],
    metricsDelta: "+16 feature velocity metrics",
  },
  {
    id: "rung-8",
    sourceId: "customers",
    targetId: "final-training",
    operation: "MERGE",
    baseColor: "#3FA66D",
    baseCode: "A",
    operator: "JoinCustomersAndFeatures",
    description: "Merged customers cohort with churn features for AutoScientist benchmark",
    transformedColumns: ["customer_id", "target_churned_30d"],
    metricsDelta: "Final Training Specimen (Health: 99.1)",
  },
  {
    id: "rung-9",
    sourceId: "churn-features",
    targetId: "final-training",
    operation: "MERGE",
    baseColor: "#3FA66D",
    baseCode: "A",
    operator: "JoinCustomersAndFeatures",
    description: "Merged customers cohort with churn features for AutoScientist benchmark",
    transformedColumns: ["velocity_30d_vs_90d"],
    metricsDelta: "Complete 44-feature matrix",
  },
];
