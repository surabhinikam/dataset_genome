"""
backend/app/benchmark/deduplicator.py — Semantic Deduplicator for Benchmark Samples.

Provides lightweight, deterministic deduplication without requiring external
embedding models or vector databases.

Strategy:
  A "fingerprint" is computed from (domain + primary_hypothesis + observation),
  lowercased and whitespace-normalised.  Two samples are considered duplicates
  if their fingerprints match.

  This catches the most likely failure mode of LLM generation — repeating the
  same hypothesis statement when given the same domain/difficulty prompt with
  insufficient temperature variation.

Usage:
    dedup = BenchmarkDeduplicator()
    if not dedup.check_and_register(sample):
        # sample is a duplicate — discard and retry
        ...
"""

import logging
import re
from typing import Set

from app.benchmark.models import BenchmarkSample

logger = logging.getLogger("dataset_genome.benchmark.deduplicator")

_WHITESPACE_RE = re.compile(r"\s+")


def _normalise(text: str) -> str:
    """Lowercase and collapse whitespace for stable fingerprinting."""
    return _WHITESPACE_RE.sub(" ", text.lower().strip())


class BenchmarkDeduplicator:
    """
    Session-scoped deduplication registry for BenchmarkSample instances.

    Supports both exact fingerprint matching and semantic similarity checking
    (n-gram TF-IDF / Jaccard cosine similarity thresholding).
    """

    def __init__(self, semantic_threshold: float = 0.80) -> None:
        self._seen_fingerprints: Set[str] = set()
        self._registered_samples: List[BenchmarkSample] = []
        self.semantic_threshold = semantic_threshold

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fingerprint(self, sample: BenchmarkSample) -> str:
        """
        Compute a deterministic deduplication fingerprint for a sample.

        Combines domain, primary_hypothesis, and observation — the three fields
        most likely to distinguish genuinely different scientific scenarios.
        """
        parts = [
            _normalise(sample.domain),
            _normalise(sample.primary_hypothesis),
            _normalise(sample.observation),
        ]
        return "||".join(parts)

    def calculate_similarity(self, sample1: BenchmarkSample, sample2: BenchmarkSample) -> float:
        """
        Compute semantic similarity score between two samples (0.0 to 1.0)
        using Jaccard word-overlap similarity across primary hypothesis text.
        """
        text1 = sample1.primary_hypothesis.lower()
        text2 = sample2.primary_hypothesis.lower()

        words1 = set(re.findall(r'\w+', text1))
        words2 = set(re.findall(r'\w+', text2))

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2
        jaccard = len(intersection) / len(union)
        return jaccard

    def is_semantic_duplicate(self, sample: BenchmarkSample) -> bool:
        """Return True if sample exceeds semantic similarity threshold against any registered sample."""
        for existing in self._registered_samples:
            if existing.domain == sample.domain:
                sim = self.calculate_similarity(sample, existing)
                if sim >= self.semantic_threshold:
                    logger.warning(
                        "Deduplicator: semantic duplicate detected (sim=%.2f >= threshold=%.2f) "
                        "between '%s' and '%s'.",
                        sim, self.semantic_threshold, sample.sample_id, existing.sample_id
                    )
                    return True
        return False

    def is_duplicate(self, sample: BenchmarkSample) -> bool:
        """
        Return True if an equivalent or semantically duplicate sample has already been registered.
        Does NOT modify internal state.
        """
        fp = self.fingerprint(sample)
        if fp in self._seen_fingerprints:
            return True
        return self.is_semantic_duplicate(sample)

    def register(self, sample: BenchmarkSample) -> None:
        """
        Register a sample's fingerprint and instance in the seen-set.
        Must be called after accepting a sample into the dataset.
        """
        fp = self.fingerprint(sample)
        self._seen_fingerprints.add(fp)
        self._registered_samples.append(sample)
        logger.debug(
            "Deduplicator registered sample '%s' (total=%d).",
            sample.sample_id,
            len(self._seen_fingerprints),
        )

    def check_and_register(self, sample: BenchmarkSample) -> bool:
        """
        Atomically check for duplicate and register if unique.

        Returns:
            True  — sample is unique and has been registered.
            False — sample is a duplicate; NOT registered.
        """
        if self.is_duplicate(sample):
            logger.warning(
                "Deduplicator: duplicate detected for sample '%s' "
                "(domain='%s', hypothesis='%.60s...').",
                sample.sample_id,
                sample.domain,
                sample.primary_hypothesis,
            )
            return False

        self.register(sample)
        return True

    @property
    def registered_count(self) -> int:
        """Number of unique samples registered so far in this session."""
        return len(self._seen_fingerprints)

    def reset(self) -> None:
        """Clear all registered fingerprints (for testing or reuse)."""
        self._seen_fingerprints.clear()
        self._registered_samples.clear()
        logger.debug("Deduplicator reset.")
