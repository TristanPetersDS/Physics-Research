import os
import sys
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import subprocess

class PhysicsValidator:
    def __init__(self):
        # Configuration
        self.data_dir = "/home/jack/RATPAC2/ratpac-setup/ratpac/output/mtv_directionality"
        self.out_dir = os.getcwd()
        self.outdata_dir = os.path.join(self.out_dir, "validation_data")
        
        # Boolean Flags
        self.debug = False
        self.latex = True
        
        if self.debug:
            print("PhysicsValidator class method: __init__")
            
        if self.latex:
            plt.rc("font", family="serif", size = 16)
            plt.rcParams["text.usetex"] = True
            plt.rcParams["mathtext.fontset"] = "cm" # computer modern
            
        # Initialize placeholders
        self.test_num = None
        self.root_filename = "output.ntuple.root"
        self.root_file = None
        self.txt_file = None
        self.li6_perc = None
        self.df = None  # DataFrame placeholder
        
        # Initialize paths and files
        self.macro_path = os.path.join(self.out_dir, "readValidation.C")
        self.plot_dir = os.path.join(self.out_dir, "validation_plots")
        self.stats_file = None
        if not os.path.exists(self.outdata_dir):
            os.makedirs(self.outdata_dir)
        
    def configure(self):
        """Detect data files and prompt user for configuration"""
        print("\n--- MTV Directionality Physics Validator Configuration ---")
        search_pattern = os.path.join(self.data_dir, "ibd_cube_*_10k_run*")
        subdirs = glob.glob(search_pattern)
        
        if not subdirs:
            print(f"No subdirectories matching 'ibd_cube_*_10k_run*' found in {self.data_dir}.")
            sys.exit(1)
        
        available_runs = []
        for d in subdirs:
            dirname = os.path.basename(d)
            parts = dirname.split('_')
            
            if len(parts) >= 5:
                wt_str = parts[2]   
                run_str = parts[4]  
                
                potential_root = os.path.join(d, self.root_filename)
                if os.path.exists(potential_root):
                    available_runs.append((dirname, wt_str, run_str, d, potential_root))
                    
        if not available_runs:
            print(f"No '{self.root_filename}' files found in the matched subdirectories.")
            sys.exit(1)
            
        print("Available datasets:")
        available_runs.sort(key=lambda x: (x[1], x[2])) 
        
        for i, (dirname, wt, run, fullpath, root_path) in enumerate(available_runs):
            conc = "0.1%" if wt == "001wt" else "0.5%" if wt == "005wt" else wt
            print(f"  [{i+1}] Concentration: {conc}, Run: {run} (Dir: {dirname})")
            
        choice = input(f"\nSelect a dataset to extract (1-{len(available_runs)}): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(available_runs):
            selected = available_runs[int(choice)-1]
            dirname, wt_str, run_str, full_subdir_path, root_path = selected
            
            self.test_num = run_str.replace("run", "") 
            self.li6_perc = 0.1 if wt_str == "001wt" else 0.5 if wt_str == "005wt" else None
            self.root_file = root_path
            
            self.txt_file = os.path.join(self.outdata_dir, f"validation_data_{wt_str}_{run_str}.txt")
            self.stats_file = os.path.join(self.plot_dir, f"validation_statistics_{run_str}.txt")
            
            print("\nConfiguration Complete.")
            print(f"Target ROOT file: {self.root_file}")
            print(f"Output text file: {self.txt_file}")
            print(f"Output statistics file: {self.stats_file}")
            
            if not os.path.exists(self.plot_dir):
                os.makedirs(self.plot_dir)
        else:
            print("Invalid selection. Exiting.")
            sys.exit(1)
        return
        
    def extract_data(self):
        """Run the ROOT macro to dump text data."""
        if os.path.exists(self.txt_file) and os.path.getsize(self.txt_file) > 0:
            print(f"\nFound existing data: {self.txt_file}")
            ans = input("Overwrite? (y/n) [n]: ").strip().lower()
            if ans != 'y': 
                return True

        if not os.path.exists(self.root_file):
            print(f"Error: {self.root_file} not found.")
            return False

        cuts = "trackPDG == 2112 || trackPDG == -11 || trackPDG == 22 || trackPDG == 1000020040 || trackPDG == 1000010030"
        
        macro_content = f"""
void readValidation(const char* filename) {{
  TFile *_file0 = TFile::Open(filename);
  if (!_file0 || _file0->IsZombie()) {{ return; }}
  auto T = (TTree*)_file0->Get("output");
  T->SetScanField(-1);
  const char* columns = "trackPDG : trackProcess : mcx : mcy : mcz : trackPosX : trackPosY : trackPosZ : trackTime : trackKE";
  const char* cuts = "{cuts}";
  T->Scan(columns, cuts, "colsize=25 precision=9 col=::20.10");
}}
"""
        with open(self.macro_path, "w") as f:
            f.write(macro_content)

        print(f"\nRunning extraction from {os.path.basename(self.root_file)}...")
        cmd = f'root -l -q -b "{self.macro_path}(\\"{self.root_file}\\")" > "{self.txt_file}"'
        subprocess.run(cmd, shell=True, check=True)
        
        subprocess.run(f"sed -i '1,3d' {self.txt_file}", shell=True)
        subprocess.run(f"sed -i '$d' {self.txt_file}", shell=True)
        subprocess.run(f"sed -i 's/*//g' {self.txt_file}", shell=True)
        
        print(f"Extraction complete. Data saved to: {self.txt_file}")
        return True

    def parse_data(self):
        """Parse the extracted ASCII data file into a Pandas DataFrame."""
        print(f"\nParsing data from {self.txt_file} into DataFrame...")
        
        if not os.path.exists(self.txt_file):
            print("Error: Text file does not exist. Cannot parse.")
            return False

        col_names = [
            "Row", "Instance", "trackPDG", "trackProcess", "mcx", "mcy", "mcz", 
            "trackPosX", "trackPosY", "trackPosZ", "trackTime", "trackKE"
        ]
        
        try:
            self.df = pd.read_csv(
                self.txt_file,
                delim_whitespace=True, 
                names=col_names,
                on_bad_lines='skip',
                dtype=str 
            )
            
            self.df = self.df.apply(pd.to_numeric, errors='coerce')
            self.df.dropna(how='all', inplace=True)
            
            print(f"Successfully loaded {len(self.df)} lines into the DataFrame.")
            total_events = self.df['Row'].nunique()
            print(f"Total Unique Events Detected: {total_events}")
            return True
            
        except Exception as e:
            print(f"An error occurred while parsing the dataframe: {e}")
            return False

    def process_and_plot(self):
        """Generate analysis plots and statistics for the selected dataset."""
        print("\n--- Processing Data and Generating Plots ---")
        
        stats_out = open(self.stats_file, "w")
        
        # Filter for Li-6 captures
        valid_rows = self.df.groupby("Row")["trackPDG"].apply(
            lambda pdgs: (1000020040 in pdgs.values) and (1000010030 in pdgs.values)
        )
        li6_data = self.df[self.df["Row"].isin(valid_rows[valid_rows].index)]
        
        total_captures = self.df['Row'].nunique()
        li6_captures = li6_data['Row'].nunique()
        
        print(f"Extracted {li6_captures} Li-6 Captures out of {total_captures} Total Captures.")
        
        stats_out.write(f"Total Captures: {total_captures}\n")
        stats_out.write(f"Li-6 Captures: {li6_captures}\n")
        stats_out.write(f"Hydrogen Captures: {total_captures - li6_captures}\n\n")
        
        neutron_data = li6_data[li6_data["trackPDG"] == 2112]
        positron_data = li6_data[li6_data["trackPDG"] == -11]
        #gamma_data = li6_data[li6_data["trackPDG"] == 22]
        #alpha_data = li6_data[li6_data["trackPDG"] == 1000020040]
        #triton_data = li6_data[li6_data["trackPDG"] == 1000010030]
        
        n_grouped = neutron_data.groupby("Row")
        p_grouped = positron_data.groupby("Row")
        #g_grouped = gamma_data.groupby("Row")
        #a_grouped = alpha_data.groupby("Row")
        #t_grouped = triton_data.groupby("Row")
        
        # --- 1. Positron Displacement ---
        p_first = p_grouped.first()
        p_last = p_grouped.last()
        p_disp = np.sqrt((p_last["trackPosX"] - p_first["trackPosX"])**2 + 
                         (p_last["trackPosY"] - p_first["trackPosY"])**2 + 
                         (p_last["trackPosZ"] - p_first["trackPosZ"])**2)
                         
        plt.figure(figsize=(8,6))
        plt.hist(p_disp.dropna(), bins=np.linspace(0, 50, 51), histtype='step', color='red', linewidth=1.5)
        plt.xlim(0, 50)
        plt.xlabel("Positron Track Length (mm)")
        plt.ylabel("Count")
        plt.savefig(os.path.join(self.plot_dir, f"positron_track_length_run{self.test_num}.pdf"), bbox_inches="tight")
        plt.close()
        
        # --- 2. Neutron Displacement ---
        n_first = n_grouped.first()
        n_last = n_grouped.last()
        n_disp = np.sqrt((n_last["trackPosX"] - n_first["trackPosX"])**2 + 
                         (n_last["trackPosY"] - n_first["trackPosY"])**2 + 
                         (n_last["trackPosZ"] - n_first["trackPosZ"])**2)
                         
        plt.figure(figsize=(8,6))
        plt.hist(n_disp.dropna(), bins=np.linspace(0, 250, 51), histtype='step', color='orange', linewidth=1.5)
        plt.xlim(0, 250)
        plt.xlabel("Neutron Track Length (mm)")
        plt.ylabel("Count")
        plt.savefig(os.path.join(self.plot_dir, f"neutron_displacement_run{self.test_num}.pdf"), bbox_inches="tight")
        plt.close()
        
        # --- 3. Neutron Initial Kinetic Energy ---
        n_first_ke = n_first["trackKE"] * 1000 
        plt.figure(figsize=(8,6))
        plt.hist(n_first_ke.dropna(), bins=np.linspace(0, 100, 101), histtype='step', color='black', linewidth=1.5)
        plt.xlim(0, 100)
        plt.xlabel("Neutron Initial Kinetic Energy (keV)")
        plt.ylabel("Count")
        plt.savefig(os.path.join(self.plot_dir, f"neutron_initial_ke_run{self.test_num}.pdf"), bbox_inches="tight")
        plt.close()
        
        # --- 4. Neutron Capture Time ---
        n_cap_time = n_last["trackTime"] * 0.001 
        plt.figure(figsize=(8,6))
        plt.hist(n_cap_time.dropna(), bins=np.linspace(0, 100, 101), histtype='step', color='black', linewidth=1.5)
        plt.xlim(0, 100)
        plt.xlabel(r"Capture Time of IBD Neutrons ($\mu$s)")
        plt.ylabel("Count")
        plt.savefig(os.path.join(self.plot_dir, f"neutron_capture_time_run{self.test_num}.pdf"), bbox_inches="tight")
        plt.close()
        
        stats_out.write(f"Mean Positron Displacement: {p_disp.mean():.2f} +/- {p_disp.std():.2f} mm\n")
        stats_out.write(f"Mean Neutron Displacement: {n_disp.mean():.2f} +/- {n_disp.std():.2f} mm\n")
        stats_out.write(f"Mean Neutron Initial KE: {n_first_ke.mean():.2f} +/- {n_first_ke.std():.2f} keV\n")
        stats_out.write(f"Mean Neutron Capture Time: {n_cap_time.mean():.2f} +/- {n_cap_time.std():.2f} us\n")
        
        # --- Thermalization Metrics ---
        e_therm_keV = 300 * 8.617333262e-8 
        
        n_therm_time = []
        n_scat_total = []
        n_scat_before_therm = []
        n_scat_after_therm = [] 
        n_time_after_therm = [] 
        n_distances = []
        n_energies = []
        
        for name, group in n_grouped:
            g = group.dropna(subset=["trackKE"]).copy()
            if g.empty: continue
            
            g["trackKE_keV"] = g["trackKE"] * 1000
            
            # For 2D histogram
            pos = g[["trackPosX", "trackPosY", "trackPosZ"]].values
            diffs = np.diff(pos, axis=0)
            dists = np.sqrt(np.sum(diffs**2, axis=1))
            n_distances.extend(dists)
            n_energies.extend(g["trackKE_keV"].values[:-1]) 
            
            # Total Scatters (matching old logic: the size of the valid tracking group for the event)
            n_scat_total.append(len(g))
            
            # Thermalization logic:
            # We explicitly filter out the capture step (where KE exactly 0) to prevent epithermal 
            # captures from being falsely recorded as "thermalizing" exactly at the capture step.
            g_alive = g[g["trackKE_keV"] > 0]
            therm_idx = g_alive[g_alive["trackKE_keV"] <= e_therm_keV].index
            
            if len(therm_idx) > 0:
                first_therm = g.loc[therm_idx[0]]
                t_therm = first_therm["trackTime"] * 0.001 # us
                
                # Time before thermalization
                n_therm_time.append(t_therm)
                
                # Scatters before thermalization (count rows up to therm index)
                scats_before = g.loc[:therm_idx[0]]
                n_scat_before_therm.append(len(scats_before) - 1)
                
                # Time after thermalization (Capture Time - Therm Time)
                t_cap = g.iloc[-1]["trackTime"] * 0.001
                n_time_after_therm.append(t_cap - t_therm)
                
                # Scatters after thermalization (Total Scatters - Scatters Before)
                n_scat_after_therm.append(len(g) - len(scats_before))
        
        # --- 5. Total Scatters ---
        if n_scat_total:
            plt.figure(figsize=(8,6))
            plt.hist(n_scat_total, bins=np.linspace(0, 100, 101), histtype='step', color='black', linewidth=1.5)
            plt.xlim(0, 100)
            plt.xlabel("IBD Neutron Scatters")
            plt.ylabel("Count")
            plt.savefig(os.path.join(self.plot_dir, f"neutron_scatters_run{self.test_num}.pdf"), bbox_inches="tight")
            plt.close()
        
        # --- 6. Neutron Thermalization Time ---
        if n_therm_time:
            plt.figure(figsize=(8,6))
            plt.hist(n_therm_time, bins=np.logspace(-2, 3, 61), histtype='step', color='black', linewidth=1.5)
            plt.xscale('log')
            plt.xlim(1e-2, 1e3)
            plt.xlabel(r"Neutron Thermalization Time ($\mu$s)")
            plt.ylabel("Count")
            plt.savefig(os.path.join(self.plot_dir, f"neutron_thermalization_time_run{self.test_num}.pdf"), bbox_inches="tight")
            plt.close()

        # --- 7. Scatters Before Thermalization ---    
        if n_scat_before_therm:
            plt.figure(figsize=(8,6))
            plt.hist(n_scat_before_therm, bins=np.linspace(0, 50, 51), histtype='step', color='black', linewidth=1.5)
            plt.xlim(0, 50)
            plt.xlabel("Neutron Scatters Before Thermalization")
            plt.ylabel("Count")
            plt.savefig(os.path.join(self.plot_dir, f"neutron_scatters_before_therm_run{self.test_num}.pdf"), bbox_inches="tight")
            plt.close()

        # --- 8. Scatters After Thermalization ---
        if n_scat_after_therm:
            plt.figure(figsize=(8,6))
            plt.hist(n_scat_after_therm, bins=np.linspace(0, 100, 101), histtype='step', color='black', linewidth=1.5)
            plt.xlim(0, 100)
            plt.xlabel("Neutron Scatters After Thermalization")
            plt.ylabel("Count")
            plt.savefig(os.path.join(self.plot_dir, f"neutron_scatters_after_therm_run{self.test_num}.pdf"), bbox_inches="tight")
            plt.close()

        # --- 9. Time After Thermalization ---
        if n_time_after_therm:
            plt.figure(figsize=(8,6))
            plt.hist(n_time_after_therm, bins=np.logspace(-2, 3, 61), histtype='step', color='black', linewidth=1.5)
            plt.xscale('log')
            plt.xlim(1e-2, 1e3)
            plt.xlabel(r"Neutron Time After Thermalization ($\mu$s)")
            plt.ylabel("Count")
            plt.savefig(os.path.join(self.plot_dir, f"neutron_time_after_therm_run{self.test_num}.pdf"), bbox_inches="tight")
            plt.close()

        if n_therm_time:
            stats_out.write(f"Mean Time to Therm: {np.mean(n_therm_time):.2f} +/- {np.std(n_therm_time):.2f} us\n")
            stats_out.write(f"Mean Time After Therm: {np.mean(n_time_after_therm):.2f} +/- {np.std(n_time_after_therm):.2f} us\n")
            stats_out.write(f"Mean Total Scatters: {np.mean(n_scat_total):.2f} +/- {np.std(n_scat_total):.2f}\n")
            stats_out.write(f"Mean Scatters to Therm: {np.mean(n_scat_before_therm):.2f} +/- {np.std(n_scat_before_therm):.2f}\n")
            stats_out.write(f"Mean Scatters After Therm: {np.mean(n_scat_after_therm):.2f} +/- {np.std(n_scat_after_therm):.2f}\n")
            
        # --- 10. Energy vs Distance ---
        if n_distances and n_energies:
            plt.figure(figsize=(8,6))
            plt.hist2d(n_distances, n_energies, bins=[np.logspace(-4, 2, 51), np.logspace(-8, 3, 51)], 
                       cmap="plasma", norm=mcolors.LogNorm())
            plt.xscale('log')
            plt.yscale('log')
            plt.xlim(1e-4, 1e2)
            plt.ylim(1e-8, 1e3)
            plt.axhline(y=e_therm_keV, color="black", linestyle="--")
            plt.colorbar(label="Count (log scale)")
            plt.xlabel("Distance between Scatters (mm)")
            plt.ylabel("Neutron Kinetic Energy (keV)")
            plt.savefig(os.path.join(self.plot_dir, f"neutron_energy_vs_dist_run{self.test_num}.pdf"), bbox_inches="tight")
            plt.close()
            
        # --- 10. Neutron Energy vs Time for Selected Events ---
        sample_events = li6_data["Row"].unique()[:4]
        plt.figure(figsize=(8,6))
        
        for ev in sample_events:
            ev_data = neutron_data[neutron_data["Row"] == ev].dropna(subset=["trackKE"])
            if not ev_data.empty:
                t = ev_data["trackTime"] * 0.001
                #print(f"Time array (us:)\n{t}")
                ke = ev_data["trackKE"] * 1000
                #print(f"Energy array (keV:)\n{ke}")
                # remove last entry where energy = 0
                t = np.delete(t, -1)
                #print(f"Time array (us:)\n{t}")
                ke = np.delete(ke, -1)
                #print(f"Energy array (keV:)\n{ke}")
                plt.plot(t, ke, marker='o', linestyle='-', label=f"Event {int(ev)}")
                
        plt.axhline(y=e_therm_keV, color='black', linestyle='--', label='Thermal Energy')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel(r"Time ($\mu$s)")
        plt.ylabel("Neutron Kinetic Energy (keV)")
        plt.legend()
        plt.savefig(os.path.join(self.plot_dir, f"neutron_energy_vs_time_run{self.test_num}.pdf"), bbox_inches="tight")
        plt.close()

        stats_out.close()
        print(f"\nAll plots saved to: {self.plot_dir}")
        print(f"Statistics saved to: {self.stats_file}")

    def compare_doping_displacements(self):
        """Generates overlaid positron and neutron displacement plots for both 0.1% and 0.5% doping for the current run."""
        if not self.test_num:
            print("No test number selected. Cannot compare.")
            return
            
        print(f"\n--- Generating Comparison Plots for Run {self.test_num} ---")
        
        wts = ["001wt", "005wt"]
        labels = ["0.1\\%", "0.5\\%"]
        colors = ["red", "blue"]
        
        p_disps = []
        n_disps = []
        
        for wt in wts:
            subdir_pattern = os.path.join(self.data_dir, f"ibd_cube_{wt}_10k_run{self.test_num}")
            matches = glob.glob(subdir_pattern)
            if not matches:
                print(f"Could not find directory for {wt} run {self.test_num}. Skipping comparison.")
                return
                
            root_file = os.path.join(matches[0], self.root_filename)
            txt_file = os.path.join(self.outdata_dir, f"validation_data_{wt}_run{self.test_num}.txt")
            
            # Extract if needed
            if not (os.path.exists(txt_file) and os.path.getsize(txt_file) > 0):
                print(f"Extracting data for {wt}...")
                if not os.path.exists(root_file):
                    print(f"ROOT file {root_file} not found.")
                    return
                    
                cuts = "trackPDG == 2112 || trackPDG == -11 || trackPDG == 22 || trackPDG == 1000020040 || trackPDG == 1000010030"
                macro_content = f"""
void readValidation(const char* filename) {{
  TFile *_file0 = TFile::Open(filename);
  if (!_file0 || _file0->IsZombie()) {{ return; }}
  auto T = (TTree*)_file0->Get("output");
  T->SetScanField(-1);
  const char* columns = "trackPDG : trackProcess : mcx : mcy : mcz : trackPosX : trackPosY : trackPosZ : trackTime : trackKE";
  const char* cuts = "{cuts}";
  T->Scan(columns, cuts, "colsize=25 precision=9 col=::20.10");
}}
"""
                with open(self.macro_path, "w") as f:
                    f.write(macro_content)

                cmd = f'root -l -q -b "{self.macro_path}(\\"{root_file}\\")" > "{txt_file}"'
                subprocess.run(cmd, shell=True, check=True)
                subprocess.run(f"sed -i '1,3d' {txt_file}", shell=True)
                subprocess.run(f"sed -i '$d' {txt_file}", shell=True)
                subprocess.run(f"sed -i 's/*//g' {txt_file}", shell=True)
            
            # Parse
            print(f"Parsing data for {wt}...")
            col_names = ["Row", "Instance", "trackPDG", "trackProcess", "mcx", "mcy", "mcz", "trackPosX", "trackPosY", "trackPosZ", "trackTime", "trackKE"]
            try:
                df = pd.read_csv(txt_file, delim_whitespace=True, names=col_names, on_bad_lines='skip', dtype=str)
                df = df.apply(pd.to_numeric, errors='coerce')
                df.dropna(how='all', inplace=True)
            except Exception as e:
                print(f"Error parsing {txt_file}: {e}")
                return
                
            # Filter for Li-6 captures
            valid_rows = df.groupby("Row")["trackPDG"].apply(
                lambda pdgs: (1000020040 in pdgs.values) and (1000010030 in pdgs.values)
            )
            li6_data = df[df["Row"].isin(valid_rows[valid_rows].index)]
            
            # Extract Positron Displacement
            p_data = li6_data[li6_data["trackPDG"] == -11]
            p_grouped = p_data.groupby("Row")
            p_first = p_grouped.first()
            p_last = p_grouped.last()
            p_disp = np.sqrt((p_last["trackPosX"] - p_first["trackPosX"])**2 + 
                             (p_last["trackPosY"] - p_first["trackPosY"])**2 + 
                             (p_last["trackPosZ"] - p_first["trackPosZ"])**2)
            p_disps.append(p_disp.dropna())
            
            # Extract Neutron Displacement
            n_data = li6_data[li6_data["trackPDG"] == 2112]
            n_grouped = n_data.groupby("Row")
            n_first = n_grouped.first()
            n_last = n_grouped.last()
            n_disp = np.sqrt((n_last["trackPosX"] - n_first["trackPosX"])**2 + 
                             (n_last["trackPosY"] - n_first["trackPosY"])**2 + 
                             (n_last["trackPosZ"] - n_first["trackPosZ"])**2)
            n_disps.append(n_disp.dropna())

        # Plot Positron Comparison
        plt.figure(figsize=(8,6))
        for i in range(2):
            plt.hist(p_disps[i], bins=np.linspace(0, 50, 51), histtype='step', color=colors[i], linewidth=1.5, label=f"{labels[i]} $^6$Li")
        plt.xlim(0, 50)
        plt.xlabel("Positron Track Length (mm)")
        plt.ylabel("Count")
        plt.legend(framealpha=1.0)
        plt.savefig(os.path.join(self.plot_dir, f"positron_track_length_comparison_run{self.test_num}.pdf"), bbox_inches="tight")
        plt.close()
        
        # Plot Neutron Comparison
        plt.figure(figsize=(8,6))
        for i in range(2):
            plt.hist(n_disps[i], bins=np.linspace(0, 250, 51), histtype='step', color=colors[i], linewidth=1.5, label=f"{labels[i]} $^6$Li")
        plt.xlim(0, 250)
        plt.xlabel("Neutron Track Length (mm)")
        plt.ylabel("Count")
        plt.legend(framealpha=1.0)
        plt.savefig(os.path.join(self.plot_dir, f"neutron_displacement_comparison_run{self.test_num}.pdf"), bbox_inches="tight")
        plt.close()
        
        print(f"Comparison plots successfully saved to: {self.plot_dir}")


if __name__ == "__main__":
    validator = PhysicsValidator()
    validator.configure()
    
    if validator.extract_data():
        if validator.parse_data():
            validator.process_and_plot()
            
    ans = input(f"\nWould you like to generate the 0.1% vs 0.5% comparison plots for Run {validator.test_num}? (y/n) [y]: ").strip().lower()
    if ans == 'y' or ans == '':
        validator.compare_doping_displacements()
        
    sys.exit()
