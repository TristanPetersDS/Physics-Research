import os
import sys
import time
import random
import json
import math
from tqdm import tqdm
import warnings

from scipy.stats import poisson
from scipy.special import gamma
from scipy.optimize import curve_fit

import numpy as np
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

################################################################
################################################################
################################################################
class DataProcessor():
    """
    RATPAC2 DataProcessor - Post processing methods for RATPAC2 positron and neutron output track data. This code produces figures for paper B using simulated data with RATPAC2.
    """
    ################################################################
    def __init__(self):
        self.debug = False

        self.latex = True

        
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
    def procData(self):
        if self.debug:
            print("DataProcessor class method: procData")

        self.data = {}

        # Starts a timer.
        t_start = time.time()


        n = 0
        event = -1
        with tqdm(open(self.dataFile, "r"), desc="Reading RATPAC data") as f:
            for line in f:

                #print(n, line)
                if n > 4:
                    # Current format:
                    # Row    Instance  trackPDG    trackPos   trackPos   trackPos   trackTim   trackMom   trackMom   trackMom   trackKE    trackPro      evid        mcx        mcy        mcz        mcu        mcv        mcw       mcpdg
                    elems = line.split()

                    try:
                        test = elems[19]
                        simEvent = int(elems[0])
                    except IndexError:
                        continue

                    if simEvent == event:
                        pass
                    else:
                        event += 1

                        if event > 0:
                            prev_elems = prev_line.split()
                        
                            prev_simEvent = int(prev_elems[0])

                            prev_xpos = float(prev_elems[3])
                            prev_ypos = float(prev_elems[4])
                            prev_zpos = float(prev_elems[5])

                            #print("First-scatter", prev_simEvent, (prev_xpos, prev_ypos, prev_zpos))
                            self.data[prev_simEvent]["first-scatter"] = (prev_xpos, prev_ypos, prev_zpos)
                        
                        if event <= self.N-1:
                            try:
                                xpos = float(elems[3])
                                ypos = float(elems[4])
                                zpos = float(elems[5])                                
                            except IndexError:
                                xpos, ypos, zpos = (0, 0, 0)

                            try:
                                mcx = float(elems[13])
                                mcy = float(elems[14])
                                mcz = float(elems[15])
                            except IndexError:
                                mcx, mcy, mcz = (0, 0, 0)
                            
                            #print("Capture", simEvent, (xpos, ypos, zpos))
                            #print("Vertex", simEvent, (mcx, mcy, mcz))
                            self.data[simEvent] = {}
                            self.data[simEvent]["capture"] = (xpos, ypos, zpos)
                            self.data[simEvent]["vertex"] = (mcx, mcy, mcz)
                            
                        else:
                            break                

                prev_line = line
                n += 1

            f.close()


        print("Filtering fragmented events...")
        for i in list(self.data.keys()):
            if len(list(self.data[i].keys())) < 3:
                self.data.pop(i)

        print("Created", len(self.data), "dictionary entries in", time.time() - t_start, "s")

        print("Writing data to JSON file...")
        with open(self.jsonFile, "w") as f:
            json.dump(self.data, f)
            f.close()

        print("Done!")
        
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

    def poissonFunc(self, x, lam):

        return (lam**x * np.exp(-lam)) / gamma(x+1)
        

    ################################################################
    def plotNeutronHistogram(self, type_="capture", save=False):
        if self.debug:
            print("DataProcessor class method: plotNeutronHistogram")

        # type_ can be either 'capture' or 'first-scatter'

        track_lengths = []
        for event in list(self.data.keys()):

            # Pulls coordinates from data dictionary.
            x0, y0, z0 = self.data[event]["vertex"]
            x1, y1, z1 = self.data[event][type_]
    
            xbar = x1 - x0
            ybar = y1 - y0
            zbar = z1 - z0

            track_length = np.sqrt(xbar**2 + ybar**2 + zbar**2)

            track_lengths.append(track_length)

        mean = sum(track_lengths) / len(track_lengths)
        print(f"Mean neutron ({type_}) track length:", mean)

        # Plots histogram.
        xmax = 300
        hist = plt.hist(track_lengths, bins=128, color="orange")

        plt.xlim(0, xmax)
        plt.xlabel("$d_n$ (mm)")
        plt.ylabel("Count")
        plt.title(f"Neutron ({type_}) track length histogram")
        if save:
            plt.savefig(f"hist_neutron_{type_}.pdf", format="pdf")

        plt.show()

        return

    ################################################################
    def binEvents(self):
        if self.debug:
            print("DataProcessor class method: binEvents")

        t_start = time.time()
        for event in list(self.data.keys()):
            xs, ys, zs = self.data[event]["vertex"]
            xn, yn, zn = self.data[event]["capture"]

            xrand = random.uniform(-self.cube_size / 2.0, self.cube_size / 2.0)
            yrand = random.uniform(-self.cube_size / 2.0, self.cube_size / 2.0)

            xc = xn - xs - xrand
            yc = yn - ys - xrand

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

        print("Binned events:", caps)
        print("Elapsed time:", time.time() - t_start, "s")

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
            xrand = random.uniform(-self.cube_size / 2.0, self.cube_size / 2.0)
            yrand = random.uniform(-self.cube_size / 2.0, self.cube_size / 2.0)

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
    def printBinDists(self, plot=False, trange=[0, 45], save=False):
        if self.debug:
            print("DataProcessor class method: printBinDists")

        print("Segmentation:", self.seg)

        if save:
            f = open("out.txt", "w")

        for t in range(trange[0], trange[1]+1):
            caps = self.binEventsLoop(rot=t, PLOT=plot)
            print(t, caps)

            if save:
                f.write(f"Angle: {t} deg\n")
                f.write(str(caps) + "\n")

        if save:
            f.close()
                    
        return

    ################################################################
    def plotBinDistColormap(self, theta, plot_cmap=True, plot=False, save=False):
        if self.debug:
            print("DataProcessor class method: plotBinDistColormap")

        print("Segmentation:", self.seg)

        caps = self.binEventsLoop(rot=theta, PLOT=plot)

        ext_low  = -self.half_size
        ext_high =  self.half_size

        im = plt.imshow(caps, cmap="viridis", extent=(ext_low, ext_high, ext_low, ext_high))


        plt.title(f"Bin distribution colormap (rot={theta} deg, 10k events)")
        
        cbar = plt.colorbar(im)
        cbar.set_label("Counts")
        plt.xlabel("x (mm)")
        plt.ylabel("y (mm)")
        im.set_clim(0, 2000)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                text = plt.text((j-1)*self.cube_size, -(i-1)*self.cube_size, f"{int(caps[i, j])}", 
                                ha="center", va="center", color=("w" if int(caps[i, j]) <= 1250 else "k"))

        if save:
            plt.savefig(f"bin_dist_rot{theta}.pdf", format="pdf")

        plt.show()
                    
        return

    ################################################################
    def angularDist(self, type_="capture", save=False):
        """
        Usage: type_ - Can be either 'capture' or 'first-scatter'.
               save - Use True to save figure as PDF.
        """
        if self.debug:
            print("DataProcessor class method: angularDist")

        theta_dist = []
        for event in list(self.data.keys()):

            # Extract coordinates from dictionary.
            xs, ys, zs = self.data[event]["vertex"]
            xn, yn, zn = self.data[event][type_]

            # Calculates the 2d component-wise distance between IBD vertex and capture.
            x = xn - xs
            y = yn - ys

            # Initial angle of capture.
            theta = np.arctan2(y, x)

            theta_dist.append(theta)
            
        # Create the figure and polar axes
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

        # Create the polar histogram.
        hist = ax.hist(theta_dist, bins=36, edgecolor="blue", color="white", linewidth=2, bottom=0)

        print(hist[0])

        max_theta = max(hist[0])
        print(max_theta)


        #hole_rad = 1500
        hole_rad = 0.8 * max_theta

        
        #ax.set_ylim(0, 2000)
        ax.set_rorigin(-hole_rad)
        #ax.set_rgrids([500, 1000, 1500, 2000], labels=["500", "1000", "1500", "2000"])
        if max_theta >= 1000.0:
            ax.set_rgrids([ 500, 1000, 1500, 2000, 2500], labels=["500", "1000", "1500", "2000", "2500"])
        else:
            ax.set_rgrids([250, 500, 750, 1000], labels=["250", "500", "750", "1000"])

        ax.set_ylim(0, max_theta + 0.1 * max_theta)
        ax.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2],["0", "$\\pi/2$","$\\pi$","$3\\pi/2$"])
        #ax.set_yticklabels([])

        # Set the title
        if type_ == "first-scatter":
            plt.text(0, -hole_rad, "1st scatter", ha="center", va="center")
            if save:
                plt.savefig("polar_hist_1st_scat.pdf", format="pdf")

        elif type_ == "capture":
            plt.text(0, -hole_rad, "$\\longrightarrow$\n$\\nu$", ha="center", va="center")
            if save:
                plt.savefig("polar_hist_capture.pdf", format="pdf")

        else:
            print("Error: type must be either 'first-scatter' or 'capture'...")

        # Show the plot.
        plt.show()
        
        return

    ################################################################
    def x_dist(self, type_="capture", save=False):
        """
        Usage: type_ can be either 'capture' or 'first-scatter'.
        """
        if self.debug:
            print("DataProcessor class method: angularDist")

        x_dist = []
        for event in list(self.data.keys()):

            # Extract coordinates from dictionary.
            xs, ys, zs = self.data[event]["vertex"]
            xn, yn, zn = self.data[event][type_]

            x = xn - xs

            # Initial angle of capture.
            x_dist.append(x)

        plt.hist(x_dist, bins=128)
        plt.grid()
        plt.title("x-position histogram")
        plt.xlabel(f"{type_} - vertex (mm)")
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
    def testVectorSum(self):
        if self.debug:
            print("DataProcessor class method: testVectorSum")

        # Find center diag element of segmentation array.
        cent = int(np.floor(self.grid_size / 2.0))

        # Creates a reference dataset at a rotation of 'ref_angle' degrees.
        ref_angle = 35
        ref_data = self.binEventsLoop(rot=ref_angle)

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
        ref_data = self.binEventsLoop(rot=ref_angle)

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
            caps = self.binEventsLoop(rot=t)

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
################################################################
################################################################
if __name__ == "__main__":
    """
    This is the main statement where the user can execute subroutines to produce figures.
    """
    proc = DataProcessor()

    #proc.angularDist(save=False)
    #proc.angularDist(type_="first-scatter", save=False)
    #proc.angularDist(type_="capture", save=False)

    #proc.x_dist(type_="first-scatter")

    #proc.printBinDists(save=False)

    #proc.plotBinDistColormap(0, save=False)
    #proc.plotBinDistColormap(30, save=False)
    #proc.plotBinDistColormap(45, save=False)

    #proc.plotNeutronHistogram(type_="first-scatter")

    proc.frobeniusNormAnalysis()
    #proc.testVectorSum()

    sys.exit()
        
