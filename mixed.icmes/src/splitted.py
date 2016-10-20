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


#--- retrieve args
parser = argparse.ArgumentParser(
formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
'-g', '--group',
type=str,
default='low',
help='name of the sub-group of events. Can be low, mid, and high.',
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
'-Vs', '--Vsplit',
type=float,
nargs=2,
default=[375.,450.],
help='SW speed values to describe the input partition of \
the sample in three sub-groups of events.',
)
pa = parser.parse_args()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
nbefore, nafter = 2, 4
fgap            = 0.2

MCwant          = '0.1.2.2H' #'2'  #'2' #'2.2H'
CorrShift       = False #True #False #True
WangFlag        = 'NaN' #'90.0' #'NaN' #'130.0'  #'90.0'
vsw_filter      = False #False #True
z_filter_on     = False
B_filter        = False #False #True
filter_dRicme   = False #False #True

#------- nombre generico de archivos
FNAME   = 'MCflag%s_%dbefore.%dafter_fgap%1.1f' % (MCwant, nbefore, nafter, fgap)
FNAME   += '_Wang%s' % (WangFlag) 

#------------ directorios de las nubes y sheaths
if CorrShift:
    prexShift = 'wShiftCorr'
else:
    prexShift = 'woShiftCorr'

os.system('mkdir -p '+pa.plot)

#--- limites se seleccion
LOW, MID1, MID2, TOP = 100.0, pa.Vsplit[0], pa.Vsplit[1], 3000.0
if pa.group=='low':
    vlo, vhi        = LOW, MID1     # rango de velocidad Vmc
elif pa.group=='mid':
    vlo, vhi        = MID1, MID2     # rango de velocidad Vmc
elif pa.group=='high':
    vlo, vhi        = MID2, TOP     # rango de velocidad Vmc
else:
    print " --> wrong group name!\n Exiting..."
    raise SystemExit

fname_inp       = '%s_vlo.%3.1f.vhi.%3.1f' % (FNAME, vlo, vhi)
fname_inp_nro_sh   = pa.left  + '/n.events_' + fname_inp + '.txt'
fname_inp_nro_mc   = pa.right + '/n.events_' + fname_inp + '.txt'
fnro_mc = open(fname_inp_nro_mc, 'r')
fnro_sh = open(fname_inp_nro_sh, 'r')

stf = {}
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
print " vlo, vhi: ", (vlo, vhi), '\n'

for lmc, lsh in zip(fnro_mc, fnro_sh):
    l_mc    = lmc.split()
    l_sh    = lsh.split()
    varname = l_mc[0]       # nombre de la variable
    Nfinal_mc, Nfinal_sh  = int(l_mc[1]), int(l_sh[1])
    print " %s"%varname, '  Nfinal_mc:%d' % Nfinal_mc, 'Nfinal_sh:%d' % Nfinal_sh
    mc, sh  = gral(), gral()

    fname_inp_sh = pa.left  + '/' + fname_inp + '_%s.txt' % varname
    fname_inp_mc = pa.right + '/' + fname_inp + '_%s.txt' % varname
    mc.tnorm, mc.med, mc.avr, mc.std_err, mc.nValues = np.loadtxt(fname_inp_mc).T
    sh.tnorm, sh.med, sh.avr, sh.std_err, sh.nValues = np.loadtxt(fname_inp_sh).T

    # nro de datos con mas del 80% non-gap data
    TEXT['mc']  = 'events: %d'  % Nfinal_mc
    TEXT['sh']  = 'events: %d'  % Nfinal_sh
    if(vlo==LOW):
        TEXT_LOC    = stf[varname]['text_loc_1'] #1.7, 12.0
    elif(vlo==MID1): # 450.0):
        TEXT_LOC    = stf[varname]['text_loc_2'] #1.7, 12.0
    elif(vlo==MID2): # 550.0):
        TEXT_LOC    = stf[varname]['text_loc_3'] #1.7, 12.0
    else:
        print " ----> ERROR con 'v_lo'!"

    ylims       = stf[varname]['ylims'] #[4., 17.]
    ylabel      = stf[varname]['label'] #'B [nT]'
    fname_fig   = pa.plot + '/fig_vlo.%3.1f_vhi.%3.1f_%s.png'%(vlo, vhi, varname)
    makefig(mc, sh, TEXT, TEXT_LOC, ylims, ylabel, fname_fig)

print "\n output en: "
print " %s \n" % pa.plot

#EOF
