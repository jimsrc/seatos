#!/usr/bin/env ipython
from pylab import *
import numpy as np
import console_colors as ccl
from scipy.io.netcdf import netcdf_file
import os
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from numpy import array
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

class gral:
    def __init__(self):
        self.name='name'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def makefig(ax, mc, sh, TEXT, TEXT_LOC, YLIMS, varname):
    LW  = 0.3                # linewidth
    MS  = 1.5
    fmc,fsh = 3.0, 1.0      # escaleos temporales
    if(varname == 'Temp'):
        mc.med      /= 1.0e4; sh.med      /= 1.0e4
        mc.avr      /= 1.0e4; sh.avr      /= 1.0e4
        mc.std_err  /= 1.0e4; sh.std_err  /= 1.0e4
        YLIMS[0]    /= 1.0e4; YLIMS[1] /= 1.0e4
        TEXT_LOC['mc'][1] /= 1.0e4
        TEXT_LOC['sh'][1] /= 1.0e4

    # curvas del mc
    time = fsh+fmc*mc.tnorm
    cc = time>=fsh
    ax.plot(time[cc], mc.avr[cc], 'o-', color='black', markersize=MS, label='mean', lw=LW)
    ax.plot(time[cc], mc.med[cc], 'o-', color='red', alpha=.8, markersize=MS, markeredgecolor='none', label='median', lw=LW)
    # sombra del mc
    inf     = mc.avr + mc.std_err/np.sqrt(mc.nValues)
    sup     = mc.avr - mc.std_err/np.sqrt(mc.nValues)
    ax.fill_between(time[cc], inf[cc], sup[cc], facecolor='gray', alpha=0.5)
    trans   = transforms.blended_transform_factory(
                ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((fsh, 0.), width=fmc, height=1,
                transform=trans, color='blue',
                alpha=0.3)
    ax.add_patch(rect1)

    # curvas del sheath
    time = fsh*sh.tnorm
    cc = time<=fsh
    ax.plot(time[cc], sh.avr[cc], 'o-', color='black', markersize=MS, lw=LW)
    ax.plot(time[cc], sh.med[cc], 'o-', color='red', alpha=.8, markersize=MS, markeredgecolor='none', lw=LW)
    # sombra del sheath
    inf     = sh.avr + sh.std_err/np.sqrt(sh.nValues)
    sup     = sh.avr - sh.std_err/np.sqrt(sh.nValues)
    ax.fill_between(time[cc], inf[cc], sup[cc], facecolor='gray', alpha=0.5)
    #trans   = transforms.blended_transform_factory(
    #            ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((0., 0.), width=fsh, height=1,
                transform=trans, color='orange',
                alpha=0.3)
    ax.add_patch(rect1)

    #ax.legend(loc='best', fontsize=10)
    ax.tick_params(labelsize=10)
    ax.grid()
    ax.set_xlim(-2.0, 7.0)
    ax.set_ylim(YLIMS)
    ax.text(TEXT_LOC['mc'][0], TEXT_LOC['mc'][1], TEXT['mc'], fontsize=7)
    ax.text(TEXT_LOC['sh'][0], TEXT_LOC['sh'][1], TEXT['sh'], fontsize=7)

    if(varname in ('beta','Temp', 'rmsB', 'rmsBoB')):
        ax.set_yscale('log')
    else:
        ax.set_yscale('linear')

    return ax


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
stf = {}
stf['B']    = {
                'label': 'B [nT]',
                'ylims': [5., 29.],
                'text_loc_1': {'mc':[4.5, 15.0], 'sh':[-1.95, 12.0]},
                'text_loc_2': {'mc':[4.5, 18.0], 'sh':[-1.95, 12.0]},
                'text_loc_3': {'mc':[4.5, 12.0], 'sh':[-1.95, 12.0]},
                'nrow': 1
                }
stf['V']    = {
                'label': 'V [km/s]',
                'ylims': [350., 800.],
                'text_loc_1': {'mc':[4.5, 500.0], 'sh':[-1.95, 520.0]},
                'text_loc_2': {'mc':[4.5, 600.0], 'sh':[-1.95, 600.0]},
                'text_loc_3': {'mc':[4.5, 410.0], 'sh':[-1.95, 600.0]},
                'nrow': 2
                }
stf['rmsBoB']    = {
                'label': 'rmsBoB [1]',
                'ylims': [0.015, 0.21],
                'text_loc_1': {'mc':[4.5, 0.020], 'sh':[-1.95, 0.02]},
                'text_loc_2': {'mc':[4.5, 0.095], 'sh':[-1.95, 0.02]},
                'text_loc_3': {'mc':[4.5, 0.099], 'sh':[-1.95, 0.02]},
                'nrow': 6
                }
stf['rmsB']    = {
                'label': 'rmsB [nT]',
                'ylims': [0.1, 4.0],
                'text_loc_1': {'mc':[4.5, 1.0], 'sh':[-1.95, 1.3]},
                'text_loc_2': {'mc':[4.5, 1.0], 'sh':[-1.95, 1.3]},
                'text_loc_3': {'mc':[4.5, 1.0], 'sh':[-1.95, 1.3]}
                }
stf['beta']    = {
                'label': '$\\beta$ [1]',
                'ylims': [0.02, 10.0],
                'text_loc_1': {'mc':[4.5, 0.1], 'sh':[-1.95, 0.2]},
                'text_loc_2': {'mc':[4.5, 0.1], 'sh':[-1.95, 0.2]},
                'text_loc_3': {'mc':[4.5, 0.1], 'sh':[-1.95, 0.2]},
                'nrow': 5
                }
stf['Pcc']    = {
                'label': '$n_p$ [$cm^{-3}$]',
                'ylims': [1, 23],
                'text_loc_1': {'mc':[4.5, 14], 'sh':[-1.95, 16.0]},
                'text_loc_2': {'mc':[4.5, 14], 'sh':[-1.95, 16.0]},
                'text_loc_3': {'mc':[4.5, 11], 'sh':[-1.95, 18.0]},
                'nrow': 3
                }
stf['Temp']    = {
                'label': 'Tp ($\\times 10^4$) [K]',
                'ylims': [1e4, 100e4],
                'text_loc_1': {'mc':[4.5, 18.0e4], 'sh':[-1.95, 20.0e4]},
                'text_loc_2': {'mc':[4.5,  2.0e4], 'sh':[-1.95, 20.0e4]},
                'text_loc_3': {'mc':[4.5,  2.0e4], 'sh':[-1.95, 20.0e4]},
                'nrow': 4
                }
stf['AlphaRatio']    = {
                'label': 'alpha ratio [1]',
                'ylims': [0.02, 0.09],
                'text_loc_1': {'mc':[4.5, 0.022], 'sh':[-1.95, 0.07]},
                'text_loc_2': {'mc':[4.5, 0.022], 'sh':[-1.95, 0.07]},
                'text_loc_3': {'mc':[4.5, 0.022], 'sh':[-1.95, 0.07]}
                }
stf['CRs']    = {
                'label': 'GCR relative rate [%]',
                'ylims': [-8.0, 1.0],
                'text_loc_1': {'mc':[4.5, -4.0], 'sh':[-1.95, -4.5]},
                'text_loc_2': {'mc':[4.5, -7.0], 'sh':[-1.95, -4.5]},
                'text_loc_3': {'mc':[4.5, -7.5], 'sh':[-1.95, -4.5]}
                }

TEXT = {}



dir_figs        = '../figs'
dir_inp_mc      = '../../../../mcs/ascii/MCflag2/wShiftCorr/_test_Vmc_'
dir_inp_sh      = '../../../../sheaths/ascii/MCflag2/wShiftCorr/_test_Vmc_'
vlo     = [100.0, 450.0, 550.0]
vhi     = [450.0, 550.0, 3000.0]
nvars   = len(stf.keys())

print " input: "
print " %s " % dir_inp_mc
print " %s \n" % dir_inp_sh
print " vlo, vhi: ", (vlo, vhi), '\n'
print " nvars: ", nvars
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

i=2
#fig = figure(1, figsize=(12, 15))
f   = plt.figure(1, figsize=(9, 10))
nr  = 1         # scale for row size
gs  = GridSpec(nrows=6*nr, ncols=2*3)
gs.update(left=0.1, right=0.98, hspace=0.13, wspace=0.15)

for i in range(3):
    fname_inp = 'MCflag2_2before.4after_fgap0.2_Wang90.0_vlo.%3.1f.vhi.%3.1f' % (vlo[i], vhi[i])
    fname_inp_nro_mc   = dir_inp_mc + '/n.events_' + fname_inp + '.txt'
    fname_inp_nro_sh   = dir_inp_sh + '/n.events_' + fname_inp + '.txt'
    fnro_mc = open(fname_inp_nro_mc, 'r')
    fnro_sh = open(fname_inp_nro_sh, 'r')
    n       = 1     # number of row
    print " ______ col %d ______" % i
    
    for lmc, lsh in zip(fnro_mc, fnro_sh):
        l_mc    = lmc.split()
        l_sh    = lsh.split()
        varname = l_mc[0]       # nombre de la variable
        if varname in ('AlphaRatio', 'CRs', 'rmsB'):
            continue

        n       = stf[varname]['nrow']
        #nax     = 3*(n-1) + i+1 #(i+1)*n   # axis index

        ax      = plt.subplot(gs[(n-1)*nr:n*nr, (2*i):(2*(i+1))])
        #ax      = fig.add_subplot(nvars, 3, nax)
        Nfinal_mc, Nfinal_sh  = int(l_mc[1]), int(l_sh[1])
        print " %s"%varname, '  Nfinal_mc:%d' % Nfinal_mc, 'Nfinal_sh:%d' % Nfinal_sh
        #print " nax: %d" % nax
        mc, sh  = gral(), gral()

        fname_inp_mc = dir_inp_mc + '/' + fname_inp + '_%s.txt' % varname
        fname_inp_sh = dir_inp_sh + '/' + fname_inp + '_%s.txt' % varname
        mc.tnorm, mc.med, mc.avr, mc.std_err, mc.nValues = np.loadtxt(fname_inp_mc).T
        sh.tnorm, sh.med, sh.avr, sh.std_err, sh.nValues = np.loadtxt(fname_inp_sh).T

        # nro de datos con mas del 80% non-gap data
        TEXT['mc']  = 'events: %d'  % Nfinal_mc
        TEXT['sh']  = 'events: %d'  % Nfinal_sh
        if(vlo[i]==100.0):
            TEXT_LOC    = stf[varname]['text_loc_1'] #1.7, 12.0
        elif(vlo[i]==450.0):
            TEXT_LOC    = stf[varname]['text_loc_2'] #1.7, 12.0
        elif(vlo[i]==550.0):
            TEXT_LOC    = stf[varname]['text_loc_3'] #1.7, 12.0
        else:
            print " ----> ERROR con 'v_lo'!"
            raise SystemExit

        ylims       = array(stf[varname]['ylims']) #[4., 17.]
        ylabel      = stf[varname]['label'] #'B [nT]'
        ax = makefig(ax, mc, sh, TEXT, TEXT_LOC, ylims, varname)

        # ticks & labels x
        if n==6: #n==nvars-1:
            ax.set_xlabel('time normalized to\nsheath/MC passage [1]', fontsize=11)
        else:
            ax.set_xlabel('')
            #ax.get_xaxis().set_ticks([])
            ax.xaxis.set_ticklabels([])

        # ticks & labels y
        if i==0:
            ax.set_ylabel(ylabel, fontsize=13)
        else:
            ax.set_ylabel('')
            #ax.get_yaxis().set_ticks([])
            ax.yaxis.set_ticklabels([])

        #n += 1  # next row/axis

    fnro_mc.close()
    fnro_sh.close()

#fig.tight_layout()
#fname_fig   = dir_figs + '/fig_vlo.%3.1f_vhi.%3.1f_%s.png'%(vlo, vhi, varname)
fname_fig = '%s/figs_splitted_1.png' % dir_figs
savefig(fname_fig, dpi=150, bbox_inches='tight')
close()

print "\n output en:\n %s\n" % fname_fig
#EOF
