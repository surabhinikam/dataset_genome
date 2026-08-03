"""
backend/app/benchmark/leaderboard.py — Benchmark Leaderboard Engine.

Ranks benchmark releases based on overall quality, adaptive score, coverage,
novelty, diversity, and publication readiness, exporting `benchmark_leaderboard.json`.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("dataset_genome.benchmark.leaderboard")


class BenchmarkLeaderboardEngine:
    """
    Ranks generated benchmark dataset versions for competitive benchmarking & leaderboards.
    """

    @staticmethod
    def update_leaderboard(
        versions_data: List[Dict[str, Any]],
        output_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """
        Rank version releases and build leaderboard JSON payload.
        """
        ranked = []
        for item in versions_data:
            version = item.get("version", "v1.0")
            quality = item.get("quality_score", 85.0)
            adaptive = item.get("adaptive_score", 88.0)
            coverage = item.get("knowledge_coverage", 90.0)
            novelty = item.get("novelty", 85.0)
            diversity = item.get("diversity_score", 85.0)
            readiness = 100.0 if item.get("is_valid", True) else 50.0

            # Composite Leaderboard Rank Score
            rank_score = round(
                quality * 0.25 +
                adaptive * 0.25 +
                coverage * 0.20 +
                novelty * 0.15 +
                diversity * 0.10 +
                readiness * 0.05,
                2
            )

            entry = {
                "version": version,
                "rank_score": rank_score,
                "overall_quality": quality,
                "adaptive_score": adaptive,
                "coverage": coverage,
                "novelty": novelty,
                "scientific_diversity": diversity,
                "publication_readiness": readiness,
                "total_samples": item.get("total_samples", 10),
            }
            ranked.append(entry)

        # Sort descending by rank score
        ranked.sort(key=lambda x: x["rank_score"], reverse=True)

        for rank_idx, entry in enumerate(ranked, 1):
            entry["rank"] = rank_idx

        leaderboard_payload = {
            "leaderboard_name": "Dataset Genome Benchmark Leaderboard",
            "total_versions": len(ranked),
            "top_version": ranked[0]["version"] if ranked else "v1.0",
            "leaderboard": ranked,
        }

        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(leaderboard_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"BenchmarkLeaderboardEngine saved leaderboard to '{p}'.")

        return leaderboard_payload
