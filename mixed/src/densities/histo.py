#!/usr/bin/env ipython
from pylab import *
import numpy as np
from scipy.io.netcdf import netcdf_file

MCwant      = '2'
nbefore     = 2
nafter      = 4
WangFlag    = 'NaN'
fgap        = 0.2
v_lo        = 100.0 #550.0  #450.0 #100.0
v_hi        = 450.0 #3000.0 #550.0 #450.0
prexShift   = 'wShiftCorr'

DIR_FIGS        = '../plots/%s/MCflag%s' % (prexShift, MCwant)
DIR_ASCII       = '../../ascii/MCflag%s/%s' % (MCwant, prexShift)
DIR_ASCII_MC    = '../../../mcs/ascii/MCflag%s/%s' % (MCwant, prexShift)
DIR_ASCII_SH    = '../../../sheaths/ascii/MCflag%s/%s' % (MCwant, prexShift)
FNAMEs          = 'MCflag%s_%dbefore.%dafter_Wang%s_fgap%1.1f_vlo.%3.1f.vhi.%4.1f' % (MCwant, nbefore, nafter, WangFlag, fgap, v_lo, v_hi)
#FNAME_FIGS  = '%s/_hist_%s' % (DIR_FIGS, FNAMEs)
sh_fname_inp    = '%s/_stuff_%s.nc' % (DIR_ASCII_SH, FNAMEs)
mc_fname_inp    = '%s/_stuff_%s.nc' % (DIR_ASCII_MC, FNAMEs)

sh_f_in         = netcdf_file(sh_fname_inp, 'r')
mc_f_in         = netcdf_file(mc_fname_inp, 'r')

sh_Pcc          = sh_f_in.variables['Pcc'].data
sh_dt_Pcc       = sh_f_in.variables['dt_sheath_Pcc'].data
sh_V            = sh_f_in.variables['V'].data
sh_id_Pcc       = set(sh_f_in.variables['IDs_Pcc'].data)
sh_id_V         = set(sh_f_in.variables['IDs_V'].data)
sh_ids          = sh_id_Pcc.intersection(sh_id_V)

mc_Pcc          = mc_f_in.variables['Pcc'].data
mc_dt_Pcc       = mc_f_in.variables['dt_mc_Pcc'].data
mc_V            = mc_f_in.variables['V'].data
mc_id_Pcc       = set(mc_f_in.variables['IDs_Pcc'].data)
mc_id_V         = set(mc_f_in.variables['IDs_V'].data)
mc_ids          = mc_id_Pcc.intersection(mc_id_V)
#---------------------------------- calculamos las surface densities
nbins   = 10
n       = len(sh_ids)
sh_var  = np.zeros(n)
mc_var  = np.zeros(n)
co_var  = np.zeros(n)
i=0
for ID_Pcc_sh, i_Pcc_sh in zip(sh_id_Pcc, range(len(sh_id_Pcc))):
    for ID_Vsh, i_Vsh in zip(sh_id_V, range(len(sh_id_V))):
        for ID_Pcc_mc, i_Pcc_mc in zip(mc_id_Pcc, range(len(mc_id_Pcc))):
            for ID_Vmc, i_Vmc in zip(mc_id_V, range(len(mc_id_V))):
                ok = (ID_Pcc_sh==ID_Vsh==ID_Pcc_mc==ID_Vmc) and (ID_Vsh in sh_ids) and (ID_Vmc in mc_ids)   # interesecc de parametros mc y sheath
                if ok:
                    sh_sigma  = sh_Pcc[i_Pcc_sh]*sh_dt_Pcc[i_Pcc_sh]*sh_V[i_Vsh]
                    mc_sigma  = mc_Pcc[i_Pcc_mc]*mc_dt_Pcc[i_Pcc_mc]*mc_V[i_Vmc]
                    co_var[i] = sh_sigma/mc_sigma        # ratio de densidades: (\sigma de la sheath)/(\sigma de la mc)
                    i+=1

sh_var *= 86400.*1e5            # [1/cm2]
#---------------------------------- begin: figura
XRANGE  = [0., 0.7] #[0., 1.4e14]
fig     = figure(1, figsize=(6,4))
ax      = fig.add_subplot(111)

h, x    = np.histogram(co_var, bins=nbins, range=XRANGE, normed=True)
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
ax.set_xlabel('$\sigma_{sh}$ / $\sigma_{mc}$  [1]')
ax.set_ylabel('[%]')
ax.set_xlim(XRANGE)
ax.set_ylim(0., 40.)

fname_fig = '%s/_hist.co_%s.png' % (DIR_FIGS, FNAMEs)
savefig(fname_fig, format='png', dpi=135, bbox_inches='tight')
close()
print " -------> genere: %s" % fname_fig
#---------------------------------- end: figura
sh_f_in.close()
##
