"""
services/autoscientist/prompt_builder.py — Grounded Prompt Builder for LLM Scientific Narrator.

Assembles strictly grounded prompts for Gemini 2.5 Pro ensuring zero metric hallucination.
"""

import json
from typing import Any, Dict
from services.autoscientist.llm_models import ExplanationTarget


class NarratorPromptBuilder:
    """
    Builder for generating grounded system and user prompts for LLM explanation tasks.
    """

    SYSTEM_INSTRUCTION = (
        "You are an expert LLM Scientific Narrator for the Dataset Genome AutoScientist platform.\n"
        "Your sole role is to provide clear, human-readable explanations of existing scientific outputs.\n"
        "CRITICAL RULES:\n"
        "1. You are an EXPLAINER, NOT a decision-maker. Do NOT invent new scientific hypotheses or alter reasoning.\n"
        "2. STRICT ZERO HALLUCINATION: You MUST NEVER invent or fabricate metrics, numbers, percentages, or claims not present in the input JSON context.\n"
        "3. Output MUST be a valid JSON object containing exactly 4 keys:\n"
        "   - 'scientific_summary': Detailed scientific narrative of underlying domain principles.\n"
        "   - 'executive_summary': High-level concise executive summary for C-suite leaders.\n"
        "   - 'technical_summary': Technical data engineering and algorithmic details.\n"
        "   - 'business_summary': Business impact, ROI potential, and risk mitigation summary.\n"
    )

    @classmethod
    def build_prompt(cls, target_type: ExplanationTarget, payload_data: Dict[str, Any]) -> str:
        """
        Assemble user prompt with structured input payload for Gemini 2.5 Pro.
        """
        json_payload_str = json.dumps(payload_data, indent=2, default=str)

        prompt = (
            f"Explain the following scientific workflow stage ({target_type.value}) for Dataset Genome.\n\n"
            f"--- INPUT STRUCTURED DATA ---\n"
            f"```json\n"
            f"{json_payload_str}\n"
            f"```\n\n"
            f"Generate the 4-part JSON explanation (scientific_summary, executive_summary, technical_summary, business_summary) "
            f"strictly using only the provided facts."
        )

        return prompt
