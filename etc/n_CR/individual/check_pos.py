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
from h5py import File as h5
#++++++++++++++++++++++++++++++++++++++++++++++++++++

class Lim:
    def __init__(self, min_, max_, n):
        self.min = min_
        self.max = max_
        self.n   = n
    def delta(self):
        return (self.max-self.min) / (1.0*self.n)

"""
dir_inp_sh      = '{dir}/sheaths.icmes/ascii/MCflag0.1.2.2H/woShiftCorr/_auger_' .format(dir=env['MEAN_PROFILES_ACE'])
dir_inp_mc      = '{dir}/icmes/ascii/MCflag0.1.2.2H/woShiftCorr/_auger_' .format(dir=env['MEAN_PROFILES_ACE'])
#dir_inp_sh      = '{dir}/sheaths/ascii/MCflag2/wShiftCorr/_test_Vmc_' .format(dir=env['MEAN_PROFILES_ACE'])
#dir_inp_mc      = '{dir}/mcs/ascii/MCflag2/wShiftCorr/_test_Vmc_' .format(dir=env['MEAN_PROFILES_ACE'])
fname_inp_part  = 'MCflag0.1.2.2H_2before.4after_fgap0.2_WangNaN' # '_vlo.100.0.vhi.375.0_CRs.Auger_BandScals.txt'
#fname_inp_part  = 'MCflag2_2before.4after_fgap0.2_Wang90.0'
"""

#CRstr       = 'CRs.Auger_BandScals'
#CRstr       = 'CRs.Auger_BandMuons'
CRstr       = 'CRs.Auger_scals'

vlo, vhi = 100., 375.
#vlo, vhi = 375., 450.
#vlo, vhi = 450., 3000.

dir_inp = '../out/individual'
fname_inp = '{dir}/_nCR_vlo.{lo:5.1f}.vhi.{hi:4.1f}_{name}.h5' .format(dir=dir_inp, lo=vlo, hi=vhi, name=CRstr)

#++++++++++++++++++++++++++++++++++++++++++++++++ ajuste
#--- parameter boundaries && number of evaluations
fi = h5(fname_inp, 'r') # input
fpar = {} # fit parameters
for pname in fi.keys():
    if pname=='grids':
        #fpar[pname] = {}
        for pname_ in fi['grids'].keys():
            # grilla de exploracion con
            # formato: [min, max, delta, nbin]
            fpar['grids/'+pname_] = fi['grids/'+pname_][...]
        continue

    fpar[pname] = fi[pname].value
    #fi[pname] = fit.par[pname]
#print fpar

print " ---> vlo, vhi: ", vlo, vhi 
for nm in fpar.keys():
    if nm.startswith('grids'):
        continue
    min_, max_ = fpar['grids/'+nm][0], fpar['grids/'+nm][1]
    delta = fpar['grids/'+nm][2]
    v = fpar[nm]
    pos = (v - min_)/(max_-min_)
    d = delta/(max_-min_)
    print nm+': ', pos, d, '; \t', v



"""
#--- slice object
rranges = ( 
    slice(tau.min, tau.max, tau.delta()),
    slice(q.min, q.max, q.delta()),
    slice(off.min, off.max, off.delta()),
    slice(bp.min, bp.max, bp.delta()),
    slice(bo.min, bo.max, bo.delta()),
)
"""

#EOF
