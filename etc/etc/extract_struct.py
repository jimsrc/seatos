#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
from datetime import datetime, time, timedelta
from shared import shared_funcs as sf
import numpy as np
import argparse, os


#--- retrieve args
parser = argparse.ArgumentParser(
formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
'-InpACE', '--inp_ace',
type=str,
default='{HOME}/data_ace/64sec_mag-swepam/ace.1998-2014.nc'.format(**os.environ),
help='input filename of ACE data',
)
parser.add_argument(
'-dd', '--dir_data',
type=str,
default='../ascii',
help='directory for output data',
)
parser.add_argument(
'-dp', '--dir_plot',
type=str,
default='../plots',
help='directory for output plots',
)
parser.add_argument(
'-lim', '--limits',
type=float,
nargs=2,
default=[550.,3000.],
help='limits for the values of the Vsw (SW speed), to define\
 a filter of events. Recommended partition: 100, 450, 550, 3000.'
)
parser.add_argument(
'-ts', '--tshift',
action='store_true',
default=False,
help='to perform a time-shift to ACE data, so that the\
time-stamps of data is consistent with Richardson\'s list of\
ICME borders.'
)
parser.add_argument(
'-if', '--icme_flag',
type=str,
default='2',
help="""
list of Richardson's ICME-flags. They are: 
'0' for irregulars,
'1' for smooth B rotation,
'2' for MCs,
and '2H' for MCs by Huttunen etal05.
To specify several flags, separe by dots (e.g. '0.1.2H').
"""
)

pa = parser.parse_args()



class boundaries:
    def __init__(self):
        name = 'name'

HOME                = os.environ['HOME']
gral                = sf.general()
day                 = 86400.
#---- cosas input
gral.fnames = fnames = {}
fnames['ACE']       = pa.inp_ace #'%s/data_ace/64sec_mag-swepam/ace.1998-2014.nc' % HOME
fnames['McMurdo']   = '%s/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat' % HOME
#fnames['table_richardson']  = '../../../../data_317events_iii.nc'
#fnames['table_richardson']  = '%s/ASOC_ICME-FD/icmes_richardson/data/data_317events_iii.nc' % HOME
fnames['table_richardson']  = '%s/ASOC_ICME-FD/icmes_richardson/data/rich_events_ace.nc' % HOME

#---- directorios de salida
gral.dirs =  dirs   = {}
dirs['dir_plots']   = pa.dir_plot #'../plots'
dirs['dir_ascii']   = pa.dir_data #'../ascii'
dirs['suffix']      = '_test_Vmc_'    # sufijo para el directorio donde guardare


#------- seleccionamos MCs con label-de-catalogo (lepping=2, etc)
#MCwant  = {'flags':     ('0', '1', '2', '2H'),
#           'alias':     '0.1.2.2H'}       # para "flagear" el nombre/ruta de las figuras
#MCwant  = {'flags':     ('1', '2', '2H'),
#           'alias':     '1.2.2H'}         # para "flagear" el nombre/ruta de las figuras
#MCwant  = {'flags':     ('2', '2H'),
#           'alias':     '2.2H'}           # para "flagear" el nombre/ruta de las figuras
MCwant  = {'flags':     pa.icme_flag.split('.'), #('2',),
           'alias':     pa.icme_flag } #'2'}            # para "flagear" el nombre/ruta de las figuras

FILTER                  = {}
FILTER['Mcmultiple']    = False # True para incluir eventos multi-MC
FILTER['CorrShift']     = pa.tshift #True
FILTER['wang']          = True #False #True
FILTER['vsw_filter']    = True
FILTER['z_filter_on']   = False
FILTER['MCwant']        = MCwant
FILTER['B_filter']      = False
FILTER['filter_dR.icme'] = False #True

CUTS                    = {}
CUTS['ThetaThres']      = 90.0      # all events with theta>ThetaThres
CUTS['dTday']           = 0.0
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

#--- bordes de estructura
tb = sf.RichTable('{ASO}/icmes_richardson/RichardsonList_until.2016.csv'.format(**os.environ))
tb.read()
bounds      = boundaries()
bounds.tini = tb.tshck      #tb.tini_mc #tb.tshck 
bounds.tend = tb.tini_mc    #tb.tend_mc #tb.tini_mc

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
gral.data_name      = 'ACE'

FILTER['vsw_filter']    = False
emgr    = sf.events_mgr(gral, FILTER, CUTS, bounds, nBin, fgap, tb, None)

#++++ limites
emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = pa.limits
emgr.filter_events()
emgr.load_files_and_timeshift_ii()
emgr.collect_data()

# save to file
#---- dest directory
assert os.path.isdir(pa.dir_data), \
    " ## ERROR ## --> doesn't exist: "+pa.dir_data
dir_dst = '%s/MCflag%s' % (pa.dir_data, FILTER['MCwant']['alias'])
if FILTER['CorrShift']:
    dir_dst += '/wShiftCorr/events_data'
else:
    dir_dst += '/woShiftCorr/events_data'
if not(os.path.isdir(dir_dst)): os.system('mkdir -p '+dir_dst)
#-------------------

events  = emgr.out['events_data'].keys()
n_evnts = len(events)

for id, i in zip(events, range(n_evnts)):
    t        = emgr.out['events_data'][id]['t_days']
    ndata    = len(t)
    data_out = np.nan*np.ones((ndata, 3))
    data_out[:,0] = t
    B = emgr.out['events_data'][id]['B.'+emgr.data_name] # B-data from 'id' event
    rmsB = emgr.out['events_data'][id]['rmsB.'+emgr.data_name] # data from 'id' event
    data_out[:,1] = B
    data_out[:,2] = rmsB
    
    fname_out = '%s/event.data_vlo.%04d_vhi.%04d_id.%s.txt' % (dir_dst, emgr.CUTS['v_lo'], emgr.CUTS['v_hi'], id[3:])
    np.savetxt(fname_out, data_out, fmt='%g')

    # append a legend
    f = open(fname_out, 'a')  # append to file
    dtsh = emgr.dt_sh[int(id[3:])]  # [days] sheath duration
    dtmc = emgr.dt_mc[int(id[3:])]  # [days] MC duration
    COMMS =  '# dt_sheath [days]: %g' % dtsh
    COMMS += '\n# dt_MC [days]: %g' % dtmc
    f.write(COMMS)
    f.close()

print " --> saved in: "+dir_dst

#EOF
