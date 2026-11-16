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

## tasks/analysis/qa_1_offline

All 21 questions of the IRIS-HEP LLM performance suite ([gordonwatts/iris-hep-llm-performance](https://github.com/gordonwatts/iris-hep-llm-performance), `iris-hep-llm-questions.yaml`, commit `edb61b9`), made to run offline. Upstream fetches data through ServiceX; here each script reads local ATLAS Open Data PHYSLITE files with uproot, so no credentials are needed. The prompt follows the upstream template. The agent writes `/workspace/q<n>/script.py` for each question and gets the pinned [IRIS-HEP skills](https://github.com/iris-hep/marketplace) (`skills_dir`).

**Definitions.** Upstream's questions leave some choices open, and its reference values come from ServiceX/func_adl defaults. The instruction states one definition for each such choice. Each was chosen by reproducing upstream's numbers on the file upstream most likely used (`tests/reference.py`):

| Choice | Definition | Upstream check |
|---|---|---|
| Arithmetic | float64; PHYSLITE stores float32, and float32 trijet masses pick different combinations in q6 | — |
| ETmiss | First `MET_Core_AnalysisMET` term (SoftClusCore), which is what `MissingET().First()` returns; not a METMaker-rebuilt ETmiss | q5, q8 exact; q1, q4 within 0.6% (different JZ2 file) |
| b-tagging discriminant | DL1dv01, f_c = 0.018 | q6 exact, q17 1% |
| q5 denominator | All events, not selected events | exact |
| q18 η cut | \|η\| < 2.4 (upstream text says η < 2.4, but its value needs \|η\|) | 0.3% |
| q16 tt̄ mass | Lepton + neutrino (ETmiss, p_z = 0) + 4 leading jets | 0.05% |
| q20 variable | `numberOfPrecisionLayers` (`numberOfGoodPrecisionLayers` also exists) | — |
| q21 valid link | `m_persKey != 0` | 0.04% |

The other questions use the literal reading of upstream's text. Some upstream values differ by more than 1% because upstream used different files or settings: q12 (avg +3.6%), q13 (+1.5%) and q15 (−6%; the JZ2/JZ3 files differ in event count). **q19:** upstream's `HLT_j460=902` cannot come from one file. File `37861619._000001` gives 191, which agrees with 190 events having an offline leading jet above 460 GeV.

**Scoring.** Reward = fraction of the 21 questions passed. For each question the grader:
- copies the script to an empty directory and runs it on held-out files of the same dataset;
- computes the reference with `tests/reference.py` on the same files;
- requires the plot(s) and the same number of `METRIC:` lines, with every value within 1e-5 relative (q19: `triggers.md` and the exact `HLT_j460` count).

Every development and held-out answer differs by more than the tolerance (the smallest gap is q9, 6e-5), so hard-coding development results fails. The oracle turns `solution/reference.py`, an identical copy of `tests/reference.py` that must be kept in sync, into 21 stand-alone scripts. Spec v0.1 only defines `log-gain-vs-expert`, so this task declares `score = "fraction-passed"`.

### Data (CERN Open Data 2024 research release, CC0; not committed)

| DSID | Questions | Record | Development file → `environment/data/` | Held-out file → `tests/data/` |
|---|---|---|---|---|
| 364702 dijet JZ2 | q1–4, 9, 11, 14, 15 | [80014](https://opendata.cern.ch/record/80014) | `38191877._000140` (1.16 GB) | `38191877._000142` (1.17 GB) |
| 364703 dijet JZ3 | q15 | 80014 | `38191774._000013` (1.12 GB) | `38191774._000012` (1.12 GB) |
| 410471 ttbar all-had | q6, 7, 10, 17–19, 21 | [80017](https://opendata.cern.ch/record/80017) | `37861619._000001` (0.46 GB) | `37861619._000245` (0.46 GB) |
| 700325 Z→μμ | q5, 12, 13, 20 | [80010](https://opendata.cern.ch/record/80010) | `37621409._000001` (0.58 GB) | `37621417._000006` (0.23 GB) |
| 700588 lllvjj | q8 | 80010 | `37110891._000001` (0.61 GB) | none: only one public file |
| 301333 Z′→tt | q16 | [80011](https://opendata.cern.ch/record/80011) | `38191516._000001` (0.96 GB) | none: only one public file |

```bash
cd tasks/analysis/qa_1_offline
URL=https://eospublic.cern.ch//eos/opendata/atlas/rucio/mc20_13TeV
get() { curl -fL -o "$1/DAOD_PHYSLITE.$2.pool.root.1" "$URL/DAOD_PHYSLITE.$2.pool.root.1"; }
for f in 38191877._000140 38191774._000013 37861619._000001 37621409._000001 37110891._000001 38191516._000001; do get environment/data $f; done
for f in 38191877._000142 38191774._000012 37861619._000245 37621417._000006; do get tests/data $f; done
harbor run -p tasks/analysis/qa_1_offline -a oracle
```

The image holds 4.9 GB of development files, and `tests/data` holds 3.0 GB. `atlasopenmagic` (`get_urls('<DSID>')`, release `2024r-pp`) lists every file of a dataset.

### Licence

The questions, prompt template and upstream reference values come from iris-hep-llm-performance under the BSD 3-Clause License, copyright 2026 Gordon Watts; its licence is kept in `tasks/analysis/qa_1_offline/LICENSE-iris-hep-llm-performance`. The IRIS-HEP skills (BSD 3-Clause, copyright 2025 IRIS-HEP) are cloned into the image at build time, not vendored here. The data files are CC0.

### Known limitations

- q8 and q16 are graded on their development files, because 700588 and 301333 have one public file each. The grader hash-checks those files, but a script could hard-code those two answers.
- The held-out files are public on CERN Open Data. An agent with network access could find them, but it would still have to compute the answers, since no reference values are stored.
- The network stays public so installed agents can reach their model API. The verifier shares the agent's container.
