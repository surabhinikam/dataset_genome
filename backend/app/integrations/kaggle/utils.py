"""
backend/app/integrations/kaggle/utils.py — Kaggle Utility Functions.
"""

import json
from pathlib import Path
from typing import Dict, Any

def create_kaggle_metadata(title: str, slug: str, licenses: list, target_path: Path) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "title": title,
        "id": f"datasetgenome/{slug}",
        "licenses": licenses,
    }
    target_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return target_path
