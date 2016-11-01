#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
import numpy as np
import shared.cython_wrapper as cw
import shared.shared_funcs as sf
import shared.readers as rd
import os

m = cw.simple()
subdir = '{HOME}/data_ace/mag_data_1sec'.format(**os.environ)

bartels = rd.get_all_bartels()
bins = 1000
ini, end = 0., 1.
wbin = (end-ini)/bins
hx = np.arange(0., 1., wbin) + 0.5*wbin
hc = np.zeros(bins, dtype=np.int)
dtmin, dtmax = 1e31, 0.

for nm, bart in bartels.iteritems():
    fnm = subdir+'/mag_data_1sec_{bart}.hdf'.format(bart=bart['bartel'])
    if not os.path.isfile(fnm): 
        break
    #print nm, bart['bartel'], bart['date']
    #print fnm, os.path.isfile(fnm)
    t_ace = m.get_data(fnm, 'ACEepoch')
    dt = t_ace[1:] - t_ace[:-1]
    dt_set = np.unique(dt)
    dtmin = np.min([dtmin, dt_set.min()])
    dtmax = np.max([dtmax, dt_set.max()])
    hc[:] += np.histogram(dt_set, bins=bins, range=(ini,end))[0]
"""
result (for ALL THE FILES!):
    dtmin : 0.98999989032745361
    dtmax : 1.0
    dtmax - dtmin: 0.010000109672546387
    dtmax - dtmin > 0.01 == True
"""

#EOF
