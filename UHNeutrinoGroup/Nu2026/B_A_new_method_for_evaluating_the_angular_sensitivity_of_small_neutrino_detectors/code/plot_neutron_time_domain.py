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
# strings for doping concentrations and file processing
doping_conc = ["0.1\\%", "0.5\\%"]
run_nums = ["run0", "run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8", "run9"]
# variable to choose the run number
rnum = 0
preamble_str = "/home/jack/Documents/Directionality/Paper_B/simulations/ibd_cube_"
fname_str = "/neutrons.txt"
doping_fname = {"0.1\\%": "001wt_10k_", "0.5\\%": "005wt_10k_new_macro_"}
# Filepaths for each concentration
data_files = {
    "0.1\\%": preamble_str + doping_fname["0.1\\%"] + run_nums[rnum] + fname_str,
    "0.5\\%": preamble_str + doping_fname["0.5\\%"] + run_nums[rnum] + fname_str
}
doping_choice = doping_conc[0]# 0 for 0.1%, 1 for 0.5%
# thermal energy at 300K, in keV
e_therm = 3*8.617333262e-6
print(f"Thermal energy at 300K: {e_therm} keV")
# Names for data headers
col_names = [
        "Row", "Instance", "trackPDG", "trackPosX", "trackPosY", "trackPosZ",
        "trackTime", "trackMomX", "trackMomY", "trackMomZ", "trackKE",
        "trackPro"
    ]
# Read the file and detect where data begins
with open(data_files[doping_choice], "r") as file:
    lines = file.readlines()
# Identify the first numeric data row (ignoring headers)
data_start_idx = next(i for i, line in enumerate(lines) if line.strip() and line.strip()[0].isdigit())
# Read data using Pandas, skipping non-data lines
data = pd.read_csv(
    data_files[doping_choice],
    delim_whitespace=True,  # Use whitespace as delimiter -- method to be deprecated. Use sep='\s+', in future versions with updated python3
    skiprows=data_start_idx,  # Skip header lines
    names=col_names
)
# Convert numeric columns to appropriate data types
data[col_names] = data[col_names].astype(float)
# Remove NaN entries
data.dropna(subset=["trackTime","trackKE"], how="all", inplace=True)
# Identify valid events that contain both helium-4 and hydrogen-3 tracks
valid_rows = data.groupby("Row")["trackPDG"].apply(
    lambda pdgs: (pdg_codes[4] in pdgs.values) and (pdg_codes[5] in pdgs.values)
)
# Keep only the rows where the corresponding "Row" is valid
filtered_data = data[data["Row"].isin(valid_rows[valid_rows].index)]
# Debugging: Print the number of valid rows after filtering
print(f"Number of valid rows after filtering for lithium-6 capture: {len(filtered_data.groupby('Row').last().reset_index())}")
event_nums = filtered_data["Row"].unique()
events = []
if (doping_choice=="0.1\\%"):
    # group events -- events to plot: 0, 11, 561, 9966 for _001wt
    events = [event_nums[0], event_nums[10], event_nums[490], event_nums[8600]]
    print(f"Plotting events {events}")
    # string for plot save file
    f_str = "_001wt"
elif (doping_choice=="0.5\\%"):
    # events to plot: 0, 10, 507, 8868 for _005wt
    events = [event_nums[0], event_nums[10], event_nums[490], event_nums[8600]]
    print(f"Plotting events {events}")
    # string for plot save file
    f_str = "_005wt"
else:
    # exit on error - select a valid doping concentration
    raise ValueError(f"Invalid string for doping concentration: {doping_choice}. Choose either \"0.1\\%\" or \"0.5\\%\".")
for i, event in enumerate(events):
    event_data = filtered_data[(filtered_data["Row"]==event) & (filtered_data["trackPDG"]==pdg_codes[2]) & (filtered_data["trackKE"]!=0)]# plot neutrons only for selected events
    x_values = 0.001*event_data["trackTime"]# convert to microseconds
    y_values = 1000*event_data["trackKE"]# convert to keV
    plt.figure(figsize=(6, 4))
    # Plot selected entry
    plt.semilogy(
        x_values,
        y_values,
        marker="o",
        linestyle="-",
        color="black",
        label=f"Event {event:.0f}"
    )
    # Add dashed line for thermal energy
    plt.axhline(y=e_therm, color="black", linestyle="--")
    plt.xlabel("time ($\\mu$s)")
    plt.ylabel("Neutron KE (keV)")
    plt.legend(loc="upper right", framealpha=1.0)
    plt.grid(True)
    plt.minorticks_on()
    # Adjust layout
    plt.tight_layout()
    plt.savefig("plots/neutron_time_domain"+f_str+"_"+run_nums[rnum]+f"_event{event:.0f}.pdf", bbox_inches="tight")
    plt.show()
