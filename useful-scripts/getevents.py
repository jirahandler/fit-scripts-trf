#!/usr/bin/env python3

import uproot
import glob
import os

def count_events_in_files():
    """
    Finds all files matching 'delphes_*.root' in the current directory,
    counts the number of events in the 'Delphes' TTree for each file,
    and prints a summary.
    """
    # --- Configuration ---
    # The pattern to match the ROOT files.
    file_pattern = "delphes_*.root"
    # The name of the TTree to read from the ROOT files.
    # For Delphes files, this is typically 'Delphes'.
    tree_name = "Delphes"

    # --- Script Logic ---
    total_events = 0
    file_count = 0

    print(f"Searching for files matching: '{file_pattern}' in the current directory...")

    # Find all files in the current directory matching the pattern
    file_list = glob.glob(file_pattern)

    if not file_list:
        print("\nNo files found matching the pattern. Please make sure you are in the correct directory.")
        return

    print(f"Found {len(file_list)} files. Processing...\n")
    print("-" * 50)
    print(f"{'Filename':<35} | {'Number of Events'}")
    print("-" * 50)

    # Loop through each file found
    for filename in sorted(file_list):
        try:
            # Open the ROOT file
            with uproot.open(filename) as file:
                # Check if the specified TTree exists in the file
                if tree_name not in file:
                    print(f"'{filename}': SKIPPED (TTree '{tree_name}' not found)")
                    continue

                # Access the TTree
                tree = file[tree_name]

                # Get the number of entries (events)
                num_events = tree.num_entries

                # Print the result for the current file
                print(f"{filename:<35} | {num_events}")

                # Add to the total count
                total_events += num_events
                file_count += 1

        except Exception as e:
            # Handle potential errors like corrupted files
            print(f"Could not process '{filename}'. Error: {e}")

    # Print the final summary
    print("-" * 50)
    print(f"\n{'Summary':-^50}")
    print(f"Processed {file_count} file(s).")
    print(f"Total number of events: {total_events}")
    print("-" * 50)

if __name__ == "__main__":
    # To run this script, you need to install the 'uproot' library.
    # You can install it using pip:
    # pip install uproot

    count_events_in_files()
