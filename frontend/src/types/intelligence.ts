/**
 * types/intelligence.ts — TypeScript types for Dataset Genome Analysis & Profilers.
 *
 * Mirrors backend/schemas/intelligence.py.
 */

export type IssueSeverity = "critical" | "warning" | "info";

export interface DatasetIssue {
  id: string;
  title: string;
  description: string;
  severity: IssueSeverity;
  column_name?: string;
  recommendation: string;
}

export interface CompletenessMetrics {
  score: number;
  total_cells: number;
  missing_cells: number;
  missing_cell_ratio: number;
  complete_row_ratio: number;
  column_missing_rates: Record<string, number>;
}

export interface ConsistencyMetrics {
  score: number;
  total_rows: number;
  duplicate_rows: number;
  duplicate_ratio: number;
  type_uniformity_scores: Record<string, number>;
  mixed_type_columns: string[];
}

export interface BalanceMetrics {
  score: number;
  categorical_entropy: Record<string, number>;
  majority_class_ratios: Record<string, number>;
  imbalanced_columns: string[];
}

export interface ColumnOutlierDetail {
  q1: number;
  q3: number;
  iqr: number;
  lower_bound: number;
  upper_bound: number;
  outlier_count: number;
  outlier_ratio: number;
}

export interface NoiseMetrics {
  score: number;
  total_outliers: number;
  outlier_ratio: number;
  column_outliers: Record<string, ColumnOutlierDetail>;
}

export interface CorrelationPair {
  column_1: string;
  column_2: string;
  coefficient: number;
}

export interface CorrelationMetrics {
  score: number;
  numeric_columns: string[];
  high_correlation_pairs: CorrelationPair[];
  matrix: Record<string, Record<string, number>>;
}

export interface FeatureQualityMetrics {
  score: number;
  total_features: number;
  constant_columns: string[];
  low_variance_columns: string[];
  id_like_columns: string[];
}

export interface HealthScoreResult {
  overall_score: number;
  grade: "Excellent" | "Good" | "Fair" | "Poor";
  grade_color: string;
  breakdown: Record<string, number>;
}

export interface GenomeReport {
  dataset_id: string;
  filename: string;
  num_rows: number;
  num_cols: number;
  column_names: string[];
  health_score: HealthScoreResult;
  completeness: CompletenessMetrics;
  consistency: ConsistencyMetrics;
  balance: BalanceMetrics;
  noise: NoiseMetrics;
  correlation: CorrelationMetrics;
  feature_quality: FeatureQualityMetrics;
  issues: DatasetIssue[];
  analyzed_at: string;
}
