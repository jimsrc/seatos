#!/usr/bin/env ipython
from pylab import *
import numpy as np
import load_avrs as p

XTICKS      = [1, 2, 3]
VARNAMES    = ['low $V_{mc}$\n$V_{mc}<400$', 
                'mid $V_{mc}$\n$450<V_{mc}<550$', 
                'high $V_{mc}$\n$V_{mc}>550$']
sig     = np.array([p.sigma_p0.mean(), p.sigma_p1.mean(), p.sigma_p2.mean()])
Np      = [p.np0.mean(), p.np1.mean(), p.np2.mean()]
#---------------------------------- begin: figura
fig     = figure(1, figsize=(5,3.5))
ax0     = fig.add_subplot(111)
ax1     = ax0.twinx()

l1, = ax0.plot(XTICKS, sig/(1.0e13), '-ok', ms=10., mfc='none', label='$\sigma_{sh}$')
l2, = ax1.plot(XTICKS, Np, '--sk', ms=10., mfc='none', label='$Np_{sh}$')

ax0.grid()
ax0.set_xlim(0.7, 3.3)
ax0.set_xticks(XTICKS)
ax0.set_xticklabels(VARNAMES, fontsize=14, rotation='40')
ax0.set_ylabel('$\sigma_{sh}$ [$1/cm^2$] $\\times 10^{13}$\n(proton surface density)', fontsize=15)
ax1.set_ylabel('$Np_{sh}$ [$1/cm^3$]')
ax0.set_ylim(2.0, 4.3)
ax1.set_ylim(7, 20)
#ax0.legend(loc=(0.7, 0.85), frameon=False)
#ax1.legend(loc=(0.7, 0.70), frameon=False)
ax0.legend(handles=[l1, l2], loc='best')

fname_fig = '../figs/surf.densities_vs_Vmc.png'
savefig(fname_fig, format='png', dpi=130, bbox_inches='tight')
print " ---> generamos: " + fname_fig
close()
#---------------------------------- end: figura
