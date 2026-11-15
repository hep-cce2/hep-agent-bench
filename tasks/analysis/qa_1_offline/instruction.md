Please write a stand-alone Python file that does the following:

Plot the ETmiss of all events in the ATLAS PHYSLITE file given as the script's only command-line
argument. For ETmiss, use the magnitude of the first term of the `MET_Core_AnalysisMET` container
(built from its `mpx` and `mpy`), in GeV.

Save plots as plot_<n>.png in the current directory. Put all Python code in a single script.py file.

For each plot, compute the unweighted mean from the raw values used to fill the histogram and
the unweighted average number of entries per event (entries divided by the number of events
after all filtering). Immediately print exactly one line per plot in this format:
METRIC: avg_entries_per_event=<N> mean=<M>
Do not use histogram APIs to compute these metrics, and do not apply weights.

Work in `/workspace`: the file must be `/workspace/script.py`. A development file is in
`/workspace/data/DAOD_PHYSLITE.38191877._000140.pool.root.1` (ATLAS Open Data, Pythia8 dijet JZ2,
DSID 364702, 120,000 events); run your script on it and produce a plot before declaring success.
Python 3.13 with uproot, awkward, numpy, hist, matplotlib and mplhep is installed; the script must use only
what is installed in the image (no network access, no `uv` auto-install). The IRIS-HEP analysis skills
(awkward, hist, vector) are available to you.

How your work is graded, after you finish:

- `/workspace/script.py` is copied to an empty directory and run there as
  `python3 script.py <held-out PHYSLITE file>`, on a different file of the same dataset.
  It must finish within 15 minutes, write `plot_1.png`, and print exactly one `METRIC:` line.
- Both numbers on that line must agree with the grader's own computation on the held-out file
  within 1e-4 (relative). Anything else scores zero.
