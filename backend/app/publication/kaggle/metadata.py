"""
backend/app/publication/kaggle/metadata.py — Kaggle Metadata Generator.

Generates dataset-metadata.json required by Kaggle CLI.
"""

import json
from pathlib import Path

class KaggleMetadataGenerator:
    """Generates Kaggle CLI metadata json."""

    def generate(self, title: str, slug: str, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "title": title,
            "id": f"datasetgenome/{slug}",
            "licenses": [{"name": "CC0-1.0"}],
        }
        out_path = target_dir / "dataset-metadata.json"
        out_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return out_path
