#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
import shared.shared_funcs as sf
import shared.console_colors as ccl
import numpy as np
import argparse, os
from glob import glob
#--- figures
from pylab import figure, close
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms


#--- funcs
def get_units(obs):
    if any([_nm in obs for _nm in ('B')]) and \
            ('rmsBoB' not in obs) and \
            ('ratio' not in obs):
        return '[nT]'
    elif any([_nm in obs for _nm in ('V')]):
        return '[km/s]'
    elif any([_nm in obs for _nm in ('beta','rmsBoB','ratio')]):
        return '[1]'
    else:
        return '[?]'

def get_meta(fnm):
    meta = {} # meta info
    for line in open(fnm,'r').readlines():
        if not line.startswith('#'):
            continue
        if line.split()[1]=='dt':
            meta['dt'] = float(line.split()[-1])
        if line.split()[1]=='ini':
            # grab all after the first ':', and clear the '\n'
            meta['ini'] = line[-line[::-1].rfind(':')+1:-1] 

    return meta


#--- retrieve args
parser = argparse.ArgumentParser(
formatter_class=argparse.ArgumentDefaultsHelpFormatter,
description="""
Script to mix together time profiles of different structures 
one next to the other. For ex., put the profiles of MCs next to the profiles of sheaths.
Finally, we produce figures of this mixed profiles.
""",
)
parser.add_argument(
'-left', '--left',
type=str,
default='./test',
help='input directory for left part',
)
parser.add_argument(
'-right', '--right',
type=str,
default='./test',
help='input directory for right part',
)
parser.add_argument(
'-plot', '--plot',
type=str,
default='./figs'
)
parser.add_argument(
'-obs', '--obs',
type=str,
nargs='+',
default=['Bmag.ACE1sec','rmsB.ACE1sec'],
help="""
keynames of the variables to extract. 
For ACE, use:
B, rmsB, rmsBoB, V, beta, Pcc, Temp, AlphaRatio.
For Auger_..., use:
CRs.
""",
)
parser.add_argument(
'-ba', '--BefAft',
type=int,
nargs=2,
default=[0,0],
help="""
Fractions of the extraction time-span in units of the time-width 
of the structure. These fractions refer to before and 
after the leading and trailing border respectively. Can 
be float values. 
Must be integers.
""",
)

pa = parser.parse_args()

print "----------------------------"
#--- check
#for idir in (pa.left, pa.right):
for obs in pa.obs:
    print " > checking: "+obs
    # observable name must be between '_' characters
    fnm_ls_left  = glob(pa.left +'/*_%s_*.txt'%obs)
    fnm_ls_right = glob(pa.right+'/*_%s_*.txt'%obs)
    n_left, n_right = len(fnm_ls_left), len(fnm_ls_right)
    assert n_left>0 and n_right>0,\
    """
    we have no files in left-dir (N:{n_left}) or 
    right-dir (N:{n_right}), with the pattern '*_{pattern}_*.txt'
    """.format(n_left=n_left, n_right=n_right, pattern=obs)
    #assert len(fnm_ls)==1,\
    #"""
    #There must be ONLY ONE file in '{dir}' for
    #each observable.
    #This wasn't satisfied for '{obs}', as we have:\n {flist}
    #""".format(
    #    dir=idir, 
    #    obs=obs, 
    #    flist=reduce(lambda x, y: x+y, [' '+_f+'\n' for _f in fnm_ls]),
    #)


#--- all IDs of events w/ some data
id_events = []
#--- grab data from left & right :-)
buff = sf.dummy2()
for obs in pa.obs:
    # list of files on the right
    fnm_ls_right = glob(pa.right+'/*_%s_*.txt'%obs)
    # buffers for left and right
    le, ri = buff[obs].le, buff[obs].ri = sf.dummy2(), sf.dummy2()
    buff[obs].units = get_units(obs)
    # iterate over files, for each observable
    for fnm_left in glob(pa.left+'/*_%s_*.txt'%obs):
        # list of base-filenames on the right
        fnms_right_base = [_f.split('/')[-1] for _f in fnm_ls_right]
        # find match on the right
        if fnm_left.split('/')[-1] in fnms_right_base:
            fnm_right = pa.right +'/'+ fnm_left.split('/')[-1] # right match for this left
            print fnm_right.split('/')[-1]
            assert os.path.isfile(fnm_right) 
            # event id
            ind_id = fnm_left.split('/')[-1].rfind('id.')+3
            id = int(fnm_left.split('/')[-1][ind_id:ind_id+3]) # [int]
            if id not in id_events: id_events.append(id) # collect
            # get data
            le[id].t, le[id].data = np.loadtxt(fnm_left, unpack=True)
            ri[id].t, ri[id].data = np.loadtxt(fnm_right, unpack=True)
            # get widths
            meta = get_meta(fnm_left)
            le[id].dt  = meta['dt']
            le[id].ini = meta['ini']
            meta = get_meta(fnm_right)
            ri[id].dt  = meta['dt']
            ri[id].ini = meta['ini']

print "--> finished i/o"



nr  = 1         # scale for row size
tfac = 24. # '1' to show in days
nobs  = len(pa.obs)
#--- ratio of (right-width)/(left-ratio)
opt = {
'ms'  : 3,
'mec' : 'none',
}
for id in id_events:
    ok = True
    # this event-id must have data in ALL observables
    for obs in pa.obs:
        ok &= id in buff[obs].le.keys() and id in buff[obs].ri.keys()
        ok &= ~np.isnan(np.nanmean(buff[obs].le[id].data)) # any valid data?
        ok &= ~np.isnan(np.nanmean(buff[obs].ri[id].data)) # any valid data?

    if not ok:
        continue # next event-id

    dt_left = buff[obs].le[id].dt
    dt_right = buff[obs].ri[id].dt
    # x-limits for plot
    xlim = -dt_left, dt_left+2.*dt_right
    # new fig
    #fig   = figure(1, figsize=(6,4))
    fig   = plt.figure(1, figsize=(9, 10))
    gs  = GridSpec(nrows=6*nr, ncols=2)
    gs.update(left=0.1, right=0.98, hspace=0.13, wspace=0.15)
    print id
    for obs, io in zip(pa.obs, range(nobs)):
        le, ri = buff[obs].le[id], buff[obs].ri[id]
        #ax    = fig.add_subplot(nobs, 1, io+1)
        ax      = plt.subplot(gs[io*nr:(io+1)*nr, 0:2])
        trans = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
        #--- left
        t, data = le.t, le.data
        # only plot what is BEFORE 'left' structure ends
        cc = t<=dt_left
        _max_le = np.nanmax(data[(cc)&(t>xlim[0])])
        _min_le = np.nanmin(data[(cc)&(t>xlim[0])])
        ax.plot(tfac*t[cc], data[cc], '-ok', **opt)
        #--- right
        t, data = ri.t, ri.data
        # only plot what is AFTER 'right' structure begins
        cc = t>=dt_left
        _max_ri = np.nanmax(data[(cc)&(t<xlim[1])])
        _min_ri = np.nanmin(data[(cc)&(t<xlim[1])])
        ax.plot(tfac*t[cc], data[cc], '-ok', **opt)

        #--- shade for left
        rect1 = patches.Rectangle((0., 0.), width=tfac*dt_left, height=1,
            transform=trans, color='orange',
            alpha=0.3)
        ax.add_patch(rect1)
        #--- shade for right
        rect1 = patches.Rectangle((tfac*dt_left, 0.), width=tfac*dt_right, height=1,
            transform=trans, color='blue',
            alpha=0.3)
        ax.add_patch(rect1)

        #--- deco
        ax.set_xlim(np.min([tfac*xlim[0],-tfac*1.]), tfac*xlim[1])
        ax.set_ylim(top=np.max([_max_le,_max_ri]))
        ax.grid(True)
        ax.set_ylabel(obs.split('.')[0]+' '+buff[obs].units)
        # ticks & labels x
        if io+1==nobs: #n==nvars-1:
            #ax.set_xlabel('time normalized to\nsheath/MC passage [1]', fontsize=11)
            ax.set_xlabel('days since shock\n(%s)'%le.ini)
        else:
            ax.set_xlabel('')
            #ax.get_xaxis().set_ticks([])
            ax.xaxis.set_ticklabels([])

        if obs.split('.')[0] in ('rmsB','rmsB_ratio','beta'):
            #import pdb; pdb.set_trace()
            ax.set_ylim(bottom=np.max([1e-3,np.min([_min_le,_min_ri])]))
            ax.set_yscale('log')

    #--- save
    fname_fig = pa.plot+'/test_%03d.png'%id
    fig.savefig(fname_fig, dpi=100, bbox_inches='tight')
    close(fig)

#EOF
