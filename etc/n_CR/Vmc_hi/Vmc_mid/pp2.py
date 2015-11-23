#!/usr/bin/env ipython
from pylab import *
from load_data import sh, mc, cr
import share.funcs as ff
#++++++++++++++++++++++++++++++++++++++++++++++++++++

mc.cc   = mc.t>0.0
mc.tout = 3.0*mc.t[mc.cc]+1.0
mc.rms  = mc.avr[mc.cc]
cr.mc.crs   = cr.mc.avr[mc.cc]

sh.cc   = sh.t<1.0
sh.tout = sh.t[sh.cc]
sh.rms  = sh.avr[sh.cc]
cr.sh.crs   = cr.sh.avr[sh.cc]

tpre    = 0.0 #-1.0  # tiempo antes del cual se toma data para el rms-del-quiet-SW
rms_o   = np.mean(sh.rms[sh.t<tpre]) #0.06 #0.025 #np.mean(sh.rms[sh.t<-1.0]) #0.03
t       = np.concatenate([sh.tout, mc.tout])
rms     = np.concatenate([sh.rms, mc.rms])
crs     = np.concatenate([cr.sh.crs, cr.mc.crs])
t, rms, crs  = t[t>=0.0], rms[t>=0.0], crs[t>=0.0]
dt      = t[1:-1] - t[0:-2]
cte     = 0.0
#q       = -440.0 #-170.0

#--- 'fc' es la version trozos de 'rms'
cc      = ((rms-rms_o)>=0.0) & (t<5.0)
fc      = np.zeros(rms.size)
fc[cc]  = (rms-rms_o)[cc]

#tau = 3.0
#ncr = nCR2([t, fc], tau, q)

#++++++++++++++++++++++++++++++++++++++++++++++++ figura
fig     = figure(1, figsize=(6,4))
ax0     = fig.add_subplot(111)
ax1     = ax0.twinx()
#--- plot der
ax1.plot(t[1:-1], fc[1:-1], c='gray')

tau_o, q, off   = 5., -6., 0.1 #2.0, -400.0
fit         = ff.fit_forbush([t, fc, crs], [tau_o, q, off])
fit.make_fit()
print fit.par
#ncr     = nCR2([t, fc], tau, q)

"""
#--- plot izq
ax0.plot(t, ncr, label='$\\tau=%2.2g$'%tau)

ax0.plot(t, crs, '-o', c='k', ms=3)
ax0.axhline(y=0.0, c='g')
ax0.axvline(x=0, ls='--', c='gray', lw=3)
ax0.axvline(x=1, ls='--', c='gray', lw=3)
ax0.axvline(x=4, ls='--', c='gray', lw=3)
ax0.legend()
ax0.grid()
ax0.set_xlim(-2,+7)
ax0.set_ylim(-10, +5.)

fname_fig = './test_2.png'
savefig(fname_fig, dpi=135, bbox_inches='tight')
close()
"""
