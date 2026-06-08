import math
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
# lists for doping concentrations run numbers for file processing
doping_conc = "0.1\\%"
run_nums = ["run0", "run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8", "run9"]
# variable to choose the run number
rnum = 0
preamble_str = "/home/jack/Documents/Directionality/Paper_B/simulations/ibd_cube_001wt_10k_"
fname_str = "/neutrons.txt"
doping_str = "001wt_"
# Filepaths for each concentration
data_file = preamble_str + run_nums[rnum] + fname_str
# Names for data headers
col_names = [
        "Row", "Instance", "trackPDG", "trackPosX", "trackPosY", "trackPosZ",
        "trackTime", "trackMomX", "trackMomY", "trackMomZ", "trackKE",
        "trackPro"#, "evid", "mcx", "mcy", "mcz", "mcu", "mcv", "mcw", "mcpdg"
    ]
# Colors for different doping concentrations
plot_styles = {"0.1\\%": "-"}
plt.figure(figsize=(6, 4))
if doping_conc == "0.1\\%":
    print(f"Processing run # {rnum} 0.1% wt lithium-6...")
else:
    raise ValueError(f"Invalid string for doping concentration: {doping_conc}. Choose only \"0.1\\%\" wt doping.")
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
print("Number of lithium-6 captures" + doping_str + f": {li6_captures}\nNumber of hydrogen captures: {total_captures - li6_captures}\nTotal number of captures: {total_captures}")
neutron_data = filtered_data[filtered_data["trackPDG"] == pdg_codes[2]]
neutron_scatters = neutron_data.groupby("Row").size()
# mean and standard deviation
mean_val = np.nanmean(neutron_scatters)
std_dev = np.nanstd(neutron_scatters)
print(f"Mean number of scatters: {mean_val:.0f}\nStd dev: {std_dev:.0f}")
# compute histogram bins
bin_edges = np.linspace(0, 100, 101)
hist_values, _ = np.histogram(neutron_scatters, bins=bin_edges)
# plot using stairs
plt.stairs(hist_values, bin_edges, color="black", linestyle=plot_styles[doping_conc], label=f"{doping_conc}", alpha=1.0)
print("Done!")
plt.xlim(0,100)
plt.xlabel("IBD Neutron Scatters")
plt.ylabel("Counts")
plt.legend(title="\\% wt $^6$Li doping", framealpha=1.0)
plt.grid()
# Adjust layout
plt.tight_layout()
plt.savefig("plots/neutron_scatters_" + run_nums[rnum] + ".pdf", bbox_inches='tight')
plt.show()
