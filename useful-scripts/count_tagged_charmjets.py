import uproot
import awkward as ak
import sys

def count_tagged_charm_jets(filename):
    """
    Quickly counts the number of true charm jets that are tagged in a Delphes file.
    """
    print(f"Processing file: {filename}")
    try:
        with uproot.open(filename) as f:
            tree = f['Delphes']

            # Load only the branches we need as awkward arrays
            b_tags = tree['Jet.BTag'].array(library='ak')
            flavors = tree['Jet.Flavor'].array(library='ak')

            # Create a boolean mask for tagged charm jets
            # Condition 1: The jet is tagged (BTag > 0)
            # Condition 2: The jet is a true charm jet (abs(Flavor) == 4)
            is_tagged_charm = (b_tags > 0) & (ak.abs(flavors) == 4)

            # Sum up all the 'True' values to get the total count
            total_tagged_charm = ak.sum(is_tagged_charm)

            print(f"Found {total_tagged_charm} tagged charm-flavored jets.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 count_tagged_charm.py <your_delphes_file.root>")
    else:
        # You can pass one or more files to the script
        for filename in sys.argv[1:]:
            count_tagged_charm_jets(filename)
