# hep-agent-bench

Benchmark tasks for AI agents, built from real HEP software problems and curated by the HEP-CCE Scaling ML group. Each task is a [Harbor](https://harborframework.com) task under `tasks/` (`instruction.md`, `task.toml`, `environment/`, `tests/`, `solution/`) that follows the [hep-agent-bench spec](https://github.com/hep-cce2/hep-agent-bench-spec). Graders use the [`hepbench`](https://github.com/hep-cce2/hep-agent-bench-tools) helpers.

New tasks are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md).

## tasks/simulation/celeritas/dune-zwires-pr2255

Speed up [Celeritas](https://github.com/celeritas-project/celeritas) optical-photon transport (`celer-optical`, CUDA, ORANGE geometry) on the DUNE Z-wires geometry without changing its physics. The agent starts from Celeritas `e906a7a8b` on `develop` and gets only a general goal, not where to look. The expert result is the next commit, [celeritas#2255](https://github.com/celeritas-project/celeritas/pull/2255) ("Fix infinities and unions in bounding zone", `d048aa67c`), which fixes ORANGE bounding boxes so that the DUNE photon detectors get finite ones. The dune-perf history (celeritas-project/dune-perf, private) shows it as the single largest step on this problem at that time (355 s → 197 s on a V100).

**Scoring.** The grader builds three versions of `celer-optical` with the same CMake options (`tests/build.sh`): the agent's tree, the pinned baseline, and the expert (baseline + `tests/expert.patch`, the `src/` diff of #2255). Each runs every held-out problem: 16.8 M optical photons from a held-out point in the liquid argon, with a held-out seed. Then:

1. on every problem, the agent must generate all photons, and its total step count must be within `STEP_TOLERANCE` (0.2%) of the baseline's (otherwise reward 0). Baseline and expert give identical step counts for the same seed; changing the seed moves the count by about 0.035%;
2. time = `setup` + `total` (transport) from the `celer-optical` output, summed over the problems;
3. speedup = baseline time / agent time, and reward = `min(1, log(agent speedup) / log(expert speedup))`.

On the RTX A6000 the expert gives 1.19× on the development problem (baseline 142 s, expert 119 s) and 1.20× over 4 held-out problems (262 s → 218 s), with identical step counts. The oracle scores 1.0. The gain is smaller than on a V100 because FP64 is slow on the A6000.

### Setup on the GPU host

```bash
docker pull docker.io/celeritas/ci-rocky-cuda12:2024-12-29
# Held-out problems (not committed): source positions and seeds drawn from a private seed
python tasks/simulation/celeritas/dune-zwires-pr2255/tests/make_heldout.py <private-seed> 4
```

The development problem (`environment/bench/dev.inp.json`) and the geometry (`dune-zwires.gdml`, from dune-perf `models/`, derived from DUNE's public `dune10kt_v6_refactored_1x2x6.gdml`; its provenance is in the file header) are committed. The grader uses its own copies in `tests/`.

### Run

```bash
CELER_GPU=0 harbor run -p tasks/simulation/celeritas/dune-zwires-pr2255 -a oracle
CELER_GPU=0 harbor run -p tasks/simulation/celeritas/dune-zwires-pr2255 -a terminus-2 -m openai/<model> --ak api_base=http://<host>:<port>/v1
```

`CELER_GPU` selects the device (default 0). A trial runs 3 builds (about 1 min each on 72 cores) and 12 runs (15–140 s each on the A6000, about 12 min in total).

### Known limitations

- **Copying the expert.** The expert is a public, merged PR, so three things guard against copying it:
  1. `network_mode = "no-network"`: the agent cannot reach GitHub, so it cannot fetch upstream Celeritas. terminus-2 calls the model from the host; for agents installed in the container Harbor allowlists only their inference host. The grader is offline too (hepbench v0.1.0 is vendored in `tests/hepbench`).
  2. The image holds only the baseline tree, as one fresh commit with no upstream history, and the CI base image predates #2255.
  3. `metrics.json` reports `expert_overlap`: the share of the expert patch's added code lines (≥ 12 characters, not comments) that also appear in the agent's `src/` changes. `suspected_copy` is set at `COPY_FLAG_THRESHOLD` (0.5) for manual review. It does not change the reward, because the oracle would fail it. This mainly catches a fix the model has memorized: #2255 was merged in Feb 2026 and may be in training data, which no sandbox can prevent.
- The verifier shares the agent's container (as in frnn), so a root agent could tamper with the toolchain. Use `verifier.environment_mode = "separate"` for adversarial runs.
- The gate checks photon count and total steps, not hit-level observables: `celer-optical` at this commit writes no detector scoring.
- `CUDAARCHS=86` (A6000) is set in the image. Change it there to grade on another GPU.

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
