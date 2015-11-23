#!/usr/bin/env ipython
import os
from pylab import *
from numpy import *
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import console_colors as ccl
import numpy as np

def run_plot(dir_mc, dir_sh, dir_figs, FNAME, nbins, MCwant, WangFlag, fgap, N_MCs, N_SHs):
    #------------------------------
    # NOTA: "N-mcs" y "N-sheaths" chekearlos a ojo!
    # varname, range-for-plot, label, N-mcs, N-sheaths
    VARstf = {}
    VARstf['B']         = [[5., 29.], 'B [nT]']
    VARstf['V']         = [[350., 750.], 'Vsw [km/s]' ]
    VARstf['rmsBoB']    = [[0.015, 0.14], 'rms($\hat B$/|B|) [1]']
    VARstf['beta']      = [[0.03, 10.], '$\\beta$ [1]']
    VARstf['Pcc']       = [[1., 21.], 'proton density [#/cc]']
    VARstf['Temp']      = [[1e4, 4e5], 'Temp [K]']    
    VARstf['AlphaRatio']= [[0.001, 0.09], 'alpha ratio [K]']
    VARstf['CRs']       = [[-0.6, +0.5], 'GCR deviation [%]']

    print ccl.On+" generando figuras en: %s"%dir_figs + ccl.W
    #------------------------------
    #--- lista de variables q voy a plotear
    NAMES_VARstf    = set(VARstf.keys())
    NAMES_Nmc       = set(N_MCs.keys())
    VARNAMES        = NAMES_Nmc.intersection(NAMES_VARstf)
    if len(VARNAMES) == 0:
        print ccl.Rn + "\n ----> no generamos ninguna figura!!" + ccl.W
        raise SystemExit

    #for i in range(nvars):
    for varname in VARNAMES:
        #varname = VARstf[i][0]
        ylims   = VARstf[varname][0]
        ylabel  = VARstf[varname][1]
        Nmc     = N_MCs[varname] #VARstf[i][3]
        Nsh     = N_SHs[varname] #VARstf[i][4]
        fname_var = '%s_%s' % (FNAME, varname)
        fname_sh  = dir_sh+'/'+fname_var+'.txt'
        fname_mc  = dir_mc+'/'+fname_var+'.txt'

        varsh   = loadtxt(fname_sh, unpack=True)
        varmc   = loadtxt(fname_mc, unpack=True)
        cond_sh = varsh[0]<1.0
        cond_mc = varmc[0]>0.0
        #------ sheath
        t_sh        = varsh[0][cond_sh]
        var_med_sh  = varsh[1][cond_sh]
        var_avr_sh  = varsh[2][cond_sh]
        var_std_sh  = varsh[3][cond_sh]
        var_n_sh    = varsh[4][cond_sh]
        #------ mc
        t_mc        = varmc[0][cond_mc]*3. + 1.0
        var_med_mc  = varmc[1][cond_mc]
        var_avr_mc  = varmc[2][cond_mc]
        var_std_mc  = varmc[3][cond_mc]
        var_n_mc    = varmc[4][cond_mc]

        #---------------------------------------------------
        fig = figure(1, figsize=(11, 5.5))
        ax  = fig.add_subplot(111)

        ax.plot(t_sh, var_avr_sh, '-o', alpha=.9, color='black', markeredgecolor='none', markersize=5, label='average')
        ax.plot(t_mc, var_avr_mc, '-o', alpha=.9, color='black', markeredgecolor='none', markersize=5)
        # bandas de errores en sheath
        inf = var_avr_sh-var_std_sh/sqrt(var_n_sh)
        sup = var_avr_sh+var_std_sh/sqrt(var_n_sh)
        ax.fill_between(t_sh, inf, sup, facecolor='gray', alpha=0.5)
        # bandas de errores en MC
        inf = var_avr_mc - var_std_mc/sqrt(var_n_mc)
        sup = var_avr_mc + var_std_mc/sqrt(var_n_mc)
        ax.fill_between(t_mc, inf, sup, facecolor='gray', alpha=0.5)
        # pinta ventana de sheath
        trans   = transforms.blended_transform_factory(
                ax.transData, ax.transAxes)
        rect1   = patches.Rectangle((0., 0.), width=1.0, height=1,
                transform=trans, color='orange',
                alpha=0.3)
        ax.add_patch(rect1)
        # pinta ventana de mc
        rect1   = patches.Rectangle((1., 0.), width=3.0, height=1,
                transform=trans, color='blue',
                alpha=0.2)
        ax.add_patch(rect1)

        ax.plot(t_sh, var_med_sh, '-o', markersize=5 ,alpha=.8, color='red', markeredgecolor='none', label='median')
        ax.plot(t_mc, var_med_mc, '-o', markersize=5 ,alpha=.8, color='red', markeredgecolor='none')
        ax.plot(t_sh, np.zeros(t_sh.size), '--', c='green', alpha=0.7, lw=5)
        ax.plot(t_mc, np.zeros(t_mc.size), '--', c='green', alpha=0.7, lw=5)

        ax.grid()
        ax.set_ylim(ylims);
        ax.set_xlim(-2., 7.)
        ax.legend(loc='upper right')
        ax.set_xlabel('mixed time scale [1]', fontsize=20)
        ax.set_ylabel(ylabel, fontsize=20)
        ax.tick_params(labelsize=20)
        TITLE = '# of MCs: %d \n\
                # of sheaths: %d \n\
                %dbins per time unit \n\
                MCflag: %s \n\
                WangFlag: %s' % (Nmc, Nsh, nbins, MCwant, WangFlag)
        #ax.set_title(TITLE)
        if varname=='beta':
            ax.set_yscale('log')
        fname_fig = dir_figs+'/'+fname_var
        savefig('%s.png'%fname_fig, dpi=200, format='png', bbox_inches='tight')
        print ccl.Rn + " ---> generamos: " + fname_fig + ccl.W
        #savefig('%s.pdf'%fname_fig, dpi=200, format='pdf', bbox_inches='tight')
        #savefig('%s.eps'%fname_fig, dpi=200, format='eps', bbox_inches='tight')
        close()
##
