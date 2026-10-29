# HEP-CCE benchmark tasks for AI agents

Harbor-format tasks (https://harborframework.com) built from real HEP software problems. Each task is a directory under `tasks/` with `instruction.md`, `task.toml`, `environment/`, `tests/` and `solution/`.

## tasks/frnn-exact-optimization

Speed up exact fixed-radius nearest-neighbor edge building in [libFRNN](https://github.com/xju2/libFRNN) (CUDA) on a real tracking event, without changing a single edge. Built on the pinned environment in [agent-env-frnn](https://github.com/xju2/agent-env-frnn).

**Scoring.** The grader builds three versions of the `frnn` Python package: the agent's tree, the pinned baseline, and the expert result (libFRNN v1.1.0 source, `tests/expert.patch`). Then:

1. the agent's `frnn.build_edges` must reproduce the reference edges of a held-out event exactly (otherwise reward 0);
2. all three are timed on the same GPU in the same container (median of `TIMED_ITERATIONS` calls, each on a freshly permuted copy of the points);
3. reward = `min(1, log(agent speedup) / log(expert speedup))`, both speedups over the baseline.

Because the expert is measured live, the target adapts to whichever GPU the trial runs on; no per-device reference numbers are stored. `metrics.json` also reports the uncapped `log_speedup_vs_expert`, which exceeds 1 when an agent beats the expert.

Results go to `/logs/verifier/metrics.json` in each trial.

### Setup on the GPU host

```bash
# 1. Base image
git clone https://github.com/xju2/agent-env-frnn && docker build --tag agent-env-frnn:cuda13.0-pytorch2.13 agent-env-frnn

# 2. Data (not committed)
#    development event, visible to the agent:
cp embedding_data.csv edge_list.csv tasks/frnn-exact-optimization/environment/data/
#    held-out event, only copied in at grading time:
cp heldout_embedding.csv tasks/frnn-exact-optimization/tests/data/embedding_data.csv
cp heldout_edges.csv     tasks/frnn-exact-optimization/tests/data/edge_list.csv

```

Both CSV pairs use the same format as `agent-env-frnn/data` (points one per row, edges as a 2 × E array). The held-out event can have any number of points.

The oracle (`solution/`) applies the source changes of libFRNN v1.1.0 to the pinned checkpoint.

### Run

```bash
nvidia-smi -L                                       # find the GPU index
FRNN_GPU=1 harbor run -p tasks/frnn-exact-optimization -a oracle
FRNN_GPU=1 harbor run -p tasks/frnn-exact-optimization -a terminus-2 \
    -m openai/<model> --ak api_base=http://<host>:<port>/v1
```

`FRNN_GPU` selects the device (default 0); run all arms of a comparison on the same GPU.

### Known limitations

- The verifier shares the agent's container and the agent runs as root. The grader checks the baseline source against its pinned manifest, but a determined agent could still tamper with the toolchain. Use `verifier.environment_mode = "separate"` before treating scores as adversarially robust.
- The network is public so installed agents can reach their model API; an agent could in principle fetch later libFRNN commits. Restrict `network_mode` / `allowed_hosts` for leaderboard runs.
- If only one event is available, using it for both `environment/data` and `tests/data` still works but no longer guards against an agent caching that event's answer.
