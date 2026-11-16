There are 21 analysis questions below. For each question `<n>`, write a stand-alone Python file `/workspace/q<n>/script.py` that does what the question asks.

Every script takes the input PHYSLITE file(s) as command-line arguments: one file, or two for q15. Run it as `python3 script.py FILE [FILE2]`. It must save its plot(s) as PNG files in the current directory (any names, e.g. `plot_<n>.png`; q6 makes two); put all of its Python code in that single file. You must run each script on its development file(s) and produce its plot(s) before declaring success.

For each plot, compute the unweighted mean from the raw values used to fill the histogram, and the unweighted average number of entries per event (entries divided by the number of events after all filtering, unless the question says otherwise). Immediately print exactly one line per plot, in plot order, in this format:
METRIC: avg_entries_per_event=<N> mean=<M>
Do not use histogram APIs to compute these metrics, and do not apply weights.

## Environment

- The files are ATLAS Open Data (DAOD_PHYSLITE, Run 2 MC, 13 TeV); the event tree is `CollectionTree`. Python 3.13 with uproot, awkward, numpy, hist, matplotlib and mplhep is installed. Scripts may use only what is installed: there is no network access at grading time.
- Development files are in `/workspace/data/` (file names start `DAOD_PHYSLITE.` and end `.pool.root.1`):

  | Dataset | Development file |
  |---|---|
  | 364702 Pythia8 dijet JZ2 | `38191877._000140` |
  | 364703 Pythia8 dijet JZ3 | `38191774._000013` |
  | 410471 Powheg+Pythia8 ttbar all-hadronic | `37861619._000001` |
  | 700325 Sherpa Z→μμ | `37621409._000001` |
  | 700588 Sherpa lllvjj | `37110891._000001` |
  | 301333 Pythia8 Z′(3 TeV)→tt | `38191516._000001` |

- The IRIS-HEP analysis skills (awkward, hist, vector) are available to you.

## Conventions (all questions)

- Use GeV for energies, momenta and masses (PHYSLITE stores MeV).
- **Jets** are `AnalysisJets`, **electrons** are `AnalysisElectrons`, **muons** are `AnalysisMuons`, and **light leptons** are electrons and muons together. Apply no selection beyond what a question asks for. Use the jets' stored mass, 0.000511 GeV for electrons and 0.10566 GeV for muons.
- **ETmiss** is the first term of `MET_Core_AnalysisMET`. Its vector is (`mpx`, `mpy`) of that term, and ETmiss is the vector's magnitude.
- The **b-tagging discriminant** of a jet is DL1dv01: ln(p_b / (0.018·p_c + 0.982·p_u)), using `BTagging_AntiKt4EMPFlow` `DL1dv01_pb/pc/pu`. That container is aligned one-to-one with the jets.
- Do all arithmetic in float64: PHYSLITE stores most values as float32, so cast them on reading.
- **ΔR** = sqrt(Δη² + Δφ²), with Δφ wrapped into [−π, π).
- **"Events"** means all events in the input file(s), unless the question applies a selection.

## Questions

Each question gives its dataset; the script runs on a file of that dataset.

- **q1** (364702): Plot the ETmiss of all events.
- **q2** (364702): Plot the pT of all jets.
- **q3** (364702): Plot the pT of jets with |η| < 1.
- **q4** (364702): Plot the ETmiss of events that have at least two jets with pT > 40 GeV.
- **q5** (700325): Plot the ETmiss of events that have an opposite-charge muon pair with an invariant mass between 60 and 120 GeV. For avg_entries_per_event, divide by the number of all events in the file.
- **q6** (410471): For events with at least three jets, plot two things, in this order. Plot 1: the pT of the trijet four-momentum whose invariant mass is closest to 172.5 GeV in each event. Plot 2: the maximum b-tagging discriminant value among the jets in this trijet.
- **q7** (410471): Plot the scalar sum, in each event, of the pT of jets with pT > 30 GeV that are not within ΔR < 0.4 of any light lepton with pT > 10 GeV. Every event contributes one entry; an event with no such jets contributes 0.
- **q8** (700588): Take events with at least three light leptons and at least one same-flavour opposite-charge (SFOS) light-lepton pair. In each, find the SFOS pair whose invariant mass is closest to 91.2 GeV. Plot the transverse mass, mT = sqrt(2 pT ETmiss (1 − cos Δφ)), of the ETmiss vector and the highest-pT light lepton not in this pair.
- **q9** (364702): Plot the number of jets per event.
- **q10** (410471): Plot the pT of electrons with pT > 25 GeV in the first 20000 events of the file.
- **q11** (364702): Plot the leading jet pT (the highest-pT jet in each event), for events with at least one jet.
- **q12** (700325): In events with at least two muons, plot the invariant mass of every unique same-charge muon pair. For avg_entries_per_event, divide the number of pairs by the number of events with at least two muons, including events that contain no same-charge pair.
- **q13** (700325): Plot the ETmiss of events with no jets.
- **q14** (364702): Plot ΔR between the two leading (highest-pT) jets, for events with at least two jets.
- **q15** (364702 and 364703): The script gets two files: the JZ2 file first, then the JZ3 file. Make a stacked histogram of the pT of the highest-pT jet in each event, for leading jets with 100 ≤ pT ≤ 200 GeV, from both files. Print one METRIC line for the whole stacked plot. For avg_entries_per_event, divide the number of histogram entries by the total number of events in both files, including events with no jets or with a leading jet outside the range.
- **q16** (301333): Plot the reconstructed top-quark pair mass around 3 TeV in events with exactly one charged lepton. Baseline object cuts: jets pT > 30 GeV, electrons pT > 25 GeV, muons pT > 25 GeV. Require exactly one light lepton and at least four jets. Reconstruct the pair mass as the invariant mass of three things: the lepton, a neutrino (the ETmiss vector with pz = 0 and zero mass), and the four highest-pT jets. Do not add extra shaping cuts.
- **q17** (410471): Plot the b-tagging discriminant value for all jets.
- **q18** (410471): Plot the b-tagging discriminant value for all jets with pT > 45 GeV and |η| < 2.4, in events that have at least two such jets.
- **q19** (410471): Count how many events fired each single-jet trigger (the HLT chains named `HLT_j<threshold>`, e.g. `HLT_j460`). Use the HLT physics-pass decision of each chain. Do three things:
  1. Write a markdown table to `triggers.md` and print it to stdout. Put the total number of events at the top, then one row per trigger with its name and count.
  2. Make a plot where the x-axis is the trigger name and the y-axis is the number of times it fired.
  3. Print a line `HLT_j460=<n>`, where `<n>` is the number of events in which `HLT_j460` fired. This question prints no METRIC line.
- **q20** (700325): Plot the number of precision layers (`numberOfPrecisionLayers`) for every muon. Include muons with zero precision layers, and do not apply object or event cuts. Keep events with no muons in the event count used for avg_entries_per_event.
- **q21** (410471): Plot the number of valid ghost-associated tracks (`GhostTrack`) for every jet. Count only non-null track links, since thinning can invalidate links; a null link has `m_persKey == 0`. Include jets with zero valid tracks, and do not apply object or event cuts. Keep events with no jets in the event count used for avg_entries_per_event.

## How your work is graded, after you finish

- Each `/workspace/q<n>/script.py` is copied to an empty directory and run as `python3 script.py <file(s)>`. The input is a held-out file of the same dataset, different from the development file (for 700588 and 301333 the only public file, the development file, is used). Each run has a time limit of 10 minutes.
- A question passes when the script exits successfully and writes at least one PNG file per plot (two for q6). Its METRIC lines must match the grader's own computation on that file: same number of lines, and every value within a relative 1e-5. For q19, `triggers.md` must exist and the `HLT_j460=<n>` count must match exactly.
- The reward is the fraction of the 21 questions that pass.
