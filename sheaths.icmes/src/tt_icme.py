#!/usr/bin/env ipython
"""
Analisis of sheath-from-icme for Auger Low Energy data

IMPORTANT:
    - Note that 'structure' argument refers to MC, sheath, ICME,
      sheath-of-icme, taking the following possible values:
      'i'       : ICME
      'mc'      : MC
      'sh.i'    : sheath of ICME
      'sh.mc'   : sheath of MC,

      and 'events_mgr.filter_events()' uses this flag to know which 
      average values it will use to filter events.
"""
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
PAO                 = os.environ['PAO']
gral                = general()
day                 = 86400.
#---- cosas input
gral.fnames = fnames = {}
# DATASETS
fnames['ACE']       = '%s/data_ace/64sec_mag-swepam/ace.1998-2015.nc' % HOME
fnames['McMurdo']   = '%s/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat' % HOME
fnames['Auger_scals'] = '%s/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5' % PAO


fnames['table_richardson']  = '%s/ASOC_ICME-FD/icmes_richardson/data/rich_events_ace.nc' % HOME

#---- directorios de salida
gral.dirs =  dirs   = {}
dirs['dir_plots']   = '../plots'
dirs['dir_ascii']   = '../ascii'
dirs['suffix']      = '_auger_'  # sufijo para el directorio donde guardare
                                 # estas figuras

#-------------------------------------------------------------
#------- seleccionamos MCs con label-de-catalogo (lepping=2, etc)
MCwant  = {'flags':     ('0', '1', '2', '2H'),
           'alias':     '0.1.2.2H'}       # para "flagear" el nombre/ruta de las figuras
#MCwant  = {'flags':     ('1', '2', '2H'),
#           'alias':     '1.2.2H'}         # para "flagear" el nombre/ruta de las figuras
#MCwant  = {'flags':     ('2', '2H'),
#           'alias':     '2.2H'}           # para "flagear" el nombre/ruta de las figuras
#MCwant  = {'flags':     ('2',),
#           'alias':     '2'}            # para "flagear" el nombre/ruta de las figuras

FILTER                  = {}
FILTER['Mcmultiple']    = False #True para incluir eventos multi-MC
FILTER['CorrShift']     = False #True
FILTER['wang']          = False #False #True
FILTER['vsw_filter']    = False #True
FILTER['z_filter_on']   = False
FILTER['MCwant']        = MCwant
FILTER['B_filter']      = False
FILTER['filter_dR.icme'] = False #True
FILTER['choose_1998-2006'] = False # False:no excluye el periodo 1998-2006

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
# Analisis de sheath-from-icme para Auger
bounds      = boundaries()
bounds.tini = tb.tshck #tb.tini_mc #tb.tini_mc #tb.tshck 
bounds.tend = tb.tini_icme #tb.tend_mc #tb.tend_mc #tb.tini_mc

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
gral.data_name      = 'Auger_scals' #'McMurdo' #'ACE'

FILTER['vsw_filter']    = False
emgr = events_mgr(gral, FILTER, CUTS, bounds, nBin, fgap, tb, z_exp, structure='i')
emgr.run_all()
emgr.lock_IDs()
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

emgr.data_name      = 'ACE' #'Auger' #'McMurdo'
emgr.run_all()

emgr.data_name      = 'McMurdo' #'Auger' #'McMurdo'
emgr.run_all()

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
