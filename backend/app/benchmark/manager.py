"""
backend/app/benchmark/manager.py — Official Benchmark Manager.

Master coordinator orchestrating benchmark dataset generation, validation, statistics computation,
versioning lineage tracking, multi-format exporting, and report generation for Dataset Genome Benchmark v1.0.
"""

import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from app.benchmark.exporter import BenchmarkExporter
from app.benchmark.generator import BenchmarkGenerator, SUPPORTED_DOMAINS
from app.benchmark.models import (
    BenchmarkReport,
    BenchmarkSample,
    BenchmarkStatistics,
    ValidationResult,
)
from app.benchmark.report import export_benchmark_report_json, export_benchmark_report_markdown
from app.benchmark.statistics import BenchmarkStatisticsEngine
from app.benchmark.validator import BenchmarkValidator
from app.benchmark.versioning import BenchmarkVersionManager

logger = logging.getLogger("dataset_genome.benchmark.manager")


class DatasetGenomeBenchmarkManager:
    """
    Master coordinator for creating, validating, versioning, exporting,
    and reporting the Official Dataset Genome Benchmark v1.0 dataset.
    """

    def __init__(self) -> None:
        self.generator = BenchmarkGenerator()
        self.validator = BenchmarkValidator()
        self.statistics_engine = BenchmarkStatisticsEngine()
        self.exporter = BenchmarkExporter()
        self.version_manager = BenchmarkVersionManager()

    def build_official_benchmark(
        self,
        samples_per_domain: int = 4,
        version_tag: str = "v1.0",
        export_dir: Optional[Union[str, Path]] = None,
    ) -> Tuple[List[BenchmarkSample], BenchmarkReport]:
        """
        Synthesize, validate, calculate stats, version, and export the official benchmark suite.
        """
        logger.info(f"DatasetGenomeBenchmarkManager initiating Official Benchmark '{version_tag}' build...")

        # 1. Generation
        samples = self.generator.generate_benchmark_suite(
            samples_per_domain=samples_per_domain,
            domains=SUPPORTED_DOMAINS,
        )

        # 2. Validation
        val_result: ValidationResult = self.validator.validate_benchmark_suite(samples)

        # 3. Statistics Computation
        stats: BenchmarkStatistics = self.statistics_engine.compute_statistics(samples)

        # 4. Versioning Registration
        version_rec = self.version_manager.register_version(
            version_tag=version_tag,
            stats=stats,
            changes_description=f"Official Release of Benchmark {version_tag} across {len(SUPPORTED_DOMAINS)} scientific domains.",
        )

        # 5. Multi-Format Exports
        exported_formats = ["JSON", "JSONL", "CSV", "Parquet", "HuggingFace"]
        if export_dir:
            target_dir = Path(export_dir)
            target_dir.mkdir(parents=True, exist_ok=True)
            self.exporter.export_json(samples, output_path=target_dir / f"benchmark_{version_tag}.json")
            self.exporter.export_jsonl(samples, output_path=target_dir / f"benchmark_{version_tag}.jsonl")
            self.exporter.export_csv(samples, output_path=target_dir / f"benchmark_{version_tag}.csv")
            self.exporter.export_parquet(samples, output_path=target_dir / f"benchmark_{version_tag}.parquet")
            self.exporter.export_huggingface_format(samples, output_path=target_dir / f"benchmark_{version_tag}_hf.json")

        report_id = f"rpt-bm-{uuid.uuid4().hex[:8]}"
        report = BenchmarkReport(
            report_id=report_id,
            version=version_tag,
            statistics=stats,
            validation=val_result,
            version_history=self.version_manager.list_versions(),
            exported_formats=exported_formats,
        )

        if export_dir:
            export_benchmark_report_json(report, output_path=target_dir / "benchmark_report.json")
            export_benchmark_report_markdown(report, output_path=target_dir / "benchmark_report.md")

        logger.info(
            f"DatasetGenomeBenchmarkManager complete! Built '{version_tag}' with {len(samples)} samples. "
            f"Validation Status: {'PASS' if val_result.is_valid else 'FAIL'}, Adaptive Score: {stats.adaptive_score}/100."
        )
        return samples, report
