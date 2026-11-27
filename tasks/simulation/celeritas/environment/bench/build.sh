#!/bin/bash
# Configure and build celer-optical from a Celeritas source tree, with the exact options the grader uses.
# usage: build.sh SOURCE_DIR BUILD_DIR   -> BUILD_DIR/bin/celer-optical
set -euo pipefail
SRC=$(realpath "$1")
BUILD=$2
source /etc/profile.d/celeritas_spack_env.sh
cmake -S "$SRC" -B "$BUILD" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_ARCHITECTURES="${CUDAARCHS:-86}" \
    -DCELERITAS_USE_CUDA=ON \
    -DCELERITAS_USE_Geant4=ON \
    -DCELERITAS_CORE_GEO=ORANGE \
    -DCELERITAS_REAL_TYPE=double \
    -DCELERITAS_USE_VecGeom=OFF -DCELERITAS_USE_ROOT=OFF -DCELERITAS_USE_HepMC3=OFF \
    -DCELERITAS_USE_MPI=OFF -DCELERITAS_USE_OpenMP=OFF -DCELERITAS_USE_PNG=OFF \
    -DCELERITAS_USE_DD4hep=OFF -DCELERITAS_USE_LArSoft=OFF -DCELERITAS_USE_covfie=OFF \
    -DCELERITAS_USE_Python=OFF -DCELERITAS_USE_Perfetto=OFF \
    -DCELERITAS_BUILD_TESTS=OFF -DCELERITAS_BUILD_DOCS=OFF
cmake --build "$BUILD" --target celer-optical -j "${BUILD_JOBS:-$(nproc)}"
