import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# Use LaTeX font
plt.rc('font', family='serif', size=14)
plt.rcParams['text.usetex'] = True
plt.rcParams['mathtext.fontset'] = 'cm'  # Computer Modern
# particle names corresponding to PDG codes listed below
particles = ["positron", "electron", "neutron", "proton", "helium-4", "hydrogen-3"]
# PDG codes for positrons, neutrons, protons, helium-4 and hydrogen-3
pdg_codes = [-11, 11, 2112, 2212, 1.00002004e+09, 1.00001003e+09]
# Strings for doping concentrations and file processing
doping_str = "0.1\\% wt"  # Only plotting 0.1% Li-6
run_nums = ["run0", "run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8", "run9"]#
preamble_str = "/home/jack/Documents/Directionality/Paper_B/simulations/ibd_cube_"
fname_str = "/neutrons.txt"
doping_fname = "001wt_10k_"#"005wt_10k_new_macro_"
# Filepaths for each run
data_files = {run: preamble_str + doping_fname + run + fname_str for run in run_nums}
# Names for data headers
col_names = [
    "Row", "Instance", "trackPDG", "trackPosX", "trackPosY", "trackPosZ",
    "trackTime", "trackMomX", "trackMomY", "trackMomZ", "trackKE", "trackPro"
]
# Define distinct colors for different runs
color_map = plt.cm.get_cmap("viridis", len(run_nums))  # Use a colormap for distinct colors
# Define histogram bins
bin_edges = np.linspace(0, 100, 101)
# Initialize array to store aggregated histogram counts
aggregated_hist_values = np.zeros(len(bin_edges) - 1)
plt.figure(figsize=(6, 4))
# Loop through each run for 0.1% Li-6 doping
for i, run in enumerate(run_nums):
    if (run=="run1")|(run=="run7")|(run=="run9"):
        print(f"Skipping {run}...\n")
        continue
    print(f"Processing {doping_str} lithium-6 for {run}...")
    # Read the file and detect where data begins
    data_file = data_files[run]
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
    filtered_data = data[data["Row"].isin(valid_rows[valid_rows].index)]
    # Get number of Li-6 captures
    li6_captures = len(filtered_data.groupby("Row").last().reset_index())
    print(f"Number of lithium-6 captures for {run}: {li6_captures}")
    neutron_data = filtered_data[filtered_data["trackPDG"] == pdg_codes[2]]#() & (filtered_data["Row"] >= 5000)]
    neutron_scatters = neutron_data.groupby("Row").size()
    # Mean and standard deviation
    mean_val = np.nanmean(neutron_scatters)
    std_dev = np.nanstd(neutron_scatters)
    print(f"{run} mean number of scatters: {mean_val:.0f}\nStd dev: {std_dev:.0f}")
    # Compute histogram bins
    hist_values, _ = np.histogram(neutron_scatters, bins=bin_edges)
    # Accumulate histogram values for the aggregated plot
    aggregated_hist_values += hist_values
    # Plot using stairs with different colors for each run
    plt.stairs(hist_values, bin_edges, color=color_map(i), label=f"{run}", alpha=1.0)
    print("Done!")
plt.xlim(0, 100)
plt.xlabel("IBD Neutron Scatters")
plt.ylabel("Counts")
plt.legend(title="Runs", framealpha=1.0)
plt.grid()
# Adjust layout
plt.tight_layout()
plt.savefig("plots/neutron_scatters_comparison_001wt_runs0thru9_except1_7and9.pdf", bbox_inches='tight')#
plt.show()
# ==============================
# PLOT AGGREGATED DATA
# ==============================
plt.figure(figsize=(6, 4))
# Compute error bars (Poisson statistics)
#errors = np.sqrt(aggregated_hist_values)
# Compute bin centers for error bars
#bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
# Plot aggregated histogram
plt.stairs(aggregated_hist_values, bin_edges, color="black", label="all runs except 1, 7 and 9", alpha=1.0)#
# Add error bars
#plt.errorbar(bin_centers, aggregated_hist_values, yerr=errors, fmt="o", color="black", capsize=3, markersize=4, label="Poisson Errors")
plt.xlim(0, 100)
plt.xlabel("IBD Neutron Scatters")
plt.ylabel("Counts")
plt.legend(title="Aggregated", framealpha=1.0)
plt.grid()
# Adjust layout
plt.tight_layout()
plt.savefig("plots/neutron_scatters_comparison_001wt_aggregated_runs0thru9_except1_7and9.pdf", bbox_inches='tight')#
plt.show()
