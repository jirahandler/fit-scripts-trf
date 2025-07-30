import os
import math
from glob import glob
import uproot
import numpy as np
import matplotlib.pyplot as plt
from puma import Histogram, HistogramPlot

# --- Configuration ---

# Define the path to your top-level directory
base_path = "."

# Define the analysis regions, which correspond to the TTree names in your files
regions = ["untagged", "c_tagged"]

# Define variables to exclude from plotting
variables_to_exclude = ["nBjets", "nCjets", "jet1_phi", "jet2_phi", "nJets", "event_xsec", "event_weight"]

# --- File Discovery ---

# Find all background files using a wildcard
all_bkg_files = glob(os.path.join(base_path, "bkg", "*.root"))
# CORRECTED: Exclude wlnu and ttbar files from the list
bkg_files = [f for f in all_bkg_files if 'wlnu' not in os.path.basename(f) and 'ttbar' not in os.path.basename(f)]

if not bkg_files:
    raise FileNotFoundError("No background .root files found in ./bkg/ after excluding wlnu and ttbar. Please check the path.")
else:
    print(f"Found the following background files to process: {bkg_files}")


# Find all signal files and categorize them by type (dm, lq)
sig_files = {
    "dm": glob(os.path.join(base_path, "sig", "dm", "*.root")),
    "lq": glob(os.path.join(base_path, "sig", "lq", "*.root")),
}

# --- Plotting ---

# Create a base output directory for the plots
os.makedirs("plots", exist_ok=True)

# Loop through each defined region (TTree)
for region in regions:
    print(f"Processing Region: {region}")
    print("====================================")

    # --- Automatically discover and filter variables for the current region ---
    variables = []
    try:
        # Use the first background file to discover variables for this region
        with uproot.open(bkg_files[0]) as f:
            if region not in f:
                print(f"TTree '{region}' not found in {bkg_files[0]}. Skipping this region.")
                continue # Skip to the next region
            tree = f[region]
            # Discover all variables
            discovered_variables = [key for key in tree.keys()]
            # Filter out excluded variables
            variables = [v for v in discovered_variables if v not in variables_to_exclude]
            print(f"Successfully discovered and filtered variables. Plotting {len(variables)} variables in TTree '{region}'.")
    except Exception as e:
        print(f"Error reading variables for region '{region}' from {bkg_files[0]}: {e}")
        continue # Skip to the next region

    if not variables:
        print(f"No variables to plot for region '{region}'. Skipping.")
        continue

    # Loop through each signal category (dm, lq)
    for sig_category, files in sig_files.items():
        if not files:
            print(f"No signal files found for category '{sig_category}'. Skipping.")
            continue

        # Create a subdirectory for the region and signal category
        output_dir = os.path.join("plots", region, sig_category)
        os.makedirs(output_dir, exist_ok=True)

        # Loop through each signal file in the category
        for sig_file in files:
            sig_name = os.path.splitext(os.path.basename(sig_file))[0].replace("flat_tuple_", "")
            print(f"\n  Processing signal file: {sig_name}")

            # --- Create a Canvas of Subplots ---
            n_vars = len(variables)
            ncols = int(np.ceil(np.sqrt(n_vars)))
            nrows = int(np.ceil(n_vars / ncols))

            fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 4))
            axes = axes.flatten()

            # Loop through each variable and its corresponding subplot axis
            for i, var in enumerate(variables):
                ax = axes[i]
                print(f"    -> Plotting variable: {var}")

                # --- Load all data for this variable ---
                try:
                    with uproot.open(sig_file) as f:
                        if region not in f or var not in f[region]:
                            print(f"    ! Warning: '{region}/{var}' not in {sig_file}. Skipping plot.")
                            ax.text(0.5, 0.5, f"'{var}'\nnot found in signal", ha='center', va='center', style='italic')
                            ax.set_yticklabels([])
                            ax.set_xticklabels([])
                            continue
                        signal_values = f[region].arrays([var], library="np")[var]
                except Exception as e:
                    print(f"    ! Error loading signal {var} from {sig_file}: {e}")
                    continue

                background_data = {}
                all_bkg_values_for_var = []
                for bkg_file in bkg_files:
                    try:
                        with uproot.open(bkg_file) as f:
                            if region in f and var in f[region]:
                                bkg_values = f[region].arrays([var], library="np")[var]
                                background_data[bkg_file] = bkg_values
                                all_bkg_values_for_var.append(bkg_values)
                    except Exception as e:
                        print(f"    ! Error loading background {var} from {bkg_file}: {e}")

                if len(signal_values) == 0 and not all_bkg_values_for_var:
                    ax.text(0.5, 0.5, f"No data for '{var}'", ha='center', va='center')
                    continue

                # --- Manual Plotting using Matplotlib ---
                all_values = np.concatenate([signal_values] + all_bkg_values_for_var)
                if len(all_values) == 0:
                    ax.text(0.5, 0.5, f"No data for '{var}'", ha='center', va='center')
                    continue

                # Use percentiles for robust axis range determination
                lower_bound = np.percentile(all_values, 1)
                upper_bound = np.percentile(all_values, 99)
                if lower_bound == upper_bound:
                    upper_bound += 1
                bins = np.linspace(lower_bound, upper_bound, 51)

                # --- Normalization Calculation ---
                total_signal_entries = len(signal_values)

                # --- Plot overlaid backgrounds (Normalized to signal) ---
                bkg_colors = ['green', 'blue', 'cyan']
                color_index = 0
                for bkg_file, bkg_values in background_data.items():
                    if len(bkg_values) > 0 and total_signal_entries > 0:
                        # Calculate the scale factor to match the total signal yield
                        scale_factor = total_signal_entries / len(bkg_values)
                        weights = np.ones_like(bkg_values) * scale_factor

                        bkg_name = os.path.splitext(os.path.basename(bkg_file))[0].replace("flat_tuple_", "")
                        ax.hist(bkg_values, bins=bins, weights=weights, label=bkg_name, histtype='step', linewidth=1.5, color=bkg_colors[color_index % len(bkg_colors)])
                        color_index += 1

                # --- Plot signal overlaid (raw counts) ---
                if len(signal_values) > 0:
                    ax.hist(signal_values, bins=bins, label="Signal", histtype='step', color="crimson", linewidth=2)

                ax.set_xlabel(var.replace("_", " "))
                # Update y-axis label to reflect normalization
                ax.set_ylabel("Events (Normalized to Signal)")
                ax.legend(fontsize='x-small')
                ax.grid(True, which='both', linestyle='--', linewidth=0.5)

            # Turn off any unused subplots
            for j in range(n_vars, len(axes)):
                axes[j].axis('off')

            fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            fig.suptitle(f"Variable Distributions for {sig_name} ({region} region)", fontsize=16, weight='bold')

            plot_filename = os.path.join(output_dir, f"{sig_name}_{region}_all_variables.png")
            fig.savefig(plot_filename, dpi=150)
            plt.close(fig)
            print(f"    => Saved canvas plot to {plot_filename}")

print("\nAll plots for all regions have been generated.")
