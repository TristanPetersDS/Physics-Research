
import os
import sys
import time
import random
import json
import math
from tqdm import tqdm
import copy

import pandas as pd

from scipy.stats import poisson
from scipy.special import gamma
from scipy.optimize import curve_fit
import scipy.integrate as spi

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

################################################################
################################################################
################################################################
class DataProcessor():
    """
    RATPAC2 DataProcessor - Post processing methods for RATPAC2 positron and neutron output track data. This code produces figures for paper B using simulated data with RATPAC2.
    """
    ################################################################
    def __init__(self):

        # Control booleans.
        self.debug = False
        self.latex = True
        
        if self.debug:
            print("DataProcessor class method: __init__")

        if self.latex:
            #plt.rc("font", family="serif", size = 16)
            plt.rc("font", family="serif", size = 19)
            plt.rcParams["text.usetex"] = True
            plt.rcParams["mathtext.fontset"] = "cm" # computer modern

        ################################
        # Number of events to read and process from the RATPAC output. WARNING: No longer used to read data.
        self.N = 10000

        # Neutron file plus other track PDGs. This class converts and stores ASCII neutron data into pandas dataframe.
        self.dataFile = "/Users/gabriel/Downloads/ibd_cube_001wt_10k_run1/truth.txt"

        # Positron file if available. If not then set this variable to None.
        #self.positronFile = "/Users/gabriel/Downloads/ibd_cube_001wt_10k_run1/positrons.txt"
        self.positronFile = None

        # Initialization variables for 2d square grid segmentation of size (self.grid_size x self.grid_size). This variable represents the number of squares on a side of the grid. Must be an odd number so that there is a clearly defined center segment for prompt.
        self.grid_size = 9

        # Size of individual square segment in mm.
        #self.cube_size = 5
        self.cube_size = 50
        #self.cube_size = 150

        # Set the kind of neutron event state to observe. Currently only 'capture', '1st-scatter', or '2nd-scatter' supported. Current routines that depend on self.kind are: neutronHistogram, angularDist, cloudPlot, dimDist
        #self.kind = "1st-scatter"
        #self.kind = "2nd-scatter"
        self.kind = "capture"

        # Reads ASCII data and store in memory as pandas dataframe.
        self.initData()
        
        # Initializes the 2d square grid geometry specified in initGrid subroutine.
        self.initGrid()

        # Setting the kind must come after initData in initialization. After that no need to worry, can run whenever.
        self.setKind(self.kind)
        
        ################################
        # Simulation parameters.
        self.mux = 200        # Mean (center of dist in x)
        self.muy = 0          # Mean (center of dist in y)
        self.sigma = 28       # Standard deviation
        self.Nsim = 10000     # Number of points

        # Generate coordinates from normal distribution
        self.x_coords_sim = np.random.normal(self.mux, self.sigma, self.Nsim)
        self.y_coords_sim = np.random.normal(self.muy, self.sigma, self.Nsim)

        return

    ################################################################
    def initData(self):
        if self.debug:
            print("DataProcessor class method: initData")

        try:
            self.data = pd.read_csv(self.dataFile, sep="\\s+", skiprows=1, header=0, skipinitialspace=True)
        except Exception as err:
            print("Error in reading neutron data or creating pandas dataframe:")
            print(err)

            print()
            print("Quitting...")
            sys.exit()

        if self.positronFile == None:
            return

        try:
            self.positron_data = pd.read_csv(self.positronFile, sep="\\s+", skiprows=1, header=0, skipinitialspace=True)
        except Exception as err:
            print("Error in reading positron data or creating pandas dataframe:")
            print(err)

            print()
            print("Quitting...")
            sys.exit()
            
        return

    ################################################################
    def initGrid(self):
        if self.debug:
            print("DataProcessor class method: initGrid")

        # Size of half of the total detector grid in mm.
        self.half_size = self.cube_size * self.grid_size / 2.0

        # Initializes matrix for segmentation.
        self.seg = np.zeros((self.grid_size, self.grid_size), dtype=dict)

        # Creates bounds and event count bins for specified detector geometry.
        for i in range(self.grid_size):
            for j in range(self.grid_size):

                xlow  = self.cube_size * j - self.half_size
                xhigh = self.cube_size * j + self.cube_size - self.half_size
                
                yhigh = -(self.cube_size * i - self.half_size)
                ylow  = -(self.cube_size * i + self.cube_size - self.half_size)

                self.seg[i][j] = {"xbounds": [xlow, xhigh],
                                  "ybounds": [ylow, yhigh],
                                  "counts":  0}

        return

    ################################################################
    def setKind(self, kind):
        if self.debug:
            print("DataProcessor class method: setKind")

        self.kind = kind
        
        # Get the last row of each event.
        if kind == "capture":
            locs = self.data.groupby("Row").last()
        elif kind == "1st-scatter":
            locs = self.data.groupby("Row").nth(1)
        elif kind == "2nd-scatter":
            locs = self.data.groupby("Row").nth(2)
        else:
            print("Invalid input. Please use only 'capture', '1st-scatter', or '2nd-scatter'.")
            return

        self.coords = {
            "x" : locs["trackPosX"] - locs["mcx"],
            "y" : locs["trackPosY"] - locs["mcy"],
            "z" : locs["trackPosZ"] - locs["mcz"]
        }

        return


    ################################################################
    def neutronHistogram(self, save=False):
        if self.debug:
            print("DataProcessor class method: neutronHistogram")

        # Calculate the Euclidean distance between the neutron event location and MC truth location.
        distances = np.sqrt((self.coords["x"])**2 + (self.coords["y"])**2 + (self.coords["z"])**2)
        
        mean = sum(distances) / len(distances)
        print(f"Mean neutron ({self.kind}) track length:", mean)

        # Plots histogram.
        hist = plt.hist(distances, bins=64, color="orange", histtype="step")

        plt.xlabel("$d_n$ (mm)")
        plt.ylabel("Count")
        
        plt.title(f"Neutron ({self.kind.replace('-', ' ')}) track length histogram")
        
        if save:
            plt.savefig(f"neutron_histogram_{self.kind}.pdf", format="pdf", bbox_inches="tight")

        plt.show()

        return

    ################################################################
    def positronHistogram(self, save=False):
        if self.debug:
            print("DataProcessor class method: positronHistogram")

        if self.positronFile == None:
            print("No positron file defined...")
            return

        # Get the last row (annihilation location) of each event.
        locs = self.positron_data.groupby("Row").last()

        pl = len(locs)

        neu_locs = self.data.groupby("Row").last()

        px_coords = locs["trackPosX"] - neu_locs["mcx"]
        py_coords = locs["trackPosY"] - neu_locs["mcy"]
        pz_coords = locs["trackPosZ"] - neu_locs["mcz"]

        # Calculate the Euclidean distance between the neutron event location and MC truth location.
        distances = np.sqrt((px_coords)**2 + (py_coords)**2 + (pz_coords)**2)
        
        mean = sum(distances) / len(distances)
        print(f"Mean positron track length:", mean)

        # Plots histogram.
        hist = plt.hist(distances, bins=512, color="red", histtype="step")

        plt.xlim(0, 50)

        plt.xlabel("$d_+$ (mm)")
        plt.ylabel("Count")
        
        plt.title(f"Positron track length histogram")
        
        if save:
            plt.savefig(f"positron_histogram.pdf", format="pdf", bbox_inches="tight")

        plt.show()

        return

    ################################################################
    def binEvents(self, theta, plot=False):
        if self.debug:
            print("DataProcessor class method: binEvents")

        seg = copy.deepcopy(self.seg)

        locs = self.data.groupby("Row").last()

        x_coords = locs["trackPosX"] - locs["mcx"]
        y_coords = locs["trackPosY"] - locs["mcy"]
        z_coords = locs["trackPosZ"] - locs["mcz"]

        for x, y, z in zip(x_coords, y_coords, z_coords):

            # Generate a random point in the center square segment.
            xrand = random.uniform(-self.cube_size / 2.0, self.cube_size / 2.0)
            yrand = random.uniform(-self.cube_size / 2.0, self.cube_size / 2.0)

            # Distance calculation in 2d.
            r = np.sqrt(x**2 + y**2)

            # Initial angle of capture.
            theta0 = np.arctan2(y, x)

            # Rotation calculation.
            phi = theta * np.pi / 180.0

            # Coordinate transformation.
            xprime = r * np.cos(theta0 - phi)
            yprime = r * np.sin(theta0 - phi)

            # Randomizes the rotated event in the center square segment.
            xc = xprime + xrand
            yc = yprime + yrand

            if plot:
                plt.plot([xrand], [yrand], "k.", label="IBD vertex")
                plt.plot([x + xrand], [y + yrand], "r.", label="Event +x-dir")
                plt.plot([xc], [yc], "b.", label="Rotated event")
                plt.xlim(-self.half_size, self.half_size)
                plt.ylim(-self.half_size, self.half_size)
                for i in range(1, self.grid_size):
                        plt.axvline(i * self.cube_size - self.half_size)
                        plt.axhline(i * self.cube_size - self.half_size)
                plt.gca().set_aspect("equal")
                plt.title(f"event={event}, rot={theta}")
                plt.xlabel("x (mm)")
                plt.ylabel("y (mm)")
                plt.legend()
                plt.show()

            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    s = seg[i][j]
                    
                    if (s["xbounds"][0] < xc) and (xc < s["xbounds"][1]) and \
                       (s["ybounds"][0] < yc) and (yc < s["ybounds"][1]):
                        s["counts"] += 1
                        
        caps = np.zeros((self.grid_size, self.grid_size), dtype=int)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                caps[i][j] = seg[i][j]["counts"]

        return caps

    ################################################################
    def printBinDists(self, theta_range=[0, 45], plot=False, save=False):
        if self.debug:
            print("DataProcessor class method: printBinDists")

        print("Segmentation:", self.seg)

        if save:
            f = open("bin_dists.txt", "w")

        for theta in range(theta_range[0], theta_range[1]+1):
            caps = self.binEvents(theta, plot=plot)
            print(f"theta = {theta} deg")
            print(caps)

            if save:
                f.write(f"Angle: {theta} deg\n")
                f.write(str(caps) + "\n")

        if save:
            f.close()
                    
        return

    ################################################################
    def binDistColormap(self, theta, plot_cmap=True, plot=False, save=False):
        if self.debug:
            print("DataProcessor class method: binDistColormap")

        print("Segmentation:", self.seg)

        caps = self.binEvents(theta)

        ext_low  = -self.half_size
        ext_high =  self.half_size

        im = plt.imshow(caps, cmap="viridis", extent=(ext_low, ext_high, ext_low, ext_high))


        plt.title(f"Bin distribution colormap (theta={theta} deg, 10k events)")

        cmax = 1000
        
        cbar = plt.colorbar(im)
        cbar.set_label("Counts")
        plt.xlabel("x (mm)")
        plt.ylabel("y (mm)")
        im.set_clim(0, cmax)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                text = plt.text((j-np.floor((self.grid_size / 2.0)))*self.cube_size, -(i-np.floor((self.grid_size / 2.0)))*self.cube_size, f"{int(caps[i, j])}", 
                                ha="center", va="center", color=("w" if int(caps[i, j]) <= 0.6 * cmax else "k"))

        if save:
            plt.savefig(f"bin_dist_cmap_{theta}deg.pdf", format="pdf")

        plt.show()
                    
        return

    ################################################################
    def angularDist(self, save=False):
        """
        Usage: save - Use True to save figure as PDF.
        """
        if self.debug:
            print("DataProcessor class method: angularDist")

        theta_dist = []

        for x, y, z in zip(self.coords["x"], self.coords["y"], self.coords["z"]):

            # Initial angle of capture.
            theta = np.arctan2(y, x)

            theta_dist.append(theta)
            
        # Create the figure and polar axes
        fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

        # Create the polar histogram.
        hist = ax.hist(theta_dist, bins=np.linspace(-np.pi, np.pi, 37), edgecolor="blue", color="white", linewidth=2, bottom=0)
        
        print(hist[0])

        max_theta = max(hist[0])

        hole_rad = 0.8 * max_theta

        plt.gca().set_yticklabels([])
        plt.gca().yaxis.set_major_locator(MaxNLocator(nbins=5))
        
        ax.set_rorigin(-hole_rad)

        ax.set_ylim(0, max_theta + 0.1 * max_theta)
        ax.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2], ["0", "$\\pi/2$","$\\pi$","$3\\pi/2$"])

        plt.text(0, -hole_rad, self.kind.replace("-", " "), ha="center", va="center")
        if save:
            plt.savefig(f"polar_hist_{self.kind}.pdf", format="pdf", bbox_inches="tight")

        plt.show()
        
        return

    ################################################################
    def cloudPlot(self, save=False):
        """
        Usage: save - Use True to save figure as PDF.
        """
        if self.debug:
            print("DataProcessor class method: angularDist")
            
        # Create the figure and polar axes
        fig = plt.figure()
        ax = fig.add_subplot()

        ax.set_title(self.kind.replace("-", " "))

        ax.plot(self.coords["x"], self.coords["y"], ".", markersize=1)

        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")

        l = (100 if self.kind == "capture" else 20)
            
        ax.set_xlim(-l, l)
        ax.set_ylim(-l, l)

        ax.set_aspect("equal")
        
        if save:
            plt.savefig(f"cloud_plot_{self.kind}.pdf", format="pdf", bbox_inches="tight")

        plt.show()
                    
        return


    ################################################################
    def dimDist(self, dim, save=False):
        """
        Usage: dim can be either 'x', 'y', or 'z'
        """
        if self.debug:
            print("DataProcessor class method: dimDist")

        plt.hist(self.coords[dim], bins=128, histtype="step")            
        plt.grid()
        plt.title(f"{dim}-location histogram ({self.kind.replace('-', ' ')})")
        plt.xlabel(f"{self.kind} - vertex (mm)")
        plt.ylabel("Counts")
        plt.show()
        
        return
    
    ################################################################
    def gaussian(self, x, amplitude, mean, stddev):
        return amplitude * np.exp(-((x - mean) / stddev)**2 / 2)
    
    ################################################################
    def abs_sin(self, x, amplitude, freq, offset):
        return amplitude * np.abs(np.sin(freq * (x - offset)))

    ################################################################
    def frobeniusNormAnalysis(self, save=False):
        if self.debug:
            print("DataProcessor class method: frobeniusNormAnalysis")

        ### PARAMETERS ###
        # Simulation parameters. The variable 'ref_angle' is the angle of the reference dataset. The variable 'data_range' is the angular range on either side of the reference angle to test. the range of the simulation is ref_data +/- data_range.
        ref_angle = 45
        data_range = 180

        # Range of the data (ref_data +/- fit_range) to use. Minor bug: maximum value for this variable is data_range - 1.
        fit_range = 179

        ### INITIALIZATION ###
        # Find center diagonal element of segmentation array. Used to zero center segment if necessary.
        center_elem = int(np.floor(self.grid_size / 2.0))

        # Creates a reference dataset at a rotation of 'ref_angle' degrees.
        ref_data = self.binEvents(theta=ref_angle)

        # Creates range of angles to test using 'ref_angle' and 'data_range' variables.
        trange = [ref_angle - data_range, ref_angle + data_range]

        # Zero out center element (prompt segment).
        #ref_data[cent, cent] = 0

        print(f"Grid geometry: ({self.grid_size} x {self.grid_size})")
        print(f"Size of segment: {self.cube_size} mm")
        print("Reference dataset:")
        print(ref_data)

        # Normalizes array to prepare for Frobenius norm calculation.
        ref_data = ref_data / np.sum(ref_data)

        ### FROBENIUS NORM ###
        angles = []
        norms = []
        # Loops through discrete range of angles and creates bin distribution.
        for t in tqdm(range(trange[0], trange[1]+1), desc="Calculating Frobenius norms"):
            caps = self.binEvents(theta=t)

            # Zero out center element (prompt segment).
            #caps[cent, cent] = 0

            # Normalizes and flattens bin distributions and compares them with the reference dataset with the Frobenius norm of the difference.
            caps = caps / np.sum(caps)

            f_norm = np.sqrt(np.sum(np.square(ref_data - caps)))

            angles.append(t)
            norms.append(f_norm)

        # Find best angle (minimum Frobenius norm of difference) in data.
        best_angle = angles[np.argmin(norms)]

        ### GAUSSIAN FIT ###
        # Requirements for appropriate Gaussian fit.
        y_shift = np.max(norms)
        fit_norms = np.array([(y_shift - fn) for fn in norms])

        # Careful: assumes ref_angle is within t_range!!!
        fit_angles = angles[(ref_angle - trange[0] - fit_range):-(trange[1] - ref_angle - fit_range)]
        fit_norms = fit_norms[(ref_angle - trange[0] - fit_range):-(trange[1] - ref_angle - fit_range)]

        # Perform Gaussian fit.
        popt, pcov = curve_fit(self.gaussian, fit_angles, fit_norms, p0=[np.max(fit_norms), ref_angle, 1])
        y_fit = self.gaussian(fit_angles, popt[0], popt[1], popt[2])

        # Calculates statistical uncertainty in theta.
        delta_theta = popt[2] / np.sqrt(len(fit_angles))

        print("Gaussian fit:", popt)
        print("Uncertainty (theta):", delta_theta)

        ### SINE FIT ###
        # Setup |sin(x)| fit.
        sin_y_shift = np.min(norms)
        sin_fit_norms = np.array([(fn - sin_y_shift) for fn in norms])

        # Careful: assumes ref_angle is within t_range!!!
        sin_fit_angles = angles[(ref_angle - trange[0] - fit_range):-(trange[1] - ref_angle - fit_range)]
        sin_fit_norms = sin_fit_norms[(ref_angle - trange[0] - fit_range):-(trange[1] - ref_angle - fit_range)]

        # Perform sine fit.
        sin_popt, sin_pcov = curve_fit(self.abs_sin, sin_fit_angles, sin_fit_norms, p0=[np.max(sin_fit_norms), np.pi/360.0, ref_angle])
        sin_y_fit = self.abs_sin(sin_fit_angles, sin_popt[0], sin_popt[1], sin_popt[2])

        print("Sine fit:", sin_popt)

        fig_width = 10.5
        fig_height = 7.3
        plt.figure(figsize=(fig_width, fig_height))
        
        ### PLOT DATA ###
        # Create analysis plot.
        plt.plot(sin_fit_angles, [y + sin_y_shift for y in sin_y_fit], color="red", label=f"$|\\sin\\vartheta|$ fit (${round(sin_popt[2], 2)}" + "^\\circ$)")
        plt.plot(fit_angles, [y_shift - y for y in y_fit], "-", color="green", label=f"Gaussian (${round(popt[1],2)}\\pm{round(delta_theta, 2)}" + "^\\circ$)")
        plt.plot(angles, norms, "b.", label="Frobenius norm", alpha=0.3)
        plt.axvline(ref_angle, linestyle="--", color="gray")
        plt.xlabel("$\\vartheta$ (${}^\\circ$)")
        plt.ylabel("Frobenius norm of difference")
        plt.legend(loc="upper left")

        plt.text(ref_angle + 5, 0.95 * y_shift, f"$\\vartheta = {ref_angle}"+"^\\circ$")

        if save:
            plt.savefig(f"fn_analysis_plot.pdf", format="pdf", bbox_inches="tight")

        plt.show() 
                    
        return

    ################################################################
    def testVectorSum(self):
        if self.debug:
            print("DataProcessor class method: testVectorSum")

        # Find center diag element of segmentation array.
        cent = int(np.floor(self.grid_size / 2.0))

        # Creates a reference dataset at a rotation of 'ref_angle' degrees.
        ref_angle = 35
        ref_data = self.binEvents(theta=ref_angle)

        x_ref = np.cos(ref_angle * np.pi / 180.0)
        y_ref = -np.sin(ref_angle * np.pi / 180.0)

        print(self.seg)
        print(ref_data)

        x_coord = 0
        y_coord = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x_cent = (self.seg[i, j]["xbounds"][0] + self.seg[i, j]["xbounds"][1] ) / 2.0
                y_cent = (self.seg[i, j]["ybounds"][0] + self.seg[i, j]["ybounds"][1] ) / 2.0
                print(i, j, self.seg[i, j], ref_data[i, j], x_cent, y_cent)

                x_coord += ref_data[i, j] * x_cent
                y_coord += ref_data[i, j] * y_cent


        x_unit = x_coord / np.sqrt(x_coord**2 + y_coord**2)
        y_unit = y_coord / np.sqrt(x_coord**2 + y_coord**2)
        
        print(x_unit, y_unit)

        # Find center diag element of segmentation array.
        cent = int(np.floor(self.grid_size / 2.0))

        # Creates a reference dataset at a rotation of 'ref_angle' degrees.
        ref_angle = 45
        ref_data = self.binEvents(theta=ref_angle)

        trange = [ref_angle, ref_angle + 360]


        # Zero out center element (prompt segment).
        #ref_data[cent, cent] = 0

        print(f"Grid size: ({self.grid_size} x {self.grid_size}), {self.cube_size} mm")
        print(ref_data)


        ##### Compare to Frobenius norm....
        # Normalizes array to prepare for Frobenius norm calculation.
        ref_data = ref_data / np.sum(ref_data)
        #ref_data = ref_data / np.linalg.det(ref_data)

        angles = []
        norms = []
        # Loops through discrete range of angles and creates bin distribution.
        for t in tqdm(range(trange[0], trange[1]+1)):
            caps = self.binEvents(theta=t)

            # Zero out center element (prompt segment).
            #caps[cent, cent] = 0

            # Normalizes and flattens bin distributions and compares them with the reference dataset with the Frobenius norm of the difference.
            caps = caps / np.sum(caps)
            #caps = caps / np.linalg.det(caps)

            f_norm = np.sqrt(np.sum(np.square(ref_data - caps)))
            #f_norm = np.abs(np.linalg.det(ref_data) -np.linalg.det(caps))

            #print("==============================================")
            #print(t, sum(sum(caps)), caps)
            #print(f"{t} deg. -- Frobenius norm: {f_norm}")
            angles.append(t)
            norms.append(f_norm)

        # Find best angle in data.
        best_angle = angles[np.argmin(norms)]

        x_fn = np.cos(best_angle * np.pi / 180.0)
        y_fn = -np.sin(best_angle * np.pi / 180.0)



        plt.arrow(0, 0, x_ref, y_ref, color="black", length_includes_head=True,
                  head_width=0.05, head_length=0.05)
        plt.arrow(0, 0, x_unit, y_unit, color="red", length_includes_head=True,
                  head_width=0.05, head_length=0.05)
        plt.arrow(0, 0, x_ref, y_ref, color="green", length_includes_head=True,
                  head_width=0.05, head_length=0.05)
        plt.xlim(-1, 1)
        plt.ylim(-1, 1)
        plt.show()

        return

    ################################################################
    def testNormalDist(self):
        if self.debug:
            print("DataProcessor class method: testNormalDist")

        # Parameters
        mu = 5.0       # Mean (center)
        sigma = 1.0    # Standard deviation
        num_points = 1000  # Total number of points (must be even)
        
        # Generate half of the points normally
        half_points = num_points // 2
        x_half = np.random.normal(mu, sigma, half_points)
        
        # Create a mirrored version of these points
        x_mirrored = 2 * mu - x_half  # Reflect across mu
        
        # Combine to get a symmetrical distribution
        x_coords = np.concatenate((x_half, x_mirrored))
        
        # Plot the symmetrical Gaussian distribution
        plt.hist(x_half, bins=30, density=True, alpha=0.6, color="b", edgecolor="black")
        plt.axvline(mu, color="r", linestyle="dashed", linewidth=2, label=f"Mean ({mu})")
        plt.xlabel("x-coordinate")
        plt.ylabel("Density")
        plt.title("Symmetrical Gaussian Distribution of x-coordinates")
        plt.legend()
        plt.show()
            
        return

    ################################################################
    def testPoissonDist(self):
        if self.debug:
            print("DataProcessor class method: testPoissonDist")

        # Example data
        data = np.random.poisson(5, 1000)

        # Fit the Poisson distribution
        mu = np.mean(data)  # Estimate lambda (rate parameter) from the data
        dist = poisson(mu)

        # Plot the histogram of the data and the fitted Poisson distribution
        plt.hist(data, bins=np.arange(data.max() + 2) - 0.5, density=True, alpha=0.5, label="Data")
        x = np.arange(0, data.max() + 1)
        plt.plot(x, dist.pmf(x), "ro-", label="Fitted Poisson")
        plt.xlabel("Number of Events")
        plt.ylabel("Probability")
        plt.legend()
        plt.show()

        return

    ################################################################
    def binEventsSimLoop(self, rot=0):
        if self.debug:
            print("DataProcessor class method: binEventsSimLoop")

        self.initGrid()

        for x, y in zip(self.x_coords_sim, self.y_coords_sim):

            # Distance calculation in 2d.
            r = np.sqrt(x**2 + y**2)

            # Initial angle of capture.
            theta = np.arctan2(y, x)

            # Rotation calculation.
            phi = rot * np.pi / 180.0

            # Coordinate transformation.
            xprime = r * np.cos(theta - phi)
            yprime = r * np.sin(theta - phi)

            # Randomizes the rotated event in the center square segment.
            xc = xprime
            yc = yprime

            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    s = self.seg[i][j]
                    
                    if (s["xbounds"][0] < xc) and (xc < s["xbounds"][1]) and \
                       (s["ybounds"][0] < yc) and (yc < s["ybounds"][1]):
                        s["counts"] += 1
                        
        caps = np.zeros((self.grid_size, self.grid_size), dtype=int)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                caps[i][j] = self.seg[i][j]["counts"]

        return caps
    
    ################################################################
    def frobeniusNormAnalysisSim(self, save=False):
        if self.debug:
            print("DataProcessor class method: frobeniusNormAnalysisSim")

        ### PARAMETERS ###
        # Simulation parameters. The variable 'ref_angle' is the angle of the reference dataset. The variable 'data_range' is the angular range on either side of the reference angle to test. the range of the simulation is ref_data +/- data_range.
        ref_angle = 0
        data_range = 180

        # Range of the data (ref_data +/- fit_range) to use. Minor bug: maximum value for this variable is data_range - 1.
        fit_range = 179

        # Creates a reference dataset at a rotation of 'ref_angle' degrees.
        ref_data = self.binEventsSimLoop(rot=ref_angle)

        # Creates range of angles to test using 'ref_angle' and 'data_range' variables.
        trange = [ref_angle - data_range, ref_angle + data_range]

        print(f"Grid geometry: ({self.grid_size} x {self.grid_size})")
        print(f"Size of segment: {self.cube_size} mm")
        print("Reference dataset:")
        print(ref_data)

        #ref_data_backup = ref_data

        # Normalizes array to prepare for Frobenius norm calculation.
        ref_data = ref_data / np.sum(ref_data)

        ### FROBENIUS NORM ###
        angles = []
        norms = []
        # Loops through discrete range of angles and creates bin distribution.
        for t in tqdm(range(trange[0], trange[1]+1), desc="Calculating Frobenius norms"):
            caps = self.binEventsSimLoop(rot=t)

            # Normalizes and flattens bin distributions and compares them with the reference dataset with the Frobenius norm of the difference.
            caps = caps / np.sum(caps)

            f_norm = np.sqrt(np.sum(np.square(ref_data - caps)))

            angles.append(t)
            norms.append(f_norm)

        ### GAUSSIAN FIT ###
        # Requirements for appropriate Gaussian fit.
        y_shift = np.max(norms)
        fit_norms = np.array([(y_shift - fn) for fn in norms])

        # Careful: assumes ref_angle is within t_range!!!
        fit_angles = angles[(ref_angle - trange[0] - fit_range):-(trange[1] - ref_angle - fit_range)]
        fit_norms = fit_norms[(ref_angle - trange[0] - fit_range):-(trange[1] - ref_angle - fit_range)]

        # Perform Gaussian fit.
        popt, pcov = curve_fit(self.gaussian, fit_angles, fit_norms, p0=[np.max(fit_norms), ref_angle, 1])
        y_fit = self.gaussian(fit_angles, popt[0], popt[1], popt[2])

        # Calculates statistical uncertainty in theta.
        delta_theta = popt[2] / np.sqrt(len(fit_angles))

        print("Gaussian fit:", popt)
        print("Uncertainty (theta):", delta_theta)

        ### SINE FIT ###
        # Setup |sin(x)| fit.
        sin_y_shift = np.min(norms)
        sin_fit_norms = np.array([(fn - sin_y_shift) for fn in norms])

        # Careful: assumes ref_angle is within t_range!!!
        sin_fit_angles = angles[(ref_angle - trange[0] - fit_range):-(trange[1] - ref_angle - fit_range)]
        sin_fit_norms = sin_fit_norms[(ref_angle - trange[0] - fit_range):-(trange[1] - ref_angle - fit_range)]

        # Perform sine fit.
        sin_popt, sin_pcov = curve_fit(self.abs_sin, sin_fit_angles, sin_fit_norms, p0=[np.max(sin_fit_norms), np.pi/360.0, ref_angle])
        sin_y_fit = self.abs_sin(sin_fit_angles, sin_popt[0], sin_popt[1], sin_popt[2])

        print("Sine fit:", sin_popt)
        
        ### PLOT DATA ###
        # Create analysis plot.
        plt.plot(sin_fit_angles, [y + sin_y_shift for y in sin_y_fit], color="red")
        plt.plot(fit_angles, [y_shift - y for y in y_fit], "-", color="green")
        plt.plot(angles, norms, "b.", alpha=0.5)
        plt.axvline(ref_angle, linestyle="--", color="gray")
        plt.xlabel("$\\vartheta$ (${}^\\circ$)")
        plt.ylabel("Frobenius norm of difference")

        if save:
            plt.savefig(f"test_fn_sim_mux{self.mux}.pdf", format="pdf", bbox_inches="tight")
        
        plt.show()
                    
        return

    def sym_2d_norm_dist(self, x, y, theta, sigma, r):
        norm_fac = 1 / (2 * np.pi * sigma**2)
        return norm_fac * np.exp(-(x**2 + y**2 + r**2) / (2 * sigma**2)) * np.exp(-(r * (x * np.cos(theta) + y * np.sin(theta))) / (sigma**2))

    def sym_2d_norm_dist_diff(self, x, y, theta_ref, theta_rot, sigma, r):
        theta_ref *= np.pi / 180.0
        theta_rot *= np.pi / 180.0
        return ( self.sym_2d_norm_dist(x, y, theta_ref, sigma, r) - self.sym_2d_norm_dist(x, y, theta_rot, sigma, r) )**2

    ################################################################
    def continuousFrobeniusNorm(self, save=False):
        if self.debug:
            print("DataProcessor class method: continuousFrobeniusNorm")

        ref_angle = 0

        sigma = 50
        r = 0.0001

        x_min, x_max = -100, 100  # Limits for x
        y_min, y_max = -100, 100  # Limits for y
        
        grid_size_sim = 20

        # Test plot.
        # Create a grid of x and y values
        x = np.linspace(x_min, x_max, grid_size_sim)  # 100 points from x_min to x_max
        y = np.linspace(y_min, y_max, grid_size_sim)  # 100 points from y_min to y_max
        X, Y = np.meshgrid(x, y)     # Create a 2D grid
        Z = self.sym_2d_norm_dist_diff(X, Y, 0, 45, sigma, r)               # Compute function values on the grid
        
        # Plot the data
        plt.imshow(Z, cmap='viridis')
        plt.colorbar(label='Function Value')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('2D Function Grid')
        plt.show()

        

        # Perform the double integrals.
        angles = []
        norms = []
        discrete_norms = []
        for theta in range(ref_angle-180, ref_angle+180, 1):

            Z1 = self.sym_2d_norm_dist(X, Y, ref_angle * np.pi / 180, sigma, r)
            Z1 = Z1 / np.sum(Z1)
            Z2 = self.sym_2d_norm_dist(X, Y, theta * np.pi / 180, sigma, r)
            Z2 = Z2 / np.sum(Z2)

            dfnd = np.sqrt(np.sum(np.square(Z1 - Z2)))
            discrete_norms.append(dfnd)

            
            result, error = spi.dblquad(self.sym_2d_norm_dist_diff, x_min, x_max, lambda x: y_min, lambda x: y_max, args=(ref_angle, theta, sigma, r,))
            CFN = np.sqrt(result)
            
            #print(theta, CFN, dfnd)
            
            angles.append(theta)
            norms.append(CFN)


        # Perform sine fit.
        sin_popt, sin_pcov = curve_fit(self.abs_sin, angles, norms, p0=[np.max(norms), np.pi/360.0, ref_angle])
        sin_y_fit = self.abs_sin(angles, sin_popt[0], sin_popt[1], sin_popt[2])


        plt.plot(angles, np.array(norms) / max(norms), ".", color="m", label="Simulation data")
        plt.plot(angles, np.array(discrete_norms) / max(discrete_norms), ".", color="b", label="Discrete sim. data")
        plt.plot(angles, np.array(sin_y_fit) / max(sin_y_fit), color="lightgreen", label="Sine fit")
        plt.xlabel("$\\vartheta$ (${}^\\circ$)")
        plt.ylabel("CFND")
        plt.grid()
        plt.legend()

        if save:
            plt.savefig(f"cfnd.pdf", format="pdf", bbox_inches="tight")

        plt.show()

        return

    ################################################################
    def plotTracks3D(self, event, view=(90, 270, 0), save=False):
        if self.debug:
            print("DataProcessor class method: plotTracks3D")

        if self.positronFile == None:
            print("No positron file defined...")
            return


        pos_event = self.positron_data[self.positron_data["Row"] == event]
        neu_event = self.data[self.data["Row"] == event]

        mcx_data = neu_event["mcx"]
        mcy_data = neu_event["mcy"]
        mcz_data = neu_event["mcz"]

        mcx = mcx_data.iloc[0]
        mcy = mcy_data.iloc[0]
        mcz = mcz_data.iloc[0]

        pl = len(pos_event)
        nl = len(neu_event)

        pos_x_data = pos_event["trackPosX"] - np.full(pl, mcx)
        pos_y_data = pos_event["trackPosY"] - np.full(pl, mcy)
        pos_z_data = pos_event["trackPosZ"] - np.full(pl, mcz)

        neu_x_data = neu_event["trackPosX"] - mcx_data
        neu_y_data = neu_event["trackPosY"] - mcy_data
        neu_z_data = neu_event["trackPosZ"] - mcz_data

        print("Plotting 3d track data...")
        # Show the newly created dictionary (track data). Plots the provided event number.
        fig = plt.figure()
        ax = plt.axes(projection="3d")

        # initializes with a top-view perspective.
        ax.view_init(view[0], view[1], view[2])

        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
        ax.set_zlabel("z (mm)")
    
        ax.plot3D(neu_x_data, neu_y_data, neu_z_data, color="orange", label="Neutron")
        ax.plot3D(pos_x_data, pos_y_data, pos_z_data, color="red", label="Positron")

        ax.scatter(0, 0, 0, color="black", label="IBD vertex")
        ax.scatter(neu_x_data.iloc[nl-1], neu_y_data.iloc[nl-1], neu_z_data.iloc[nl-1], marker="x", color="orange", label="Capture")
        ax.scatter(pos_x_data.iloc[pl-1], pos_y_data.iloc[pl-1], pos_z_data.iloc[pl-1], marker="x", color="red", label="Annihilation")

        #plt.legend(loc="upper left")

        if save:
            plt.savefig("track_plot_3d.pdf", format="pdf", bbox_inches="tight")

        plt.show()

        print("Done!")

        return

    ################################################################
    def plotTracks2D(self, event, save=False):
        if self.debug:
            print("DataProcessor class method: plotTracks2D")

        if self.positronFile == None:
            print("No positron file defined...")
            return

        pos_event = self.positron_data[self.positron_data["Row"] == event]
        neu_event = self.data[self.data["Row"] == event]

        mcx_data = neu_event["mcx"]
        mcy_data = neu_event["mcy"]

        mcx = mcx_data.iloc[0]
        mcy = mcy_data.iloc[0]

        pl = len(pos_event)
        nl = len(neu_event)

        pos_x_data = pos_event["trackPosX"] - np.full(pl, mcx)
        pos_y_data = pos_event["trackPosY"] - np.full(pl, mcy)

        neu_x_data = neu_event["trackPosX"] - mcx_data
        neu_y_data = neu_event["trackPosY"] - mcy_data

        print("Plotting 2d track data...")
        # Show the newly created dictionary (track data). Plots the provided event number.
        fig = plt.figure()
        ax = plt.axes()

        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
    
        ax.plot(neu_x_data, neu_y_data, color="orange", label="Neutron")
        ax.plot(pos_x_data, pos_y_data, color="red", label="Positron")

        ax.scatter(0, 0, color="black", label="IBD vertex")
        ax.scatter(neu_x_data.iloc[nl-1], neu_y_data.iloc[nl-1], marker="x", color="orange", label="Capture")
        ax.scatter(pos_x_data.iloc[pl-1], pos_y_data.iloc[pl-1], marker="x", color="red", label="Annihilation")

        #plt.legend(loc="upper left")

        if save:
            plt.savefig("track_plot_2d.pdf", format="pdf", bbox_inches="tight")

        plt.show()

        print("Done!")

        return


################################################################
################################################################
################################################################
if __name__ == "__main__":
    """
    This is the main statement where the user can execute subroutines to produce figures.
    """
    proc = DataProcessor()

    #proc.setKind("2nd-scatter")

    #proc.neutronHistogram(save=False)

    #print(proc.binEvents(theta=180, plot=False))

    #proc.printBinDists()

    #proc.binDistColormap(45)

    #proc.setKind("1st-scatter")
    #proc.angularDist(save=False)

    #proc.setKind("capture")
    #proc.angularDist(save=False)

    #proc.setKind("1st-scatter")
    #proc.cloudPlot(save=False)
    
    proc.setKind("capture")
    proc.cloudPlot(save=True)

    #proc.setKind("capture")

    #proc.dimDist("x", save=False)
    #proc.dimDist("y", save=False)
    #proc.dimDist("z", save=False)

    #proc.frobeniusNormAnalysis()

    #proc.plotTracks3D(0)
    #proc.plotTracks3D(255, view=[20,225,0], save=False)

    #proc.plotTracks2D(255, save=False)

    #proc.positronHistogram(save=False)

    sys.exit()
        
