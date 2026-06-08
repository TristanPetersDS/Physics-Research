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

# thermal energy at 300K, in keV
e_therm = 3*8.617333262e-6
print(f"Thermal energy at 300K: {e_therm} keV")

# strings for doping concentrations and file processing
doping_conc = ["0.1\\%"]
run_nums = ["run0", "run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8", "run9"]
# variable to choose the run number
rnum = 0
preamble_str = "/home/jack/Documents/Directionality/Paper_B/simulations/ibd_cube_001wt_10k_"
fname_str = "/neutrons.txt"
doping_fname = {"0.1\\%": "001wt_10k_"}
# Filepaths for each concentration
data_files = {
    "0.1\\%": preamble_str + run_nums[rnum] + fname_str,
}

# Names for data headers
col_names = [
        "Row", "Instance", "trackPDG", "trackPosX", "trackPosY", "trackPosZ",
        "trackTime", "trackMomX", "trackMomY", "trackMomZ", "trackKE",
        "trackPro"#, "evid", "mcx", "mcy", "mcz", "mcu", "mcv", "mcw", "mcpdg"
    ]

# Colors for different doping concentrations
plot_styles = {"0.1\\%": "-"}

scatters_before = {}
time_before = {}
scatters_after = {}
time_after = {}

for doping_str in doping_conc:
    if doping_str == "0.1\\%":
        print(f"Processing run # {rnum} 0.1% wt lithium-6...")
    else:
        raise ValueError(f"Invalid string for doping concentration: {doping_str}. Choose only \"0.1\\%\" wt doping concentration.")
    # Read the file and detect where data begins
    data_file = data_files[doping_str]
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
    print("Number of lithium-6 captures in " + doping_str + f": {li6_captures}\nNumber of hydrogen captures: {total_captures - li6_captures}\nTotal number of captures: {total_captures}")
    neutron_data = filtered_data[filtered_data["trackPDG"] == pdg_codes[2]]
    # Find thermalization events
    thermalization_data = neutron_data.groupby("Row").apply(lambda df: df[df["trackKE"] <= e_therm].head(1))
    thermalization_data = thermalization_data.reset_index(drop=True)
    # Compute number of scatters before thermalization, and print mean and standard deviation
    scatters_before[doping_str] = neutron_data.groupby("Row").apply(lambda df: len(df[df["trackKE"] > e_therm]))
    mean_scatters = np.nanmean(scatters_before[doping_str])
    std_scatters = np.nanstd(scatters_before[doping_str])
    print(f"Mean number of scatters before thermalization: {mean_scatters:.0f}\nStd dev: {std_scatters:.0f}")
    # Compute time before thermalization, and print mean and standard deviation
    time_before[doping_str] = thermalization_data["trackTime"] - neutron_data.groupby("Row")["trackTime"].min()
    mean_time = np.nanmean(time_before[doping_str])
    std_time = np.nanstd(time_before[doping_str])
    print(f"Mean time to thermalize: {mean_time:.0f} ns\nStd dev: {std_time:.0f} ns")
    # Filter events occurring after thermalization
    after_thermalization_data = neutron_data.merge(
        thermalization_data[["Row", "trackTime"]], on="Row", suffixes=("", "_thermal")
    )
    after_thermalization_data = after_thermalization_data[after_thermalization_data["trackTime"] > after_thermalization_data["trackTime_thermal"]]
    # Compute number of scatters after thermalization
    scatters_after[doping_str] = after_thermalization_data.groupby("Row").size()
    mean_scatters = np.nanmean(scatters_after[doping_str])
    std_scatters = np.nanstd(scatters_after[doping_str])
    print(f"Mean number of scatters between thermalization and capture: {mean_scatters:.0f}\nStd dev: {std_scatters:.0f}")
    # Compute time after thermalization
    time_after[doping_str] = neutron_data.groupby("Row")["trackTime"].max() - thermalization_data["trackTime"]
    mean_time = np.nanmean(time_after[doping_str])
    std_time = np.nanstd(time_after[doping_str])
    print(f"Mean time between themalization and capture: {mean_time:.0f} ns\nStd dev: {std_time:.0f} ns\nDone!")
# Histogram bins
scatter_bins = np.linspace(0, 25, 26)
time_bins = np.logspace(-1, 5, 51)  # Log scale for time
# **Plot 1: Scatters Before Thermalization**
plt.figure(figsize=(6,4))
hist_values, _ = np.histogram(scatters_before["0.1\\%"], bins=scatter_bins)
plt.stairs(hist_values, scatter_bins, linestyle=plot_styles["0.1\\%"], color="black", label=f"0.1\\%")
plt.xlim(0,25)
plt.xlabel("IBD Neutron Scatters before thermalization")
plt.ylabel("Counts")
plt.legend(title="$^6$Li doping", framealpha=1.0)
plt.grid()
# Adjust layout
plt.tight_layout()
plt.savefig("plots/neutron_scatters_before_thermalization_" + run_nums[rnum] + ".pdf", bbox_inches='tight')
plt.show()
# **Plot 2: Scatters Before Thermalization**
plt.figure(figsize=(6,4))
hist_values, _ = np.histogram(time_before["0.1\\%"], bins=time_bins)
plt.stairs(hist_values, time_bins, linestyle=plot_styles["0.1\\%"], color="black", label=f"0.1\\%")
plt.xscale("log")
plt.xlabel("Time before Thermalization (ns)")
plt.ylabel("Counts")
plt.legend(title="$^6$Li doping", framealpha=1.0)
plt.grid()
# Adjust layout
plt.tight_layout()
plt.savefig("plots/neutron_time_before_thermalization_" + run_nums[rnum] + ".pdf", bbox_inches='tight')
plt.show()
# Re-bin for after thermalization
scatter_bins = np.linspace(0, 100, 101)
time_bins = np.logspace(1, 6, 61)  # Log scale for time
# **Plot 3: Scatters Before Thermalization**
plt.figure(figsize=(6,4))
for doping_str in doping_conc:
    hist_values, _ = np.histogram(scatters_after[doping_str], bins=scatter_bins)
    plt.stairs(hist_values, scatter_bins, linestyle=plot_styles[doping_str], color="black", label=f"{doping_str}")
plt.xlim(0,100)
plt.xlabel("IBD Neutron Scatters after thermalization")
plt.ylabel("Counts")
plt.legend(title="$^6$Li doping", framealpha=1.0)
plt.grid()
# Adjust layout
plt.tight_layout()
plt.savefig("plots/neutron_scatters_after_thermalization_" + run_nums[rnum] + ".pdf", bbox_inches='tight')
plt.show()
# **Plot 4: Scatters Before Thermalization**
plt.figure(figsize=(6,4))
for doping_str in doping_conc:
    hist_values, _ = np.histogram(time_after[doping_str], bins=time_bins)
    plt.stairs(hist_values, time_bins, linestyle=plot_styles[doping_str], color="black", label=f"{doping_str}")
plt.xscale("log")
plt.xlabel("Time from Thermalization to Capture (ns)")
plt.ylabel("Counts")
plt.legend(title="$^6$Li doping", framealpha=1.0)
plt.grid()
# Adjust layout
plt.tight_layout()
plt.savefig("plots/neutron_time_after_thermalization_" + run_nums[rnum] + ".pdf", bbox_inches='tight')
plt.show()
