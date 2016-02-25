#!/usr/bin/env ipython
from pylab import *
import numpy as np
from scipy.io.netcdf import netcdf_file
import console_colors as ccl
import os


MCwant      = '2'
nbefore     = 2
nafter      = 4
WangFlag    = '90.0' #'NaN'
fgap        = 0.2
#v_lo        = 550.0 #550.0  #450.0 #100.0
#v_hi        = 3000.0 #3000.0 #550.0 #450.0
prexShift   = 'wShiftCorr'

#+++++++++++++++ filtros
FILTER                      = {}
FILTER['vsw_filter']        = True #False
FILTER['B_filter']          = False
FILTER['filter_dR.icme']    = False
LO, HI                      = 550.0, 3000.0 #100.0, 450.0 #450.0, 550.0 #550.0, 3000.0

# NOTA: estos directorios deberian existir
dir_suffix  = '/_test_Vmc_'
DIR_FIGS    = '../../plots/MCflag%s/%s' % (MCwant, prexShift) + dir_suffix
DIR_ASCII   = '../../ascii/MCflag%s/%s' % (MCwant, prexShift) + dir_suffix
#os.system('mkdir -p %s %s' % (DIR_FIGS, DIR_ASCII)) # si no existen, los creo!
print ccl.On + " ---> leyendo data de: " + DIR_ASCII + ccl.W


#FNAMEs      = 'MCflag%s_%dbefore.%dafter_Wang%s_fgap%1.1f_vlo.%3.1f.vhi.%4.1f' % (MCwant, nbefore, nafter, WangFlag, fgap, v_lo, v_hi)
FNAMEs = 'MCflag%s_%dbefore.%dafter_fgap%1.1f' % (MCwant, nbefore, nafter, fgap)
FNAMEs += '_Wang%s' % (WangFlag)
if FILTER['vsw_filter']:        FNAMEs += '_vlo.%03.1f.vhi.%04.1f' % (LO, HI)
if FILTER['B_filter']:          FNAMEs += '_Blo.%2.2f.Bhi.%2.2f' % (LO, HI)
if FILTER['filter_dR.icme']:    FNAMEs += '_dRlo.%2.2f.dRhi.%2.2f' % (LO, HI)

# _stuff_MCflag2_2before.4after_fgap0.2_Wang90.0_
#FNAME_FIGS  = '%s/_hist_%s' % (DIR_FIGS, FNAMEs)
fname_inp   = '%s/_stuff_%s.nc' % (DIR_ASCII, FNAMEs)

f_in        = netcdf_file(fname_inp, 'r')

Pcc         = f_in.variables['Pcc'].data
dt_sh_Pcc   = f_in.variables['dt_sheath_Pcc'].data
Vsh         = f_in.variables['V'].data
id_Pcc      = set(f_in.variables['IDs_Pcc'].data)
id_Vsh      = set(f_in.variables['IDs_V'].data)
ids         = id_Pcc.intersection(id_Vsh)
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
    for ID_Vsh, i_Vsh in zip(id_Vsh, range(len(id_Vsh))):
        ok = (ID_Pcc==ID_Vsh) and (ID_Vsh in ids)
        if ok:
            var_sh[i] = Pcc[i_Pcc]*dt_sh_Pcc[i_Pcc]*Vsh[i_Vsh]
            i+=1

var_sh *= 86400.*1e5


"""
#---------------------------------- begin: figura

XRANGE  = [0., 1.4e14]
fig     = figure(1, figsize=(6,4))
ax      = fig.add_subplot(111)

h, x    = np.histogram(var_sh, bins=nbins, range=XRANGE, normed=True)
x       = .5*(x[:-1] + x[1:])
dx      = x[1]-x[0]
h       *= dx*100.
avr     = np.mean(var_sh)
med     = np.median(var_sh)

LABEL   = 'N: %d' % n
TIT1    = 'normalized histogram (area=100%)'
TIT2    = '%4.1f km/s < Vmc < %4.1f km/s' % (LO, HI)
TITLE   = TIT1+'\n'+TIT2
ax.plot(x, h, 'o-', label=LABEL)
ax.axvline(x=avr, c='blue', alpha=.4, lw=4, label="mean")
ax.axvline(x=med, c='black', alpha=.4, lw=4, label="median")

ax.legend()
ax.grid()
ax.set_title(TITLE)
ax.set_xlabel('surface density at sheath $\sigma_{sh}$ [$1/cm^2$]')
ax.set_ylabel('[%]')
ax.set_xlim(XRANGE)
ax.set_ylim(0., 55.)

# generamos figura
fname_fig   = '%s/_hist_.sh_%s.png' % (DIR_FIGS, FNAMEs)
savefig(fname_fig, format='png', dpi=135, bbox_inches='tight')
close(fig)
print ccl.Rn + " -------> genere: %s" % fname_fig + ccl.W
#---------------------------------- end: figura



#---------------------------------- begin: ascii
fname_txt   = '%s/_hist_.sh_%s.txt' % (DIR_ASCII, FNAMEs)
data_out    = np.array([x, h]).T
np.savetxt(fname_txt, data_out, fmt='%5.3g')
print ccl.Rn + " -------> genere: %s" % fname_txt + ccl.W
#---------------------------------- end: ascii



#
del Pcc, dt_sh_Pcc, Vsh  # para evitar el RunTimeWarning del netcdf_file()
#pause(3)
f_in.close()
##
"""
