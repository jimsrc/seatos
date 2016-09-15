#!/usr/bin/env ipython
from pylab import *
from numpy import *
from scipy.io.netcdf import netcdf_file
from datetime import datetime, time, timedelta
import argparse
#------------ shared libraries:
"""
--- antes de modificar cosas, tener en cuenta los bugs en: 
'../../shared_lib/COMENTARIOS.txt' 

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

#--- retrieve args
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
'-auger', '--inp_auger',
type=str,
default=None,
help='input filename of Auger histograms-data'
)
parser.add_argument(
'-fig', '--dir_fig',
type=str,
default='../plots',
help='output directory for figures'
)
parser.add_argument(
'-prof', '--dir_prof',
type=str,
default='../ascii',
help='output directory for data of built mean-profiles'
)

pa = parser.parse_args()


HOME                = os.environ['HOME']
PAO                 = os.environ['PAO']
PAO_PROCESS         = os.environ['PAO_PROCESS']
gral                = general()
day                 = 86400.
#---- cosas input
gral.fnames = fnames = {}
fnames['ACE']       = '%s/data_ace/64sec_mag-swepam/ace.1998-2015.nc' % HOME
fnames['McMurdo']   = '%s/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat' % HOME
fnames['Auger_scals']     = '%s/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5' % PAO
fnames['Auger_BandMuons'] = pa.inp_auger #'%s/data_auger/data_histogramas/all.array.avrs/temp.corrected/shape.ok_and_3pmt.ok/15min/test_temp.corrected.nc' % PAO
fnames['Auger_BandMuons_avrs'] = '%s/long_trends/code_figs/avr_histos_press_shape.ok_and_3pmt.ok.txt' % PAO_PROCESS  # average histogram
fnames['Auger_BandScals'] = fnames['Auger_BandMuons']
fnames['Auger_BandScals_avrs'] = fnames['Auger_BandMuons_avrs']

fnames['table_richardson']  = '%s/ASOC_ICME-FD/icmes_richardson/data/rich_events_ace.nc' % HOME
for name in fnames.keys():
    assert isfile(fnames[name]),\
        " --> NO EXISTE: " + fnames[name]

#---- directorios de salida
gral.dirs =  dirs   = {}
dirs['dir_plots']   = pa.dir_fig  #'../plots'
dirs['dir_ascii']   = pa.dir_prof #'../ascii'
dirs['suffix']      = '_auger_'    # sufijo para el directorio donde guardare
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
FILTER['Mcmultiple']    = False # True para incluir eventos multi-MC
FILTER['CorrShift']     = False #True
FILTER['wang']          = False #True #False #True
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
bounds      = boundaries()
bounds.tini = tb.tini_icme    #tb.tshck      #tb.tini_mc #tb.tshck 
bounds.tend = tb.tend_icme    #tb.tend_mc #tb.tini_mc

#++++++++++++++++++++++++++++++++++++++++++++++++ Auger Scalers
gral.data_name      = 'Auger_scals' #'McMurdo' #'ACE'

FILTER['vsw_filter']    = False
emgr = events_mgr(gral, FILTER, CUTS, bounds, nBin, fgap, tb, z_exp, structure='i')
emgr.run_all()
emgr.lock_IDs()

#++++ limites
LOW, MID1, MID2, TOP = 100.0, 375.0, 450.0, 3000.0
emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 # 100.0, 450.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 # 450.0, 550.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP # 550.0, 3000.0
emgr.run_all()

#++++++++++++++++++++++++++++++++++++++++++++++++ Auger Band-Scals
emgr.data_name      = 'Auger_BandScals'

emgr.FILTER['vsw_filter'] = False
emgr.run_all()

#++++ split
emgr.FILTER['vsw_filter'] = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 # 100.0, 450.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 # 450.0, 550.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP # 550.0, 3000.0
emgr.run_all()

#++++++++++++++++++++++++++++++++++++++++++++++++ Auger Band-Muons
emgr.data_name      = 'Auger_BandMuons'

emgr.FILTER['vsw_filter'] = False
emgr.run_all()

#++++ split
emgr.FILTER['vsw_filter'] = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 # 100.0, 450.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 # 450.0, 550.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP # 550.0, 3000.0
emgr.run_all()

#++++++++++++++++++++++++++++++++++++++++++++++++ McMurdo
emgr.data_name      = 'McMurdo'

emgr.FILTER['vsw_filter']    = False
emgr.run_all()

#++++ split
emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 # 100.0, 450.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 # 450.0, 550.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP # 550.0, 3000.0
emgr.run_all()

#++++++++++++++++++++++++++++++++++++++++++++++++ ACE
emgr.data_name      = 'ACE' #'McMurdo'

emgr.FILTER['vsw_filter']    = False
emgr.run_all()

#++++ split
emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 # 100.0, 450.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 # 450.0, 550.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP # 550.0, 3000.0
emgr.run_all()
#EOF
