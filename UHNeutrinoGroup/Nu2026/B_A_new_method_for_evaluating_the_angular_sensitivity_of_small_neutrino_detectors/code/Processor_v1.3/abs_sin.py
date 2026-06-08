
import json
import os
import sys
import random
from tqdm import tqdm
from scipy.optimize import curve_fit

import numpy as np
import matplotlib.pyplot as plt

class DataProcessor():
    """
    RATPAC2 DataProcessor - Post processing methods for RATPAC2 positron and neutron output track data. This code produces figures for paper B using simulated data with RATPAC2.
    """
    ################################################################
    def __init__(self):
        self.debug = False

        self.latex = False

        
        if self.latex:
            plt.rc('font', family='serif', size = 18)
            plt.rcParams['text.usetex'] = True
            plt.rcParams['mathtext.fontset'] = 'cm' # computer modern


        if self.debug:
            print("DataProcessor class method: __init__")

        # Number of events to read and process from the RATPAC output. This is only used if the procData subroutine is called.
        self.N = 10000

        # Path to JSON file that either exists or shall be created by this script.
        self.jsonFile = "../data/run_new_macro.json"

        # This version of the code only requires one text file for neutron track data which includes the MC truth position of the IBD event (IBD vertex location).
        self.dataFile = "/Users/gabriel/Downloads/ibd_cube_005wt_new_macro_run1/data.txt"

        # Checks if the JSON file exists, otherwise processes RATPAC ASCII output and creates JSON file at specified path. Can either run readData or procData. Not necessary to run both consecutively.
        if os.path.isfile(self.jsonFile):
            self.readData()
        else:
            self.procData()

        # Initializes the 2d square grid geometry specified in initGrid subroutine.
        self.initGrid()

        return

    ################################################################
    def readData(self):
        if self.debug:
            print("DataProcessor class method: readData")

        print("Reading data from JSON file...")
        with open(self.jsonFile, "r") as f:
            
            # Load the dictionary from the file.
            self.data = json.load(f)
            f.close()

        print("Done!")
        #print(len(self.data))

        return 

    ################################################################
    def initGrid(self):
        if self.debug:
            print("DataProcessor class method: initGrid")

        # Initialization variables for 2d square grid segmentation of size (self.grid_size x self.grid_size). This variable represents the number of squares on a side of the grid. Must be an odd number so that there is a clearly defined center segment for prompt.
        self.grid_size = 5

        # Size of individual square segment in mm.
        #self.cube_size = 5
        self.cube_size = 50
        #self.cube_size = 150

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

                self.seg[i][j] = {"xbounds":[xlow, xhigh],
                                  "ybounds":[ylow, yhigh],
                                  "counts":0}

        return


    ################################################################
    def binEventsLoop(self, rot=0, PLOT=False):
        if self.debug:
            print("DataProcessor class method: binEventsLoop")

        self.initGrid()

        for event in list(self.data.keys()):

            # Extract coordinates from dictionary.
            xs, ys, zs = self.data[event]["vertex"]
            xn, yn, zn = self.data[event]["capture"]

            # Generate a random point in the center square segment.
            #xrand = random.uniform(-self.cube_size / 2.0, self.cube_size / 2.0)
            #yrand = random.uniform(-self.cube_size / 2.0, self.cube_size / 2.0)

            xrand = 0
            yrand = 0

            # Calculates the 2d component-wise distance between IBD vertex and capture.
            x = xn - xs
            y = yn - ys

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
            xc = xprime + xrand
            yc = yprime + yrand

            if PLOT:
                plt.plot([xrand], [yrand], "k.", label="IBD vertex")
                plt.plot([x + xrand], [y + yrand], "r.", label="Event +x-dir")
                plt.plot([xc], [yc], "b.", label="Rotated event")
                plt.xlim(-self.half_size, self.half_size)
                plt.ylim(-self.half_size, self.half_size)
                for i in range(1, self.grid_size):
                        plt.axvline(i * self.cube_size - self.half_size)
                        plt.axhline(i * self.cube_size - self.half_size)
                plt.gca().set_aspect("equal")
                plt.title(f"event={event}, rot={rot}")
                plt.xlabel("x (mm)")
                plt.ylabel("y (mm)")
                plt.legend()
                plt.show()

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
    def gaussian(self, x, amplitude, mean, stddev):
        return amplitude * np.exp(-((x - mean) / stddev)**2 / 2)
    ################################################################
    def abs_sin(self, x, amplitude, freq, offset):
        return amplitude * np.abs(np.sin(freq * (x - offset)))

    ################################################################
    def frobeniusNormAnalysis(self):
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
        ref_data = self.binEventsLoop(rot=ref_angle)

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
            caps = self.binEventsLoop(rot=t)

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
        
        ### PLOT DATA ###
        # Create analysis plot.
        plt.plot(sin_fit_angles, [y + sin_y_shift for y in sin_y_fit], color="red", label=f"Sine fit (${round(sin_popt[2], 3)}" + "^\circ$)")
        plt.plot(fit_angles, [y_shift - y for y in y_fit], "-", color="green", label=f"Gaussian fit (${round(popt[1],3)}\\pm{round(delta_theta, 3)}" + "^\circ$)")
        plt.plot(angles, norms, "b.", label="Frobenius norm of diff.", alpha=0.3)
        plt.axvline(ref_angle, linestyle="--", color="black", label=f"Reference angle (${ref_angle}^\circ$)")
        #plt.axvline(best_angle, color="green", label=f"Absolute minimum ({best_angle} deg)")
        plt.title(f"Frobenius norms of differences ($\\theta = {ref_angle}"+"^\circ$)")
        plt.xlabel("Angle $\\vartheta$ (${}^\circ$)")
        plt.ylabel("Frobenius norm of difference")
        plt.legend(loc="lower right")
        plt.show()
                    
        return


################################################################
################################################################
################################################################
if __name__ == "__main__":
    """
    This is the main statement where the user can execute subroutines to produce figures.
    """
    proc = DataProcessor()

    proc.frobeniusNormAnalysis()

    sys.exit()
