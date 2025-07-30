import uproot
import numpy as np
import os

# --- Main Configuration ---

# 1. Base path to the original, c-tagged ntuples
NTUPLE_BASE_PATH = "/home/sgoswami/monobcntuples/local-samples/trf-workdir/SR/flattenedNTuples"

# 2. Variable to be histogrammed
VARIABLE_TO_HIST = "met_sig"
HIST_BINS = np.linspace(0, 30, 16) # 15 bins from 0 to 30

# 3. File paths for all samples relative to the base path
SAMPLE_PATHS = {
    "znunu":     "bkg/flat_tuple_znunu_600K.root",
    "ttbar":     "bkg/flat_tuple_ttbar.root",
    "wjets":     "bkg/flat_tuple_wlnu.root", # This script assumes wlnu0 and wlnu1 are combined into this file.
    "LQ_1p6TeV": "sig/lq/flat_tuple_lq_1p6TeV_merged_600K.root",
    "LQ_2TeV":   "sig/lq/flat_tuple_lq_2TeV_merged_600K.root",
    "LQ_2p4TeV": "sig/lq/flat_tuple_lq_2p4TeV_merged_600K.root",
    "DM_1p0TeV": "sig/dm/flat_tuple_yy_1p0TeV_qcd.root",
    "DM_1p5TeV": "sig/dm/flat_tuple_yy_1p5TeV_qcd.root",
    "DM_2p5TeV": "sig/dm/flat_tuple_yy_2p5TeV_qcd.root",
}

# 4. Background Normalization Factors (scales raw c-tag yields to final expected yields)
BACKGROUND_NORM_FACTORS = {
    "znunu": 101.736,    # (702081.8 / 6901.0)
    "wjets": 19876.78,   # (516796.4 / 26.0)
    "ttbar": 499.29,     # (55421.2 / 111.0)
}

# 5. Raw Background Yields from c-tagging ntuples
BACKGROUND_YIELDS = {
    "tagged":   {"znunu": 121.0, "ttbar": 15.0, "wjets": 1.0},
    "untagged": {"znunu": 6780.0, "ttbar": 96.0, "wjets": 25.0}
}

# 6. Signal Calculation Constants
ZNN_TARGET_YIELD = 702063.8
BKG_XSEC_PB = 1063.2
BKG_EFF = 1.0
LQ_MAGNIFICATION = 1000.0
# CORRECTED: DM_MAGNIFICATION is now a dictionary mapping signal point to its factor
DM_MAGNIFICATION = {
    "DM_1p0TeV": 1000.0,
    "DM_1p5TeV": 10000.0,
    "DM_2p5TeV": 100000.0,
}

# 7. Signal Point Metadata
SIGNAL_METADATA = {
    "LQ_1p6TeV": {"type": "LQ", "xsec_pb": 0.13,    "n_gen_ntuple": 36504, "survived": 502915, "produced": 600000},
    "LQ_2TeV":   {"type": "LQ", "xsec_pb": 0.05,    "n_gen_ntuple": 35282, "survived": 500561, "produced": 600000},
    "LQ_2p4TeV": {"type": "LQ", "xsec_pb": 0.03025, "n_gen_ntuple": 34319, "survived": 499548, "produced": 600000},
    "DM_1p0TeV": {"type": "DM", "xsec_pb": 0.04,    "n_gen_ntuple": 12807, "survived": 100000, "produced": 100000},
    "DM_1p5TeV": {"type": "DM", "xsec_pb": 0.001615,"n_gen_ntuple": 26885, "survived": 100000, "produced": 100000},
    "DM_2p5TeV": {"type": "DM", "xsec_pb": 7.831e-6,"n_gen_ntuple": 52144, "survived": 100000, "produced": 100000},
}

def create_individual_histograms():
    """Stage 1: Creates a separate histogram file for each MC process with raw event counts."""
    print("\n--- STAGE 1: Generating individual histograms for all MC samples ---")
    for process_name, relative_path in SAMPLE_PATHS.items():
        input_file = os.path.join(NTUPLE_BASE_PATH, relative_path)
        output_file = f"histo_{process_name}.root"
        if not os.path.exists(input_file):
            print(f"  WARNING: Input file not found for '{process_name}': {input_file}. Skipping.")
            continue

        with uproot.open(input_file) as f_in, uproot.recreate(output_file) as f_out:
            for category, tree_name_in_file in [("c_tagged", "c_tagged"), ("untagged", "untagged")]:
                hist_name = f"{VARIABLE_TO_HIST}_{category}"
                if tree_name_in_file in f_in and VARIABLE_TO_HIST in f_in[tree_name_in_file]:
                    data = f_in[tree_name_in_file][VARIABLE_TO_HIST].array(library="np")
                    shape_hist, _ = np.histogram(data, bins=HIST_BINS)

                    # Save the raw, unscaled histogram
                    f_out[hist_name] = (shape_hist, HIST_BINS)
                    print(f"  -> Created '{hist_name}' in '{output_file}' (raw counts)")

def create_asimov_data():
    """Stage 2: Generates inflated Asimov data histograms for every signal point."""
    print("\n--- STAGE 2: Generating Asimov data for all signal points ---")
    for point_name, point_meta in SIGNAL_METADATA.items():
        point_name_tagged = f"{point_name}_ctagged"
        print(f"--- Processing Asimov for: {point_name_tagged} ---")
        output_hist_file = f"asimov_histograms_{point_name_tagged}.root"
        if os.path.exists(output_hist_file):
            os.remove(output_hist_file)

        # Calculate the total target signal yield
        sig_eff = point_meta["survived"] / point_meta["produced"]
        xsec_ratio = point_meta["xsec_pb"] / BKG_XSEC_PB
        eff_ratio = sig_eff / BKG_EFF
        target_signal_yield = ZNN_TARGET_YIELD * xsec_ratio * eff_ratio

        # CORRECTED: Look up the correct magnification factor based on signal type and point name
        if point_meta['type'] == 'LQ':
            magnification = LQ_MAGNIFICATION
        else: # It's a DM point
            magnification = DM_MAGNIFICATION.get(point_name, 1.0) # Default to 1.0 if not found

        final_signal_yield = target_signal_yield * magnification

        # Get the raw event counts for tagged/untagged split from the original ntuple
        raw_counts = {}
        total_raw_signal_events = 0
        signal_ntuple_path = os.path.join(NTUPLE_BASE_PATH, SAMPLE_PATHS[point_name])
        with uproot.open(signal_ntuple_path) as f_sig_in:
            for cat, tree_name in [("c_tagged", "c_tagged"), ("untagged", "untagged")]:
                tree = f_sig_in.get(tree_name)
                raw_counts[cat] = tree.num_entries if tree else 0
                total_raw_signal_events += raw_counts[cat]

        with uproot.recreate(output_hist_file) as f_out:
            for category, tree_name_in_file in [("c_tagged", "c_tagged"), ("untagged", "untagged")]:
                hist_name = f"{VARIABLE_TO_HIST}_{category}"
                asimov_hist = np.zeros(len(HIST_BINS) - 1, dtype=np.float64)

                bkg_yields_category = "tagged" if category == "c_tagged" else "untagged"

                # Process Backgrounds by reading their source ntuples
                for process, raw_yield in BACKGROUND_YIELDS[bkg_yields_category].items():
                    norm_factor = BACKGROUND_NORM_FACTORS.get(process, 1.0)
                    scaled_target_yield = raw_yield * norm_factor

                    ntuple_path = os.path.join(NTUPLE_BASE_PATH, SAMPLE_PATHS[process])
                    if not os.path.exists(ntuple_path): continue
                    with uproot.open(ntuple_path) as f_bkg_in:
                        tree = f_bkg_in.get(tree_name_in_file)
                        if tree and VARIABLE_TO_HIST in tree:
                            data = tree[VARIABLE_TO_HIST].array(library="np")
                            shape_hist, _ = np.histogram(data, bins=HIST_BINS)
                            if np.sum(shape_hist) > 0:
                                asimov_hist += (shape_hist / np.sum(shape_hist)) * scaled_target_yield

                # Process Signal by reading its source ntuple
                with uproot.open(signal_ntuple_path) as f_sig_in:
                    tree = f_sig_in.get(tree_name_in_file)
                    if tree and VARIABLE_TO_HIST in tree:
                        signal_data = tree[VARIABLE_TO_HIST].array(library="np")
                        signal_shape_hist, _ = np.histogram(signal_data, bins=HIST_BINS)
                        if np.sum(signal_shape_hist) > 0:
                            yield_fraction = raw_counts[category] / total_raw_signal_events if total_raw_signal_events > 0 else 0
                            yield_for_category = final_signal_yield * yield_fraction
                            asimov_hist += (signal_shape_hist / np.sum(signal_shape_hist)) * yield_for_category

                # Write final Asimov histogram
                if np.sum(asimov_hist) > 0:
                    f_out[hist_name] = asimov_hist, HIST_BINS
                    print(f"  -> Wrote final Asimov histogram '{hist_name}' to '{output_hist_file}'")
                else:
                    print(f"  WARNING: Asimov histogram for '{hist_name}' is empty. Not writing.")

def main():
    """Main function to run all processing steps."""
    create_individual_histograms()
    create_asimov_data()
    print("\n--- All histograms created successfully. ---")

if __name__ == "__main__":
    main()
