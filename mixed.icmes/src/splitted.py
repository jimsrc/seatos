#!/usr/bin/env ipython
from pylab import *
import numpy as np
import console_colors as ccl
from scipy.io.netcdf import netcdf_file
import os, argparse
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from mix_funcs import gral, makefig
from os.path import isdir, isfile
from glob import glob


#--- retrieve args
parser = argparse.ArgumentParser(
formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
'-right', '--right',
type=str,
default='../../icmes/ascii3',
help='input directory for right part',
)
parser.add_argument(
'-left', '--left',
type=str,
default='../../sheaths.icmes/ascii3',
help='input directory for left part',
)
parser.add_argument(
'-plot', '--plot',
type=str,
default='../plots3'
)
parser.add_argument(
'-lim', '--lim',
type=float,
nargs=2,
default=None, # no split by default
help="""
SW speed values to describe the input partition of 
the sample in three sub-groups of events.
Is not specified, we asume that input filenames don't 
include values of velocity splitting.
""",
metavar=('Vsw1','Vsw2'),
)
parser.add_argument(
'-ftext', '--ftext',
action='store_true',
default=False,
help='if not used, we put the number of events in the title.\
Otherwise, we use the text-positions hardcoded in the script.',
)
pa = parser.parse_args()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
os.system('mkdir -p '+pa.plot)

#--- limites se seleccion
if pa.lim is not None:
    vlo, vhi = pa.lim


#--- find our file 'n.events_...txt'
str_vsplit = '_' if pa.lim is None else '_vlo.%3.1f.vhi.%3.1f'%(pa.lim[0], pa.lim[1])
pattern    = 'n.events_*%s.txt' % (str_vsplit)
fnm_ls_le = glob(pa.left+'/'+pattern)
# we should only have ONE!
assert len(fnm_ls_le)==1,\
    """
    --> we have:\n %r\n
    --> we requested:\n %s
    """%(fnm_ls_le, pa.left+'/'+pattern)
# this files have the variable-names and the number 
# of filtered-in events
fnro_mc = open(pa.right+'/'+fnm_ls_le[0].split('/')[-1], 'r')
fnro_sh = open(pa.left +'/'+fnm_ls_le[0].split('/')[-1], 'r')


stf = {}
stf['Bmag.ACE1sec']    = {
    'label': 'B [nT]',
    'ylims': [5., 27.],
    'text_loc_1': {'mc':[4.5, 10.0], 'sh':[-1.95, 12.0]},
    'text_loc_2': {'mc':[4.5, 10.0], 'sh':[-1.95, 12.0]},
    'text_loc_3': {'mc':[4.5, 12.0], 'sh':[-1.95, 12.0]}
    }
stf['rmsB.ACE1sec']    = {
    'label': 'rmsB [nT]',
    'ylims': [0.9, 20.],
    'text_loc_1': {'mc':[4.5, 10.0], 'sh':[-1.95, 12.0]},
    'text_loc_2': {'mc':[4.5, 10.0], 'sh':[-1.95, 12.0]},
    'text_loc_3': {'mc':[4.5, 12.0], 'sh':[-1.95, 12.0]}
    }
stf['rmsB_ratio.ACE1sec']    = {
    'label' : '$\delta B^2_{{\perp}} / \delta B^2_{{\parallel}}$',
    'ylims': [0.8, 100.],
    'text_loc_1': {'mc':[4.5, 2.0], 'sh':[-1.95, 2.0]},
    'text_loc_2': {'mc':[4.5, 2.0], 'sh':[-1.95, 2.0]},
    'text_loc_3': {'mc':[4.5, 2.0], 'sh':[-1.95, 2.0]}
    }
stf['B.ACE']    = {
    'label': 'B [T]',
    'ylims': [3., 14.],
    'text_loc_1': {'mc':[4.5, 10.0], 'sh':[-1.95, 12.0]},
    'text_loc_2': {'mc':[4.5, 10.0], 'sh':[-1.95, 12.0]},
    'text_loc_3': {'mc':[4.5, 12.0], 'sh':[-1.95, 12.0]}
    }
stf['V.ACE']    = {
    'label': 'Vsw [Km/s]',
    'ylims': [300., 600.],
    'text_loc_1': {'mc':[4.5, 500.0], 'sh':[-1.95, 520.0]},
    'text_loc_2': {'mc':[4.5, 600.0], 'sh':[-1.95, 600.0]},
    'text_loc_3': {'mc':[4.5, 410.0], 'sh':[-1.95, 500.0]}
    }
stf['rmsBoB.ACE']    = {
    'label': 'rmsBoB [1]',
    'ylims': [0.015, 0.21],
    'text_loc_1': {'mc':[4.5, 0.020], 'sh':[-1.95, 0.02]},
    'text_loc_2': {'mc':[4.5, 0.095], 'sh':[-1.95, 0.02]},
    'text_loc_3': {'mc':[4.5, 0.099], 'sh':[-1.95, 0.02]}
    }
stf['rmsB.ACE']    = {
    'label': 'rmsB [nT]',
    'ylims': [0.1, 4.],
    'text_loc_1': {'mc':[4.5, 1.0], 'sh':[-1.95, 1.0]},
    'text_loc_2': {'mc':[4.5, 1.0], 'sh':[-1.95, 1.0]},
    'text_loc_3': {'mc':[4.5, 0.8], 'sh':[-1.95, 1.0]}
    }
stf['beta.ACE']    = {
    'label': 'beta [1]',
    'ylims': [0.02, 10.0],
    'text_loc_1': {'mc':[4.5, 0.1], 'sh':[-1.95, 0.2]},
    'text_loc_2': {'mc':[4.5, 0.1], 'sh':[-1.95, 0.2]},
    'text_loc_3': {'mc':[4.5, 0.1], 'sh':[-1.95, 0.2]}
    }
stf['Pcc.ACE']    = {
    'label': 'proton density [#/cc]',
    'ylims': [1, 23],
    'text_loc_1': {'mc':[4.5, 14], 'sh':[-1.95, 16.0]},
    'text_loc_2': {'mc':[4.5, 14], 'sh':[-1.95, 16.0]},
    'text_loc_3': {'mc':[4.5, 11], 'sh':[-1.95, 18.0]}
    }
stf['Temp.ACE']    = {
    'label': 'Temp ($\\times 10^4$) [K]',
    'ylims': [1e4, 100e4],
    'text_loc_1': {'mc':[4.5, 18.0e4], 'sh':[-1.95, 20.0e4]},
    'text_loc_2': {'mc':[4.5,  2.0e4], 'sh':[-1.95, 20.0e4]},
    'text_loc_3': {'mc':[4.5,  2.0e4], 'sh':[-1.95, 20.0e4]}
    }
stf['AlphaRatio.ACE']    = {
    'label': 'alpha ratio [1]',
    'ylims': [0.02, 0.09],
    'text_loc_1': {'mc':[4.5, 0.022], 'sh':[-1.95, 0.07]},
    'text_loc_2': {'mc':[4.5, 0.022], 'sh':[-1.95, 0.07]},
    'text_loc_3': {'mc':[4.5, 0.022], 'sh':[-1.95, 0.07]}
    }
stf['CRs.McMurdo']    = {
    'label': 'GCRs @McMurdo [%]',
    'ylims': [-8.0, 1.0],
    'text_loc_1': {'mc':[4.5, -4.0], 'sh':[-1.95, -4.5]},
    'text_loc_2': {'mc':[4.5, -7.0], 'sh':[-1.95, -4.5]},
    'text_loc_3': {'mc':[4.5, -7.5], 'sh':[-1.95, -4.5]}
    }
stf['CRs.Auger_scals']    = {
    'label': 'GCRs @Auger-scals [%]',
    'ylims': [-1.0, 0.2],
    'text_loc_1': {'mc':[4.5, -0.50], 'sh':[-1.95, -0.5]},
    'text_loc_2': {'mc':[4.5, -0.50], 'sh':[-1.95, -0.5]},
    'text_loc_3': {'mc':[4.5, -0.85], 'sh':[-1.95, -0.5]}
    }
stf['CRs.Auger_BandScals']    = {
    'label': 'GCRs @Auger-BandScals [%]',
    'ylims': [-1.0, 0.2],
    'text_loc_1': {'mc':[4.5, -0.50], 'sh':[-1.95, -0.5]},
    'text_loc_2': {'mc':[4.5, -0.50], 'sh':[-1.95, -0.5]},
    'text_loc_3': {'mc':[4.5, -0.85], 'sh':[-1.95, -0.5]}
    }
stf['CRs.Auger_BandMuons']    = {
    'label': 'GCRs @Auger-BandMuons [%]',
    'ylims': [-1.0, 0.4],
    'text_loc_1': {'mc':[4.5, -0.50], 'sh':[-1.95, -0.5]},
    'text_loc_2': {'mc':[4.5, -0.50], 'sh':[-1.95, -0.5]},
    'text_loc_3': {'mc':[4.5, -0.85], 'sh':[-1.95, -0.5]}
    }

TEXT = {}

print " input: "
print " %s " % pa.left
print " %s \n" % pa.right

for lmc, lsh in zip(fnro_mc, fnro_sh):
    l_mc    = lmc.split()
    l_sh    = lsh.split()
    varname = l_mc[0]       # nombre de la variable
    Nfinal_mc, Nfinal_sh  = int(l_mc[1]), int(l_sh[1])
    print " %s"%varname, '  Nfinal_mc:%d' % Nfinal_mc, 'Nfinal_sh:%d' % Nfinal_sh
    mc, sh  = gral(), gral()

    #--- filename pattern 
    str_vsplit = '_' if pa.lim is None else '_vlo.%3.1f.vhi.%3.1f'%(pa.lim[0], pa.lim[1])
    pattern    = 'MC*%s_%s.txt' % (str_vsplit, varname)
    fnm_ls_le  = glob(pa.left+'/'+pattern)
    assert len(fnm_ls_le)==1
    basename = fnm_ls_le[0].split('/')[-1]

    #--- read data
    fname_inp_sh = pa.left +'/'+basename
    fname_inp_mc = pa.right+'/'+basename
    mc.tnorm, mc.med, mc.avr, mc.std_err, mc.nValues = np.loadtxt(fname_inp_mc).T
    sh.tnorm, sh.med, sh.avr, sh.std_err, sh.nValues = np.loadtxt(fname_inp_sh).T

    #--- text on figure
    # nro de datos con mas del 80% non-gap data
    TEXT['mc']  = ' N: %d'  % Nfinal_mc
    TEXT['sh']  = ' N: %d'  % Nfinal_sh
    #--- position of text
    if pa.ftext:
        if(vlo==LOW):
            TEXT_LOC    = stf[varname]['text_loc_1'] #1.7, 12.0
        elif(vlo==MID1): # 450.0):
            TEXT_LOC    = stf[varname]['text_loc_2'] #1.7, 12.0
        elif(vlo==MID2): # 550.0):
            TEXT_LOC    = stf[varname]['text_loc_3'] #1.7, 12.0
        else:
            print " ----> ERROR con 'v_lo'!"
    else:
        TEXT_LOC = None

    ylims       = stf[varname]['ylims'] #[4., 17.]
    ylabel      = stf[varname]['label'] #'B [nT]'
    fname_fig   = pa.plot + '/fig%s_%s.png'%(str_vsplit, varname)
    makefig(mc, sh, TEXT, ylims, ylabel, fname_fig, pa.ftext, TEXT_LOC)


print "\n output en: "
print " %s \n" % pa.plot

#EOF
