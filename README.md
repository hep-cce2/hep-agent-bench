# hep-agent-bench

Benchmark tasks for AI agents, built from real HEP software problems and curated by the HEP-CCE Scaling ML group. Each task is a [Harbor](https://harborframework.com) task under `tasks/` (`instruction.md`, `task.toml`, `environment/`, `tests/`, `solution/`) that follows the [hep-agent-bench spec](https://github.com/hep-cce2/hep-agent-bench-spec). Graders use the [`hepbench`](https://github.com/hep-cce2/hep-agent-bench-tools) helpers.

New tasks are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md).

## tasks/frnn-exact-optimization

Speed up exact fixed-radius nearest-neighbor edge building in [libFRNN](https://github.com/xju2/libFRNN) (CUDA) on a real tracking event, without changing a single edge. Built on the pinned environment in [agent-env-frnn](https://github.com/xju2/agent-env-frnn).

**Scoring.** The grader builds three versions of the `frnn` Python package: the agent's tree, the pinned baseline, and the expert result (libFRNN v1.1.0 source, `tests/expert.patch`). Then:

1. the agent's `frnn.build_edges` must reproduce the reference edges of all 50 held-out events exactly (otherwise reward 0);
2. all three are timed on the same GPU in the same container, on a fixed subset of 5 held-out events (per event, the median of `TIMED_ITERATIONS` calls, each on a freshly permuted copy of the points);
3. speedup = total baseline time / total agent time over those events, and reward = `min(1, log(agent speedup) / log(expert speedup))`.

Because the expert is measured live, the target adapts to whichever GPU the trial runs on; no per-device reference numbers are stored. `metrics.json` also reports the uncapped `log_speedup_vs_expert`, which exceeds 1 when an agent beats the expert.

Results go to `/logs/verifier/metrics.json` in each trial.

### Setup on the GPU host

```bash
# 1. Base image
git clone https://github.com/xju2/agent-env-frnn && docker build --tag agent-env-frnn:cuda13.0-pytorch2.13 agent-env-frnn

# 2. Data (not committed)
#    development event, visible to the agent (public):
curl -O https://portal.nersc.gov/cfs/m3443/xju/frnn_data/embedding_data.csv \
     -O https://portal.nersc.gov/cfs/m3443/xju/frnn_data/edge_list.csv
mv embedding_data.csv edge_list.csv tasks/frnn-exact-optimization/environment/data/
#    held-out events (private; ask the maintainers for ttbar_mu200_itk_50evts/):
python tasks/frnn-exact-optimization/tests/make_heldout.py ttbar_mu200_itk_50evts tasks/frnn-exact-optimization/tests/data
```

The development event is in the CSV format of `agent-env-frnn/data` (points one per row, edges as a 2 × E array). The held-out events are ttbar, ⟨μ⟩ = 200, ITk events, one folder each with `embedding.npy` (N × 12, float32), `edges_libfrnn.npy`, `edges_frnn.npy` and `meta.json`. `make_heldout.py` checks each event's settings, cross-checks the two reference edge files, and writes `tests/data/`: the points (`<event>.npy`, about 13 MB each) and `heldout.json` with each event's edge count and SHA-256 digest, plus the 5 timed events. The reference edges themselves never enter the container. A failing event is reported in `metrics.json` (`failed_events`) with its edge count.

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
- The grader installs `hepbench` at grading time from `HEPBENCH_TOOLS` (a pinned git tag, see `task.toml`), so the verifier needs network access to GitHub, or point `HEPBENCH_TOOLS` at a local wheel.
- The network is public so installed agents can reach their model API; an agent could in principle fetch later libFRNN commits. Restrict `network_mode` / `allowed_hosts` for leaderboard runs.
- The held-out events must stay private: an agent with network access that could download them could look up stored answers by input.
