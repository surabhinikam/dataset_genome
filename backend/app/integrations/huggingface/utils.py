"""
backend/app/integrations/huggingface/utils.py — Transformers SDK Integration Utilities.

Provides utilities for loading compatible models and tokenizers.
Supports configurable model names without hardcoding specific models.
"""

import logging
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("dataset_genome.integrations.huggingface.utils")


class TransformersLoader:
    """
    Configurable model and tokenizer loader abstraction for Hugging Face Transformers.
    """

    def __init__(self, default_model_name: str = "meta-llama/Llama-3.2-1B") -> None:
        self.default_model_name = default_model_name

    def load_tokenizer(self, model_name: Optional[str] = None, **kwargs: Any) -> Any:
        """Load tokenizer using transformers AutoTokenizer."""
        target_name = model_name or self.default_model_name
        logger.info(f"TransformersLoader: Loading tokenizer for '{target_name}'...")

        try:
            from transformers import AutoTokenizer
            return AutoTokenizer.from_pretrained(target_name, **kwargs)
        except Exception as exc:
            logger.info(f"Mock Mode (`transformers` SDK omitted or unauthenticated): Returning mock tokenizer for '{target_name}'.")
            return {"model_name": target_name, "type": "MockTokenizer"}

    def load_model(self, model_name: Optional[str] = None, **kwargs: Any) -> Any:
        """Load causal language model using transformers AutoModelForCausalLM."""
        target_name = model_name or self.default_model_name
        logger.info(f"TransformersLoader: Loading model for '{target_name}'...")

        try:
            from transformers import AutoModelForCausalLM
            return AutoModelForCausalLM.from_pretrained(target_name, **kwargs)
        except Exception as exc:
            logger.info(f"Mock Mode (`transformers` SDK omitted or unauthenticated): Returning mock model for '{target_name}'.")
            return {"model_name": target_name, "type": "MockAutoModelForCausalLM"}

    def load_model_and_tokenizer(self, model_name: Optional[str] = None) -> Tuple[Any, Any]:
        """Load both model and tokenizer."""
        tok = self.load_tokenizer(model_name=model_name)
        mdl = self.load_model(model_name=model_name)
        return mdl, tok
