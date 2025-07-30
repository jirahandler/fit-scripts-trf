import numpy as np
import matplotlib.pyplot as plt

def eff_light_jet(pt):
  """Efficiency formula for light-flavor jets (mistag rate)."""
  return 0.002 + 7.3e-06 * pt

def eff_c_jet(pt):
  """Efficiency formula for c-jets (mistag rate)."""
  return 0.20 * np.tanh(0.02 * pt) * (1 / (1 + 0.0034 * pt))

def eff_b_jet(pt):
  """Efficiency formula for b-jets."""
  return 0.80 * np.tanh(0.003 * pt) * (30 / (1 + 0.086 * pt))

# --- Plotting ---

# Define a range of pt values from 0 to 1000 GeV
pt_range = np.linspace(0, 5500, 5000)

# Calculate the efficiencies for each jet type over the pt range
light_eff = eff_light_jet(pt_range)
c_jet_eff = eff_c_jet(pt_range)
b_jet_eff = eff_b_jet(pt_range)

# Create the plot
plt.figure(figsize=(10, 6))

plt.plot(pt_range, b_jet_eff, label='b-jets (PDG ID 5)', color='blue', linewidth=2)
plt.plot(pt_range, c_jet_eff, label='c-jets (PDG ID 4)', color='green', linewidth=2)
plt.plot(pt_range, light_eff, label='Light-flavor jets (PDG ID 0)', color='red', linewidth=2, linestyle='--')

# --- Formatting ---
plt.title('Delphes Flavor Tagging Efficiency vs. Jet $p_T$')
plt.xlabel('Jet $p_T$ [GeV]')
plt.ylabel('Tagging Efficiency')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.ylim(0, 1.0) # Set y-axis limit from 0 to 1
plt.xlim(0, 5500) # Set x-axis limit
plt.show()
