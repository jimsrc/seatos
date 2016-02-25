#!/usr/bin/env ipython
from mix_funcs import *

nbins       = 50
MCwant      = '2'
CorrShift   = True #False #True
fgap        = 0.2
WangFlag    = 'NaN' #'NaN' #'130'  #'90'
v_lo        = 100.0 #550.0  #450.0 #100.0
v_hi        = 3000.0 #1500.0 #550.0 #450.0


if CorrShift==True:
    prexShift = 'wShiftCorr'
else:
    prexShift = 'woShiftCorr'

#------------ nro de perfiles promediados por variable (MC)
N_MCs   = {}
fname_nro_mcs   = '../../../mcs/ascii/MCflag%s/%s/n.events_MCflag%s_2before.4after_Wang%s_fgap%1.1f_vlo.%3.1f.vhi.%4.1f_forbush.txt' % (MCwant, prexShift, MCwant, WangFlag, fgap, v_lo, v_hi)
f = open(fname_nro_mcs, 'r')
for line in f:
    ll          = line.split(' ')
    varname, N  = ll[0], ll[1]
    N_MCs[varname] = int(N)
f.close()

#------------ nro de perfiles promediados por variable (sheath)
N_SHs   = {}
fname_nro_shs   = '../../../sheaths/ascii/MCflag%s/%s/n.events_MCflag%s_2before.4after_Wang%s_fgap%1.1f_vlo.%3.1f.vhi.%4.1f_forbush.txt' % (MCwant, prexShift, MCwant, WangFlag, fgap, v_lo, v_hi)
f = open(fname_nro_shs, 'r')
for line in f:
    ll          = line.split(' ')
    varname, N  = ll[0], ll[1]
    N_SHs[varname] = int(N)
f.close()
#-------------------------
run_plot(nbins, MCwant, WangFlag, CorrShift, fgap, N_MCs, N_SHs, v_lo, v_hi)
