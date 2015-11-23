#!/usr/bin/env ipython
from pylab import *
import numpy as np
from scipy.io.netcdf import netcdf_file
import console_colors as ccl
import os


#++++++++++++++++++++++++++++++++++++++++++++++++++
def get_sigma_p(fname_inp):
    f_in        = netcdf_file(fname_inp, 'r')

    Pcc         = f_in.variables['Pcc'].data
    dt_sh_Pcc   = f_in.variables['dt_sheath_Pcc'].data
    Vsh         = f_in.variables['V'].data
    id_Pcc      = set(f_in.variables['IDs_Pcc'].data)
    id_Vsh      = set(f_in.variables['IDs_V'].data)
    ids         = id_Pcc.intersection(id_Vsh)
    #--------------- calculamos las surface densities
    n       = len(ids)
    var_sh  = np.nan*np.ones(n)
    np_sh   = np.nan*np.ones(n)
    v_sh    = np.nan*np.ones(n)
    dr_sh   = np.nan*np.ones(n)
    i=0
    for ID_Pcc, i_Pcc in zip(id_Pcc, range(len(id_Pcc))):
        for ID_Vsh, i_Vsh in zip(id_Vsh, range(len(id_Vsh))):
            ok = (ID_Pcc==ID_Vsh) and (ID_Vsh in ids)
            if ok:
                dr_sh[i]  = dt_sh_Pcc[i_Pcc]*Vsh[i_Vsh]
                var_sh[i] = Pcc[i_Pcc]*dr_sh[i]
                np_sh[i]  = Pcc[i_Pcc]
                v_sh[i]   = Vsh[i_Vsh]
                i+=1

    var_sh *= 86400.0*1e6
    dr_sh  *= (86400.0)/(1.5e8) # asi resulta en [AU]
    return var_sh, np_sh, v_sh, dt_sh_Pcc, dr_sh

#++++++++++++++++++++++++++++++++++++++++++++++++++


MCwant      = '2'
nbefore     = 2
nafter      = 4
WangFlag    = '90.0' #'NaN'
fgap        = 0.2
#v_lo        = 550.0 #550.0  #450.0 #100.0
#v_hi        = 3000.0 #3000.0 #550.0 #450.0
prexShift   = 'wShiftCorr'

#+++++++++++++++ filtros
#FILTER                      = {}
#FILTER['vsw_filter']        = True #False
#FILTER['B_filter']          = False
#FILTER['filter_dR.icme']    = False


# NOTA: estos directorios deberian existir
dir_suffix  = '/_test_Vmc_'
DIR_FIGS    = '../../../plots/MCflag%s/%s' % (MCwant, prexShift) + dir_suffix
DIR_ASCII   = '../../../ascii/MCflag%s/%s' % (MCwant, prexShift) + dir_suffix
#os.system('mkdir -p %s %s' % (DIR_FIGS, DIR_ASCII)) # si no existen, los creo!
print ccl.On + " ---> leyendo data de: " + DIR_ASCII + ccl.W


LO, HI  = 100.0, 450.0 #100.0, 450.0 #450.0, 550.0 #550.0, 3000.0
FNAMEs = 'MCflag%s_%dbefore.%dafter_fgap%1.1f_Wang%s_vlo.%03.1f.vhi.%04.1f' % (MCwant, nbefore, nafter, fgap, WangFlag, LO, HI)
fname_inp   = '%s/_stuff_%s.nc' % (DIR_ASCII, FNAMEs)
sigma_p0, np0, v0, dtsh0, drsh0 = get_sigma_p(fname_inp)


LO, HI  = 450.0, 550.0 #100.0, 450.0 #450.0, 550.0 #550.0, 3000.0
FNAMEs = 'MCflag%s_%dbefore.%dafter_fgap%1.1f_Wang%s_vlo.%03.1f.vhi.%04.1f' % (MCwant, nbefore, nafter, fgap, WangFlag, LO, HI)
fname_inp   = '%s/_stuff_%s.nc' % (DIR_ASCII, FNAMEs)
sigma_p1, np1, v1, dtsh1, drsh1 = get_sigma_p(fname_inp)


LO, HI  = 550.0, 3000.0 #100.0, 450.0 #450.0, 550.0 #550.0, 3000.0
FNAMEs = 'MCflag%s_%dbefore.%dafter_fgap%1.1f_Wang%s_vlo.%03.1f.vhi.%04.1f' % (MCwant, nbefore, nafter, fgap, WangFlag, LO, HI)
fname_inp   = '%s/_stuff_%s.nc' % (DIR_ASCII, FNAMEs)
sigma_p2, np2, v2, dtsh2, drsh2 = get_sigma_p(fname_inp)



