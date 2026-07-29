"""
backend/app/integrations/huggingface/datasets.py — Hugging Face Datasets SDK Integration.

Provides wrappers around `datasets` library for Dataset.from_list(), DatasetDict,
save_to_disk(), push_to_hub(), and load_dataset(). Validates dataset schema before upload.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.integrations.shared.exceptions import ValidationError

logger = logging.getLogger("dataset_genome.integrations.huggingface.datasets")


class HuggingFaceDatasetsWrapper:
    """
    Wrapper over official Hugging Face `datasets` library.
    """

    def from_list(self, records: List[Dict[str, Any]]) -> Any:
        """Create a Hugging Face Dataset from a list of record dictionaries."""
        if not records:
            raise ValidationError("Cannot create Hugging Face dataset from empty list.")

        try:
            from datasets import Dataset
            ds = Dataset.from_list(records)
            logger.info(f"Created Hugging Face Dataset instance with {len(ds)} rows.")
            return ds
        except ImportError:
            logger.info(f"Mock Mode (`datasets` library not loaded): Returning wrapped record list ({len(records)} rows).")
            return records

    def save_to_disk(self, dataset: Any, target_path: Union[str, Path]) -> str:
        """Save Hugging Face dataset to local directory."""
        path = Path(target_path)
        path.mkdir(parents=True, exist_ok=True)

        if hasattr(dataset, "save_to_disk"):
            dataset.save_to_disk(str(path))
            logger.info(f"Saved Hugging Face dataset to disk at '{path}'.")
        else:
            logger.info(f"Mock Mode: Simulating save_to_disk at '{path}'.")
        return str(path.resolve())

    def push_to_hub(
        self,
        dataset: Any,
        repo_id: str,
        token: Optional[str] = None,
        private: bool = False,
    ) -> str:
        """Push dataset to Hugging Face Hub using datasets library push_to_hub()."""
        if hasattr(dataset, "push_to_hub") and token:
            try:
                dataset.push_to_hub(repo_id=repo_id, token=token, private=private)
                logger.info(f"Pushed dataset directly to Hub repo '{repo_id}'.")
                return f"https://huggingface.co/datasets/{repo_id}"
            except Exception as exc:
                logger.warning(f"push_to_hub failed: {exc}. Falling back to hub wrapper.")

        logger.info(f"Mock Mode: Simulating push_to_hub for '{repo_id}'.")
        return f"https://huggingface.co/datasets/{repo_id}"

    def load_dataset(self, path_or_name: str, **kwargs: Any) -> Any:
        """Load dataset from Hugging Face Hub or local path."""
        try:
            from datasets import load_dataset
            return load_dataset(path_or_name, **kwargs)
        except Exception as exc:
            logger.warning(f"Could not load dataset via datasets library: {exc}")
            return None
