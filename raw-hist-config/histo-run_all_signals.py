import subprocess
import os

# --- Main Configuration ---
SKELETON_CONFIG_PATH = "trf-config-hist.txt"

# --- Calculation Constants ---
ZNN_TARGET_YIELD = 702063.8
BKG_XSEC_PB = 1063.2
BKG_EFF = 1.0
LQ_MAGNIFICATION = 1000.0
DM_MAGNIFICATION = 100000.0

# --- Signal Point Metadata ---
SIGNAL_POINTS = [
    {"name": "LQ_1p6TeV", "type": "LQ", "mass": "1.6 TeV", "xsec_pb": 0.13,    "n_gen_ntuple": 36504, "survived": 502915, "produced": 600000},
    {"name": "LQ_2TeV",   "type": "LQ", "mass": "2 TeV",   "xsec_pb": 0.05,    "n_gen_ntuple": 35282, "survived": 500561, "produced": 600000},
    {"name": "LQ_2p4TeV", "type": "LQ", "mass": "2.4 TeV", "xsec_pb": 0.03025, "n_gen_ntuple": 34319, "survived": 499548, "produced": 600000},
    {"name": "DM_1p0",    "type": "DM", "mass": "1.0 TeV", "xsec_pb": 0.04,    "n_gen_ntuple": 12807, "survived": 100000, "produced": 100000},
    {"name": "DM_1p5",    "type": "DM", "mass": "1.5 TeV", "xsec_pb": 0.001615,"n_gen_ntuple": 26885, "survived": 100000, "produced": 100000},
    {"name": "DM_2p5",    "type": "DM", "mass": "2.5 TeV", "xsec_pb": 7.831e-6,"n_gen_ntuple": 52144, "survived": 100000, "produced": 100000},
]

def main():
    """
    Loops through all signal points, calculates the signal scale factor,
    generates a config, and runs TrexFitter.
    """
    print("--- Starting Standalone TrexFitter Run for All Signal Points ---")

    try:
        with open(SKELETON_CONFIG_PATH, "r") as f:
            base_config = f.read()
    except FileNotFoundError:
        print(f"FATAL: Skeleton config not found at: {SKELETON_CONFIG_PATH}")
        return

    for point in SIGNAL_POINTS:
        print(f"\n{'='*50}\nProcessing: {point['name']}\n{'='*50}")

        # --- Calculate the Signal Scale Factor ---
        sig_eff = point["survived"] / point["produced"]
        xsec_ratio = point["xsec_pb"] / BKG_XSEC_PB
        eff_ratio = sig_eff / BKG_EFF
        target_signal_yield = ZNN_TARGET_YIELD * xsec_ratio * eff_ratio
        base_sf = target_signal_yield / point["n_gen_ntuple"]
        magnification = LQ_MAGNIFICATION if point['type'] == 'LQ' else DM_MAGNIFICATION
        final_sf = base_sf * magnification
        print(f"  Calculated signal scale factor: {final_sf:.8f}")

        # --- Define placeholders for the skeleton config ---
        asimov_hist_file = f"asimov_histograms_{point['name']}"
        histo_signal_file = f"histo_{point['name']}"

        replacements = {
            "JOB_NAME":             point["name"],
            "OUTPUT_DIRECTORY":     f"./{point['name']}_fit",
            "SIGNAL_LABEL":         f"{point['type']} {point['mass']}",
            "ASIMOV_HIST_FILE":     asimov_hist_file,
            "HISTO_SIGNAL_FILE":    histo_signal_file,
            "SIGNAL_SCALE_FACTOR":  f"{final_sf:.8f}",
        }

        # --- Generate and Run TrexFitter Config ---
        temp_config = base_config
        for placeholder, value in replacements.items():
            temp_config = temp_config.replace(placeholder, value)

        config_filename = f"config_{point['name']}.txt"
        with open(config_filename, "w") as f:
            f.write(temp_config)
        print(f"Generated config: {config_filename}")

        command = ["trex-fitter", "hwpdf", config_filename]
        print(f"Executing: {' '.join(command)}")

        try:
            subprocess.run(command, check=True, text=True)
            print(f"--- Successfully completed {point['name']} ---")
        except subprocess.CalledProcessError as e:
            print(f"--- ERROR: TRexFitter failed for {point['name']} ---")
            break
        except FileNotFoundError:
            print("\nERROR: 'trex-fitter' command not found. Is it in your PATH?")
            break

if __name__ == "__main__":
    main()
