#!/usr/bin/env ipython
from pylab import *
from numpy import *
from scipy.io.netcdf import netcdf_file
from datetime import datetime, time, timedelta
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
import sys, os, argparse
import shared.shared_funcs as sf 
#------------------------------
from shared.ShiftTimes import *
import numpy as np
#from shared.z_expansion_gulisano import z as z_exp
import shared.console_colors as ccl
#import shared.read_NewTable as tb


#--- retrieve args
parser = argparse.ArgumentParser(
formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
'-ace', '--ace',
type=str,
default='{HOME}/data_ace/64sec_mag-swepam/ace.1998-2015.nc'.format(**os.environ),
help='input filename of ACE data',
)
parser.add_argument(
'-mu', '--mcmurdo',
type=str,
default='{HOME}/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat'.format(**os.environ)
)
parser.add_argument(
'-avr', '--avr',
type=str,
default='{ASO}/icmes_richardson/data/rich_events2_ace.nc'.format(**os.environ),
help='.nc file with the average values inside diferent ICME sub-structures.'
)
parser.add_argument(
'-rc', '--rich_csv',
type=str,
default='{ASO}/icmes_richardson/RichardsonList_until.2016.csv'.format(**os.environ),
help='.csv file of Richardson\'s table',
)
parser.add_argument(
'-ah', '--auger_hsts',
type=str,
default='{AUGER_REPO}/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5'.format(**os.environ),
help='.h5 file with Auger charge-histograms data (until temperature-correction).'
)
parser.add_argument(
'-as', '--auger_scls',
default='{PAO}/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5'.format(**os.environ),
help='.h5 file with Auger scalers (until pressure correction).'
)
parser.add_argument(
'-dp', '--dir_plot',
type=str,
default='../plots3',
help='directory for output figures.'
)
parser.add_argument(
'-dd', '--dir_data',
type=str,
default='../ascii3',
help='directory for output data.',
)
parser.add_argument(
'-s', '--suffix',
type=str,
default='__auger__',
help='suffix string used as the name of the last inner\
 output-subdirectory (created automatically)'
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
PAO                 = os.environ['PAO']
PAO_PROCESS         = os.environ['PAO_PROCESS']
gral                = sf.general()
day                 = 86400.
#---- cosas input
gral.fnames = fnames = {}
fnames['ACE']       = pa.ace #'%s/data_ace/64sec_mag-swepam/ace.1998-2015.nc' % HOME
fnames['McMurdo']   = pa.mcmurdo #'%s/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat' % HOME
fnames['Auger_scals']     = pa.auger_scls #'%s/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5' % PAO
#fnames['Auger_BandMuons'] = '%s/data_auger/data_histogramas/all.array.avrs/temp.corrected/shape.ok_and_3pmt.ok/15min/test_temp.corrected.nc' % PAO
fnames['Auger_BandMuons'] = pa.auger_hsts #'{AUGER_REPO}/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5'.format(**os.environ)
fnames['Auger_BandScals'] = fnames['Auger_BandMuons']

fnames['table_richardson']  = pa.avr #'%s/ASOC_ICME-FD/icmes_richardson/data/rich_events2_ace.nc' % HOME
fname_rich = pa.rich_csv #'{ASO}/icmes_richardson/RichardsonList_until.2016.csv'.format(**os.environ)
#for name in fnames.keys():
#    assert os.path.isfile(fnames[name]),\
#        " --> NO EXISTE: " + fnames[name]

tb = sf.RichTable(fname_rich)
tb.read()

#---- directorios de salida
gral.dirs =  dirs   = {}
dirs['dir_plots']   = pa.dir_plot #'../plots3'
dirs['dir_ascii']   = pa.dir_data #'../ascii3'
dirs['suffix']      = '_auger_'    # sufijo para el directorio donde guardare
                                    # estas figuras

#-------------------------------------------------------------
#------- seleccionamos MCs con label-de-catalogo (lepping=2, etc)
MCwant  = {
'flags': pa.icme_flag.split('.'), #('0', '1', '2', '2H'),
'alias': pa.icme_flag, #'0.1.2.2H'}   # para "flagear" el nombre/ruta de las figuras
} 
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
bounds.tini = tb.tshck      #tb.tini_mc #tb.tshck 
bounds.tend = tb.tini_icme    #tb.tend_mc #tb.tini_mc

#++++++++++++++++++++++++++++++++++++++++++++++++ Auger Scalers
gral.data_name      = 'Auger_scals' #'McMurdo' #'ACE'

FILTER['vsw_filter']    = False
emgr = sf.events_mgr(gral, FILTER, CUTS, bounds, nBin, fgap, tb, None, structure='sh.i')
emgr.run_all()
#emgr.lock_IDs()

#++++ limites
LOW, MID1, MID2, TOP = 100.0, 375.0, 450.0, 3000.0
emgr.FILTER['vsw_filter']    = True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 # 100.0, 450.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 # 450.0, 550.0
emgr.run_all()
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP # 550.0, 3000.0
emgr.run_all()

if pa.auger_hsts!='0':
    #++++++++++++++++++++++++++++++++ Auger Band-Scals
    emgr.data_name      = 'Auger_BandScals'

    emgr.FILTER['vsw_filter'] = False
    emgr.run_all()

    #++++ split
    emgr.FILTER['vsw_filter'] = True
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 
    emgr.run_all()
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 
    emgr.run_all()
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP 
    emgr.run_all()

    #++++++++++++++++++++++++++++++++ Auger Band-Muons
    emgr.data_name      = 'Auger_BandMuons'

    emgr.FILTER['vsw_filter'] = False
    emgr.run_all()

    #++++ split
    emgr.FILTER['vsw_filter'] = True
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 
    emgr.run_all()
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 
    emgr.run_all()
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP 
    emgr.run_all()

#++++++++++++++++++++++++++++++++++++++++++++++++ McMurdo
if pa.mcmurdo!='0':
    emgr.data_name      = 'McMurdo'

    emgr.FILTER['vsw_filter']    = False
    emgr.run_all()

    #++++ split
    emgr.FILTER['vsw_filter']    = True
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 
    emgr.run_all()
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 
    emgr.run_all()
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP 
    emgr.run_all()

#++++++++++++++++++++++++++++++++++++++++++++++++ ACE
if pa.ace!='0':
    emgr.data_name      = 'ACE' #'McMurdo'

    emgr.FILTER['vsw_filter']    = False
    emgr.run_all()

    #++++ split
    emgr.FILTER['vsw_filter']    = True
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 
    emgr.run_all()
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 
    emgr.run_all()
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP 
    emgr.run_all()
#EOF
