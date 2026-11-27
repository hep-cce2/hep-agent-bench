"""Write reward.txt and metrics.json (spec: grading.md, "Results")."""

from __future__ import annotations

import json
import math
from pathlib import Path


def write_result(logs_dir, reward: float, correct: bool, **metrics) -> dict:
    """Write the Harbor reward and the spec's metrics.json; returns the metrics written."""
    from . import SPEC_VERSION

    if not (0.0 <= reward <= 1.0) or math.isnan(reward):
        raise ValueError(f"reward must be in [0, 1], got {reward}")
    logs = Path(logs_dir)
    logs.mkdir(parents=True, exist_ok=True)
    out = {"spec_version": SPEC_VERSION, "reward": reward, "correct": bool(correct), **metrics}
    (logs / "metrics.json").write_text(json.dumps(out, indent=2) + "\n")
    (logs / "reward.txt").write_text(f"{reward:.6f}\n")
    return out
