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

## tasks/analysis/qa_1

Question q1 of the IRIS-HEP LLM performance suite ([gordonwatts/iris-hep-llm-performance](https://github.com/gordonwatts/iris-hep-llm-performance), `iris-hep-llm-questions.yaml`, commit `edb61b9`): write a single uv-runnable `script.py` that fetches one file of an ATLAS Open Data PHYSLITE dataset through ServiceX, plots ETmiss and prints a `METRIC:` line. The prompt is the upstream template with q1 filled in, plus where to work and how it is graded. The agent gets the pinned [IRIS-HEP skills](https://github.com/iris-hep/marketplace) (`skills_dir`), as the upstream runs do.

**Scoring.** Pass/fail. The grader re-runs `/workspace/script.py` with `uv run --script` in an empty directory; it must write `plot_1.png` and print exactly one `METRIC: avg_entries_per_event=<N> mean=<M>` line with both numbers within 2% (relative) of the upstream reference (1.0 and 16.451025). Spec v0.1 only defines `log-gain-vs-expert`, so this task declares `score = "pass-fail"`.

### Setup

```bash
cp ~/servicex.yaml tasks/analysis/qa_1/environment/servicex.yaml   # git-ignored; mounted read-only at /root/servicex.yaml
harbor run -p tasks/analysis/qa_1 -a oracle
```

Without that file Docker creates an empty directory in its place and ServiceX fails to authenticate. The oracle (`solution/script.py`) is a short reference script.

### Licence

The question, prompt and reference values come from iris-hep-llm-performance under the BSD 3-Clause License, copyright 2026 Gordon Watts; its licence is kept in `tasks/analysis/qa_1/LICENSE-iris-hep-llm-performance`. The IRIS-HEP skills (BSD 3-Clause, copyright 2025 IRIS-HEP) are cloned into the image at build time, not vendored here.

### Known limitations

- The reference values are public in the upstream repository, and the network is open (the agent needs ServiceX), so an agent could look them up and hard-code the `METRIC:` line. The grader re-runs the script and requires a plot, but does not check that the numbers came from the data.
- Grading depends on a live ServiceX endpoint and the agent's ServiceX token; the verifier shares the agent's container.

## tasks/analysis/qa_1_offline

The same question as `qa_1`, without ServiceX or credentials: the agent reads a local ATLAS Open Data PHYSLITE file with uproot. The script takes the file as its argument and is graded on a different, held-out file of the same dataset.

**ETmiss definition.** Upstream's ServiceX query `MissingET().First()` returns the first term of `MET_Core_AnalysisMET`, which is the SoftClusCore soft term and not a full ETmiss rebuilt with METMaker. Its mean on these files (16.42–16.52 GeV) matches the upstream reference, 16.451 GeV. The instruction names this term explicitly, so the task has one right answer.

**Scoring.** Pass/fail. The grader runs `python3 script.py <held-out file>` in an empty directory. The script must write `plot_1.png` and print one `METRIC:` line. Both numbers must match the grader's own computation on the held-out file within 1e-4 (relative). The development and held-out means differ by 0.6%, so a hard-coded development answer fails. The analysis stack and `hepbench` are baked into the image, so grading needs no network.

### Data (CERN Open Data record [80014](https://opendata.cern.ch/record/80014), CC0; Pythia8 dijet JZ2, DSID 364702; not committed)

```bash
URL=https://eospublic.cern.ch//eos/opendata/atlas/rucio/mc20_13TeV
# development file, copied into the image at /workspace/data/ (1.16 GB)
curl -fL -o tasks/analysis/qa_1_offline/environment/data/DAOD_PHYSLITE.38191877._000140.pool.root.1 \
     $URL/DAOD_PHYSLITE.38191877._000140.pool.root.1
# held-out file, seen only by the grader (1.17 GB)
curl -fL -o tasks/analysis/qa_1_offline/tests/data/DAOD_PHYSLITE.38191877._000142.pool.root.1 \
     $URL/DAOD_PHYSLITE.38191877._000142.pool.root.1
harbor run -p tasks/analysis/qa_1_offline -a oracle
```

The checksums (adler32) are `6a9c9561` for `._000140` and `4d48314a` for `._000142`; both files have 120,000 events.

### Known limitations

- The held-out file is public on CERN Open Data. An agent with network access could find it, but it would still have to compute the answer, since no reference values are stored.
- The network stays public so installed agents can reach their model API. The verifier shares the agent's container.
