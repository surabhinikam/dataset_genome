"""
backend/app/publication/huggingface/card_generator.py — MODULE 3 & 4: Card Generators.

Generates Hugging Face Dataset Card README.md (MODULE 3) and Model Card README.md (MODULE 4).
"""

import logging
from typing import Any, Dict, List, Optional

from app.adaptive_data.models import TrainingReadyDataset
from app.integrations.autoscientist.models import AutoScientistResult
from app.publication.config import DEFAULT_PUBLICATION_CONFIG, PublicationConfig

logger = logging.getLogger("dataset_genome.publication.huggingface.card_generator")


class CardGenerator:
    """
    MODULE 3 & 4 — Card Generator.
    """

    def __init__(self, config: PublicationConfig = DEFAULT_PUBLICATION_CONFIG) -> None:
        self.config = config

    def generate_dataset_card(self, dataset: TrainingReadyDataset) -> str:
        """MODULE 3: Generate Hugging Face Dataset Card README.md."""
        bs = dataset.balance_summary
        cs = dataset.cleaning_summary

        lines: List[str] = [
            "---",
            "language:",
            "- en",
            "license:",
            f"- {self.config.default_license}",
            "tags:",
            "- dataset-genome",
            "- autoscientist",
            "- scientific-reasoning",
            "pretty_name: Dataset Genome Benchmark",
            "---",
            "",
            "# Dataset Genome — Scientific Reasoning Benchmark",
            "",
            "## Project Overview & Scientific Motivation",
            "Dataset Genome is an autonomous, open-source scientific reasoning benchmark designed to evaluate "
            "and improve AI model capabilities in observation analysis, hypothesis generation, and experimental design.",
            "",
            "## Dataset Schema & Statistics",
            f"- **Dataset Version**: `{dataset.dataset_version}`",
            f"- **Total Retained Samples**: `{cs.cleaned_sample_count}`",
            f"- **Adaptive Score**: `{dataset.adaptive_score:.1f} / 100`",
            f"- **Training Readiness**: `{dataset.training_ready}`",
            "",
            "### Domain Distribution",
        ]

        for dom, cnt in bs.domain_distribution.items():
            lines.append(f"- **{dom}**: {cnt} sample(s)")

        lines.extend([
            "",
            "## Known Limitations & Future Improvements",
            "- Telemetry records represent controlled synthetic & empirical experiments.",
            "- Future iterations will incorporate live physical laboratory sensor streams.",
            "",
            "## Citation",
            "```bibtex",
            "@article{dataset_genome_2026,",
            "  title={Dataset Genome: Autonomous Scientific Reasoning Benchmark},",
            f"  author={{{self.config.author}}},",
            f"  year={{2026}},",
            f"  version={{{dataset.dataset_version}}}",
            "}",
            "```",
        ])

        return "\n".join(lines)

    def generate_model_card(self, result: AutoScientistResult, model_version: str = "v1.0") -> str:
        """MODULE 4: Generate Hugging Face Model Card README.md."""
        eval_rep = result.evaluation

        lines: List[str] = [
            "---",
            "language:",
            "- en",
            "license:",
            f"- {self.config.default_license}",
            "tags:",
            "- autoscientist",
            "- reasoning-model",
            "pipeline_tag: text-generation",
            "---",
            "",
            f"# AutoScientist Reasoning Model ({model_version})",
            "",
            "## Model Description & Pipeline",
            "The AutoScientist Reasoning Model formulates hypotheses and plans laboratory experiments based on structured 10-point reasoning chains.",
            "",
            "## Evaluation Metrics & Benchmarks",
            f"- **Job ID**: `{result.job_id}`",
            f"- **Reasoning Quality**: `{eval_rep.reasoning_quality_score:.1f} / 100`",
            f"- **Hypothesis Accuracy**: `{eval_rep.hypothesis_accuracy * 100:.1f}%`",
            f"- **Model Confidence**: `{eval_rep.confidence_score * 100:.1f}%`",
            "",
            "## Intended Use & Limitations",
            "- Intended for scientific hypothesis generation and anomaly troubleshooting.",
            "",
            "## Citation",
            "```bibtex",
            "@article{autoscientist_model_2026,",
            "  title={AutoScientist Reasoning Model},",
            f"  author={{{self.config.author}}},",
            f"  year={{2026}},",
            f"  version={{{model_version}}}",
            "}",
            "```",
        ]

        return "\n".join(lines)
