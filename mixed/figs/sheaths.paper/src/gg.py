#!/usr/bin/env ipython
from pylab import *
import numpy as np
import console_colors as ccl
from scipy.io.netcdf import netcdf_file
import os
import matplotlib.patches as patches
import matplotlib.transforms as transforms

class gral:
    def __init__(self):
        self.name='name'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def makefig(medVAR, avrVAR, stdVAR, nVAR, tnorm, 
        TEXT, TEXT_LOC, YLIMS, YLAB, fname_fig):
    fig     = figure(1, figsize=(13, 6))
    ax      = fig.add_subplot(111)

    varname = fname_fig[:-4].split('_')[1]
    if(varname == 'Temp'):
        medVAR  /= 1.0e4
        avrVAR  /= 1.0e4
        stdVAR  /= 1.0e4
        YLIMS[0] /= 1.0e4; YLIMS[1] /= 1.0e4
        TEXT_LOC[1] /= 1.0e4

    ax.plot(tnorm, avrVAR, 'o-', color='black', markersize=5, label='mean')
    ax.plot(tnorm, medVAR, 'o-', color='red', alpha=.8, markersize=5, markeredgecolor='none', label='median')
    inf     = avrVAR + stdVAR/np.sqrt(nVAR)
    sup     = avrVAR - stdVAR/np.sqrt(nVAR)
    ax.fill_between(tnorm, inf, sup, facecolor='gray', alpha=0.5)
    trans   = transforms.blended_transform_factory(
                ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((0., 0.), width=1.0, height=1,
                transform=trans, color='blue',
                alpha=0.3)
    ax.add_patch(rect1)

    ax.legend(loc='best', fontsize=20)
    ax.tick_params(labelsize=17)
    ax.grid()
    ax.set_xlim(-1.0, 3.0)
    ax.set_ylim(YLIMS)
    ax.text(TEXT_LOC[0], TEXT_LOC[1], TEXT, fontsize=22)
    ax.set_xlabel('time normalized to MC passage time [1]', fontsize=20)
    ax.set_ylabel(YLAB, fontsize=22)


    if(varname == 'beta'):
        ax.set_yscale('log')
    else:
        ax.set_yscale('linear')


    savefig(fname_fig, format='png', dpi=100, bbox_inches='tight')
    close()


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

dir_inp         = '../../../../mcs/ascii/MCflag2/wShiftCorr'
fname_inp       = 'MCflag2_2before.4after_fgap0.2_Wang90.0'
fname_inp_nro   = dir_inp + '/n.events_' + fname_inp + '.txt'
fnro = open(fname_inp_nro, 'r')

stf = {}
stf['B']    = {
                'label': 'B [T]',
                'ylims': [4., 17.],
                'text_loc': [1.7, 12.0]
                }
stf['V']    = {
                'label': 'Vsw [Km/s]',
                'ylims': [400., 550.],
                'text_loc': [2.0, 410.0]
                }
stf['rmsBoB']    = {
                'label': 'rmsBoB [1]',
                'ylims': [0.01, 0.10],
                'text_loc': [1.7, 0.03]
                }
stf['beta']    = {
                'label': 'beta [1]',
                'ylims': [0.1, 6.0],
                'text_loc': [1.7, 0.2]
                }
stf['Pcc']    = {
                'label': 'proton density [#/cc]',
                'ylims': [2, 17],
                'text_loc': [1.7, 11]
                }
stf['Temp']    = {
                'label': 'Temp ($\\times 10^4$) [K]',
                'ylims': [1e4, 25e4],
                'text_loc': [1.1, 17e4]
                }
stf['AlphaRatio']    = {
                'label': 'alpha ratio [1]',
                'ylims': [0.02, 0.08],
                'text_loc': [-0.95, 0.06]
                }
stf['CRs']    = {
                'label': 'GCR relative rate [%]',
                'ylims': [-5.0, 1.0],
                'text_loc': [2.0, -2.5]
                }


for l in fnro:
    line    = l.split()
    varname = line[0]       # nombre de la variable
    Nfinal  = int(line[1])  # events w/80%% of data (ESTE ME INTERESA!)
    Nselec  = int(line[2])  # # of selected events
    print " %s"%varname, '  Nfinal:%d' % Nfinal, '  Nselec:%d'%Nselec
    mc, sh  = gral(), gral()

    fname_inp_ascii = dir_inp + '/' + fname_inp + '_%s.txt' % varname
    tnorm, mediana, average, std_err, nValues = np.loadtxt(fname_inp_ascii).T

    TEXT        = 'events w/80%% \nof data: %d'  % Nfinal
    TEXT_LOC    = stf[varname]['text_loc'] #1.7, 12.0
    ylims       = stf[varname]['ylims'] #[4., 17.]
    ylabel      = stf[varname]['label'] #'B [nT]'
    fname_fig   = '../figs/fig_%s.png' % varname
    makefig(mediana, average, std_err, nValues, tnorm, TEXT, TEXT_LOC, ylims, ylabel, fname_fig)

