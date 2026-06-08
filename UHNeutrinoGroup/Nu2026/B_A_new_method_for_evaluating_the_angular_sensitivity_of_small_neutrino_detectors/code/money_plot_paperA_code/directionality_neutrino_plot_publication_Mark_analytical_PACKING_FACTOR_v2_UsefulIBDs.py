import math
import matplotlib
import matplotlib.pyplot as plt
from cycler import cycler
import numpy as np
import pandas as pd
plt.rc('font', family='serif', size = 19)
plt.rcParams['text.usetex'] = True
plt.rcParams['mathtext.fontset'] = 'cm' # computer modern

plt.figure(figsize=(6, 4))

#plt.style.use('classic')
Nmax = 10000
N = np.arange(1.0, Nmax, 0.5)

def ares(P, d, N):
    return ( math.atan(P/d/(N**0.5)) ) * 180 / math.pi

fdata = 'DeltaPhiTable_extra_col.txt'
data = pd.read_csv(fdata, delim_whitespace=True, header=0)
print(data)

fig, ax = plt.subplots()
clr = ['b', 'g', 'r', 'c', 'm', 'y', '#ff7f0e', '#8c564b']
#ax.plot(N, sandd, color='red', linewidth=3.0, label='SANDD')
#ax.plot(N, chooz, color='blue', linewidth=3.0, label='Double CHOOZ')
#ax.plot(N, chooz, color='blue', label='DC (can make a curve?)')
#ax.plot(N, sandd, color='red', label='SANDD')
#ax.plot(N, np.vectorize(ares)(data.P_mm[1], data.l_mm[1], N), label=data.Expr[1])
for i in range(len(data.index)):
    ax.plot(N, np.vectorize(ares)(data.P_mm[i], data.l_mm[i], N*data.PackFactor[i]), color=data.clr[i], linestyle=data.ln_style[i], label=data.Expr[i], linewidth=0.9)

#fsize = 12
#ax.set(xlabel='Number of Antineutrinos Detected', ylabel=r'Angular resolution (degrees)', fontsize=fsize)
#ax.set_xlabel('Number of detected IBDs', fontsize=fsize)
#ax.set_ylabel('Angular Resolution [degrees]', fontsize=fsize)
#ax.set_xlabel('Number of Detected IBDs',ha='left')
ax.set_xlabel(r'Number of Detected Useful IBDs')
ax.set_ylabel('Angular Resolution (degrees)')
#ax.set_ylabel(r'$\Delta \varphi \ (^\circ)$')
#ax.xaxis.set_label_coords(0.41,-0.1)
#ax.yaxis.set_label_coords(-0.14,.56)
#plt.xlabel('Number of Detected IBDs',loc='right')

ax.grid()

ax.set_xscale('log')
ax.set_xlim(10, Nmax)

#plt.legend(loc='upper right', numpoints=1, edgecolor='black', facecolor='white', framealpha=1., fancybox=False, fontsize=12)

plt.tight_layout()
plt.savefig("angular_resolution_analytic_PackFactor_v2Useful.pdf", bbox_inches='tight')
#plt.show()

ax.set_ylim(1,100)
ax.set_yscale('log')
#plt.legend(loc='lower left', numpoints=1, edgecolor='black', facecolor='white', framealpha=1., fancybox=False, fontsize=12, ncol=2,handleheight=2.4, labelspacing=0.05)
lines = ax.get_lines()
legend1 = plt.legend([lines[j] for j in range(0, 4, 1)], [lines[j].get_label() for j in range(0, 4, 1)], title='3D', loc='lower left', facecolor='white', framealpha=1, fontsize=12, numpoints=1, edgecolor='black', fancybox=False) # loc='lower center') #'upper left')
legend2 = plt.legend([lines[j] for j in range(4, 7, 1)], [lines[j].get_label() for j in range(4, 7, 1)], title='2D', loc='upper right', facecolor='white', framealpha=1, fontsize=12, numpoints=1, edgecolor='black', fancybox=False) # loc='lower center') #'upper left')

ax.add_artist(legend1)
ax.add_artist(legend2)


plt.tight_layout()
plt.savefig("angular_resolution_analytic_ylog_PackFactor_v2Useful.pdf", bbox_inches='tight')
