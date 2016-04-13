#!/usr/bin/env ipython
from pylab import *
#from load_data import sh, mc, cr
import func_data as fd
import share.funcs as ff
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from os import environ as env
from os.path import isfile, isdir
#++++++++++++++++++++++++++++++++++++++++++++++++++++

dir_inp_sh      = '{dir}/sheaths.icmes/ascii/MCflag0.1.2.2H/woShiftCorr/_auger_/' .format(dir=env['MEAN_PROFILES_ACE'])
dir_inp_mc      = '{dir}/icmes/ascii/MCflag0.1.2.2H/woShiftCorr/_auger_/' .format(dir=env['MEAN_PROFILES_ACE'])
#dir_inp_sh      = '{dir}/sheaths/ascii/MCflag2/wShiftCorr/_test_Vmc_' .format(dir=env['MEAN_PROFILES_ACE'])
#dir_inp_mc      = '{dir}/mcs/ascii/MCflag2/wShiftCorr/_test_Vmc_' .format(dir=env['MEAN_PROFILES_ACE'])
fname_inp_part  = 'MCflag0.1.2.2H_2before.4after_fgap0.2_WangNaN' # '_vlo.100.0.vhi.375.0_CRs.Auger_BandScals.txt'
#fname_inp_part  = 'MCflag2_2before.4after_fgap0.2_Wang90.0'

CRstr           = 'CRs.Auger_BandScals'
mgr             = fd.mgr_data(dir_inp_sh, dir_inp_mc, fname_inp_part)
#sh, mc, cr      = mgr.run(vlo=100.0, vhi=375.0, CRstr=CRstr)
#sh, mc, cr      = mgr.run(vlo=375.0, vhi=450.0, CRstr=CRstr)
sh, mc, cr      = mgr.run(vlo=450.0, vhi=3000.0, CRstr=CRstr)
fname_fig       = '../figs/indiv/nCR_vlo.{lo:4.1f}.vhi.{hi:4.1f}.png' .format(lo=mgr.vlo, hi=mgr.vhi)
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
org_t   = t.copy()
org_crs = crs.copy()
t, rms, crs, B  = t[t>=0.0], rms[t>=0.0], crs[t>=0.0], B[t>=0.0]
dt      = t[1:-1] - t[0:-2]
cte     = 0.0
#q       = -390.0 #-350.0 #-385.01000158 #-440.0 #-170.0

#--- 'fc' es la version trozos de 'rms'
cc      = ((rms-rms_o)>=0.0) & (t<5.0)
fc      = np.zeros(rms.size)
fc[cc]  = (rms-rms_o)[cc]
b       = B

#++++++++++++++++++++++++++++++++++++++++++++++++ figura
fig     = figure(1, figsize=(6,3.))
ax     = fig.add_subplot(111)
#ax1     = ax.twinx()
#--- plot der
#ax1.plot(t[1:-1], fc[1:-1], c='gray')      # rmsB
#ax1.plot(t[1:-1], b[1:-1], c='gray')       # B field


tau_o, q, off   = 5., -6., 0.1 #2.0, -400.0
bp, bo          = -0.1, 10.0

fit     = ff.fit_forbush([t, fc, crs, b], [tau_o, q, off, bp, bo])
fit.make_fit()
print fit.par
#raise SystemExit
"""
tau, bp     = 2.36, 0.0
q, off, bo  = -9.373, 0.89, 16.15
"""
#ncr     = ff.nCR2([t, fc, b], tau, q, off, bp, bo)
ncr     = ff.nCR2([t, fc, b], **fit.par)
sqr     = np.nanmean(np.power(crs - ncr, 2.0))

#--- plot izq
ax.plot(org_t, org_crs, '-o', c='gray', ms=3)
ax.plot(t, ncr, '-', c='red', lw=5, alpha=0.8, label='$\\{tau:3.3g}$'.format(**fit.par))

#++++ region sheath (naranja)
trans   = transforms.blended_transform_factory(ax.transData, ax.transAxes)
rect1   = patches.Rectangle((0., 0.), width=1, height=1, 
            transform=trans, color='orange',
            alpha=0.3)
ax.add_patch(rect1)
#++++ region mc (blue)
trans   = transforms.blended_transform_factory(ax.transData, ax.transAxes)
rect1   = patches.Rectangle((1., 0.), width=3, height=1, 
            transform=trans, color='blue',
            alpha=0.3)
ax.add_patch(rect1)

ax.plot(t, crs, '-o', c='k', ms=3)
#ax.axhline(y=0.0, c='g')
ax.grid()
ax.set_xlabel('time normalized to sheath/MC passage [1]', fontsize=14)
ax.set_ylabel('$n_{CR}$ [%]', fontsize=21)
ax.set_ylim(-1., 0.5)
"""
#+++++ bordes
ax.axvline(x=0, ls='--', c='gray', lw=3)
ax.axvline(x=1, ls='--', c='gray', lw=3)
ax.axvline(x=4, ls='--', c='gray', lw=3)
ax.legend()
ax.grid()
ax.set_ylabel('n_CR  [%]')
ax.set_xlim(-2,+7)
ax.set_ylim(-8, +2.)
"""
savefig(fname_fig, dpi=135, bbox_inches='tight')
print " ---> generamos: " + fname_fig
close()
"""
#+++++ guardo ajuste en ascii
out = np.array([t, ncr, crs]).T
fname_out = './final_fit.txt'
np.savetxt(fname_out, out, fmt='%8.3g')
print " ---> " + fname_out
"""
