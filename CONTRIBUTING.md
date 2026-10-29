# Contributing a task

A good task is a real problem your team has already solved (or knows how to solve) at expert level, where success can be checked automatically. Examples in progress: Celeritas (kernel → mini-app → detector stack) and RNTuple compression.

## 1. Propose it

Open an issue with:
- **Problem**: the code, the pinned starting commit, and what the agent should improve.
- **Expert result**: the commit, release or patch that represents an expert-level solution. The grader measures it live, so it must be buildable from the starting commit.
- **Gate**: how correctness is checked: exact match, lossless round trip, or physics validation with a stated tolerance ([grading.md](https://github.com/hep-cce2/hep-agent-bench-spec/blob/main/grading.md#correctness-gate)).
- **Figure of merit**: what is measured, as a gain over the baseline (time, compression ratio, …).
- **Data**: a development input for the agent and a different held-out input for grading, with sizes and where they will live.
- **Hardware**: CPU or GPU, and any architecture limits.

## 2. Build it

Use [`tasks/frnn-exact-optimization`](tasks/frnn-exact-optimization) as the template, and follow [task-format.md](https://github.com/hep-cce2/hep-agent-bench-spec/blob/main/task-format.md). The usual pieces:

1. `environment/Dockerfile`: the pinned starting point in the agent's workspace, plus a second, read-only copy of the baseline for the grader (frnn: `/opt/frnn-checkpoint`).
2. `tests/source-manifest.json`: `python -m hepbench.snapshot create --repo <checkout of the starting commit> --upstream <url>`.
3. `tests/expert.patch`: `git diff <start> <expert> -- <source dirs>`, and `solution/solve.sh` that applies it.
4. `tests/test.sh`: verify and export the baseline, build all three versions, run the gate on held-out data, measure, then call `hepbench.write_result`.
5. The canary line in every script, and the `[metadata]` fields in `task.toml`.
6. A section in [README.md](README.md): what the task is, how it is scored, and how a grader obtains the data.

## 3. Check it

- `harbor lint tasks/<name>` passes.
- The oracle scores 1: `harbor run -p tasks/<name> -a oracle`.
- A wrong result scores 0, and an unchanged tree scores 0.
- Held-out data and anything large are not committed.

Then open a PR. If your task needs something the spec doesn't cover (a new kind of gate, a score with several figures of merit, an HPC backend), raise it in [hep-agent-bench-spec](https://github.com/hep-cce2/hep-agent-bench-spec/issues) too.
