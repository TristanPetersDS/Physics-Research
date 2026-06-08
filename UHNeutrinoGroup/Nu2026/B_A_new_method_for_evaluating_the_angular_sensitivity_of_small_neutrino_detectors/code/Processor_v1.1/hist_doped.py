
import json
import numpy as np
import matplotlib.pyplot as plt

SAVE = False

# 0.1% doped data file.
datafile001wt = "../data/10k_run0.json"

# 0.5% doped data file.
datafile005wt = "../data/10k_005wt_run0.json"
        
with open(datafile001wt, "r") as f:
    data001wt = json.load(f)
    f.close()
    
with open(datafile005wt, "r") as f:
    data005wt = json.load(f)
    f.close()

#print(data001wt)
#print(data005wt)

#xmax = 1000

#----------------------------
d001wt_track_lengths = []
for event in list(data001wt.keys()):

    # Pulls coordinates from data dictionary.
    x0, y0, z0 = data001wt[event]["vertex"]
    x1, y1, z1 = data001wt[event]["annihilation"]
    
    xbar = x1 - x0
    ybar = y1 - y0
    zbar = z1 - z0

    track_length = np.sqrt(xbar**2 + ybar**2 + zbar**2)

    #if track_length <= xmax:
    d001wt_track_lengths.append(track_length)

mean001wt = sum(d001wt_track_lengths) / len(d001wt_track_lengths)
print(f"Mean positron track length for 0.1% doped:", mean001wt, "mm")



#----------------------------
d005wt_track_lengths = []
for event in list(data005wt.keys()):

    # Pulls coordinates from data dictionary.
    x0, y0, z0 = data005wt[event]["vertex"]
    x1, y1, z1 = data005wt[event]["annihilation"]
    
    xbar = x1 - x0
    ybar = y1 - y0
    zbar = z1 - z0

    track_length = np.sqrt(xbar**2 + ybar**2 + zbar**2)

    #if track_length <= xmax:
    d005wt_track_lengths.append(track_length)

mean005wt = sum(d005wt_track_lengths) / len(d005wt_track_lengths)
print(f"Mean positron track length for 0.5% doped:", mean005wt, "mm")

#d001wt_track_lengths.append(xmax)
#d005wt_track_lengths.append(xmax)

bin_width = 1.0
nbins = 100
bins = []
for i in range(nbins+1):
    bins.append(bin_width * i)


hist1 = plt.hist(d001wt_track_lengths, bins=bins, edgecolor=(1,0,0,1.0), fc=(1,0,0,0.05), label=f"0.1%, mean: {round(mean001wt, 2)} mm")
hist2 = plt.hist(d005wt_track_lengths, bins=bins, edgecolor=(0,0,1,0.8), fc=(1,1,1,0), label=f"0.5%, mean: {round(mean005wt, 2)} mm")

plt.legend()
plt.grid()

plt.xlim(0, 50)
plt.xlabel("Track length (mm)")
plt.ylabel("Simulation count")
plt.title("Positron track lengths (10k events)")

if SAVE:
    plt.savefig("positron_track_length_hist.pdf", format="pdf")

plt.show()


print("===========================================")


#----------------------------
d001wt_track_lengths = []
for event in list(data001wt.keys()):

    # Pulls coordinates from data dictionary.
    x0, y0, z0 = data001wt[event]["vertex"]
    x1, y1, z1 = data001wt[event]["capture"]
    
    xbar = x1 - x0
    ybar = y1 - y0
    zbar = z1 - z0

    track_length = np.sqrt(xbar**2 + ybar**2 + zbar**2)

    #if track_length <= xmax:
    d001wt_track_lengths.append(track_length)

mean001wt = sum(d001wt_track_lengths) / len(d001wt_track_lengths)
print(f"Mean neutron track length for 0.1% doped:", mean001wt, "mm")



#----------------------------
d005wt_track_lengths = []
for event in list(data005wt.keys()):

    # Pulls coordinates from data dictionary.
    x0, y0, z0 = data005wt[event]["vertex"]
    x1, y1, z1 = data005wt[event]["capture"]
    
    xbar = x1 - x0
    ybar = y1 - y0
    zbar = z1 - z0

    track_length = np.sqrt(xbar**2 + ybar**2 + zbar**2)

    #if track_length <= xmax:
    d005wt_track_lengths.append(track_length)

mean005wt = sum(d005wt_track_lengths) / len(d005wt_track_lengths)
print(f"Mean neutron track length for 0.5% doped:", mean005wt, "mm")

#d001wt_track_lengths.append(xmax)
#d005wt_track_lengths.append(xmax)

bin_width = 5.0
nbins = 100
bins = []
for i in range(nbins+1):
    bins.append(bin_width * i)


hist1 = plt.hist(d001wt_track_lengths, bins=bins, edgecolor=(1,0,0,1.0), fc=(1,0,0,0.05), label=f"0.1%, mean: {round(mean001wt, 2)} mm")
hist2 = plt.hist(d005wt_track_lengths, bins=bins, edgecolor=(0,0,1,0.8), fc=(1,1,1,0), label=f"0.5%, mean: {round(mean005wt, 2)} mm")

plt.legend()
plt.grid()

plt.xlim(0, 250)
plt.xlabel("Track length (mm)")
plt.ylabel("Simulation count")
plt.title("Neutron track lengths (10k events)")

if SAVE:
    plt.savefig("neutron_track_length_hist.pdf", format="pdf")


plt.show()


exit()
