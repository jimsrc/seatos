#!/usr/bin/env ipython
from pylab import *
#from load_data import sh, mc, cr
import func_data as fd
import share.funcs as ff
#import CythonSrc.funcs as ff
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

#CRstr           = 'CRs.Auger_BandScals'
#CRstr           = 'CRs.Auger_BandMuons'
CRstr           = 'CRs.Auger_scals'
mgr             = fd.mgr_data(dir_inp_sh, dir_inp_mc, fname_inp_part)
sh, mc, cr      = mgr.run(vlo=100.0, vhi=375.0, CRstr=CRstr)
#sh, mc, cr      = mgr.run(vlo=375.0, vhi=450.0, CRstr=CRstr)
#sh, mc, cr      = mgr.run(vlo=450.0, vhi=3000.0, CRstr=CRstr)
fname_fig       = '../figs/indiv/nCR_vlo.{lo:4.1f}.vhi.{hi:4.1f}_{name}.png' .format(lo=mgr.vlo, hi=mgr.vhi, name=CRstr)
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

##++++++++++++++++++++++++++++++++++++++++++++++++ figura
#fig     = figure(1, figsize=(6,3.))
#ax     = fig.add_subplot(111)

tau_, q_, off_   = 5., -6., 0.1 #2.0, -400.0
bp_, bo_         = -0.1, 10.0

class Lim:
    def __init__(self, min_, max_, n):
        self.min = min_
        self.max = max_
        self.n   = n
    def delta(self):
        return (self.max-self.min) / (1.0*self.n)

tau = Lim(0.2, 10., n=20)
q   = Lim(-20., -0.1, n=20)
off = Lim(0., 1., n=20)
bp  = Lim(-1., 0., n=20)
bo  = Lim(0., 20., n=20)

rranges = ( 
    slice(tau.min, tau.max, tau.delta()),
    slice(q.min, q.max, q.delta()),
    slice(off.min, off.max, off.delta()),
    slice(bp.min, bp.max, bp.delta()),
    slice(bo.min, bo.max, bo.delta()),
)

fit     = ff.fit_forbush([t, fc, crs, b], [tau_, q_, off_, bp_, bo_])
fit.make_fit_brute(rranges)
