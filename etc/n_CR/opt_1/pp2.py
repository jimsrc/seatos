#!/usr/bin/env ipython
from pylab import *
from load_data import sh, mc, cr
import funcs as ff

mc.cc   = mc.t>0.0
mc.tout = 3.0*mc.t[mc.cc]+1.0
mc.rms  = mc.avr[mc.cc]
cr.mc.crs   = cr.mc.avr[mc.cc]

sh.cc   = sh.t<1.0
sh.tout = sh.t[sh.cc]
sh.rms  = sh.avr[sh.cc]
cr.sh.crs   = cr.sh.avr[sh.cc]

rms_o   = 0.025 #np.mean(sh.rms[sh.t<-1.0]) #0.03 #np.mean(sh.rms[sh.t<-1.0])
t       = np.concatenate([sh.tout, mc.tout])
rms     = np.concatenate([sh.rms, mc.rms]) - rms_o
crs     = np.concatenate([cr.sh.crs, cr.mc.crs])
t, rms, crs  = t[t>=0.0], rms[t>=0.0], crs[t>=0.0]
f       = np.zeros(rms.size)
f[rms>=0] = rms[rms>=0.0]
dt      = t[1:-1] - t[0:-2]
cte     = 0.0
q       = -170.0
tau_o   = 2.0
#fit     = ff.fit_forbush([t, rms, crs], [rms_o, tau_o, q])
fit     = ff.fit_forbush([t, f, crs], [rms_o, tau_o, q])
fit.make_fit()
