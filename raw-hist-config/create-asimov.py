import uproot
import numpy as np
import os

# --- Main Configuration ---

# 1. Base path to the original, flattened ntuples
NTUPLE_BASE_PATH = "/home/sgoswami/monobcntuples/local-samples/trf-workdir/SR/flattenedNTuples"

# 2. --- CORRECTED: Variable to be histogrammed ---
VARIABLE_TO_HIST = "met_sig" # Changed from "met_significance" to match your ntuples
HIST_BINS = np.linspace(0, 30, 16) # 15 bins from 0 to 30, as in your original config

# 3. File paths for all samples relative to the base path
SAMPLE_PATHS = {
    "znunu":     "bkg/flat_tuple_znunu_600K.root",
    "ttbar":     "bkg/flat_tuple_ttbar.root",
    "wjets":     "bkg/flat_tuple_wlnu.root",
    "LQ_1p6TeV": "sig/lq/flat_tuple_lq_1p6TeV_merged_600K.root",
    "LQ_2TeV":   "sig/lq/flat_tuple_lq_2TeV_merged_600K.root",
    "LQ_2p4TeV": "sig/lq/flat_tuple_lq_2p4TeV_merged_600K.root",
    "DM_1p0":    "sig/dm/flat_tuple_yy_1p0_qcd.root",
    "DM_1p5":    "sig/dm/flat_tuple_yy_1p5_qcd.root",
    "DM_2p5":    "sig/dm/flat_tuple_yy_2p5_qcd.root",
}

# 4. Fixed Background Yields (from your spreadsheet)
BACKGROUND_YIELDS = {
    "tagged":   {"znunu": 53414.6, "ttbar": 44972.5, "wjets": 18745.3},
    "untagged": {"znunu": 648667.2, "ttbar": 10448.7, "wjets": 498051.1}
}

# 5. Signal Calculation Constants
ZNN_TARGET_YIELD = 702063.8
BKG_XSEC_PB = 1063.2
BKG_EFF = 1.0
LQ_MAGNIFICATION = 1000.0
DM_MAGNIFICATION = 100000.0

# 6. Signal Point Metadata
SIGNAL_METADATA = {
    "LQ_1p6TeV": {"type": "LQ", "xsec_pb": 0.13,    "n_gen_ntuple": 36504, "survived": 502915, "produced": 600000},
    "LQ_2TeV":   {"type": "LQ", "xsec_pb": 0.05,    "n_gen_ntuple": 35282, "survived": 500561, "produced": 600000},
    "LQ_2p4TeV": {"type": "LQ", "xsec_pb": 0.03025, "n_gen_ntuple": 34319, "survived": 499548, "produced": 600000},
    "DM_1p0":    {"type": "DM", "xsec_pb": 0.04,    "n_gen_ntuple": 12807, "survived": 100000, "produced": 100000},
    "DM_1p5":    {"type": "DM", "xsec_pb": 0.001615,"n_gen_ntuple": 26885, "survived": 100000, "produced": 100000},
    "DM_2p5":    {"type": "DM", "xsec_pb": 7.831e-6,"n_gen_ntuple": 52144, "survived": 100000, "produced": 100000},
}

def create_individual_histograms():
    """Creates a separate histogram file for each MC process."""
    print("\n--- Generating individual histograms for all MC samples ---")
    for process_name, relative_path in SAMPLE_PATHS.items():
        input_file = os.path.join(NTUPLE_BASE_PATH, relative_path)
        output_file = f"histo_{process_name}.root"
        if not os.path.exists(input_file):
            print(f"  WARNING: Input file not found for '{process_name}': {input_file}. Skipping.")
            continue

        with uproot.open(input_file) as f_in, uproot.recreate(output_file) as f_out:
            for category, tree_name_in_file in [("tagged", "b_tagged"), ("untagged", "untagged")]:
                hist_name = f"{VARIABLE_TO_HIST}_{category}"
                if tree_name_in_file in f_in:
                    # Check if the variable exists before trying to access it
                    if VARIABLE_TO_HIST not in f_in[tree_name_in_file]:
                        print(f"  ERROR: Variable '{VARIABLE_TO_HIST}' not found in TTree '{tree_name_in_file}' of file {input_file}. Skipping.")
                        continue
                    data = f_in[tree_name_in_file][VARIABLE_TO_HIST].array(library="np")
                    shape_hist, _ = np.histogram(data, bins=HIST_BINS)
                    f_out[hist_name] = shape_hist, HIST_BINS
                    print(f"  -> Created '{hist_name}' in '{output_file}'")

def create_asimov_data():
    """Generates inflated Asimov data histograms for every signal point."""
    print("\n--- Generating Asimov data for all signal points ---")
    for point_name, point_meta in SIGNAL_METADATA.items():
        print(f"--- Processing Asimov for: {point_name} ---")
        output_hist_file = f"asimov_histograms_{point_name}.root"
        if os.path.exists(output_hist_file): os.remove(output_hist_file)

        # Calculate the target signal yield
        sig_eff = point_meta["survived"] / point_meta["produced"]
        xsec_ratio = point_meta["xsec_pb"] / BKG_XSEC_PB
        eff_ratio = sig_eff / BKG_EFF
        target_signal_yield = ZNN_TARGET_YIELD * xsec_ratio * eff_ratio
        magnification = LQ_MAGNIFICATION if point_meta['type'] == 'LQ' else DM_MAGNIFICATION
        final_signal_yield = target_signal_yield * magnification

        with uproot.recreate(output_hist_file) as f_out:
            for category, tree_name_in_file in [("tagged", "b_tagged"), ("untagged", "untagged")]:
                asimov_hist = np.zeros(len(HIST_BINS) - 1)

                # Process Backgrounds
                for process, target_yield in BACKGROUND_YIELDS[category].items():
                    input_file = os.path.join(NTUPLE_BASE_PATH, SAMPLE_PATHS[process])
                    with uproot.open(input_file) as f_in:
                        if tree_name_in_file in f_in:
                            data = f_in[tree_name_in_file][VARIABLE_TO_HIST].array(library="np")
                            shape_hist, _ = np.histogram(data, bins=HIST_BINS)
                            if np.sum(shape_hist) > 0:
                                asimov_hist += (shape_hist / np.sum(shape_hist)) * target_yield

                # Process Signal
                signal_input_file = os.path.join(NTUPLE_BASE_PATH, SAMPLE_PATHS[point_name])
                with uproot.open(signal_input_file) as f_in:
                    if tree_name_in_file in f_in:
                        signal_data = f_in[tree_name_in_file][VARIABLE_TO_HIST].array(library="np")
                        signal_shape_hist, _ = np.histogram(signal_data, bins=HIST_BINS)
                        if np.sum(signal_shape_hist) > 0:
                            tagged_tree = f_in.get("b_tagged")
                            untagged_tree = f_in.get("untagged")
                            total_raw_signal_events = (tagged_tree.num_entries if tagged_tree else 0) + \
                                                      (untagged_tree.num_entries if untagged_tree else 0)

                            raw_events_in_category = len(signal_data)
                            yield_fraction = raw_events_in_category / total_raw_signal_events if total_raw_signal_events > 0 else 0
                            yield_for_category = final_signal_yield * yield_fraction
                            asimov_hist += (signal_shape_hist / np.sum(signal_shape_hist)) * yield_for_category

                # Write final Asimov histogram
                hist_name = f"{VARIABLE_TO_HIST}_{category}"
                f_out[hist_name] = asimov_hist, HIST_BINS
                print(f"  -> Wrote final Asimov histogram '{hist_name}' to '{output_hist_file}'")

def main():
    """Main function to run all processing steps."""
    create_individual_histograms()
    create_asimov_data()
    print("\n--- All histograms created successfully. ---")

if __name__ == "__main__":
    main()
