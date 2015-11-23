#!/usr/bin/env ipython
import share.funcs as ff
from load_data import sh, mc, cr
import numpy as np
from lmfit import Parameters
"""
Se corre:
./diff.py 2> diff.txt
"""
#++++++++++++++++++++++++++++++++++++++++++++++++++++

#-- mc:
mc.cc   = mc.t>0.0
mc.tout = 3.0*mc.t[mc.cc]+1.0
mc.rms  = mc.rmsB[mc.cc]
mc.B    = mc.B[mc.cc]
cr.mc.crs   = cr.mc.avr[mc.cc]

#-- sheath
sh.cc   = sh.t<1.0
sh.tout = sh.t[sh.cc]
sh.rms  = sh.rmsB[sh.cc]
sh.B    = sh.B[sh.cc]
cr.sh.crs   = cr.sh.avr[sh.cc]

tpre    = 0.0 #-1.0  # tiempo antes del cual se toma data para el rms-del-quiet-SW
rms_o   = np.mean(sh.rms[sh.t<tpre]) #0.06 #0.025 #np.mean(sh.rms[sh.t<-1.0]) #0.03
t       = np.concatenate([sh.tout, mc.tout])
rms     = np.concatenate([sh.rms, mc.rms])
B       = np.concatenate([sh.B, mc.B])
crs     = np.concatenate([cr.sh.crs, cr.mc.crs])
t, rms, crs, B = t[t>=0.0], rms[t>=0.0], crs[t>=0.0], B[t>=0.0]
dt      = t[1:-1] - t[0:-2]
cte     = 0.0
#q       = -440.0 #-170.0

#--- 'fc' es la version trozos de 'rms'
cc      = ((rms-rms_o)>=0.0) & (t<5.0)
fc      = np.zeros(rms.size)
fc[cc]  = (rms-rms_o)[cc]

#b       = B-5.0
#b[b<=0] = 0.0
b       = B

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++

tau_o, bp   = 3.0, -0.1           # LIBRES
q, off, bo  = -5.53, 0.64, 10.0   # FIJOS 

p   = Parameters()
p.add('q', value=-5.53, vary=False)
p.add('tau', value=3.0, vary=False)
p.add('off', value=0.64, vary=False)
p.add('bp', value=-0.1, vary=False)
p.add('bo', value=10.0, vary=False)

TAUs    = np.linspace(2.5, 12.0, 50)
BPs     = np.linspace(-0.5, 0.0, 50)

for p['tau'].value in TAUs:
    for p['bp'].value in BPs:
        fit     = ff.fit_forbush([t, fc, crs, b], [tau_o, q, off, bp, bo])
        diff    = fit.residuals(p)

#print diff
#diff = ff.nCR2([t, rms, B], tau, q, off, bp, bo)
