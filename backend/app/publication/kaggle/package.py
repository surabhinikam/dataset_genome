"""
backend/app/publication/kaggle/package.py — Kaggle Dataset Packager.
"""

import json
from pathlib import Path
from app.adaptive_data.models import TrainingReadyDataset

class KagglePackager:
    """Copies sample dataset files into Kaggle bundle."""

    def prepare(self, dataset: TrainingReadyDataset, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        ds_dir = target_dir / "dataset"
        ds_dir.mkdir(exist_ok=True)

        samples = [r.model_dump() for r in dataset.cleaned_records[:5]]
        (target_dir / "sample_examples.json").write_text(json.dumps(samples, indent=2, default=str), encoding="utf-8")
        return target_dir
