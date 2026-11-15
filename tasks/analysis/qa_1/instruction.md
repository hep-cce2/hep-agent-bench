Please write a stand-alone Python file that uv can run and auto-install
dependencies for. It must do the following:

Plot the ETmiss of all events in the rucio dataset user.zmarshal:user.zmarshal.364702_OpenData_v1_p6026_2024-04-23.

Save plots as plot_<n>.png. Put all Python code in a single script.py file.
You must successfully run it on one input file from the dataset specified in the question above,
and produce a plot before declaring success.

For each plot, compute the unweighted mean from the raw values used to fill the histogram and
the unweighted average number of entries per event (entries divided by the number of events
after all filtering). Immediately print exactly one line per plot in this format:
METRIC: avg_entries_per_event=<N> mean=<M>
Do not use histogram APIs to compute these metrics, and do not apply weights.

Work in `/workspace`: the file must be `/workspace/script.py`. A ServiceX client configuration is
already in `~/servicex.yaml`; do not copy it into `/workspace` or print its token. `uv` is installed.
The IRIS-HEP analysis skills (ServiceX, func_adl, awkward, hist, vector) are available to you.

How your work is graded, after you finish:

- `/workspace/script.py` is copied to an empty directory and run there with `uv run --script script.py`.
  It must finish within 30 minutes, write `plot_1.png`, and print exactly one `METRIC:` line.
- Both numbers on that line are compared with a reference: each must agree within 2% (relative).
  Anything else scores zero.
