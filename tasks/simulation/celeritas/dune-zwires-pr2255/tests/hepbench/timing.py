"""Timing protocol (spec: grading.md, "Timing")."""

from __future__ import annotations

import statistics
import time
from typing import Callable


def median_time(fn: Callable, make_input: Callable[[int], object], iterations: int) -> tuple:
    """Median wall time of fn(make_input(i)) for i in range(iterations), plus all times.

    make_input runs outside the timer and should return a fresh input each call (e.g. a
    seeded permutation) so a cached earlier result cannot be replayed. fn must not return
    before its work is done: synchronize the device inside it. Warm up before calling this.
    """
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    times = []
    for i in range(iterations):
        x = make_input(i)
        start = time.perf_counter()
        fn(x)
        times.append(time.perf_counter() - start)
    return statistics.median(times), times
