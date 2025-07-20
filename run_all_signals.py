import subprocess
import re

#Config
ZNN_TARGET_YIELD = 702063.8
BKG_XSEC_PB = 1063.2
BKG_EFF = 1.0

# Factors for LQ and DM
LQ_MAGNIFICATION = 1000.0
DM_MAGNIFICATION = 100000.0

# Define the 6 signal points
signal_points = [
    # Leptoquarks
    {"name": "LQ_1p6TeV", "type": "LQ", "mass": "1.6 TeV", "xsec_pb": 0.13,    "n_gen_ntuple": 36504, "survived": 502915, "produced": 600000, "ntuple_file": "./sig/lq/flat_tuple_lq_1p6TeV_merged_600K"},
    {"name": "LQ_2TeV",   "type": "LQ", "mass": "2 TeV",   "xsec_pb": 0.05,    "n_gen_ntuple": 35282, "survived": 500561, "produced": 600000, "ntuple_file": "./sig/lq/flat_tuple_lq_2TeV_merged_600K"},
    {"name": "LQ_2p4TeV", "type": "LQ", "mass": "2.4 TeV", "xsec_pb": 0.03025, "n_gen_ntuple": 34319, "survived": 499548, "produced": 600000, "ntuple_file": "./sig/lq/flat_tuple_lq_2p4TeV_merged_600K"},
    # Dark Matter (yy_qcd)
    {"name": "DM_1TeV",   "type": "DM", "mass": "1.0 TeV", "xsec_pb": 0.04,    "n_gen_ntuple": 12807, "survived": 100000, "produced": 100000, "ntuple_file": "./sig/dm/flat_tuple_yy_1p0_qcd"},
    {"name": "DM_1p5TeV", "type": "DM", "mass": "1.5 TeV", "xsec_pb": 0.001615,  "n_gen_ntuple": 26885, "survived": 100000, "produced": 100000, "ntuple_file": "./sig/dm/flat_tuple_yy_1p5_qcd"},
    {"name": "DM_2p5TeV", "type": "DM", "mass": "2.5 TeV", "xsec_pb": 7.831e-6,  "n_gen_ntuple": 52144, "survived": 100000, "produced": 100000, "ntuple_file": "./sig/dm/flat_tuple_yy_2p5_qcd"},
]

def main():
    try:
        with open("skeleton-trf-config.txt", "r") as f:
            base_config = f.read()
    except FileNotFoundError:
        print("ERROR: skeleton-trf-config.txt not found. Please create it first.")
        return

    for point in signal_points:
        print(f"\n{'='*50}\nProcessing: {point['name']}\n{'='*50}")

        # Calculations
        sig_eff = point["survived"] / point["produced"]
        xsec_ratio = point["xsec_pb"] / BKG_XSEC_PB
        eff_ratio = sig_eff / BKG_EFF
        target_signal_yield = ZNN_TARGET_YIELD * xsec_ratio * eff_ratio
        base_sf = target_signal_yield / point["n_gen_ntuple"]

        if point["type"] == "LQ":
            final_sf = base_sf * LQ_MAGNIFICATION
            print(f"Applying LQ magnification: {LQ_MAGNIFICATION}x")
        else: # "DM"
            final_sf = base_sf * DM_MAGNIFICATION
            print(f"Applying DM magnification: {DM_MAGNIFICATION}x")

        # Use regex to replace placeholders
        temp_config = base_config
        label = f"{point['type']} {point['mass']}"

        temp_config = re.sub(r'JOB_NAME', point["name"], temp_config)
        temp_config = re.sub(r'OUTPUT_DIRECTORY', f"./{point['name']}_fit", temp_config)
        temp_config = re.sub(r'SIGNAL_LABEL', label, temp_config)
        temp_config = re.sub(r'SIGNAL_NTUPLE_PATH', point["ntuple_file"], temp_config)
        temp_config = re.sub(r'SIGNAL_SCALE_FACTOR', f"{final_sf:.8f}", temp_config)

        # Write and run the config
        config_filename = f"config_{point['name']}.txt"
        with open(config_filename, "w") as f:
            f.write(temp_config)
        print(f"Generated config: {config_filename} with FINAL magnified SF = {final_sf:.8f}")

        command = ["trex-fitter", "nwdfp", config_filename]
        print(f"Executing: {' '.join(command)}")

        try:
            subprocess.run(command, check=True, text=True)
            print(f"--- Successfully completed {point['name']} ---")
        except subprocess.CalledProcessError as e:
            print(f"--- ERROR: TRexFitter failed for {point['name']} ---")
            break
        except FileNotFoundError:
            print("\nERROR: 'trex-fitter' command not found.")
            break

if __name__ == "__main__":
    main()
