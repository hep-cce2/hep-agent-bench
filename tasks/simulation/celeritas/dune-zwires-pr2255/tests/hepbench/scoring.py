"""Map a continuous figure of merit to a reward in [0, 1] (spec: grading.md, "Scores")."""

from __future__ import annotations

import math


def log_gain_vs_expert(agent_gain: float, expert_gain: float) -> float:
    """log(agent_gain) / log(expert_gain), uncapped: 1 matches the expert, > 1 beats it.

    A gain is a ratio over the baseline where larger is better, e.g. baseline_time / agent_time
    or agent_compression / baseline_compression.
    """
    if not (agent_gain > 0 and expert_gain > 0):
        raise ValueError(f"gains must be positive (agent {agent_gain}, expert {expert_gain})")
    if expert_gain <= 1:
        raise ValueError(f"expert does not improve on the baseline here ({expert_gain:.4g}x)")
    return math.log(agent_gain) / math.log(expert_gain)


def gated_reward(correct: bool, score: float) -> float:
    """0 unless the correctness gate passed; otherwise score clamped to [0, 1]."""
    return min(1.0, max(0.0, score)) if correct else 0.0
