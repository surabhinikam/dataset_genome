"""
backend/app/publication/kaggle/validator.py — Kaggle Package Validator.
"""

from pathlib import Path

class KaggleValidator:
    """Validates Kaggle bundle structure."""

    def validate(self, bundle_dir: Path) -> bool:
        meta = bundle_dir / "dataset-metadata.json"
        return meta.exists() and meta.stat().st_size > 0
