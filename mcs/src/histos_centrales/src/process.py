#!/usr/bin/env ipython
from pylab import *
import numpy as np
import os
import h5py
import funcs as ff
import matplotlib.patches as patches
import matplotlib.transforms as transforms

#+++++++++++++++++++++++++++++++++++++++
import c_rebineo_test as inp

dir_figs    = '../plots'
tnorm       = inp.emgr.out['tnorm']
cent        = (inp.nBin['before'] + 0.5)*inp.nBin['bins_per_utime'] #125   # bin central del MC
wid         = 16 #16  # ancho de la "muestra central" (debe ser PAR!)
h           = {}

# semillas: A, mu, sig
sems = {
    'B'             : [650., 2.8, 0.5],
    'Pcc'           : [400., 2.8, 0.5],
    'V'             : [8*2400., 400., 100.],
    'AlphaRatio'    : [10., -2.3, 1.7],
    'beta'          : [80, -1.6, 1.1],      # probe muchas semillas aqui
    'rmsBoB'        : [15., 0.1, 2.0],
    'Temp'          : [1e2, -1.5, 0.35],    # weird
    'o7o6'          : [10., 0.1, 1.7]
}
#--- limites de los histogramas
xlims = {
    'B'             : [0.0, 35.0],
    'Pcc'           : [0.0, 20.0],
    'V'             : [300.0, 800.0],
    'AlphaRatio'    : [0.0, 0.2],
    'beta'          : [0.0, 0.8],
    'rmsBoB'        : [0.0, 0.06],
    'Temp'          : [0.0, (8e4/1e5)],    # weird
    'o7o6'          : [0.0, 2.3]
}

label = {
    'B'             : 'B',
    'Pcc'           : 'proton density',
    'V'             : 'V',
    'AlphaRatio'    : 'alpha ratio',
    'beta'          : 'beta',
    'rmsBoB'        : 'rmsBoB',
    'Temp'          : 'Temperature',    
    'o7o6'          : 'O7/O6'
}

dperc = 33.3
# generamos histogramas y sus fiteos log-normales
for varname in inp.emgr.rebined_data.keys():
    n_events, nbins_total   = inp.emgr.rebined_data[varname].shape
    c_bins                  = np.nan*np.ones((n_events, wid))
    for i in range(n_events):
        c_bins[i,:] = inp.emgr.rebined_data[varname][i][cent-wid/2:cent+wid/2]  # bines centrales

    cc      = np.isnan(c_bins)
    N       = size(find(~cc))
    data    = c_bins[~cc]
    if varname=='Temp':
        data /= 1e5         # lo quiero en unidades [1e5K]
    perc_0  = np.percentile(data, q=(50.0-0.5*dperc))   # percentil inferior
    perc_1  = np.percentile(data, q=(50.0+0.5*dperc))   # percentil superior
    w_perc  = perc_1-perc_0                             # mi "distribution width"
    med     = np.percentile(data, q=50.0)               # mediana
    avr     = np.mean(data)                             # media
    width   = w_perc/med                                # "ancho normalizado" ("verdadero ancho")
    #hc, hx  = ff.get_histogram(data, nbins=25)
    hc, hx  = ff.get_histogram(data, nbins=30, lims=xlims[varname])
    h[varname] = np.array([hx, hc])
    close()

    sem_A, sem_mu, sem_sig = sems[varname]
    A, mu, sig = ff.make_fit([hx, hc], [sem_A, sem_mu, sem_sig], ff.lognormal)

    #--- figura
    fig     = figure(1, figsize=(6,3))
    ax      = fig.add_subplot(111)
    #TITLE   =  'width=%2.2f\nmean-median=%2.2g' % (width, (avr-med))
    TITLE   =  'mean-median=%2.2g' % ((avr-med))
    ax.set_title(TITLE, fontsize=15)
    # histograma de data
    N = hc.sum()
    LABEL = 'N:%d' % (N)
    ax.plot(hx, hc, '-o', c='black', label=LABEL)
    dx = hx[1]-hx[0]
    #ax.bar(hx, hc, width=dx, align='center', color='black', alpha=.6, label=LABEL)
    ax.axvline(med, ls='--', lw=2, c='black')
    # pinta el "distribution width"
    trans   = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((perc_0, 0.), width=w_perc, height=1,
            transform=trans, color='brown',
            alpha=0.4)
    ax.add_patch(rect1)
    # histograma fiteado
    LABEL = '$\mu=%1.2g$\n$\sigma=%1.2g$' % (mu, sig)
    ax.plot(hx, ff.lognormal(hx, A, mu, sig), '-', c='red', lw=3, label=LABEL, alpha=.7)

    ax.legend(loc='best')
    ax.grid()
    ax.set_xlabel(label[varname], fontsize=13)
    ax.set_ylabel('#', fontsize=13)
    fname_out = dir_figs+'/hist_%s' % varname
    #savefig(fname_out+'.png', dpi=100, bbox_inches='tight')
    savefig(fname_out+'.png', dpi=135, bbox_inches='tight')
    close()
    print " --->  ", varname
    print "     avr, med, A: %g, %g, %g\n" % (avr, med, A)

