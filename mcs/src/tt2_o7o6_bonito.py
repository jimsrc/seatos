#!/usr/bin/env ipython
import os
from rebineo_o7o6 import *
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import console_colors as ccl

def makefig(medVAR, avrVAR, stdVAR, nVAR, tnorm, 
        dTday, SUBTITLE, YLIMS, YLAB, fname_fig):
    fig     = figure(1, figsize=(13, 6))#figsize=(6, 3))
    ax      = fig.add_subplot(111)

    ax.plot(tnorm, avrVAR, '-o', c='black', alpha=1., markersize=5, markeredgecolor='none', label='mean')
    ax.plot(tnorm, medVAR, '-o', c='red', alpha=.8, markersize=5, markeredgecolor='none', label='median')
    inf     = avrVAR + stdVAR/sqrt(nVAR)
    sup     = avrVAR - stdVAR/sqrt(nVAR)
    ax.fill_between(tnorm, inf, sup, facecolor='gray', alpha=0.5)
    trans   = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((0., 0.), width=1.0, height=1,
            transform=trans, color='blue',
            alpha=0.3)
    ax.add_patch(rect1)

    ax.legend(loc='upper right')
    ax.grid()
    ax.set_ylim(YLIMS)
    TITLE = SUBTITLE
    LABSIZE = 22
    ax.set_title(TITLE, fontsize=25)
    ax.set_xlabel('time normalized to MC passage time [1]', fontsize=LABSIZE)
    ax.set_ylabel(YLAB, fontsize=LABSIZE)
    ax.tick_params(labelsize=20)
    savefig('%s.png'%fname_fig, format='png', dpi=180, bbox_inches='tight')
    savefig('%s.pdf'%fname_fig, format='pdf', dpi=180, bbox_inches='tight')
    #savefig('%s.eps'%fname_fig, format='eps', dpi=380, bbox_inches='tight')
    close()

def wangflag(ThetaThres):
    if ThetaThres<0:
        return 'NaN'
    else:
        return str(ThetaThres)

#-------------------- para figuras:
Nsh = dVARS[0][0]
WangFlag = 'NaN'#wangflag(ThetaThres)
# prefijo gral para los nombres de los graficos:
if CorrShift:
    prexShift =  'wShiftCorr'
else:
    prexShift = 'woShiftCorr'
DIR_FIGS    = '../plots/MCflag%s/%s/bonito' % (MCwant['alias'], prexShift)
DIR_ASCII   = '../ascii/MCflag%s/%s/bonito' % (MCwant['alias'], prexShift)
try:
    os.system('mkdir -p %s' % DIR_FIGS)
    os.system('mkdir -p %s' % DIR_ASCII)
    print ccl.On + " -------> creando: %s" % DIR_FIGS + ccl.W
    print ccl.On + " -------> creando: %s" % DIR_ASCII + ccl.W
except:
    print ccl.On +  " Ya existe: %s" %DIR_FIGS + ccl.W
    print ccl.On +  " Ya existe: %s" %DIR_ASCII + ccl.W

FNAMEs = 'MCflag%s_%dbefore.%dafter_Wang%s_fgap%1.1f' % (MCwant['alias'], nbefore, nafter, WangFlag, fgap)
FNAME_ASCII = '%s/%s' % (DIR_ASCII, FNAMEs)
FNAME_FIGS  = '%s/%s' % (DIR_FIGS, FNAMEs)

#----------------------------------------------------------------------------------------------------
for i in range(nvars):
    fname_fig = '%s_%s' % (FNAME_FIGS, VARS[i][1])
    print ccl.Rn+ " ------> %s" % fname_fig
    ylims   = VARS[i][2]
    ylabel  = VARS[i][3]
    mediana = dVARS[i][4]
    average = dVARS[i][3]
    std_err = dVARS[i][5]
    nValues = dVARS[i][6]       # nmbr of good values aporting data
    binsPerTimeUnit = nbin/(1+nbefore+nafter)
    #SUBTITLE = '# of MCs: %d' % (nEnough[i])
    SUBTITLE = '# events with >80%% of data: %d' % (nEnough[i]) 

    makefig(mediana, average, std_err, nValues, tnorm,
            dTday, SUBTITLE, ylims, ylabel, fname_fig)

    fdataout = '%s_%s.txt' % (FNAME_ASCII, VARS[i][1])
    dataout = array([tnorm, mediana, average, std_err, nValues])
    print " ------> %s\n" % fdataout + ccl.W
    savetxt(fdataout, dataout.T, fmt='%12.5f')
##
