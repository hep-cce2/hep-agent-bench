# Base image from https://github.com/xju2/agent-env-frnn: build it first on the GPU host with
#   docker build --tag agent-env-frnn:cuda13.0-pytorch2.13 .
FROM agent-env-frnn:cuda13.0-pytorch2.13

# zeus has an RTX 2080 (sm_75) and an RTX A6000 (sm_86).
ENV CUDAARCHS="75;86"

# Seed /workspace/libFRNN from the pinned checkpoint and make the baseline commit at build time.
RUN frnn-entrypoint true

# Development event the agent may use (embedding_data.csv, edge_list.csv); the graded event lives in tests/data.
COPY data/ /workspace/libFRNN/data/
