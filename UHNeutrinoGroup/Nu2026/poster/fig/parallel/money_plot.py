
import numpy as np
import matplotlib.pyplot as plt

#plt.rc("font", family="serif", size = 18)
#plt.rcParams["text.usetex"] = True
#plt.rcParams["mathtext.fontset"] = "cm" # computer modern


from scipy.optimize import curve_fit

def quadratic(x, a, b, c):
    return a*x**2 + b*x + c

def cubic(x, a, b, c, d):
    return a*x**3 + b*x**2 + c*x + d

dbasename = "data19"

dataf_5 = dbasename + "/func_iter_dx_5_detected.txt"
dataf_50 = dbasename + "/func_iter_dx_50_detected.txt"
dataf_150 = dbasename + "/func_iter_dx_150_detected.txt"

#iter_arr = [10000, 3333, 1000, 333, 100, 100, 100, 100]
iter_arr  = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]


dx_5 = []
dt_5 = []
de_5 = []

dx_50 = []
dt_50 = []
de_50 = []

dx_150 = []
dt_150 = []
de_150 = []


with open(dataf_5, "r") as f:
    i = 0
    for line in f:
        elems = line.split()

        #print(elems)

        dx_5.append(float(elems[0]))
        dt_5.append(float(elems[1]))
        de_5.append(float(elems[1]) / np.sqrt(iter_arr[i]))

        i += 1

    f.close()

with open(dataf_50, "r") as f:
    i = 0
    for line in f:
        elems = line.split()

        #print(elems)

        dx_50.append(float(elems[0]))
        dt_50.append(float(elems[1]))
        de_50.append(float(elems[1]) / np.sqrt(iter_arr[i]))

        i += 1

    f.close()

with open(dataf_150, "r") as f:
    i = 0
    for line in f:
        elems = line.split()

        #print(elems)

        dx_150.append(float(elems[0]))
        dt_150.append(float(elems[1]))
        de_150.append(float(elems[1]) / np.sqrt(iter_arr[i]))

        i += 1

    f.close()


# Plot raw data
plt.errorbar(dx_5, dt_5, yerr=de_5, fmt=".-",
             capsize=3, label="$\Delta x = 5$ mm")
plt.errorbar(dx_50, dt_50, yerr=de_50, fmt=".-",
             capsize=3, label="$\Delta x = 50$ mm")
plt.errorbar(dx_150, dt_150, yerr=de_150, fmt=".-",
             capsize=3, label="$\Delta x = 150$ mm")

plt.xscale("log")
plt.yscale("log")


x_theo_test = np.logspace(np.log10(10), np.log10(1000000), 16)
y_theo_test = 2*np.pi*80 / np.sqrt(x_theo_test+100)

plt.plot(x_theo_test, y_theo_test, "r-")

plt.xlabel("Counts $n$")
plt.ylabel("Angular uncertainty $\\delta \\vartheta$ (${}^\\circ$)")
plt.legend()

plt.grid(True, which="both", linestyle="--", linewidth=0.5)

#plt.savefig("money_plot_10M_fid.pdf", format="pdf", bbox_inches="tight")

plt.show()

exit()
