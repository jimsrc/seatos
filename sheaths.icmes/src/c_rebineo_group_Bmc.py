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
        self.name = 'name'

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
dirs['suffix']      = '_test_Bmc_'    # sufijo para el directorio donde guardare
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

FILTER                   = {}
FILTER['Mcmultiple']     = False # True para incluir eventos multi-MC
FILTER['MCwant']         = MCwant
FILTER['CorrShift']      = True
FILTER['wang']           = True #False #True
FILTER['vsw_filter']     = False #True
FILTER['z_filter_on']    = False
FILTER['B_filter']       = True
FILTER['filter_dR.icme'] = False #True

CUTS                            = {}
CUTS['ThetaThres']              = 90.0 # all events with theta>ThetaThres
CUTS['dTday']                   = 0.0
CUTS['v_lo'], CUTS['v_hi']      = 550.0, 3000.0
CUTS['z_lo'], CUTS['z_hi']      = -50.0, 0.65 
CUTS['B_lo'], CUTS['B_hi']      = 0.0, 0.0
CUTS['dR_lo'], CUTS['dR_hi']    = 0.0, 0.0

nBin                    = {}
nBin['before']          = 2
nBin['after']           = 4
nBin['bins_per_utime']  = 50    # bins por unidad de tiempo
nBin['total']           = (1+nBin['before']+nBin['after'])*nBin['bins_per_utime']
fgap                    = 0.2

#--- bordes de estructura
bounds      = boundaries()
bounds.tini = tb.tini_mc #tb.tini_mc #tb.tshck 
bounds.tend = tb.tend_mc #tb.tend_mc #tb.tini_mc

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
gral.data_name      = 'ACE'

FILTER['B_filter']    = False
emgr    = events_mgr(gral, FILTER, CUTS, bounds, nBin, fgap, tb, z_exp)
emgr.run_all()

#++++ limites
LOW, MID1, MID2, TOP = 0.0, 11.0, 15.0, 300.0

emgr.FILTER['B_filter']    = True
emgr.CUTS['B_lo'], emgr.CUTS['B_hi'] = LOW, MID1 #0.0, 10.0 #15.0 # 300.0
emgr.run_all()

emgr.FILTER['B_filter']    = True
emgr.CUTS['B_lo'], emgr.CUTS['B_hi'] = MID1, MID2 #10.0, 15.0
emgr.run_all()

emgr.FILTER['B_filter']    = True
emgr.CUTS['B_lo'], emgr.CUTS['B_hi'] = MID2, TOP #15.0, 300.0
emgr.run_all()
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
emgr.data_name      = 'McMurdo'

emgr.FILTER['B_filter']    = False
emgr.run_all()

emgr.FILTER['B_filter']    = True
emgr.CUTS['B_lo'], emgr.CUTS['B_hi'] = LOW, MID1 #0.0, 10.0
emgr.run_all()

emgr.FILTER['B_filter']    = True
emgr.CUTS['B_lo'], emgr.CUTS['B_hi'] = MID1, MID2 #10.0, 15.0
emgr.run_all()

emgr.FILTER['B_filter']    = True
emgr.CUTS['B_lo'], emgr.CUTS['B_hi'] = MID2, TOP #15.0, 300.0
emgr.run_all()
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
