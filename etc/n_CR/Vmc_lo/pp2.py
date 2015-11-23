#!/usr/bin/env ipython
from pylab import *
from load_data import sh, mc, cr
import share.funcs as ff
#++++++++++++++++++++++++++++++++++++++++++++++++++++

#-- mc:
mc.cc   = (mc.t>0.0) & (mc.t<=2.0)
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

#tau = 3.0
#ncr = nCR2([t, fc], tau, q)

#++++++++++++++++++++++++++++++++++++++++++++++++ figura
fig     = figure(1, figsize=(6,4))
ax0     = fig.add_subplot(111)
ax1     = ax0.twinx()
#--- plot der
ax1.plot(t[1:-1], fc[1:-1], c='gray')

#tau_o, q, off, bp   = 5., -7., 0.1, -0.1 #2.0, -400.0
#tau_o, q, off, bp, bo   = 4.0, -5.53, 0.65, -0.1, 10.0 #2.0, -400.0
#tau_o, bp   = 3.0, -0.1           # LIBRES
#q, off, bo  = -5.53, 0.64, 10.0   # FIJOS

tau_o, q, off   = 5., -6., 0.1 #2.0, -400.0
bp, bo          = -0.1, 10.0

fit     = ff.fit_forbush([t, fc, crs, b], [tau_o, q, off, bp, bo])
fit.make_fit()
print fit.par
#ncr     = nCR2([t, fc], tau, q)


