"""
backend/app/benchmark/prompt_builder.py — LLM Prompt Builder for Benchmark Generation.

Constructs the system + user LLMMessage pair for each (domain, difficulty, index)
combination.  No external I/O — pure string construction.

Design principles:
  - System prompt casts the model as a domain scientist with strict JSON-only output.
  - User prompt specifies domain, difficulty constraints, and the exact JSON schema.
  - Difficulty modulates content depth:
      Easy   — single-variable hypothesis, simple experiment
      Medium — two interacting factors, standard controls
      Hard   — multi-factor confounders, advanced methodology
      Expert — multi-causal chain, quantitative thresholds, competing mechanisms
"""

import random
from typing import List, Optional

from app.llm.models import LLMMessage


# ---------------------------------------------------------------------------
# Required JSON fields that the LLM must populate in its response.
# Maps 1-to-1 to BenchmarkSample fields that are LLM-authored
# (sample_id / dataset_id / domain / difficulty / metadata are set by the caller).
# ---------------------------------------------------------------------------
_REQUIRED_FIELDS = [
    "prompt",
    "context",
    "observation",
    "problem_identification",
    "research_gap",
    "primary_hypothesis",
    "alternative_hypothesis",
    "experiment_design",
    "evaluation_metrics",
    "expected_results",
    "failure_cases",
    "scientific_conclusion",
]

# ---------------------------------------------------------------------------
# Scientific Reasoning Styles for diversity enhancement
# ---------------------------------------------------------------------------
REASONING_STYLES = {
    "Positive result": (
        "Construct a scenario where empirical findings strongly support the primary hypothesis "
        "with statistically significant positive evidence."
    ),
    "Negative result": (
        "Construct a scenario where rigorous experimental testing disproves or fails to support the primary hypothesis, "
        "confirming a null or inverse relationship despite sound methodology."
    ),
    "Ambiguous result": (
        "Construct a scenario where experimental data yields inconclusive or borderline findings, "
        "requiring nuanced statistical interpretation, higher sample power, or refined measurement resolution."
    ),
    "Conflicting literature": (
        "Construct a scenario where the primary hypothesis attempts to reconcile two contradicting findings or "
        "incompatible models published in recent literature."
    ),
    "Failed experiment": (
        "Construct a scenario where experimental execution encounters unexpected methodological failure, "
        "systematic measurement artifacts, or severe environmental interference that obscures the true underlying effect."
    ),
    "Replication study": (
        "Construct a systematic replication attempt of a landmark finding, evaluating whether the effect holds "
        "under modified conditions, different sample populations, or updated technical protocols."
    ),
    "Unexpected observation": (
        "Construct a scenario where an unpredicted empirical anomaly or surprise discovery occurs during testing, "
        "challenging established theoretical assumptions and opening new research avenues."
    ),
}

_SYSTEM_PROMPT = """\
You are an expert scientific dataset curator and domain researcher. \
Your role is to generate high-quality, scientifically rigorous benchmark samples \
for training and evaluating AI scientific reasoning models.

STRICT RULES:
1. You MUST respond ONLY with a valid JSON object — no markdown fences, no prose, no commentary.
2. Every field must contain substantive, domain-accurate scientific content.
3. Values must be quantitatively specific: include actual measurements, concentrations, \
   percentages, rates, or statistical thresholds where applicable.
4. Do NOT copy from any previous examples. Each sample must be unique.
5. The JSON object must contain exactly the keys listed in the user prompt schema.
"""

_DIFFICULTY_MODIFIERS = {
    "Easy": (
        "Focus on a single-variable cause-effect relationship. "
        "The hypothesis should be directly testable with one controlled experiment. "
        "Use simple baseline controls and 2-3 evaluation metrics."
    ),
    "Medium": (
        "Address two interacting factors. "
        "The hypothesis should account for one confounding variable. "
        "Design a controlled experiment with proper randomisation and 3-4 metrics."
    ),
    "Hard": (
        "Model a multi-factor system with at least two competing confounders. "
        "The primary hypothesis must distinguish between mechanistic alternatives. "
        "Experiment design must specify blinding, sample size, and power analysis. "
        "Include 4-5 quantitative evaluation metrics."
    ),
    "Expert": (
        "Construct a multi-causal chain with competing mechanistic pathways. "
        "The primary hypothesis must make a precise quantitative prediction "
        "(e.g. '>= 3.5-fold increase', 'p < 0.001'). "
        "The alternative hypothesis must represent a plausible rival mechanism. "
        "Experiment design must include multi-arm comparison, statistical power, "
        "and at least one negative control arm. "
        "Provide 5+ evaluation metrics with defined pass/fail thresholds."
    ),
}

_USER_PROMPT_TEMPLATE = """\
Generate a {difficulty}-difficulty scientific reasoning benchmark sample for the domain: \
**{domain}** (sample #{index}).

Reasoning Style Context: **{reasoning_style}**
Reasoning Guidance: {reasoning_style_guidance}

Difficulty guidance: {difficulty_modifier}

Respond with a JSON object containing EXACTLY these keys:

{{
  "prompt": "<Scientific inquiry question about a specific anomaly or phenomenon>",
  "context": "<Experimental setup, dataset description, or observational background>",
  "observation": "<Specific empirical finding, measurement, or anomalous data point>",
  "problem_identification": "<Core scientific problem or research bottleneck identified>",
  "research_gap": "<Specific unanswered question or knowledge gap in the literature>",
  "primary_hypothesis": "<Testable, falsifiable primary hypothesis with quantitative prediction>",
  "alternative_hypothesis": "<Plausible rival mechanism or counter-hypothesis>",
  "experiment_design": {{
    "methodology": "<Specific experimental technique or computational method>",
    "variables": {{"independent": "<IV>", "dependent": "<DV>"}},
    "control": "<Control condition or baseline>",
    "sample_size": "<n or statistical justification>"
  }},
  "evaluation_metrics": ["<Metric 1>", "<Metric 2>", "..."],
  "expected_results": "<Predicted outcome if primary hypothesis holds, with quantitative threshold>",
  "failure_cases": ["<Failure mode 1>", "<Failure mode 2>"],
  "scientific_conclusion": "<Deductive synthesis of what the results would establish>"
}}

Important: Output ONLY the JSON. No markdown. No explanation.
"""


class BenchmarkPromptBuilder:
    """
    Constructs LLMMessage lists for benchmark sample generation.

    Each call to build_messages() produces a fresh [system, user] message pair
    that is fed directly to LLMFactory.get_provider().generate().
    """

    @staticmethod
    def build_messages(
        domain: str,
        difficulty: str,
        index: int = 1,
        reasoning_style: Optional[str] = None,
    ) -> List[LLMMessage]:
        """
        Build the [system, user] message pair for one benchmark sample generation call.

        Args:
            domain:          Scientific domain (must be one of SUPPORTED_DOMAINS).
            difficulty:      Difficulty level (Easy / Medium / Hard / Expert).
            index:           Sample ordinal within the domain — used for uniqueness nudging.
            reasoning_style: Optional explicit reasoning style. If None, one is randomly sampled.

        Returns:
            List of two LLMMessage instances: [system_message, user_message].
        """
        if reasoning_style is not None and reasoning_style in REASONING_STYLES:
            selected_style = reasoning_style
        else:
            selected_style = random.choice(list(REASONING_STYLES.keys()))

        style_guidance = REASONING_STYLES[selected_style]
        modifier = _DIFFICULTY_MODIFIERS.get(difficulty, _DIFFICULTY_MODIFIERS["Medium"])

        user_content = _USER_PROMPT_TEMPLATE.format(
            domain=domain,
            difficulty=difficulty,
            index=index,
            difficulty_modifier=modifier,
            reasoning_style=selected_style,
            reasoning_style_guidance=style_guidance,
        )

        return [
            LLMMessage(role="system", content=_SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_content),
        ]

    @staticmethod
    def required_fields() -> List[str]:
        """Return the list of field names the LLM must supply in its JSON response."""
        return list(_REQUIRED_FIELDS)

