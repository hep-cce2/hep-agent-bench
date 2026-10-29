The repository in `/workspace/libFRNN` is libFRNN, an exact fixed-radius nearest-neighbor library in C++/CUDA used to build graphs for GNN-based particle tracking.

Please read docs/optimize_compute.md for the "goal" and docs/performance_report.md for the current performance report from Codex. Optimization logs can be found at docs/optimization_log.md. Your task is to continue the optimization by exploring different algorithmic designs and CUDA-specific improvements. Keep going until the inference time for the real-life example on the available GPU is well below the current implementation's.

A real-life development event is in `data/embedding_data.csv` (271,663 points in 12 dimensions) with its reference edges in `data/edge_list.csv`; `tests/compare_reference_edges.py` compares against it.

How your work is graded, after you finish:

- Your final working tree in `/workspace/libFRNN` is built as the Python package `frnn` (`pip install --no-build-isolation .`). Keep the public `frnn.build_edges(points, radius=..., max_neighbors=..., directed=True)` API.
- Correctness is checked on a different, held-out event with the same settings (`radius=0.12`, `max_neighbors=1000`, directed). The set of edges must match the exact brute-force result exactly.
- If it is correct, the median wall-clock time of `frnn.build_edges` is compared with the original implementation on the same GPU. A larger speedup earns a higher score; incorrect results score zero.
