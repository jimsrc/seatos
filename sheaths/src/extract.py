#!/usr/bin/env ipython
from pylab import *
from numpy import *
from scipy.io.netcdf import netcdf_file
from datetime import datetime, time, timedelta
#------------ shared libraries:
"""
--- antes de modificar cosas, tener en cuenta los bugs en: 
'../../shared_lib/COMENTARIOS.txt' 
"""
import sys
sys.path.append('../../shared_lib')
from shared_funcs import * #c_funcs import *
#------------------------------
#from read_NewTable import tshck, tini_icme, tend_icme, tini_mc, tend_mc, n_icmes, MCsig
from ShiftTimes import *
import numpy as np
from z_expansion_gulisano import z as z_exp
import console_colors as ccl
import read_NewTable as tb

class boundaries:
    def __init__(self):
        name = 'name'

HOME                = os.environ['HOME']
gral                = general()
day                 = 86400.
#---- cosas input
gral.fnames = fnames = {}
fnames['ACE']       = '%s/data_ace/64sec_mag-swepam/ace.1998-2014.nc' % HOME
fnames['McMurdo']   = '%s/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat' % HOME
#fnames['table_richardson']  = '../../../../data_317events_iii.nc'
#fnames['table_richardson']  = '%s/ASOC_ICME-FD/icmes_richardson/data/data_317events_iii.nc' % HOME
fnames['table_richardson']  = '%s/ASOC_ICME-FD/icmes_richardson/data/rich_events_ace.nc' % HOME

#---- directorios de salida
gral.dirs =  dirs   = {}
dirs['dir_plots']   = '../plots'
dirs['dir_ascii']   = '../ascii'
dirs['suffix']      = '_test_Vmc_'    # sufijo para el directorio donde guardare
                                    # estas figuras

#-------------------------------------------------------------
#------- seleccionamos MCs con label-de-catalogo (lepping=2, etc)
#MCwant  = {'flags':     ('0', '1', '2', '2H'),
#           'alias':     '0.1.2.2H'}       # para "flagear" el nombre/ruta de las figuras
#MCwant  = {'flags':     ('1', '2', '2H'),
#           'alias':     '1.2.2H'}         # para "flagear" el nombre/ruta de las figuras
#MCwant  = {'flags':     ('2', '2H'),
#           'alias':     '2.2H'}           # para "flagear" el nombre/ruta de las figuras
MCwant  = {'flags':     ('2',),
           'alias':     '2'}            # para "flagear" el nombre/ruta de las figuras

FILTER                  = {}
FILTER['Mcmultiple']    = False # True para incluir eventos multi-MC
FILTER['CorrShift']     = True
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
bounds      = boundaries()
bounds.tini = tb.tshck      #tb.tini_mc #tb.tshck 
bounds.tend = tb.tini_mc    #tb.tend_mc #tb.tini_mc

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
gral.data_name      = 'ACE'

FILTER['vsw_filter']    = False
emgr    = events_mgr(gral, FILTER, CUTS, bounds, nBin, fgap, tb, z_exp)
#emgr.run_all()

#++++ limites
LOW, MID1, MID2, TOP = 100.0, 450.0, 550.0, 3000.0

emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP #MID1, MID2 #LOW, MID1 #
#emgr.run_all()
emgr.filter_events()
emgr.load_data_and_timeshift()
emgr.collect_data()

# save to file
#---- dest directory
dir_dst = '../ascii/MCflag%s' % FILTER['MCwant']['alias']
if FILTER['CorrShift']:
    dir_dst += '/wShiftCorr/events_data'
else:
    dir_dst += '/woShiftCorr/events_data'
if not(os.path.isdir(dir_dst)):
    print "\n ### ERROR ### --> does NOT exist: " + dir_dst
    raise SystemExit
#-------------------

events  = emgr.out['events_data'].keys()
n_evnts = len(events)

for id, i in zip(events, range(n_evnts)):
    t        = emgr.out['events_data'][id]['t_days']
    ndata    = len(t)
    data_out = np.nan*np.ones((ndata, 3))
    data_out[:,0] = t
    B = emgr.out['events_data'][id]['B'] # B-data from 'id' event
    rmsB = emgr.out['events_data'][id]['rmsB'] # data from 'id' event
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

"""
emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 # 450.0, 550.0
emgr.run_all()

emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP # 550.0, 3000.0
emgr.run_all()
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
emgr.data_name      = 'McMurdo'

emgr.FILTER['vsw_filter']    = False
emgr.run_all()

emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 # 100.0, 450.0
emgr.run_all()

emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 # 450.0, 550.0
emgr.run_all()

emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP # 550.0, 3000.0
emgr.run_all()
"""
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
