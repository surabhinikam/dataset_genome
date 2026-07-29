"""
backend/app/publication/huggingface/validator.py — Hugging Face Package Validator.
"""

from pathlib import Path

class PackageValidator:
    """Validates Hugging Face repository files before release."""

    def validate(self, repo_dir: Path) -> bool:
        if not repo_dir.exists():
            return False
        readme = repo_dir / "README.md"
        return readme.exists() and readme.stat().st_size > 0
