## NTuple Directory Organization

```
<workdir>/SR/flattenedNTuples/
|-- bkg/
|   |-- flat_tuple_ttbar.root
|   |-- flat_tuple_wlnu0.root
|   |-- flat_tuple_wlnu1.root
|   `-- flat_tuple_znunu_600K.root
`-- sig/
    |-- dm/
    |   |-- flat_tuple_yy_1p0_qcd.root
    |   |-- flat_tuple_yy_1p5_qcd.root
    |   `-- flat_tuple_yy_2p5_qcd.root
    `-- lq/
        |-- flat_tuple_lq_1p6TeV_merged_600K.root
        |-- flat_tuple_lq_2TeV_merged_600K.root
        `-- flat_tuple_lq_2p4TeV_merged_600K.root
```

## Repository File Structure

```
fit-scripts-trf/
|-- .gitignore
|-- README.md
|-- gitcommit.src
|-- raw-ntup-config/
|   |-- ntup-run_all_signals.py
|   `-- trf-config-ntup.txt
|-- raw-hist-config/
|   |-- histo-run_all_signals.py
|   |-- prepare-histograms.py
|   `-- trf-config-hist.txt
|-- nn-score-config/
|   |-- run_all_signals.py
|   |-- evaluate_trg_ncreatentuples.py
|   `-- skeleton-trf-config-ml.txt
`-- useful-scripts/
    |-- count_tagged_charmjets.py
    |-- get_flattuple_enhanced.py
    |-- getevents.py
    |-- plot-inp-vars.py
    `-- plot-tagging-profile.py
```

## File Descriptions

| File Path                                         | Description                                                                                      |
|--------------------------------------------------|--------------------------------------------------------------------------------------------------|
| .gitignore                                        | Specifies files/directories to ignore (e.g., `output/`).                                         |
| README.md                                         | This overview and instruction file.                                                              |
| gitcommit.src                                     | Git commit message or helper text stub.                                                          |
| raw-ntup-config/ntup-run_all_signals.py          | Driver: generates TRExFitter configs and runs fits directly on NTuples.                         |
| raw-ntup-config/trf-config-ntup.txt              | Skeleton TRExFitter config template for NTuple-based fits.                                       |
| raw-hist-config/prepare-histograms.py            | Prepares histograms from NTuples (intermediate step before Asimov fits).                         |
| raw-hist-config/histo-run_all_signals.py         | Driver: generates TRExFitter configs and runs fits using histogram inputs.                      |
| raw-hist-config/trf-config-hist.txt              | Skeleton TRExFitter config template for histogram-based fits.                                    |
| nn-score-config/run_all_signals.py               | Driver: generates TRExFitter configs and runs fits using ML discriminant NTuples.               |
| nn-score-config/evaluate_trg_ncreatentuples.py   | Performs evaluation or generation of ML input NTuples (e.g., scores for TRExFitter). Must be run first before running fitting on ML scores. |
| nn-score-config/skeleton-trf-config-ml.txt       | Skeleton TRExFitter config template for ML discriminant-based fits.                             |
| useful-scripts/count_tagged_charmjets.py         | Utility script to count charm-tagged jets for diagnostics.                                       |
| useful-scripts/get_flattuple_enhanced.py         | Wrapper/driver to produce enhanced flattened tuples from Delphes outputs.                       |
| useful-scripts/getevents.py                      | Extracts or filters events from NTuples.                                                         |
| useful-scripts/plot-inp-vars.py                  | Plots input variables for inspection.                                                            |
| useful-scripts/plot-tagging-profile.py           | Diagnostic plot for jet tagging behavior (e.g., b/c-tagging profile).                            |

## How to Run

### 1. Histogram Pipeline (Fake Data Histogram NTuple Creation) ? **Conda environment only**

```bash
# Create & activate minimal env for prepare-histograms.py
conda create -n trf-hist-env python=3.9 numpy uproot -c conda-forge
conda activate trf-hist-env

# Run histogram preparation (replaces create-asimov.py)
cd raw-hist-config
python3 prepare-histograms.py

# Deactivate once done
conda deactivate
```

### 2. All Other Scripts (NTuple & ML) ? **CVMFS Apptainer container**

```bash
# Set up TRExFitter from CVMFS
setupATLAS -q
asetup StatAnalysis,0.6.1,here
```

Then run:

```bash
# Raw NTuple fits
cd raw-ntup-config
python3 ntup-run_all_signals.py
```

```bash
# Histogram-based fits (after prepare-histograms.py)
cd ../raw-hist-config
python3 histo-run_all_signals.py
```

```bash
# ML discriminant fits
cd ../nn-score-config
python3 run_all_signals.py
```

---

Let me know if you'd like me to insert badges, add usage examples, or restructure for GitHub Pages formatting.
