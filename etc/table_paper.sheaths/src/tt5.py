#!/usr/bin/env ipython
# -*- coding: utf-8 -*-

import sys, os
from tabulate import tabulate
from pylab import find
import numpy as np
# now import stuff from another directory
sys.path.append('../../../shared_lib')
import read_NewTable as tb
import ShiftTimes as st
import shared_funcs as sf

# copia del original
n = len(tb.tshck)
tshck_o = []
for i in range(n):
    tshck_o += [[ tb.tshck[i] ]]

st2 = st.ShiftCorrection(st.ShiftDts, tb.tshck) # shift the shock
ss = len(tb.tshck)
#+++++++++++++++++++++++++++++++++++++++++
HOME                = os.environ['HOME']
gral                = sf.general()
#---- cosas input
gral.fnames = fnames = {}
fnames['ACE']       = '%s/data_ace/64sec_mag-swepam/ace.1998-2014.nc' % HOME
fnames['McMurdo']   = '%s/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat' % HOME
fnames['table_richardson']  = '%s/ASOC_ICME-FD/icmes_richardson/data/rich_events_ace.nc' % HOME

#---- directorios de salida
gral.dirs =  dirs   = {}
dirs['dir_plots']   = '../plots'
dirs['dir_ascii']   = '../ascii'
dirs['suffix']      = '_dummy_'    # sufijo para el directorio donde guardare

MCwant  = {'flags':     ('2',),
           'alias':     '2'}            # para "flagear" el nombre/ruta de las figuras
FILTER                  = {}
FILTER['Mcmultiple']    = False # True para incluir eventos multi-MC
#FILTER['CorrShift']     = True
FILTER['wang']          = True #False #True
FILTER['vsw_filter']    = False #True
FILTER['z_filter_on']   = False
FILTER['MCwant']        = MCwant
FILTER['B_filter']      = False
FILTER['filter_dR.icme'] = False #True

CUTS                    = {}
CUTS['dTday']           = 0.0
CUTS['ThetaThres']      = 90.0      # all events with theta>ThetaThres
"""
CUTS['v_lo']            = 550.0
CUTS['v_hi']            = 3000.0
CUTS['z_lo']            = -50.0
CUTS['z_hi']            = 0.65

nBin                    = {}
nBin['before']          = 2
nBin['after']           = 4
nBin['bins_per_utime']  = 50    # bins por unidad de tiempo
nBin['total']           = (1+nBin['before']+nBin['after'])*nBin['bins_per_utime']
fgap                    = 0.2
"""
#--- bordes de estructura
bounds      = sf.boundaries()
bounds.tini = tb.tini_mc #tb.tini_mc #tb.tshck 
bounds.tend = tb.tend_mc #tb.tend_mc #tb.tini_mc

gral.data_name      = 'ACE'
emgr    = sf.events_mgr(gral, FILTER, CUTS, bounds, None, None, tb, None)
emgr.filter_events()

events      = find(emgr.SELECC)     # IDs of the events
n_events    = len(events)           # nmbr of events
print " ---> tenemos %d eventos!" % n_events

#++++++++++++++++++++++++++++++++++++
# NOTA IMPORTANTE: los shifts estan hechos a los 5min mas cercanos
string = []; c=0
string += [['n', 'shock [yyyy-mm-dd HH:MM]', 'sheath dt', 'MC dt','shift [min]', 'A_FD [%]']]
_dtsh, _dtmc = np.empty(n_events), np.empty(n_events)
for i in range(ss):
    #dt  = st2['dates_shifted'][i] - st2['dates_original'][i]
    ts_shift = st2['dates_shifted'][i]
    ts       = st2['dates_original'][i]
    dt       = ts_shift - ts
    dtt = dt.total_seconds()
    if dtt!=0.0 and (i in events):
        dtsh = (tb.tini_mc[i] - ts).total_seconds()/3600. #[hr] sheath duration
        dtmc = (tb.tend_mc[i] - tb.tini_mc[i]).total_seconds()/3600. #[hr] MC duration
        #print i, dtt, (dtt/60.0)%5. # el ultimo es el resto de 5min
        _dtsh[c], _dtmc[c] = dtsh, dtmc
        c +=1
        yyyy, mm, dd = ts.year, ts.month, ts.day
        HH, MM       = ts.hour, ts.minute
        str_date = '%04d-%02d-%02d %02d:%02d' % (yyyy, mm, dd, HH, MM)
        string += [[ 
                c,              # (id en el paper)
                str_date,       # shock date/time (Richardson time)
                '%2.1f'%dtsh,  # [hr] sheath duration
                dtmc,           # [hr] MC duration
                dtt/60.0,       # [min] shift: shifted-original
                '%2.1f'%emgr.Afd[i]     # [%] Forbush amplitude (mcmurdo)
                ]]

tab = tabulate(string, tablefmt='latex', headers='firstrow')
tab2 = tabulate(string, tablefmt='grid', headers='firstrow')

f = open('./long_table.txt', 'w')
f.write(tab2)
f.close()
#EOF
