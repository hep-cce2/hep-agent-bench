FROM python:3.13.9-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Analysis stack the agent's script (and the grader) may use; pinned.
RUN pip install --no-cache-dir uproot==5.7.7 awkward==2.15.0 numpy==2.5.4 hist==2.12.1 matplotlib==3.11.2 mplhep==1.3.3

# Grader helpers, installed at build time so grading needs no network; kept off the default path.
RUN pip install --no-cache-dir --no-deps --target /opt/hepbench \
    git+https://github.com/hep-cce2/hep-agent-bench-tools@21bdd68b3748721cd356f9169f23bfb4038248f2  # v0.1.0

# IRIS-HEP skills used by the upstream benchmark (iris-hep@iris-hep-tools, BSD-3-Clause), pinned.
RUN git clone https://github.com/iris-hep/marketplace.git /opt/iris-hep-marketplace \
    && git -C /opt/iris-hep-marketplace checkout --quiet 288a2fd6859bb69975d9f8ea86da135a0857c892

# Development file (CERN Open Data record 80014, CC0); the graded file lives in tests/data.
COPY data/ /workspace/data/
WORKDIR /workspace
