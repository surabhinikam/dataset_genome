"""
backend/app/publication/huggingface/metadata.py — Hugging Face Metadata Generator.
"""

import json
from pathlib import Path
from typing import Dict, Any

class MetadataGenerator:
    """Generates dataset_info.json metadata."""

    def generate(self, dataset_version: str, sample_count: int, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        info = {
            "description": "Dataset Genome Scientific Reasoning Benchmark",
            "version": dataset_version,
            "download_size": sample_count * 1500,
            "dataset_size": sample_count * 1500,
        }
        meta_path = target_dir / "dataset_info.json"
        meta_path.write_text(json.dumps(info, indent=2), encoding="utf-8")
        return meta_path
