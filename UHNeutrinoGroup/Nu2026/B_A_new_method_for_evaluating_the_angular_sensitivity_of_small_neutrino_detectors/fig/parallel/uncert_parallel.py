import os
import re
import sys
import time
import random
import json
import math
from tqdm import tqdm
import copy
import subprocess

from scipy.stats import poisson
from scipy.special import gamma
from scipy.optimize import curve_fit
import scipy.integrate as spi
from scipy.stats import vonmises

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.stats import multivariate_normal
from scipy.special import i0, i1
from scipy.special import i0e, i1e

from mpi4py import MPI

class DataProcessor():
    def __init__(self):

        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()

        # Control flags.
        self.debug = False
        self.latex = True
        
        if self.debug:
            print("DataProcessor class method: __init__")

        if self.latex:
            plt.rc("font", family="serif", size = 18)
            #plt.rc("font", family="serif", size = 19)
            #plt.rc("font", family="serif", size = 24)
            #plt.rc("font", family="serif", size = 44)
            plt.rcParams["text.usetex"] = True
            plt.rcParams["mathtext.fontset"] = "cm" # computer modern

        self.iterations = 1024

        # Initialization variables for 2d square grid segmentation of size (self.grid_size x self.grid_size). This variable represents the number of squares on a side of the grid. Must be an odd number so that there is a clearly defined center segment for prompt.
        self.grid_size = 91 # Has to be odd to simulate IBD physics, self.seg_size measured in mm
        self.seg_size = 5 # mm

        # Angle in degrees.
        self.true_angle = 0
        #self.mu = 2
        self.mu = 16.7 # RATPAC 2 centroid (mm)

        # Simulation parameters.
        self.mu_x = self.mu * np.cos(self.true_angle * np.pi / 180.0) # Mean (center of dist in x)
        self.mu_y = self.mu * np.sin(self.true_angle * np.pi / 180.0) # Mean (center of dist in y)

        #self.mu = np.sqrt(self.mu_x**2 + self.mu_y**2)
        
        #self.sigma = 10   # Standard deviation
        self.sigma = 39.3   # Standard deviation of RATPAC 2 neutron capture distribution (mm)
        self.n = 100     # Number of points

        self.l = (self.seg_size * self.grid_size) / 2.0

        self.mean = [self.mu_x, self.mu_y]  # Mean of the Gaussian distribution
        self.cov = [[self.sigma**2, 0], [0, self.sigma**2]]  # Covariance matrix

        # Define binning range
        self.x_range = (-self.l, self.l)
        self.y_range = (-self.l, self.l)

        # Create a 2D histogram with binned data over a specific range
        if self.rank == 0:
            
            if "true.npy" not in os.listdir():
                data_true = np.random.multivariate_normal(self.mean, self.cov, self.n)
                np.save("true.npy", data_true)
            else:
                data_true = np.load("true.npy")
                
            x_true, y_true = data_true[:, 0], data_true[:, 1]
            self.true, xedges_true, yedges_true = np.histogram2d(y_true, x_true, bins=self.grid_size, range=[self.x_range, self.y_range])

            #print(type(self.true), type(data_true))
            #print(self.true)

            # Uncomment to add extra fitting step.
            #_, self.true = self.perform2DFit(self.true)
            
        else:
            self.true = None # distribution to all cores here

        self.true = self.comm.bcast(self.true, root=0)
        #print(self.rank, self.true)

        self.all_angles = np.arange(-180, 180)

        self.angles = np.array_split(self.all_angles, self.size)[self.rank].tolist()
        #print(self.rank, self.angles)

        print(f"Initialized rank {self.rank}. Allocated theta = [{self.angles[0]}, {self.angles[-1]}]")

        return

    def abs_sine(self, theta, theta0, amp, y_offset):
        return amp * np.abs(np.sin((theta - theta0) * np.pi / 180.0 / 2)) + y_offset

    def gaussian_2d(self, coords, A, mu_x, mu_y, sigma_x, sigma_y):
        x, y = coords
        return A * np.exp(-((x - mu_x)**2 / (2 * sigma_x**2) + (y - mu_y)**2 / (2 * sigma_y**2)))

    def rotateCoords(self, x_coords, y_coords, theta, plot=False):
        if self.debug:
            print("DataProcessor class method: rotateCoords")

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

        return x_rot, y_rot

    def wrap_angle(self, angle):
        """
        Wrap any angle in degrees to the range (-180, 180].
        """
        wrapped = ((angle + 180) % 360) - 180
        return wrapped

    def vonmises_circ_std(self, kappa):
        print(i1e(kappa), i0e(kappa))
        R = i1e(kappa) / i0e(kappa)
        sigma_rad = np.sqrt(-2 * np.log(R))
        sigma_deg = np.rad2deg(sigma_rad)
        return sigma_rad, sigma_deg

    def directionAlgorithmMethod(self):
        if self.debug:
            print("DataProcessor class method: directionAlgorithmMethod")

        if self.rank == 0:
            data = np.random.multivariate_normal([self.mu, 0], self.cov, self.n)
            x, y = data[:, 0], data[:, 1]
        else:
            x, y = None, None

        x = self.comm.bcast(x, root=0)
        y = self.comm.bcast(y, root=0)

        norms = []

        ref = self.true / np.sum(self.true)
        
        # Calculate FND of simulated data.
        #for theta in tqdm(self.angles):
        for theta in self.angles: #PARALLEL
            x_rot, y_rot = self.rotateCoords(x, y, theta)
            
            rot, xedges_rot, y_edges_rot = np.histogram2d(y_rot, x_rot, bins=self.grid_size, range=[self.x_range, self.y_range])

            # Uncomment to add extra fitting step.
            #_, rot = self.perform2DFit(rot)

            rot = rot / np.sum(rot)

            FND = np.sqrt(np.sum(np.square(ref - rot)))
            
            norms.append(FND)

        all_norms = self.comm.gather(norms, root=0)

        if self.rank == 0:
            # Stitch them together into a single list
            stitched_norms = [val for sublist in all_norms for val in sublist]
            #print("Final stitched norms array:", stitched_norms)
        
            popt, pcov = curve_fit(self.abs_sine, self.all_angles, stitched_norms, p0=[self.true_angle, 1, 0])

            #perr = np.sqrt(np.diag(pcov))

            """
            y_fit_data = self.abs_sine(self.all_angles, popt[0], popt[1], popt[2])
            plt.plot(self.all_angles, stitched_norms, "r.")
            plt.plot(self.all_angles, y_fit_data, "k-")
            plt.show()
            """

            return popt[0]
        else:
            return None
        
    def testUncertainty(self):

        if self.rank == 0:
            thetas = []
            pbar = tqdm(total=self.iterations, dynamic_ncols=True, file=sys.stdout, miniters=1, mininterval=0)

        for i in range(self.iterations):
            theta = self.directionAlgorithmMethod()

            if self.rank == 0:
                thetas.append(theta)

                print()
                pbar.update()

        if self.rank == 0:

            pbar.close()

            thetas = [self.wrap_angle(t) for t in thetas]

            angles_deg = thetas

            n_bins = 360

            hist, bin_edges = np.histogram(angles_deg, bins=n_bins, range=(-180, 180))
            bin_centers_deg = (bin_edges[:-1] + bin_edges[1:]) / 2
            bin_centers_rad = np.deg2rad(bin_centers_deg)

            expanded_data = np.repeat(bin_centers_rad, hist)
            kappa, loc, scale = vonmises.fit(expanded_data, fscale=1)

            # Evaluate fitted PDF
            theta = np.linspace(-np.pi, np.pi, 500)
            pdf = vonmises.pdf(theta, kappa, loc=loc)

            # Scale PDF to histogram counts
            pdf_scaled = pdf / pdf.max() * hist.max()

            # ---- Plot ----
            fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6,6))

            # Histogram (bars)
            ax.bar(bin_centers_rad, hist, width=2*np.pi/n_bins, bottom=0, alpha=0.6, color='C0', edgecolor='k')

            # Fitted curve
            ax.plot(theta, pdf_scaled, 'r-', lw=2, label=f'von Mises fit\n$\\mu={np.rad2deg(loc):.1f}^\\circ, \\kappa={kappa:.2f}$')

            # Formatting
            ax.set_theta_zero_location('N')  # 0° at top
            ax.set_theta_direction(-1)       # clockwise
            ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
            
            plt.show()

            """
            plt.hist(thetas, bins=128)

            plt.xlabel("Recontructed wrapped angle")
            plt.ylabel("Counts")
            plt.show()
            """

            sigma_rad, sigma_deg = self.vonmises_circ_std(kappa)
            
            np.save(f"data/data_iter_{self.iterations}_dx_{self.seg_size}_n_{self.n}.npy", np.array(thetas))

            f = open(f"data/func_iter_{self.iterations}_dx_{self.seg_size}.txt", "a")
            f.write(f"{self.n}\t{sigma_deg}\t{np.rad2deg(loc)}\n")
            f.close()                
            
        return

    def deleteTrueData(self):
        if self.rank == 0:
            subprocess.run(["rm", "true.npy"])

        return

################################################################
################################################################
################################################################
if __name__ == "__main__":
    """
    This is the main statement where the user can execute subroutines to produce figures.
    """
    proc = DataProcessor()

    #proc.directionAlgorithmMethod()

    proc.testUncertainty()
    proc.deleteTrueData()

    sys.exit()
