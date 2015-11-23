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
t, rms, crs, B  = t[t>=0.0], rms[t>=0.0], crs[t>=0.0], B[t>=0.0]
dt      = t[1:-1] - t[0:-2]
cte     = 0.0
#q       = -390.0 #-350.0 #-385.01000158 #-440.0 #-170.0

#--- 'fc' es la version trozos de 'rms'
cc      = ((rms-rms_o)>=0.0) & (t<5.0)
fc      = np.zeros(rms.size)
fc[cc]  = (rms-rms_o)[cc]

#b       = B-17.0
#b[b<=0] = 0.0
b       = B

#tau = 3.0
#ncr = nCR2([t, fc], tau, q)

#++++++++++++++++++++++++++++++++++++++++++++++++ figura
fig     = figure(1, figsize=(6,4))
ax0     = fig.add_subplot(111)
ax1     = ax0.twinx()
#--- plot der
#ax1.plot(t[1:-1], fc[1:-1], c='gray')
ax1.plot(t[1:-1], b[1:-1], c='gray')

#tau_o, bp   = 5.4, -0.076           # LIBRES
#q, off, bo  = -5.53, 0.64, 10.0   # FIJOS
tau_o, bp   = 4.71, 0.0           # LIBRES
q, off, bo  = -6.45, 0.0, 10.0   # FIJOS

tau_o, bp   = 4.18, -0.9
q, off, bo  = -6.02, 0.0, 11.87

for tau in (3.0, 10.0, tau_o):#, 4.0):
    #ncr     = ff.func_nCR([t, fc], 0.0, tau, q)
    ncr     = ff.nCR2([t, fc, b], tau, q, off, bp, bo)
    sqr     = np.nanmean(np.power(crs - ncr, 2.0))
    print sqr
    #--- plot izq
    ax0.plot(t, ncr, lw=3, label='$\\tau=%3.3g$'%tau)

ax0.plot(t, crs, '-o', c='k', ms=3)
ax0.axhline(y=0.0, c='g')
ax0.axvline(x=0, ls='--', c='gray', lw=3)
ax0.axvline(x=1, ls='--', c='gray', lw=3)
ax0.axvline(x=4, ls='--', c='gray', lw=3)
ax0.legend()
ax0.grid()
ax0.set_ylabel('n_CR  [%]')
ax0.set_xlim(-2,+7)
ax0.set_ylim(-3, +2.)

fname_fig = './test_2.png'
savefig(fname_fig, dpi=135, bbox_inches='tight')
close()

#+++++ guardo ajuste en ascii
out = np.array([t, ncr, crs]).T
fname_out = './final_fit.txt'
np.savetxt(fname_out, out, fmt='%8.3g')
print " ---> " + fname_out
