FROM ghcr.io/astral-sh/uv:0.9.5-python3.13-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# IRIS-HEP skills used by the upstream benchmark (iris-hep@iris-hep-tools, BSD-3-Clause), pinned.
RUN git clone https://github.com/iris-hep/marketplace.git /opt/iris-hep-marketplace \
    && git -C /opt/iris-hep-marketplace checkout --quiet 288a2fd6859bb69975d9f8ea86da135a0857c892

WORKDIR /workspace
