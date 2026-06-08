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
    RATPAC2 DataProcessor - Post processing methods for RATPAC2 positron and neutron output track data. This code produces figures for paper B using simulated data with RATPAC2. This code requires positron and neutron tracks.
    """
    ################################################################
    def __init__(self):
        self.debug = True

        if self.debug:
            print("DataProcessor class method: __init__")

        # Number of events to read and process from the RATPAC output. This is only used if the procData subroutine is called.
        #self.N = 100000
        self.N = 10000

        # Path to JSON file that either exists or shall be created by this script.
        #self.dataFilePath = "../data/10k_run_mctruth.json"
        #self.dataFilePath = "../data/10k_run0.json"
        #self.dataFilePath = "../data/10k_run1.json"
        self.dataFilePath = "../data/10k_005wt_run0.json"

        # Paths to positron and neutron RATPAC output ASCII data to process. These files are used here to create a JSON file that contains the IBD vertices, positron annihilation, neutron capture, and neutron first scatter locations.
        #self.positronFile = "/Users/gabriel/Downloads/output_100k_events_positrons.txt"
        #self.positronFile = "/Users/gabriel/Downloads/ibd_cube_10k_run0/ibd_cube_10k_positrons.txt"
        #self.positronFile = "/Users/gabriel/Downloads/ibd_cube_10k_run1/ibd_cube_10k_run1_positrons.txt"
        self.positronFile = "/Users/gabriel/Downloads/ibd_cube_005wt_10k_run0/ibd_cube_005_wt_10k_run0_positrons.txt"
        
        #self.neutronFile = "/Users/gabriel/Downloads/output_100k_events_with_capture.txt"
        #self.neutronFile = "/Users/gabriel/Downloads/ibd_cube_10k_run0/ibd_cube_10k_neutrons.txt"
        #self.neutronFile = "/Users/gabriel/Downloads/ibd_cube_10k_run1/ibd_cube_10k_run1_neutrons.txt"
        self.neutronFile = "/Users/gabriel/Downloads/ibd_cube_005wt_10k_run0/ibd_cube_005wt_10k_run0_neutrons.txt"    

        # Checks if the JSON file exists, otherwise processes RATPAC ASCII output and creates JSON file at specified path. Can either run readData or procData. Not necessary to run both consecutively.
        if os.path.isfile(self.dataFilePath):
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

        # Initializes dictionary to store positron annihilation and IBD vertex and neutron capture and first scatter locations.
        self.data = {}

        # Starts a timer.
        t_start = time.time()
        
        # Open file and read text lines for positrons.
        n = 0
        event = -1
        prev_line = ""
        with tqdm(open(self.positronFile, "r"), desc="Reading positron vertices") as f:
            for line in f:
                if n > 4:                
                    elems = line.split()

                    try:
                        test = elems[11]
                        simEvent = int(elems[1])
                    except IndexError:
                        continue

                    if simEvent == event:
                        pass
                    else:
                        event += 1

                        if event > 0:
                            prev_elems = prev_line.split()
                        
                            prev_simEvent = int(prev_elems[1])

                            prev_xpos = float(prev_elems[7])
                            prev_ypos = float(prev_elems[9])
                            prev_zpos = float(prev_elems[11])

                            self.data[prev_simEvent]["annihilation"] = (prev_xpos, prev_ypos, prev_zpos)
                        
                        if event <= self.N-1:
                            try:
                                xpos = float(elems[7])
                                ypos = float(elems[9])
                                zpos = float(elems[11])
                            except IndexError:
                                xpos, ypos, zpos = (0, 0, 0)

                            self.data[simEvent] = {}
                            self.data[simEvent]["vertex"] = (xpos, ypos, zpos)
                            
                        else:
                            break                

                prev_line = line
                n += 1

            f.close()

        # Open file and read text lines for neutrons.
        n = 0
        event = -1
        prev_line = ""
        with tqdm(open(self.neutronFile, "r"), desc="Reading neutron captures") as f:
            for line in f:
                if n > 6:
                    elems = line.split()

                    try:
                        simEvent = int(elems[1])
                    except IndexError:
                        continue

                    simEvent = int(elems[1])

                    if simEvent == event:
                        pass
                    
                    else:
                        event += 1

                        if event > 0:
                            prev_elems = prev_line.split()
                        
                            prev_simEvent = int(prev_elems[1])

                            prev_xpos = float(prev_elems[7])
                            prev_ypos = float(prev_elems[9])
                            prev_zpos = float(prev_elems[11])
                            #prev_xpos = float(prev_elems[29])
                            #prev_ypos = float(prev_elems[31])
                            #prev_zpos = float(prev_elems[33])

                            #print(prev_elems)

                            self.data[prev_simEvent]["first-scatter"] = (prev_xpos, prev_ypos, prev_zpos)


                        if event <= self.N-1:
                            # Discovered that neutron file is setup to run in reverse time so this gets the first entry in the data file and is treated as the neutron capture location.
                            try:
                                xpos = float(elems[7])
                                ypos = float(elems[9])
                                zpos = float(elems[11])
                                #xpos = float(prev_elems[29])
                                #ypos = float(prev_elems[31])
                                #zpos = float(prev_elems[33])

                            except IndexError:
                                xpos, ypos, zpos = (0, 0, 0)
                                
                            try:
                                self.data[simEvent]["capture"] = (xpos, ypos, zpos)
                            except KeyError:
                                pass
                    
                        else:
                            break                

                prev_line = line
                n += 1

            f.close()

        print("Filtering fragmented events...")
        for i in list(self.data.keys()):
            if len(list(self.data[i].keys())) < 4:
                self.data.pop(i)

        print("Created", len(self.data), "dictionary entries in", time.time() - t_start, "s")

        print("Writing data to JSON file...")
        with open(self.dataFilePath, "w") as f:
            json.dump(self.data, f)
            f.close()

        print("Done!")
        
        return

    ################################################################
    def readData(self):
        if self.debug:
            print("DataProcessor class method: readData")

        print("Reading data from JSON file...")
        with open(self.dataFilePath, "r") as f:
            
            # Load the dictionary from the file.
            self.data = json.load(f)
            f.close()

        print("Done!")

        return 

    def poissonFunc(self, x, lam):

        return (lam**x * np.exp(-lam)) / gamma(x+1)
        

    ################################################################
    def plotHistogram(self, type_="positron", save=False):
        if self.debug:
            print("DataProcessor class method: plotHistogram")

        # Creates a histogram of either positron or neutron tracks using annihilation or capture and IBD locations.
        histKey = ("capture" if type_ == "neutron" else "annihilation")

        track_lengths = []
        for event in list(self.data.keys()):

            # Pulls coordinates from data dictionary.
            x0, y0, z0 = self.data[event]["vertex"]
            x1, y1, z1 = self.data[event][histKey]
    
            xbar = x1 - x0
            ybar = y1 - y0
            zbar = z1 - z0

            track_length = np.sqrt(xbar**2 + ybar**2 + zbar**2)

            track_lengths.append(track_length)

        mean = sum(track_lengths) / len(track_lengths)
        print(f"Mean {type_} track length:", mean)

        # Plots histogram.
        if type_ == "neutron":
            xmax = 300
            hist = plt.hist(track_lengths, bins=2048, color="orange")
            plt.xlim(0, xmax)
            plt.xlabel("Track length (mm)")
            plt.ylabel("Simulation count")
            plt.title("Neutron track length histogram")
            if save:
                plt.savefig("hist_neutron.pdf", format="pdf")

        elif type_ == "positron":
            plt.hist(track_lengths, bins=6000, color="red")
            plt.xlim(0, 50)
            plt.xlabel("Track length (mm)")
            plt.ylabel("Simulation count")
            plt.title("Positron track length histogram")
            if save:
                plt.savefig("hist_positron.pdf", format="pdf")

        else:
              print("Error: type_ must be either 'neutron' or 'positron'...")
              return

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
    def plotTracks(self, event, view=(90, 270, 0), save=False):
        if self.debug:
            print("DataProcessor class method: plotTracks")

        # The viewpoint argument takes tuple: (elev, azim, roll).

        # Initialize datasets for plotting.
        positron = {}
        neutron = {}

        # Open file and read text lines for positron.
        found = False
        n = 0
        with tqdm(open(self.positronFile, "r"), desc="Searching data for positron track") as f:
            for line in f:

                if n > 4:
                    elems = line.split()

                    simEvent = int(elems[1])

                    if simEvent == event:
                        xpos = float(elems[7])
                        ypos = float(elems[9])
                        zpos = float(elems[11])

                        if found:
                            positron[simEvent]["xtrack"].append(xpos)
                            positron[simEvent]["ytrack"].append(ypos)
                            positron[simEvent]["ztrack"].append(zpos)
                        else:
                            positron[simEvent] = {"xtrack":[xpos], "ytrack":[ypos], "ztrack":[zpos]}
                            found = True
                    elif simEvent < event:
                        pass
                    elif simEvent > event:
                        break

                n += 1

            f.close()

        # Open file and read text lines for neutron.
        found = False
        n = 0
        with tqdm(open(self.neutronFile, "r"), desc="Searching data for neutron track") as f:
            for line in f:

                if n > 6:
                    elems = line.split()

                    if "4" in elems[15]:
                        pass
                    else:
                        simEvent = int(elems[1])

                        if simEvent == event:
                            xpos = float(elems[7])
                            ypos = float(elems[9])
                            zpos = float(elems[11])

                            if found:
                                neutron[simEvent]["xtrack"].append(xpos)
                                neutron[simEvent]["ytrack"].append(ypos)
                                neutron[simEvent]["ztrack"].append(zpos)
                            else:
                                neutron[simEvent] = {"xtrack":[xpos], "ytrack":[ypos], "ztrack":[zpos]}
                                found = True
                        elif simEvent < event:
                            pass
                        elif simEvent > event:
                            break

                n += 1

            f.close()

        print("Plotting track data...")
        # Show the newly created dictionary (track data). Plots the provided event number.
        fig = plt.figure()
        ax = plt.axes(projection="3d")

        # initializes with a top-view perspective.
        ax.view_init(view[0], view[1], view[2])

        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
        ax.set_zlabel("z (mm)")

        # Shift data.
        xshift = positron[event]["xtrack"][0]
        yshift = positron[event]["ytrack"][0]
        zshift = positron[event]["ztrack"][0]

        for i in range(len(positron[event]["xtrack"])):
            positron[event]["xtrack"][i] -= xshift
            positron[event]["ytrack"][i] -= yshift
            positron[event]["ztrack"][i] -= zshift
            
        for i in range(len(neutron[event]["xtrack"])):
            neutron[event]["xtrack"][i] -= xshift
            neutron[event]["ytrack"][i] -= yshift
            neutron[event]["ztrack"][i] -= zshift
    
        ax.plot3D(neutron[event]["xtrack"], neutron[event]["ytrack"], neutron[event]["ztrack"], color="orange", label="Neutron")
        ax.plot3D(positron[event]["xtrack"], positron[event]["ytrack"], positron[event]["ztrack"], color="red", label="Positron")

        ax.scatter(neutron[event]["xtrack"][0], neutron[event]["ytrack"][0], neutron[event]["ztrack"][0], color="orange", label="Capture location")
        ax.scatter(positron[event]["xtrack"][0], positron[event]["ytrack"][0], positron[event]["ztrack"][0], color="red", label="True IBD vertex")

        plt.legend(loc="upper left")


        if save:
            plt.savefig("track_plot.pdf", format="pdf")

        plt.show()
        
        return

    ################################################################
    def angularDist(self, type_="capture", save=False):
        """
        Usage: type_ can be either 'capture' or 'first-scatter'.
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

        #hole_rad = 1500
        hole_rad = 500

        # Create the polar histogram.
        ax.hist(theta_dist, bins=36, edgecolor="blue", color="white", linewidth=2, bottom=0)
        
        #ax.set_ylim(0, 2000)
        #ax.set_ylim(0, 1000)
        ax.set_rorigin(-hole_rad)
        #ax.set_rgrids([500, 1000, 1500, 2000], labels=["500", "1000", "1500", "2000"])
        #ax.set_rgrids([250, 500, 750, 1000], labels=["250", "500", "750", "1000"])
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
    ### BUG IN HERE. NEED TO FIX
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

            
            if int(event) < 10:
                print("==============")
                print("vertex:", xs, ys, zs)
                print(f"{type_}", xn, yn, zn)

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

    #proc.angularDist(save=False)
    #proc.angularDist(type_="first-scatter", save=False)
    #proc.angularDist(type_="capture", save=False)

    proc.x_dist(type_="first-scatter")

    #proc.plotTracks(0)
    #proc.plotTracks(3000, view=[20,225,0], save=False)
    #proc.plotTracks(4000, save=False)

    #proc.printBinDists()

    #proc.plotHistogram()
    #proc.plotHistogram(type_="positron")
    
    sys.exit()
        
