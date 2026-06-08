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
        self.debug = True

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

        # Initialization variables for 2d square grid segmentation. This variable represents the number of squares on a side of the grid.
        self.grid_size = 3

        # Size of individual square segment in mm.
        self.cube_size = 55

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
        print(theta, caps)

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
                print(i,j, caps[i][j])
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
################################################################
################################################################
if __name__ == "__main__":
    """
    This is the main statement where the user can execute subroutines to produce figures.
    """
    proc = DataProcessor()

    proc.angularDist(save=False)
    #proc.angularDist(type_="first-scatter", save=False)
    #proc.angularDist(type_="capture", save=False)

    #proc.x_dist(type_="first-scatter")

    #proc.printBinDists(save=False)

    #proc.plotBinDistColormap(0, save=False)
    #proc.plotBinDistColormap(30, save=False)
    #proc.plotBinDistColormap(45, save=False)

    proc.plotNeutronHistogram(type_="first-scatter")

    sys.exit()
        
