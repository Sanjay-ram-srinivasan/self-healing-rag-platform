import time
import logging
from contextlib import contextmanager

logger = logging.getLogger('performance')

@contextmanager
def timed_stage(stage_name: str, timeout_seconds: float = 30.0):
    """Measure execution time of a stage and enforce a timeout.
    If the stage exceeds `timeout_seconds`, a `TimeoutError` is raised.
    """
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        logger.info(f"[TIME] {stage_name}: {elapsed:.2f}s")
        if elapsed > timeout_seconds:
            raise TimeoutError(f"{stage_name} exceeded {timeout_seconds}s (took {elapsed:.2f}s)")
