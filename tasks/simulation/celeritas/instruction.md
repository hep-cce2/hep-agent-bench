The repository in `/workspace/celeritas` is [Celeritas](https://github.com/celeritas-project/celeritas), a GPU-accelerated Monte Carlo particle transport code for high energy physics. Its `celer-optical` application transports optical (scintillation) photons through a detector geometry on the GPU, using Celeritas's own geometry engine, ORANGE, which is built from the GDML description at startup.

The DUNE far-detector physics program relies on simulating very large numbers of optical photons in its liquid-argon TPCs. Your goal is to make `celer-optical` faster on the DUNE "Z-wires" geometry (`/workspace/bench/dune-zwires.gdml`: one 10 kt DUNE module with its field cage, cathodes, APA frames, photon detectors and collection wires) without changing the physics. You may change any part of the Celeritas source tree. Use whatever investigation you see fit: profiling, reading code, experiments.

Development setup in `/workspace/bench`:

- `build.sh SOURCE_DIR BUILD_DIR` configures and builds `celer-optical` with exactly the options the grader uses (CUDA for the GPU in this container, double precision, ORANGE geometry, Geant4 for the GDML and optical material data). `bash /workspace/bench/build.sh /workspace/celeritas /workspace/build` gives `/workspace/build/bin/celer-optical`.
- `dev.inp.json` is a development problem: 16.8 M optical photons (≈9.7 eV, isotropic) from one point inside the liquid argon, with absorption, Rayleigh scattering and boundary processes. Run it with `/workspace/build/bin/celer-optical dev.inp.json` from `/workspace/bench`; the output JSON reports `result.time.setup` and `result.time.total` (transport) in seconds, and `result.counters` (photons generated, steps).
- The environment's packages are set up by `source /etc/profile.d/celeritas_spack_env.sh` (already in `~/.bashrc`).

How your work is graded, after you finish:

- Your final tree in `/workspace/celeritas` is built with the same configuration as `build.sh` (from the grader's own copy of the script, so changes to `/workspace/bench` have no effect). Keep the `celer-optical` command line, its input format and its output JSON format.
- It is run on several held-out problems: the same geometry, physics and number of photons as the development problem, but with different photon source positions and random seeds. For every problem, all photons must be generated and the total number of steps must agree with the original implementation's within 0.2%. Otherwise the score is zero.
- If it passes, the run time (`setup` + `total`) summed over the held-out problems is compared with the original implementation on the same GPU. A larger speedup earns a higher score.
