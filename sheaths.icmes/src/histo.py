#!/usr/bin/env ipython
from pylab import *
import numpy as np
from scipy.io.netcdf import netcdf_file

MCwant      = '2'
nbefore     = 2
nafter      = 4
WangFlag    = 'NaN'
fgap        = 0.2
v_lo        = 550.0 #550.0  #450.0 #100.0
v_hi        = 3000.0 #3000.0 #550.0 #450.0
prexShift   = 'wShiftCorr'

DIR_FIGS    = '../plots/MCflag%s/%s' % (MCwant, prexShift)
DIR_ASCII   = '../ascii/MCflag%s/%s' % (MCwant, prexShift)
FNAMEs      = 'MCflag%s_%dbefore.%dafter_Wang%s_fgap%1.1f_vlo.%3.1f.vhi.%4.1f' % (MCwant, nbefore, nafter, WangFlag, fgap, v_lo, v_hi)
#FNAME_FIGS  = '%s/_hist_%s' % (DIR_FIGS, FNAMEs)
fname_inp   = '%s/_stuff_%s.nc' % (DIR_ASCII, FNAMEs)

f_in        = netcdf_file(fname_inp, 'r')

Pcc         = f_in.variables['Pcc'].data
dt_mc_Pcc   = f_in.variables['dt_mc_Pcc'].data
Vmc         = f_in.variables['V'].data
id_Pcc      = set(f_in.variables['IDs_Pcc'].data)
id_Vmc      = set(f_in.variables['IDs_V'].data)
ids         = id_Pcc.intersection(id_Vmc)
#---------------------------------- calculamos las surface densities
nbins   = 10
n       = len(ids)
var_sh  = np.zeros(n)
var_mc  = np.zeros(n)
var_co  = np.zeros(n)
#var     = Pcc*dt_sh*Vsh
#for id, i in zip(ids, range(n)):
i=0
for ID_Pcc, i_Pcc in zip(id_Pcc, range(len(id_Pcc))):
    for ID_Vmc, i_Vmc in zip(id_Vmc, range(len(id_Vmc))):
        ok = (ID_Pcc==ID_Vmc) and (ID_Vmc in ids)
        if ok:
            var_mc[i] = Pcc[i_Pcc]*dt_mc_Pcc[i_Pcc]*Vmc[i_Vmc]
            i+=1

var_mc *= 86400.*1e5
#---------------------------------- begin: figura

XRANGE  = [0., 1.4e14]
fig     = figure(1, figsize=(6,4))
ax      = fig.add_subplot(111)

h, x    = np.histogram(var_mc, bins=nbins, range=XRANGE, normed=True)
x       = .5*(x[:-1] + x[1:])
dx      = x[1]-x[0]
h       *= dx*100.

LABEL   = 'N: %d' % n
TIT1    = 'normalized histogram (area=100%)'
TIT2    = '%4.1f km/s < Vicme < %4.1f km/s' % (v_lo, v_hi)
TITLE   = TIT1+'\n'+TIT2
ax.plot(x, h, 'o-', label=LABEL)
ax.legend()
ax.grid()
ax.set_title(TITLE)
ax.set_xlabel('surface density at MC $\sigma_{mc}$ [$1/cm^2$]')
ax.set_ylabel('[%]')
ax.set_xlim(XRANGE)
ax.set_ylim(0., 60.)


fname_fig   = '%s/_hist.mc_%s.png' % (DIR_FIGS, FNAMEs)
savefig(fname_fig, format='png', dpi=135, bbox_inches='tight')
close()
print " -------> genere: %s" % fname_fig
#---------------------------------- end: figura
f_in.close()
