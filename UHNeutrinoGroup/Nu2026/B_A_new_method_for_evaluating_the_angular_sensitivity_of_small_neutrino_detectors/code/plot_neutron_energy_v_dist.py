import math
import matplotlib.ticker as tick
import matplotlib.pyplot as plt
from cycler import cycler
import numpy as np
import pandas as pd
# Use LaTeX font
plt.rc('font', family='serif', size = 14)
plt.rcParams['text.usetex'] = True
plt.rcParams['mathtext.fontset'] = 'cm' # computer modern
# particle names corresponding to PDG codes listed below
particles = ["positron", "electron", "neutron", "proton", "helium-4", "hydrogen-3"]
# PDG codes for positrons, neutrons, protons, helium-4 and hydrogen-3
pdg_codes = [-11, 11, 2112, 2212, 1.00002004e+09, 1.00001003e+09]
# strings for doping concentrations and file processing
doping_str = "0.1\\%"
doping_name = {"0.1\\%": "001wt_","0.5\\%": "005wt_"}
run_nums = ["run0", "run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8", "run9"]
# thermal energy at 300K, in keV
e_therm = 300*8.617333262e-5
# variable to choose the run number
rnum = 0
preamble_str = "/home/jack/Documents/Directionality/Paper_B/simulations/ibd_cube_001wt_10k_"
fname_str = "/neutrons.txt"
# Filepaths for each concentration
data_file = preamble_str + run_nums[rnum] + fname_str
# Names for data headers
col_names = [
        "Row", "Instance", "trackPDG", "trackPosX", "trackPosY", "trackPosZ",
        "trackTime", "trackMomX", "trackMomY", "trackMomZ", "trackKE",
        "trackPro"#, "evid", "mcx", "mcy", "mcz", "mcu", "mcv", "mcw", "mcpdg"
    ]
plt.figure(figsize=(6, 4))
if doping_str == "0.1\\%":
    print(f"Processing run # {rnum} 0.1% wt lithium-6...")
else:
    raise ValueError(f"Invalid string for doping concentration: {doping_str}. Choose only \"0.1\\%\" doping.")
# Read the file and detect where data begins
with open(data_file, "r") as file:
    lines = file.readlines()
# Identify the first numeric data row (ignoring headers)
data_start_idx = next(i for i, line in enumerate(lines) if line.strip() and line.strip()[0].isdigit())
data = pd.read_csv(
    data_file,
    delim_whitespace=True,  # Use whitespace as delimiter
    skiprows=data_start_idx,  # Skip header lines
    names=col_names
)
# Convert numeric columns to appropriate data types
data[col_names] = data[col_names].astype(float)
total_captures = len(data.groupby("Row").nunique())
# Identify valid events that contain both helium-4 and hydrogen-3 tracks
valid_rows = data.groupby("Row")["trackPDG"].apply(
    lambda pdgs: (pdg_codes[4] in pdgs.values) and (pdg_codes[5] in pdgs.values)
)
# Keep only the rows where the corresponding "Row" is valid and contain neutrons
filtered_data = data[(data["Row"].isin(valid_rows[valid_rows].index))]
# Get number of Li-6 captures
li6_captures = len(filtered_data.groupby("Row").last().reset_index())
print("Number of lithium-6 captures" + doping_str + f": {li6_captures}\nNumber of captures on hydrogen: {total_captures - li6_captures}\nTotal number of captures: {total_captures}")
neutron_data = filtered_data[filtered_data["trackPDG"] == pdg_codes[2]]
# Compute scatter distances and energies
distances = []
energies = []
for _, group in neutron_data.groupby("Row"):
    if len(group) < 2:
        continue  # Skip events with only one interaction
    positions = group[["trackPosX", "trackPosY", "trackPosZ"]].values
    energy = 1e06*group["trackKE"].values[:-1]  # Exclude last energy since no next scatter, convert to eV
    # Compute Euclidean distance between successive scatters
    dist = np.linalg.norm(np.diff(positions, axis=0), axis=1)
    distances.extend(dist)
    energies.extend(energy)
# Convert lists to numpy arrays for plotting
distances = np.array(distances)
energies = np.array(energies)
# miniumum distance energy values for exception handling
EPS = 1.0e-06
min_distance = max(distances.min(), EPS)
max_distance = distances.max()
min_energy = max(energies.min(), EPS)
max_energy = energies.max()
# bins for 2-D histograms (log scale for better visualization)
num_x_bins = 50  # Number of bins for scatter distance
num_y_bins = 50  # Number of bins for neutron energy
x_bins = np.logspace(np.log10(min_distance), np.log10(max_distance), num_x_bins)
y_bins = np.logspace(np.log10(min_energy), np.log10(max_energy), num_y_bins)
# create 2-D histogram
hist, x_edges, y_edges, img = plt.hist2d(distances, energies, bins=[x_bins, y_bins], norm='log', cmap="plasma")
# Color Bar
cbar = plt.colorbar()
cbar.set_label("Counts (log scale)")
axs = plt.gca()
axs.axhline(y=e_therm, color="black", linestyle="--")
axs.set_xscale("log")
axs.set_xlim(1.0e-04,1.0e2)
axs.set_yscale("log")
axs.set_ylim(4.0e-04,2.0e5)
plt.xlabel("Distance between Scatters (mm)")
plt.ylabel("Neutron Energy (eV)")
# Grid for readability
plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=1.0)
axs.xaxis.set_major_locator(tick.LogLocator(base=10, numticks=7))
axs.yaxis.set_major_locator(tick.LogLocator(base=10, numticks=15))
# Adjust layout
plt.tight_layout()
plt.savefig("plots/neutron_energy_vs_scatter_distance_2Dhist" + doping_str + run_nums[rnum] + ".pdf", bbox_inches='tight')
plt.show()
print("Done!")

#plt.legend(title="\\% wt $^6$Li doping", framealpha=1.0)
