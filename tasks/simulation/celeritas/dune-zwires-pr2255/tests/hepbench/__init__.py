"""Grader helpers for hep-agent-bench tasks (https://github.com/hep-cce2/hep-agent-bench-spec)."""

from .results import write_result
from .scoring import gated_reward, log_gain_vs_expert
from .timing import median_time

SPEC_VERSION = "0.1"
__version__ = "0.1.0"
__all__ = ["SPEC_VERSION", "gated_reward", "log_gain_vs_expert", "median_time", "write_result"]
