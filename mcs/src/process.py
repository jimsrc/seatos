from pylab import *
import numpy as np
import os
import h5py

#+++++++++++++++++++++++++++++++++++++++
import c_rebineo_test as inp

tnorm = inp.emgr.out['tnorm']
cent        = 122
wid         = 5

varname     = 'B'
for varname in inp.emgr.rebined_data.keys():
    n_events, nbins_total   = inp.emgr.rebined_data[varname].shape
    c_bins                  = np.nan*np.ones((n_events, wid))
    for i in range(n_events):
        c_bins[i,:] = inp.emgr.rebined_data[varname][i][cent:cent+wid]  # bines centrales

    cc = np.isnan(c_bins)
    N = size(find(~cc))
    LABEL = '%s\nN:%d' % (varname, N)
    hist(c_bins[~cc], bins=20, label=LABEL)
    legend(); grid()
    fname_out = './histos_centrales/hist_%s' % varname
    savefig(fname_out+'.png', dpi=100, bbox_inches='tight')
    close()



