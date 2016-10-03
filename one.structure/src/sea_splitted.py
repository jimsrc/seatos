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
import shared.console_colors as ccl

#--- type for argparse
class str_to_other(argparse.Action):
    """
    argparse-action to handle command-line arguments of 
    the form "dd/mm/yyyy" (string type), and converts
    it to datetime object.
    """
    def __init__(self, option_strings, dest, **kwargs):
        #if nargs is not None:
        #    raise ValueError("nargs not allowed")
        super(str_to_other, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        #print '%r %r %r' % (namespace, values, option_string)
        #dd,mm,yyyy = map(int, values.split('/'))
        f1, f2 = map(float, values)
        value = [int(f1), f2]
        setattr(namespace, self.dest, value)


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
parser.add_argument(
'-st', '--struct',
type=str,
default='sh.i', # sheath-of-icme
help='alias name of structure to analyze.\
 Options are "sh.mc", "sh.i", "mc", "i" for sheath-of-mc, \
 sheath-of-icme, mc, and icme respectively.',
)
parser.add_argument(
'-wang', '--wang',
type=str,
nargs=2,
default=[0, 90.0],
help='switch to wether use or not the Wang\'s list of IP shocks.',
action=str_to_other,
metavar=('SWITCH','THRESHOLD'),
)
parser.add_argument(
'-Vs', '--Vsplit',
type=float,
nargs=2,
default=[375.,450.],
help='SW speed values to split in three sub-groups of events.',
)

pa = parser.parse_args()

class boundaries:
    def __init__(self):
        name = 'name'

def run_analysis(em, dname, LOW, MID1, MID2, TOP, lock=False):
    #+++ global
    em.data_name = dname #'Auger_BandScals'
    em.FILTER['vsw_filter'] = False
    em.run_all()
    if lock: 
        em.lock_IDs()

    #+++ split
    em.FILTER['vsw_filter'] = True
    em.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 
    em.run_all()
    em.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 
    em.run_all()
    em.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP 
    em.run_all()



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

#--- read Richardson's table of ICMEs
tb = sf.RichTable(fname_rich)
tb.read()


#---- directorios de salida
gral.dirs =  dirs   = {}
dirs['dir_plots']   = pa.dir_plot #'../plots3'
dirs['dir_ascii']   = pa.dir_data #'../ascii3'
dirs['suffix']      = pa.suffix   # sufijo para el directorio donde guardare
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
FILTER['wang']          = True if pa.wang[0] else False #True #False #True
FILTER['vsw_filter']    = False #True
FILTER['z_filter_on']   = False
FILTER['MCwant']        = MCwant
FILTER['B_filter']      = False
FILTER['filter_dR.icme'] = False #True
FILTER['choose_1998-2006'] = False # False:no excluye el periodo 1998-2006

CUTS                    = {}
CUTS['ThetaThres']      = pa.wang[1] #90.0   # all events with theta>ThetaThres
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
if pa.struct=='sh.i':
    bounds.tini = tb.tshck      #tb.tini_mc #tb.tshck 
    bounds.tend = tb.tini_icme    #tb.tend_mc #tb.tini_mc
elif pa.struct=='sh.mc':
    bounds.tini = tb.tshck
    bounds.tend = tb.tini_mc
elif pa.struct=='i':
    bounds.tini = tb.tini_icme
    bounds.tend = tb.tend_icme
elif pa.struct=='mc':
    bounds.tini = tb.tini_mc
    bounds.tend = tb.tend_mc
else:
    raise SystemExit(' ---> wrong structure! : '+pa.struct)

gral.data_name      = 'ACE' #'Auger_scals' #'McMurdo' #'ACE'
emgr = sf.events_mgr(gral, FILTER, CUTS, bounds, nBin, fgap, tb, None, structure=pa.struct)
LOW, MID1, MID2, TOP = 100., pa.Vsplit[0], pa.Vsplit[1], 3000.
if pa.auger_scls!='0':
    """  Auger Scalers  """
    run_analysis(
        emgr, 
        'Auger_scals', 
        LOW, MID1, MID2, TOP,
    )
if pa.auger_hsts!='0':
    """  Auger Histograms  """
    #+++++++++++++++++++++++++ Auger Band-Scals
    run_analysis(
        emgr,
        'Auger_BandScals',
        LOW, MID1, MID2, TOP,
        lock=True, # nos restrigimos a estos eventos de aqui en adelante!
    )
    #+++++++++++++++++++++++++ Auger Band-Muons
    run_analysis(
        emgr,
        'Auger_BandMuons',
        LOW, MID1, MID2, TOP,
    )
if pa.mcmurdo!='0':
    """  McMurdo  """
    run_analysis(
        emgr,
        'McMurdo',
        LOW, MID1, MID2, TOP,
    )
if pa.ace!='0':
    """  ACE   """
    run_analysis(
        emgr,
        'ACE',
        LOW, MID1, MID2, TOP,
    )

#EOF
