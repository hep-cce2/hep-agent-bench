# Celeritas CI image (CUDA 12.6, Geant4 11.0, cmake, ninja), as used by Celeritas's own CI.
FROM docker.io/celeritas/ci-rocky-cuda12:2024-12-29
# The image's entrypoint and shell wrapper scripts are not shipped in it.
ENTRYPOINT []
SHELL ["/bin/bash", "-c"]
CMD ["bash"]

# Starting point: the develop commit just before the expert change (celeritas-project/celeritas#2255).
ARG CELERITAS_COMMIT=e906a7a8bfc120dd6a64afc2d142a054e82ffd2f
# zeus: RTX A6000 (sm_86).
ENV CUDAARCHS=86

# The agent gets the source as a single fresh commit, without upstream history, so `git diff` shows its changes.
# /opt/celeritas-baseline is a pristine copy that the grader verifies and builds the baseline from.
RUN source /etc/profile.d/celeritas_spack_env.sh \
 && git clone --quiet --filter=blob:none --no-checkout https://github.com/celeritas-project/celeritas.git /tmp/celeritas \
 && git -C /tmp/celeritas checkout --quiet "$CELERITAS_COMMIT" \
 && rm -rf /tmp/celeritas/.git \
 && cp -a /tmp/celeritas /opt/celeritas-baseline \
 && mkdir -p /workspace && mv /tmp/celeritas /workspace/celeritas \
 && cd /workspace/celeritas \
 && git init --quiet && git add -A \
 && git -c user.name=bench -c user.email=bench@localhost commit --quiet -m "baseline: celeritas $CELERITAS_COMMIT"

# The build fetches CLI11 at configure time; download it now because the container has no network.
# build.sh points FetchContent at this copy (FETCHCONTENT_SOURCE_DIR_CLI11).
RUN mkdir -p /opt/deps/cli11 \
 && curl -fsSL https://github.com/CLIUtils/CLI11/archive/refs/tags/v2.5.0.tar.gz -o /tmp/cli11.tar.gz \
 && echo "17e02b4cddc2fa348e5dbdbb582c59a3486fa2b2433e70a0c3bacb871334fd55  /tmp/cli11.tar.gz" | sha256sum -c - \
 && tar -xzf /tmp/cli11.tar.gz --strip-components=1 -C /opt/deps/cli11 && rm /tmp/cli11.tar.gz

# Development problem, build script and geometry the agent may use.
COPY bench/ /workspace/bench/
RUN echo 'source /etc/profile.d/celeritas_spack_env.sh' >> /root/.bashrc
WORKDIR /workspace
