"""
backend/app/benchmark/exporter.py — Multi-Format Exporter for Official Benchmark v1.0.

Exports benchmark dataset samples into:
- JSON
- JSONL
- CSV
- Parquet (or Parquet-compatible tabular array)
- Hugging Face Dataset format
"""

import csv
import json
import logging
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.benchmark.models import BenchmarkSample

logger = logging.getLogger("dataset_genome.benchmark.exporter")


class BenchmarkExporter:
    """
    Multi-format exporter supporting JSON, JSONL, CSV, Parquet, and Hugging Face Dataset formats.
    """

    def export_json(
        self,
        samples: List[BenchmarkSample],
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """Export samples as formatted JSON string and optionally write to disk."""
        payload = [s.model_dump(mode="json") for s in samples]
        json_str = json.dumps(payload, indent=2, ensure_ascii=False)
        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json_str, encoding="utf-8")
            logger.info(f"BenchmarkExporter saved JSON dataset to '{p}'.")
        return json_str

    def export_jsonl(
        self,
        samples: List[BenchmarkSample],
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """Export samples as line-delimited JSONL string and optionally write to disk."""
        lines = [json.dumps(s.model_dump(mode="json"), ensure_ascii=False) for s in samples]
        jsonl_str = "\n".join(lines)
        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(jsonl_str, encoding="utf-8")
            logger.info(f"BenchmarkExporter saved JSONL dataset to '{p}'.")
        return jsonl_str

    def export_csv(
        self,
        samples: List[BenchmarkSample],
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """Export samples as tabular CSV string and optionally write to disk."""
        output = StringIO()
        fieldnames = [
            "sample_id", "dataset_id", "domain", "difficulty", "reasoning_style", "prompt", "context",
            "observation", "problem_identification", "research_gap", "primary_hypothesis",
            "alternative_hypothesis", "expected_results", "scientific_conclusion"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for s in samples:
            data = s.model_dump(mode="json")
            writer.writerow({k: data.get(k, "") for k in fieldnames})

        csv_str = output.getvalue()
        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(csv_str, encoding="utf-8")
            logger.info(f"BenchmarkExporter saved CSV dataset to '{p}'.")
        return csv_str

    def export_parquet(
        self,
        samples: List[BenchmarkSample],
        output_path: Optional[Union[str, Path]] = None,
    ) -> bytes:
        """Export samples into Apache Parquet format (using pyarrow/pandas if available, or binary serialization)."""
        try:
            import pandas as pd
            records = [s.model_dump(mode="json") for s in samples]
            df = pd.DataFrame(records)
            # Flatten complex dict/list fields to JSON string for parquet storage
            for col in ["experiment_design", "evaluation_metrics", "failure_cases", "metadata"]:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else str(x))

            if output_path:
                p = Path(output_path)
                p.parent.mkdir(parents=True, exist_ok=True)
                df.to_parquet(p, index=False)
                logger.info(f"BenchmarkExporter saved Parquet dataset via pandas to '{p}'.")
                return p.read_bytes()
            else:
                return df.to_parquet(index=False)
        except Exception as exc:
            logger.warning(f"Pandas/pyarrow parquet export fallback due to: {exc}. Exporting binary payload.")
            json_bytes = json.dumps([s.model_dump(mode="json") for s in samples]).encode("utf-8")
            if output_path:
                p = Path(output_path)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(json_bytes)
                logger.info(f"BenchmarkExporter saved Parquet fallback dataset to '{p}'.")
            return json_bytes

    def export_huggingface_format(
        self,
        samples: List[BenchmarkSample],
        output_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Export samples into Hugging Face Dataset format structure (DatasetDict compatible)."""
        features = {
            "sample_id": [s.sample_id for s in samples],
            "dataset_id": [s.dataset_id for s in samples],
            "domain": [s.domain for s in samples],
            "difficulty": [s.difficulty for s in samples],
            "reasoning_style": [getattr(s, "reasoning_style", "Positive Result") for s in samples],
            "prompt": [s.prompt for s in samples],
            "context": [s.context for s in samples],
            "observation": [s.observation for s in samples],
            "problem_identification": [s.problem_identification for s in samples],
            "research_gap": [s.research_gap for s in samples],
            "primary_hypothesis": [s.primary_hypothesis for s in samples],
            "alternative_hypothesis": [s.alternative_hypothesis for s in samples],
            "experiment_design": [s.experiment_design for s in samples],
            "evaluation_metrics": [s.evaluation_metrics for s in samples],
            "expected_results": [s.expected_results for s in samples],
            "failure_cases": [s.failure_cases for s in samples],
            "scientific_conclusion": [s.scientific_conclusion for s in samples],
            "metadata": [s.metadata for s in samples],
        }

        hf_payload = {
            "builder_name": "dataset_genome_benchmark",
            "citation": "@article{dataset_genome_2026, title={Dataset Genome: Autonomous AI Research Benchmark}}",
            "description": "Official Dataset Genome multi-domain scientific reasoning benchmark dataset.",
            "features": features,
            "num_rows": len(samples),
        }

        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(hf_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"BenchmarkExporter saved Hugging Face Dataset format payload to '{p}'.")

        return hf_payload
