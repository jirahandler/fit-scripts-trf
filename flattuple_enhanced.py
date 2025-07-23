#!/usr/bin/env python3
"""
Process all Delphes ROOT files starting with 'delphes_' in the current directory.
For each file, write out flat ntuples for events that pass the following selections:
  * At least two jets.
  * Leading jet (jet1) has pT >= 150 GeV and |eta| <= 2.4.
  * Subleading jet (jet2) has pT >= 30 GeV and |eta| <= 2.8.
  * Missing ET (MET) >= 200 GeV.

Output files are named by replacing the 'delphes' prefix with 'flat_tuple',
for example 'delphes_sample.root' becomes 'flat_tuple_sample.root'.
"""

import os
import glob
import math
import numpy as np
import uproot
import awkward as ak


def compute_leading_jets(jets_pt, jets_eta, jets_phi):
    """
    Find events that have at least two jets, sort jets by pT in descending order,
    and return arrays for the leading and subleading jets along with a mask
    for the events that passed the two-jet requirement.
    """
    # Build a mask for events with two or more jets
    mask_two_jets = ak.num(jets_pt, axis=1) >= 2

    # Select only those events
    pt_selected  = jets_pt[mask_two_jets]
    eta_selected = jets_eta[mask_two_jets]
    phi_selected = jets_phi[mask_two_jets]

    # Sort jets by pT for each event
    order = ak.argsort(pt_selected, axis=1, ascending=False)
    pt_sorted  = pt_selected[order]
    eta_sorted = eta_selected[order]
    phi_sorted = phi_selected[order]

    # Extract leading (0) and subleading (1) jets
    pt1  = pt_sorted[:, 0]
    pt2  = pt_sorted[:, 1]
    eta1 = eta_sorted[:, 0]
    eta2 = eta_sorted[:, 1]
    phi1 = phi_sorted[:, 0]
    phi2 = phi_sorted[:, 1]

    # Convert to NumPy arrays so we can slice them later
    return (
        pt1.to_numpy(),
        pt2.to_numpy(),
        eta1.to_numpy(),
        eta2.to_numpy(),
        phi1.to_numpy(),
        phi2.to_numpy(),
        mask_two_jets.to_numpy()
    )


def compute_dphi(phi1, phi2):
    """
    Compute the absolute difference in phi between two angles,
    returning a value between 0 and pi.
    """
    delta = (phi1 - phi2 + math.pi) % (2 * math.pi) - math.pi
    return np.abs(delta)


def process_file(input_path):
    # Prepare the output filename
    filename = os.path.basename(input_path)
    output_name = filename.replace('delphes', 'flat_tuple', 1)
    print(f"Reading {filename} and writing {output_name}")

    # Open the ROOT file and access the Delphes tree
    root_file = uproot.open(input_path)
    tree = root_file['Delphes']

    # Load jet variables
    jets_pt  = tree['Jet.PT'].array(library='ak')
    jets_eta = tree['Jet.Eta'].array(library='ak')
    jets_phi = tree['Jet.Phi'].array(library='ak')

    # Load MET and HT
    met_ak     = tree['MissingET.MET'].array(library='ak')
    met_phi_ak = tree['MissingET.Phi'].array(library='ak')
    ht_ak      = tree['ScalarHT.HT'].array(library='ak')

    # Load event-level cross section and weight
    xsec_ak   = tree['Event.CrossSection'].array(library='ak')
    weight_ak = tree['Event.Weight'].array(library='ak')

    # Load the b-tagging bit if it exists, otherwise assume all zeros
    try:
        btag_ak = tree['Jet.BTag'].array(library='ak')
    except uproot.KeyInFileError:
        btag_ak = ak.zeros_like(jets_pt, dtype=int)

    # Count all jets and b-jets per event
    n_jets  = ak.num(jets_pt, axis=1)
    n_bjets = ak.sum(btag_ak > 0, axis=1)

    # Get leading and subleading jets and mask for events with at least two jets
    pt1, pt2, eta1, eta2, phi1, phi2, mask2j = compute_leading_jets(
        jets_pt, jets_eta, jets_phi
    )

    # Apply jet kinematics selection
    mask_jetkin = (
        (pt1 >= 150.0) & (np.abs(eta1) <= 2.4) &
        (pt2 >= 30.0)  & (np.abs(eta2) <= 2.8)
    )

    # Convert MET to NumPy and apply the two-jet mask
    met     = met_ak[mask2j].to_numpy().squeeze()
    met_phi = met_phi_ak[mask2j].to_numpy().squeeze()

    # Keep only events that pass the jet kinematics
    pt1     = pt1[mask_jetkin].astype(np.float32)
    pt2     = pt2[mask_jetkin].astype(np.float32)
    eta1    = eta1[mask_jetkin].astype(np.float32)
    eta2    = eta2[mask_jetkin].astype(np.float32)
    phi1    = phi1[mask_jetkin].astype(np.float32)
    phi2    = phi2[mask_jetkin].astype(np.float32)
    met     = met[mask_jetkin].astype(np.float32)
    met_phi = met_phi[mask_jetkin].astype(np.float32)

    # Now apply the MET selection
    mask_met = met >= 200.0
    pt1      = pt1[mask_met]
    pt2      = pt2[mask_met]
    eta1     = eta1[mask_met]
    eta2     = eta2[mask_met]
    phi1     = phi1[mask_met]
    phi2     = phi2[mask_met]
    met      = met[mask_met]
    met_phi  = met_phi[mask_met]

    # Build an index array to slice other branches in the same order
    idx_all = np.where(mask2j)[0]
    idx_all = idx_all[mask_jetkin]
    idx_all = idx_all[mask_met]

    # Slice other event-level variables
    n_jets  = n_jets.to_numpy()[idx_all].astype(np.int32)
    n_bjets = n_bjets.to_numpy()[idx_all].astype(np.int32)
    cross   = xsec_ak.to_numpy().squeeze()[idx_all].astype(np.float32)
    weight  = weight_ak.to_numpy().squeeze()[idx_all].astype(np.float32)
    ht      = ht_ak.to_numpy().squeeze()[idx_all].astype(np.float32)

    # Compute additional derived quantities
    jet1_met_dphi    = compute_dphi(phi1, met_phi).astype(np.float32)
    met_significance = np.where(ht > 0, met / np.sqrt(ht), 0.0).astype(np.float32)

    # Gather all variables into a dictionary for output
    branches = {
        'jet1_pt': pt1,
        'jet2_pt': pt2,
        'jet1_eta': eta1,
        'jet2_eta': eta2,
        'jet1_phi': phi1,
        'jet2_phi': phi2,
        'met_pt': met,
        'jet1met_dphi': jet1_met_dphi,
        'met_sig': met_significance,
        'nJets': n_jets,
        'nBjets': n_bjets,
        'event_xsec': cross,
        'event_weight': weight
    }

    # Split events into tagged and untagged samples
    tag_mask   = branches['nBjets'] > 0
    untag_mask = branches['nBjets'] == 0
    tagged     = {k: v[tag_mask]   for k, v in branches.items()}
    untagged   = {k: v[untag_mask] for k, v in branches.items()}

    # Decide branch types based on array dtypes
    types = {name: ('float32' if arr.dtype.kind == 'f' else 'int32')
             for name, arr in branches.items()}

    # Write the output file with two TTrees
    with uproot.recreate(output_name) as out:
        out.mktree('b_tagged', types)
        out['b_tagged'].extend(tagged)
        out.mktree('untagged', types)
        out['untagged'].extend(untagged)

    print('Wrote', len(tagged['jet1_pt']), 'tagged and',
          len(untagged['jet1_pt']), 'untagged events to', output_name)


def main():
    for rootfile in glob.glob('delphes_*.root'):
        process_file(rootfile)

if __name__ == '__main__':
    main()
