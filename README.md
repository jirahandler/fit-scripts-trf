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
|-- raw-ntup-config/
|   |-- ntup-run_all_signals.py
|   `-- trf-config-ntup.txt
|-- raw-hist-config/
|   |-- create-asimov.py
|   |-- histo-run_all_signals.py
|   `-- trf-config-hist.txt
`-- nn-score-config/
    |-- run_all_signals.py
    `-- skeleton-trf-config-ml.txt
```

## File Descriptions

| File Path                                  | Description                                                                                   |
|--------------------------------------------|-----------------------------------------------------------------------------------------------|
| .gitignore                                 | Specifies files/directories to ignore (e.g., `output/`).                                      |
| README.md                                  | This overview and instructions file.                                                         |
| raw-ntup-config/ntup-run_all_signals.py    | Driver: generates TRExFitter configs and runs fits directly on NTuples.                      |
| raw-ntup-config/trf-config-ntup.txt        | Skeleton TRExFitter config template for NTuple-based fits.                                    |
| raw-hist-config/create-asimov.py           | Generates per-sample histograms and Asimov datasets from NTuples; **must run first**.        |
| raw-hist-config/histo-run_all_signals.py   | Driver: generates TRExFitter configs and runs fits using histogram inputs.                   |
| raw-hist-config/trf-config-hist.txt        | Skeleton TRExFitter config template for histogram-based fits.                                 |
| nn-score-config/run_all_signals.py         | Driver: generates TRExFitter configs and runs fits using ML discriminant NTuples.            |
| nn-score-config/skeleton-trf-config-ml.txt | Skeleton TRExFitter config template for ML discriminant-based fits.                          |
| flattuple_enhanced.py                      | Makes flattened data structures out of Delphes root files with event selections.             |

## How to Run

### 1. Histogram pipeline (Fake Data Histogram Ntuple Creation generation) **Conda environment only**

```bash
# create & activate minimal env for create-asimov.py
conda create -n trf-hist-env python=3.9 numpy uproot -c conda-forge
conda activate trf-hist-env

# run Asimov histogram generation
cd raw-hist-config
python3 create-asimov.py

# deactivate once done
conda deactivate
```

### 2. Other scripts (NTuple & ML) **CVMFS Apptainer Container**

```bash
# set up TRExFitter from CVMFS
setupATLAS -q
asetup StatAnalysis,0.6.1,here

# Raw NTuple fits
cd raw-ntup-config
python3 ntup-run_all_signals.py

# Histogram-based fits (uses outputs of create-asimov.py)
cd ../raw-hist-config
python3 histo-run_all_signals.py

# ML discriminant fits
cd ../nn-score-config
python3 run_all_signals.py
```
