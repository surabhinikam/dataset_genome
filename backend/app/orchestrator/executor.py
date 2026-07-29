"""
backend/app/orchestrator/executor.py — Stage Executor & Retry Mechanism.

Wraps execution of individual pipeline stages with automatic retry logic, timing, and exception handling.
"""

import logging
import time
from typing import Any, Callable, Tuple

logger = logging.getLogger("dataset_genome.orchestrator.executor")


class StageExecutor:
    """
    Executes individual module functions with automatic retries and timing.
    """

    def __init__(self, max_retries: int = 2) -> None:
        self.max_retries = max_retries

    def execute_stage(self, stage_name: str, func: Callable[[], Any]) -> Tuple[Any, float]:
        """
        Execute stage_name calling func with max_retries.
        
        Returns:
            Tuple of (stage_result, elapsed_seconds)
        """
        start_t = time.time()
        attempt = 0
        last_exception = None

        while attempt <= self.max_retries:
            attempt += 1
            try:
                logger.info(f"StageExecutor running '{stage_name}' (Attempt {attempt}/{self.max_retries + 1})...")
                result = func()
                elapsed = round(time.time() - start_t, 2)
                logger.info(f"StageExecutor finished '{stage_name}' successfully in {elapsed}s.")
                return result, elapsed
            except Exception as exc:
                last_exception = exc
                logger.warning(f"StageExecutor error in '{stage_name}' on attempt {attempt}: {exc}")
                if attempt <= self.max_retries:
                    time.sleep(0.1 * attempt)

        elapsed = round(time.time() - start_t, 2)
        logger.error(f"StageExecutor failed '{stage_name}' after {self.max_retries + 1} attempts.")
        raise RuntimeError(f"Stage '{stage_name}' failed after {self.max_retries + 1} attempts: {last_exception}") from last_exception
