#!/usr/bin/env ipython
"""
Script to monitor the performance and 
convergence of metho LBFGS

See:
http://www.ece.northwestern.edu/~morales/PSfiles/acm-remark.pdf
Also implementations:
scipy/optimize/__init__.py
minimize() @
~/my_projects/scipy/scipy/optimize/_minimize.py
"""
from pylab import *
#from load_data import sh, mc, cr
import func_data as fd
import share.funcs as ff
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from os import environ as env
from os.path import isfile, isdir
import argparse, itertools, sys
#++++++++++++++++++++++++++++++++++++++++++++++++++++

def str_to_other(mystr):
    """
    a callable type for my argparse
    See:
    https://docs.python.org/2/library/argparse.html?highlight=argparse#type
    """
    f1, f2, f3 = map(float, mystr.split(' '))
    return [f1, f2, int(f3)]

#--- retrieve args
parser = argparse.ArgumentParser(
formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
'-left', '--left',
type=str,
default='{MEAN_PROFILES_ACE}/sheaths.icmes/ascii\
    /MCflag0.1.2.2H/woShiftCorr/_auger_'.format(**env),
help='input directory for left part',
)
parser.add_argument(
'-right', '--right',
type=str,
default='{MEAN_PROFILES_ACE}/icmes/ascii\
    /MCflag0.1.2.2H/woShiftCorr/_auger_'.format(**env),
help='input directory for right part',
)
parser.add_argument(
'-pref', '--prefix',
type=str,
default='MCflag0.1.2.2H_2before.4after_fgap0.2_WangNaN',
help='prefix of input filenames (we build the other part\
    of the basename).',
)
parser.add_argument(
'-suff', '--suffix',
type=str,
default='CRs.Auger_scals',
help='suffix of input filenames (we build the other part\
    of the basename).'
)
parser.add_argument(
'-fig', '--fig',
type=str,
default='../figs/indiv/', # if directory, must end in '/'
help='figure full-filename or directory. If directory, it MUST\
    end with \'/\' character, and we build the basename of file.'
)
parser.add_argument(
'-lim', '--lim',
nargs=2,
type=float,
default=[100.0, 375.0],
help='lower & higher threshold values associated to\
    input filenames.',
metavar=('Vmin','Vmax'),
)
#---BEGIN: seeds for fitting
seeds_default = {
'tau'   : [4.8, 5.0, 2],
'q'     : [-2.0, -1.9, 2],
'off'   : [0.15, 0.20, 2],
'bp'    : [-0.15, -0.13, 2],
'bo'    : [8.5, 9.0, 2],
}
for seed_nm, seed_default in seeds_default.iteritems():
    #--- config all seed command-line arguments
    parser.add_argument(
    '-'+seed_nm, '--seed_'+seed_nm,
    nargs=3,
    type=str_to_other,
    default=seed_default,
    help='try seeds uniformly equiparted in a given range, \
     for `'+seed_nm+'` parameter.',
    metavar=('MIN','MAX','BINS'),
    )
#--- END
pa = parser.parse_args()


dir_inp_sh      = pa.left #'{dir}/sheaths.icmes/ascii/MCflag0.1.2.2H/woShiftCorr/_auger_/' .format(dir=env['MEAN_PROFILES_ACE'])
dir_inp_mc      = pa.right #'{dir}/icmes/ascii/MCflag0.1.2.2H/woShiftCorr/_auger_/' .format(dir=env['MEAN_PROFILES_ACE'])
#dir_inp_sh      = '{dir}/sheaths/ascii/MCflag2/wShiftCorr/_test_Vmc_' .format(dir=env['MEAN_PROFILES_ACE'])
#dir_inp_mc      = '{dir}/mcs/ascii/MCflag2/wShiftCorr/_test_Vmc_' .format(dir=env['MEAN_PROFILES_ACE'])
fname_inp_part  = pa.prefix #'MCflag0.1.2.2H_2before.4after_fgap0.2_WangNaN' # '_vlo.100.0.vhi.375.0_CRs.Auger_BandScals.txt'
#fname_inp_part  = 'MCflag2_2before.4after_fgap0.2_Wang90.0'

#CRstr           = 'CRs.Auger_BandScals'
#CRstr           = 'CRs.Auger_BandMuons'
CRstr           = pa.suffix #'CRs.Auger_scals'
mgr             = fd.mgr_data(dir_inp_sh, dir_inp_mc, fname_inp_part)
sh, mc, cr      = mgr.run(vlo=pa.lim[0], vhi=pa.lim[1], CRstr=CRstr)
#sh, mc, cr      = mgr.run(vlo=375.0, vhi=450.0, CRstr=CRstr)
#sh, mc, cr      = mgr.run(vlo=450.0, vhi=3000.0, CRstr=CRstr)

#--- `fig` argument must be full-filename or directory!
if pa.fig=='':
    raise SystemExit(' --> must specify filename or directory!')
elif pa.fig[-1]=='/':
    fname_fig = pa.fig + 'nCR_vlo.{lo:4.1f}.vhi.{hi:4.1f}\
        _{name}.png'.format(lo=mgr.vlo, hi=mgr.vhi, name=CRstr)
else:
    fname_fig = pa.fig
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

_tau  = np.linspace(*pa.seed_tau)
_q    = np.linspace(*pa.seed_q)
_off  = np.linspace(*pa.seed_off)
_bp   = np.linspace(*pa.seed_bp)
_bo   = np.linspace(*pa.seed_bo)
#tau_o, q, off   = 3., -6., 0.1 #2.0, -400.0
#bp, bo          = -0.1, 10.0

data      = np.array([t, fc, crs, b])
_fit, it  = [], 0
all_seeds = list(itertools.product(_tau,_q,_off,_bp,_bo))
for tau_o,q,off,bp,bo in all_seeds:
    print " it, total: ", it+1, len(all_seeds)
    _fit     += [ ff.fit_forbush(data, [tau_o, q, off, bp, bo]) ]
    _fit[it].make_fit(monit=True)
    it       += 1

MinRes = np.array([ _fit[i].resid for i in range(len(_fit)) ])
ind = find(MinRes.min()==MinRes)
for i in ind:
    print _fit[i].niter
    print _fit[i].par

#sys.exit(0)
#print fit.par
"""
tau, bp     = 2.36, 0.0
q, off, bo  = -9.373, 0.89, 16.15
"""

for i in range(len(ind)):
    fit  = _fit[i]
    ncr     = ff.nCR2([t, fc, b], **fit.par)
    sqr     = np.nanmean(np.square(crs - ncr))
    #++++++++++++++++++++++++++++++++++++ figura
    fig     = figure(1, figsize=(6,3.))
    ax     = fig.add_subplot(111)
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
    #+++ save fig
    fig.savefig(fname_fig+'_%d'%i,format='png',dpi=135, bbox_inches='tight')
    print " ---> generamos: " + fname_fig
    close()

"""
#+++++ guardo ajuste en ascii
out = np.array([t, ncr, crs]).T
fname_out = './final_fit.txt'
np.savetxt(fname_out, out, fmt='%8.3g')
print " ---> " + fname_out
"""
