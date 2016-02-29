#!/usr/bin/env ipython
from mix_funcs import *
import os

nbefore     = 2
nafter      = 4
fgap        = 0.2

MCwant          = '0.1.2.2H' #'2'  #'2' #'2.2H'
CorrShift       = False #True #False #True
WangFlag        = 'NaN' #'90.0' #'NaN' #'130.0'  #'90.0'
vsw_filter      = False #False #True
z_filter_on     = False
B_filter        = False #False #True
filter_dRicme   = False #False #True

#------- nombre generico de archivos
FNAME   = 'MCflag%s_%dbefore.%dafter_fgap%1.1f' % (MCwant, nbefore, nafter, fgap)
FNAME   += '_Wang%s' % (WangFlag) 

#------------ directorios de las nubes y sheaths
if CorrShift:
    prexShift = 'wShiftCorr'
else:
    prexShift = 'woShiftCorr'

dir_mc      = '../../icmes/ascii/MCflag%s/%s' % (MCwant, prexShift) 
dir_sh      = '../../sheaths.icmes/ascii/MCflag%s/%s' % (MCwant, prexShift)
dir_figs    = '../plots/%s/MCflag%s' % (prexShift, MCwant) 

dir_mc      += '/_auger_'
dir_sh      += '/_auger_'
dir_figs    += '/_auger_'

os.system('mkdir -p %s' % dir_figs)     # lo creo si no existe!

print ccl.On + " reading from: "
print " --->  " + dir_mc
print " --->  " + dir_sh
print " output: "
print " --->  " + dir_figs + '\n'
nbins       = 50

#------------ nro de perfiles promediados por variable (ICME)
N_MCs   = {}
fname_nro_mcs   = '%s/n.events_%s.txt' % (dir_mc, FNAME)
print " ---> Abriendo: " + fname_nro_mcs
f = open(fname_nro_mcs, 'r')
for line in f:
    ll          = line.split(' ')
    varname, N  = ll[0], ll[1]
    N_MCs[varname] = int(N)
f.close()

#------------ nro de perfiles promediados por variable (sheath-of-ICME)
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

#EOF
