# python3 - uncert_parallel_ratpac.py

# Author: Jeffrey G. Yepez
# Last Updated: 19 Nov 2025

import sys
import time
import math

from scipy.stats import poisson, vonmises
from scipy.special import gamma, i0, i1, i0e, i1e
from scipy.optimize import curve_fit

import numpy as np
import matplotlib.pyplot as plt

from tqdm import tqdm
from mpi4py import MPI

class DataProcessor():    
    ################################################################
    def __init__(self, n=1000, dx=5, gs=91):

        # Initializes the parameters for the parallel array.
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()

        # Control flags for code debugging and use of LaTeX in plots.
        self.debug_L1 = True
        self.debug_L2 = False
        self.latex = True

        # Flag that is used in the shuffling algorithm in sampleData() to determine which data array to sample from.
        self.flow = False
        
        if (self.rank == 0) and self.debug_L1:
            print("DataProcessor class method: __init__")

        if self.latex:
            plt.rc("font", family="serif", size = 16)
            plt.rcParams["text.usetex"] = True
            plt.rcParams["mathtext.fontset"] = "cm" # computer modern

        # Brian's ASCII output from RATPAC2 to be processed into coordinates.
        self.positron_file = "/Volumes/Photon/Manoa/Research/Data/res_1M_001wt_ref/truth.txt"
        self.neutron_file = "/Volumes/Photon/Manoa/Research/Data/res_1M_001wt_ref/neutrons.txt"
        #self.positron_file = "/Volumes/Photon/Manoa/Research/Data/res_10M_001wt_ref/output_9M_10M/truth.txt"
        #self.neutron_file = "/Volumes/Photon/Manoa/Research/Data/res_10M_001wt_ref/output_9M_10M/neutrons.txt"

        # Files for the post-processed fiducial IBD vertices and neutron capture locations.
        #self.vertices_file = "fid_vertices.npy"
        #self.captures_file = "fid_captures.npy"

        self.vertices_file = "events/fid_10M_vertices.npy"
        self.captures_file = "events/fid_10M_captures.npy"

        #self.vertices_file = "events/fid_1M_original_vertices.npy"
        #self.captures_file = "events/fid_1M_original_captures.npy"
        
        # Initialization variables for 2d square grid segmentation of size (self.grid_size x self.grid_size). This variable represents the number of square segments on a side of the grid. Must be an odd number so that there is a clearly defined center segment to model the prompt signal behavior.
        self.grid_size = gs # Has to be odd to simulate IBD physics, self.seg_size measured in mm
        self.seg_size = dx # mm

        # Expected true angle of the fiducial dataset in degrees.
        self.true_angle = 0

        # Number of samples in each run nof the direction algorithm.
        self.n = n    # Number of points

        # The half side length of all of the segments combined (detector size).
        self.l = (self.seg_size * self.grid_size) / 2.0

        # Defines binning range.
        self.x_range = (-self.l, self.l)
        self.y_range = (-self.l, self.l)

        if self.rank == 0:
            # This should only be run once to process the RATPAC2 output files. After that processData() produces and saves numpy files with the IBD vertices and neutron capture vertices that may be read by readData() and used by the program much more expediently.
            #self.processData()

            # This reads the data from the numpy data files produced by processData(). The must run successfully to perform analysis using this code.
            self.readData()            

        # Allocates an equal part of the circle to each core.
        self.all_angles = np.arange(-180, 180)
        self.angles = np.array_split(self.all_angles, self.size)[self.rank].tolist()

        print(f"Initialized rank {self.rank}. Allocated theta = [{self.angles[0]}, {self.angles[-1]}]")

        return

    ################################################################
    def processData(self):
        if (self.rank == 0) and self.debug_L1:
            print("DataProcessor class method: processData")

            """
            Processes the ASCII output from RATPAC2 produced by Brian. To be run on the host node only and run only once to produce the numpy data files that the readData() routine uses. Reads from the ASCII data from RATPAC2 to produce processed IBD vertices and neutron capture locations.
            """

            # Process the positrons file.
            #"""
            # Syntax for positrons:
            # Row Instance trackPDG trackProcess evid mcx mcy mcz mcu mcv mcw mcpdg 
            f = open(self.positron_file, "r")

            self.vertices = []

            ts = time.time()

            i = 0
            for line in f:
                if i < 4:
                    pass
                else:
                    try:
                        elems = line.split()
                        if elems[1] == "0":
                            mcx, mcy, mcz = float(elems[5]), float(elems[6]), float(elems[7])
                            self.vertices.append([mcx, mcy, mcz])
                    except Exception as err:
                        print(elems)
                        print(err)

                i += 1

            print(f"Time elapsed: {time.time() - ts}")

            print(f"Read {len(self.vertices)} event vertices...")

            np.save(self.vertices_file, np.array(self.vertices))
            #"""

            # Process the neutrons file.
            #"""
            # Syntax for neutrons:
            # ['Row', 'Instance', 'trackPDG', 'trackPosX', 'trackPosY', 'trackPosZ', 'trackTime', 'trackMomX', 'trackMomY', 'trackMomZ', 'trackKE', 'trackProcess']
            f = open(self.neutron_file, "r")

            self.captures = []

            ts = time.time()

            i = 0
            prev_line = ""
            for line in f:
                if i < 4:
                    pass
                else:
                    try:
                        elems = line.split()
                        if elems[1] == "0":
                            prev_elems = prev_line.split()
                            if len(prev_elems) > 0:
                                px, py, pz = float(prev_elems[3]), float(prev_elems[4]), float(prev_elems[5])
                                self.captures.append([px, py, pz])
                    except Exception as err:
                        prev_elems = prev_line.split()
                        px, py, pz = float(prev_elems[3]), float(prev_elems[4]), float(prev_elems[5])
                        self.captures.append([px, py, pz])

                        print(elems)
                        print(err)

                prev_line = line
                
                i += 1

            print(f"Time elapsed: {time.time() - ts}")

            print(f"Read {len(self.captures)} event captures...")

            np.save(self.captures_file, np.array(self.captures))
            #"""

            return

    ################################################################
    def readData(self):
        if (self.rank == 0) and self.debug_L1:
            print("DataProcessor class method: readData")

        """
        Reads the numpy files processed by processData() to be used for the analysis.
        """

        t_start = time.time()
        
        # Load in the data as numpy arrays.
        self.vertices = np.load(self.vertices_file)
        self.captures = np.load(self.captures_file)

        #n = min(len(self.vertices), len(self.captures))
        #self.vertices, self.captures = self.vertices[:n], self.captures[:n]

        #n = min(len(self.vertices), len(self.captures))
        #self.vertices = self.vertices[-n:]
        #self.captures = self.captures[-n:]

        # Calculate the capture locations relative to the IBD vertices for binning.
        self.coords = self.captures - self.vertices

        # Create an empty array used for the shuffling algorithm in sampleData().
        self.coords_buf = np.empty((0, 3), dtype=self.coords.dtype)

        # Sort to find usable events (excluding center element).
        R = self.seg_size / np.sqrt(2)

        self.usable_coords = []
        for c in self.coords:
            x, y, z = c

            r = np.sqrt(x**2 + y**2)

            if r > R:
                self.usable_coords.append(c)

        self.usable_coords = np.array(self.usable_coords)

        self.usable_coords_buf = np.empty((0, 3), dtype=self.usable_coords.dtype)

        # Assigns function pointers to the data
        self.data = {
            "detected" : {"main" : self.coords,        "buffer" : self.coords_buf},
            "usable"   : {"main" : self.usable_coords, "buffer" : self.usable_coords_buf}
        }

        print(f"Read {len(self.coords)} events...")
        
        print("Time to read and sort data:", time.time() - t_start)

        print(f"Percentage of detected events that are usable for detector: {(len(self.usable_coords)/len(self.coords))*100}")

        return

    ################################################################
    def averageTrackLength(self):
        if (self.rank == 0) and self.debug_L1:
            print("DataProcessor class method: averageTrackLength")

        norms = np.linalg.norm(self.coords, axis=1)

        # Calculate average neutron track length.
        avg_length = np.mean(norms)

        # Print out the value.
        print(avg_length)

        return

    ################################################################
    def sampleData(self, n_samples, center=True):
        if (self.rank == 0) and self.debug_L2:
            print("DataProcessor class method: sampleData")

        """
        Sample the fiducial dataset. Uses shuffling algorithm to mitigate oversampling of data. As samples are used they are removed from the fiducial array and copied into the buffer array. Once the fidicual dataset is depleted, the samples then begin being taken from the buffer array, deleted, and moved back into the original array. This minimizes oversampling of the dataset.
        """

        if center == True:
            k = "detected"
        else:
            k = "usable"

        # Checks the associated flag to decide from the array or buffer.
        if (len(self.data[k]["main"]) < n_samples) and (self.flow == False):
            self.flow = True
        if (len(self.data[k]["buffer"]) < n_samples) and (self.flow == True):
            self.flow = False

        # Based on flag decision, sample data array.
        if self.flow == False:
            idx = np.random.choice(self.data[k]["main"].shape[0], size=n_samples, replace=False)
            samples = self.data[k]["main"][idx]

            self.data[k]["main"] = np.delete(self.data[k]["main"], idx, axis=0)
            self.data[k]["buffer"] = np.vstack([self.data[k]["buffer"], samples])
        elif self.flow == True:
            # Samples the other array.
            idx = np.random.choice(self.data[k]["buffer"].shape[0], size=n_samples, replace=False)
            samples = self.data[k]["buffer"][idx]

            self.data[k]["buffer"] = np.delete(self.data[k]["buffer"], idx, axis=0)
            self.data[k]["main"] = np.vstack([self.data[k]["main"], samples])
        else:
            print("This will never print")

        return samples

    ################################################################
    def abs_sine(self, theta, theta0, amp, y_offset):
        if (self.rank == 0) and self.debug_L2:
            print("DataProcessor class method: abs_sine")
            
        """
        Absolute sine function used in the fitting step of the algorithm in directionAlgorithm().
        """
        return amp * np.abs(np.sin((theta - theta0) * np.pi / 180.0 / 2)) + y_offset

    ################################################################
    def rotateCoords(self, x_coords, y_coords, theta, plot=False):
        if (self.rank == 0) and self.debug_L2:
            print("DataProcessor class method: rotateCoords")

        """
        Rotates the given coordinate(s).
        """

        x_rot = []
        y_rot = []

        for x, y in zip(x_coords, y_coords):

            # Distance calculation in 2d.
            r = np.sqrt(x**2 + y**2)

            # Initial angle of capture.
            theta0 = np.arctan2(y, x)

            # Rotation calculation.
            phi = -theta * np.pi / 180.0

            # Coordinate transformation.
            xprime = r * np.cos(theta0 - phi)
            yprime = r * np.sin(theta0 - phi)

            x_rot.append(xprime)
            y_rot.append(yprime)

        x_rot = np.array(x_rot)
        y_rot = np.array(y_rot)

        return x_rot, y_rot

    ################################################################
    def wrap_angle(self, angle):
        if (self.rank == 0) and self.debug_L2:
            print("DataProcessor class method: wrap_angle")
        """
        Wrap any angle in degrees to the range (-180, 180].
        """
        wrapped = ((angle + 180) % 360) - 180
        
        return wrapped

    ################################################################
    def vonmises_circ_std(self, kappa):
        if (self.rank == 0) and self.debug_L1:
            print("DataProcessor class method: vonmises_circ_std")

        """
        Used in calcUncertainty() on the angular FND data results to calculate angular uncertainty.
        """

        R = i1e(kappa) / i0e(kappa)
        sigma_rad = np.sqrt(-2 * np.log(R))
        sigma_deg = np.rad2deg(sigma_rad)
        
        return sigma_rad, sigma_deg

    ################################################################
    def binEvents(self, x, y):
        arr, _, _ = np.histogram2d(y, x, bins=self.grid_size, range=[self.x_range, self.y_range])
        return arr / np.sum(arr)

    ################################################################
    def directionAlgorithm(self, center=True, plot=False, save=False):
        if (self.rank == 0) and self.debug_L1:
            print("DataProcessor class method: directionAlgorithm")

        # Sample both the reference and rotated datasets at the same time and distribute to all cores.
        data = self.sampleData(2 * self.n, center=center) if self.rank == 0 else None
        data = self.comm.bcast(data, root=0)

        half = self.n // 2

        # Extract the coordanates from data: The first set is used as the true dataset while the second is the rotated one.
        x1, y1 = data[:half, 0], data[:half, 1]
        x2, y2 = data[half:half * 2, 0], data[half:half * 2, 1]

        ref = self.binEvents(x1, y1)

        norms = []
        
        # Calculate FND of data sample compared with true data sample.
        for theta in self.angles:
            x, y = self.rotateCoords(x2, y2, theta)

            rot = self.binEvents(x, y)

            # Calculate the FND between the true dataset and the rotated dataset.
            norms.append(np.linalg.norm(ref - rot))

        # Collect all of the FND calculations to the host node to stitch them together.
        norms = self.comm.gather(norms, root=0)

        if self.rank == 0:
            # Stitch them together into a single list.
            stitched_norms = [val for sublist in norms for val in sublist]

            # Perform absolute sine fit.
            popt, pcov = curve_fit(self.abs_sine, self.all_angles, stitched_norms, p0=[self.true_angle, 1, 0])

            if plot:
                plt.plot(self.all_angles, stitched_norms)

                if save:
                    plt.savefig("FND.pdf", format="pdf", bbox_inches="tight")
                    
                plt.show()

            return popt[0]
        else:
            return None

    ################################################################
    def calcUncertainty(self, iterations, vary="counts", center=True, plot=False, save=False):
        if (self.rank == 0) and self.debug_L1:
            print("DataProcessor class method: calcUncertainty")

        if self.rank == 0:
            thetas = []
            pbar = tqdm(total=iterations, dynamic_ncols=True, file=sys.stdout, miniters=1, mininterval=0)

        for i in range(iterations):
            theta = self.directionAlgorithm(center=center)

            if self.rank == 0:
                thetas.append(theta)

                print()
                pbar.update()

        if self.rank == 0:

            #pbar.close()

            thetas = np.array([self.wrap_angle(t) for t in thetas])

            #print(type(angles_deg))

            kappa, loc, scale = vonmises.fit(thetas * np.pi / 180.0, fscale=1)

            #print(kappa, loc)

            #expanded_data = np.repeat(bin_centers_rad, hist)
            #kappa, loc, scale = vonmises.fit(expanded_data, fscale=1)

            #print(kappa, loc)

            if plot:

                n_bins = 36

                hist, bin_edges = np.histogram(thetas, bins=n_bins, range=(-180, 180))
                bin_centers_deg = (bin_edges[:-1] + bin_edges[1:]) / 2
                bin_centers_rad = np.deg2rad(bin_centers_deg)

                # Evaluate fitted PDF
                theta = np.linspace(-np.pi, np.pi, 500)
                pdf = vonmises.pdf(theta, kappa, loc=loc)

                # Scale PDF to histogram counts
                pdf_scaled = pdf / pdf.max() * hist.max()

                # Plot the histogram and the fit.
                fig, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(6,6))

                ax.set_yticklabels([])
                ax.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2])
                ax.set_xticklabels([r"$0$", r"$\pi/2$", r"$\pi$", r"$3\pi/2$"])

                ax.bar(bin_centers_rad, hist, width=2*np.pi/n_bins, bottom=0, alpha=1, edgecolor="b", facecolor="none", linewidth=2)

                ax.plot(theta, pdf_scaled, "r-", lw=2, label=f"$\\mu={np.rad2deg(loc):.1f}^\\circ, \\kappa={kappa:.2f}$")

                ax.set_theta_zero_location("N")
                ax.set_theta_direction(-1)
                ax.legend(loc="lower left")

                if save:
                    plt.savefig(f"polar_plot_dx_{self.seg_size}_n_{self.n}_i_{iterations}.pdf", format="pdf", bbox_inches="tight")
            
                plt.show()

            sigma_rad, sigma_deg = self.vonmises_circ_std(kappa)

            np.save(f"data/data_iter_dx_{self.seg_size}_n_{self.n}.npy", np.array(thetas))

            if center:
                k = "detected"
            else:
                k = "usable"

            if vary == "counts":
                f = open(f"data/func_iter_dx_{self.seg_size}_{k}.txt", "a")
                f.write(f"{self.n}\t{sigma_deg}\t{np.rad2deg(loc)}\n")                
            elif vary == "seg-size":
                f = open(f"data/func_iter_n_{self.n}_{k}.txt", "a")
                f.write(f"{self.seg_size}\t{sigma_deg}\t{np.rad2deg(loc)}\n")
            else:
                print("Invalid dependent variable: not saving information.")

            f.close()

        return
    
    ################################################################
    def round_to_nearest_odd(self, x):

        # Round to nearest integer.
        n = round(x)
        
        if n % 2 == 0:  
            # # If it's even choose the closer odd: n-1 or n+1.
            if abs(x - (n - 1)) <= abs(x - (n + 1)):
                return n - 1
            else:
                return n + 1
        return n
    
    ################################################################
    def gaussHist2D(self, save=False):
        if self.debug_L1:
            print("DataProcessor class method: gaussHist2D")

        """
        This is a nonparallel subroutine that runs on the host core. It plots a 2D histogram of a sample of the neutron data as a 3D bar plot.
        """

        # Take a given sample of the data.
        data = self.sampleData(self.n)
        x, y = data[:, 0], data[:, 1]

        # Produce the histogram.
        hist, xedges, yedges = np.histogram2d(y, x, bins=self.grid_size, range=[self.x_range, self.y_range])

        # Build grid positions.
        half = self.grid_size // 2
        x = (np.arange(self.grid_size) - half) * self.seg_size
        y = (np.arange(self.grid_size) - half) * self.seg_size
        xpos, ypos = np.meshgrid(x, y, indexing="ij")

        # Flatten for 3D bar plot.
        xpos = xpos.ravel()
        ypos = ypos.ravel()
        zpos = np.zeros_like(xpos)
        
        dz = hist.ravel()
        dx = dy = np.full_like(zpos, self.seg_size)

        # Plot.
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d", facecolor="white")

        ax.set_facecolor("white")

        ax.bar3d(xpos - self.seg_size / 2, ypos - self.seg_size / 2, zpos, dx, dy, dz, shade=True, color="skyblue", edgecolor="black")

        # Label axes.
        ax.set_xlabel("$x$ (mm)")
        ax.set_ylabel("$y$ (mm)")
        ax.set_zlabel("Counts")

        # Set tick marks to match the coordinates.
        tick_labels = [-150, 0, 150]
        ax.set_xticks(tick_labels)
        ax.set_yticks(tick_labels)
        ax.set_xticklabels([str(t) for t in tick_labels])
        ax.set_yticklabels([str(t) for t in tick_labels])
        
        # Adjust the elevation and azimuth for a nice view.
        ax.view_init(elev=10, azim=30)

        if save:
            plt.savefig(f"LEGO_dx_{self.seg_size}_n_{self.n}.pdf", format="pdf")

        plt.tight_layout()
        plt.show()

        return

################################################################
################################################################
################################################################
if __name__ == "__main__":
    """
    This is the main statement where the user can execute subroutines in the class.
    """
    proc = DataProcessor()

    #In the multiline comments are some functions the code can perform.

    """
    proc.gaussHist2D(save=True)
    """
    
    """
    if proc.rank == 0:
        t_start = time.time()
        
    proc.directionAlgorithm(center=True)

    if proc.rank == 0:
        print("Time to complete algorithm iteration:", time.time() - t_start)
    """

    """
    proc.calcUncertainty(1000, plot=True, save=True)
    """
    
    #"""
    # Produces the moneyplot data. Use when varying counts.

    #counts = [10, 30, 100, 300, 1000, 3000, 10000, 30000]
    #iters  = [10000, 3333, 1000, 333, 100, 100, 100, 100]

    counts = [10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000]#, 300000, 1000000]
    iters  = [100, 100, 100, 100, 100, 100, 100, 100, 100]#, 100, 100]

    #counts = np.linspace(10, 30, 11, dtype=int)
    #iters  = np.linspace(100,100,11, dtype=int)

    cnt = 0
    for c in counts:
        i = iters[cnt]
        if proc.rank == 0:
            print(c, i)
    
        proc.__init__(n=c)
        proc.calcUncertainty(i, center=False, plot=False)
        cnt += 1
    #"""
    

    """
    # Use when varying segment size.
    seg_sizes = np.linspace(5, 150, 30)

    seg_sizes = [155, 160, 165, 170, 175]
    
    for dx in seg_sizes:
        gs = proc.round_to_nearest_odd(450 / dx)
        print(dx, gs)
        
        proc.__init__(300, dx, gs)
        proc.calcUncertainty(300, vary="seg-size")

    """

    """
    proc.averageTrackLength()
    """

    sys.exit()
