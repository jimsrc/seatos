#!/usr/bin/env ipython
from mix_funcs import *
import os

nbefore     = 2
nafter      = 4
fgap        = 0.2

MCwant          = '2'  #'2' #'2.2H'
CorrShift       = True #False #True
WangFlag        = '90.0' #'NaN' #'130.0'  #'90.0'
vsw_filter      = False #False #True
z_filter_on     = False
B_filter        = False #False #True
filter_dRicme   = True #False #True

if vsw_filter:  v_lo, v_hi  = 550.0, 3000.0 #450.0, 550.0 #100.0, 450.0 #550.0, 3000.0 #3000.0 #550.0  #450.0 #100.0
if z_filter_on: z_lo, z_hi  = 0.0, 0.0 # 
if B_filter:    B_lo, B_hi  = 15.0, 300.0 #11.0, 15.0 #0.0, 11.0 #14.00, 300.00#15.0, 300.0 #10.0, 14.0 #0.0, 10.0
if filter_dRicme: dR_lo, dR_hi  = 0.3, 3.0 #0.2, 0.3 #0.0, 0.2 #0.3, 0.45 #0.4, 3.0 #0.2, 0.4 #0.0, 0.2

#------- nombre generico de archivos
FNAME   = 'MCflag%s_%dbefore.%dafter_fgap%1.1f' % (MCwant, nbefore, nafter, fgap)
FNAME   += '_Wang%s' % (WangFlag) 
if vsw_filter:      FNAME   += '_vlo.%03.1f.vhi.%04.1f' % (v_lo, v_hi)
if z_filter_on:     FNAME   += '_zlo.%2.2f.zhi.%2.2f' % (z_lo, z_hi)
if B_filter:        FNAME   += '_Blo.%2.2f.Bhi.%2.2f' % (B_lo, B_hi)
if filter_dRicme:   FNAME   += '_dRlo.%2.2f.dRhi.%2.2f' % (dR_lo, dR_hi)


#------------ directorios de las nubes y sheaths
if CorrShift:
    prexShift = 'wShiftCorr'
else:
    prexShift = 'woShiftCorr'


dir_mc      =     '../../../mcs/ascii/MCflag%s/%s' % (MCwant, prexShift) 
dir_sh      = '../../../sheaths/ascii/MCflag%s/%s' % (MCwant, prexShift)
dir_figs    = '../../plots/%s/MCflag%s' % (prexShift, MCwant) 

if vsw_filter:
    dir_mc      += '/_test_Vmc_'
    dir_sh      += '/_test_Vmc_'
    dir_figs    += '/_test_Vmc_'
elif B_filter:
    dir_mc      += '/_test_Bmc_'
    dir_sh      += '/_test_Bmc_'
    dir_figs    += '/_test_Bmc_'
elif filter_dRicme:
    dir_mc      += '/_test_dR.mc_'
    dir_sh      += '/_test_dR.mc_'
    dir_figs    += '/_test_dR.mc_'
else:
    pass
    #dir_suffix  = '_test_Bmc_' #'_test_Vmc_' #'_test_Bmc_' #'_test_dR.mc_'


os.system('mkdir -p %s' % dir_figs)     # lo creo si no existe!

print ccl.On + " reading from: "
print " --->  " + dir_mc
print " --->  " + dir_sh
print " output: "
print " --->  " + dir_figs + '\n'
nbins       = 50

#------------ nro de perfiles promediados por variable (MC)
N_MCs   = {}
fname_nro_mcs   = '%s/n.events_%s.txt' % (dir_mc, FNAME)
print " ---> Abriendo: " + fname_nro_mcs
f = open(fname_nro_mcs, 'r')
for line in f:
    ll          = line.split(' ')
    varname, N  = ll[0], ll[1]
    N_MCs[varname] = int(N)
f.close()

#------------ nro de perfiles promediados por variable (sheath)
N_SHs   = {}
fname_nro_shs   = '%s/n.events_%s.txt' % (dir_sh, FNAME)
print " ---> Abriendo: " + fname_nro_shs
f = open(fname_nro_shs, 'r')
for line in f:
    ll          = line.split(' ')
    varname, N  = ll[0], ll[1]
    N_SHs[varname] = int(N)
f.close()

#-------------------------
os.system('mkdir -p ' + dir_figs)
run_plot(dir_mc, dir_sh, dir_figs, FNAME, nbins, MCwant, WangFlag, fgap, N_MCs, N_SHs)
##
