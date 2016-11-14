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
#from shared.ShiftTimes import *
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

#--- type for argparse
class str_to_other_ii(argparse.Action):
    """
    argparse-action to handle command-line arguments of 
    the form "dd/mm/yyyy" (string type), and converts
    it to datetime object.
    """
    def __init__(self, option_strings, dest, **kwargs):
        #if nargs is not None:
        #    raise ValueError("nargs not allowed")
        super(str_to_other_ii, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        #print '%r %r %r' % (namespace, values, option_string)
        #dd,mm,yyyy = map(int, values.split('/'))
        value = [int(values[0]), values[1]]
        setattr(namespace, self.dest, value)


#--- retrieve args
parser = argparse.ArgumentParser(
formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
'-ace', '--inp_ACE',
type=str,
default='{HOME}/data_ace/64sec_mag-swepam/ace.1998-2015.nc'.format(**os.environ),
help='input filename of ACE data',
)
parser.add_argument(
'-ace1sec', '--inp_ACE1sec',
type=str,
default='{HOME}/data_ace/64sec_mag-swepam/ace.1998-2015.nc'.format(**os.environ),
help='input filename of ACE data',
)
parser.add_argument(
'-murdo', '--inp_McMurdo',
type=str,
default='{HOME}/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat'.format(**os.environ)
)
parser.add_argument(
'-ahm', '--inp_Auger_BandMuons',
type=str,
default='{AUGER_REPO}/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5'.format(**os.environ),
help='.h5 file with Auger charge-histograms data (until temperature-correction).'
)
parser.add_argument(
'-ahs', '--inp_Auger_BandScals',
type=str,
default='{AUGER_REPO}/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5'.format(**os.environ),
help='.h5 file with Auger charge-histograms data (until temperature-correction).'
)
parser.add_argument(
'-as', '--inp_Auger_scals',
default='{PAO}/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5'.format(**os.environ),
help='.h5 file with Auger scalers (until pressure correction).'
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
help='string used as the name of the last inner\
 output subdirectories (created automatically)'
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
help='SW speed values to define a partition of the sample in \
three sub-groups of events.',
)
parser.add_argument(
'-lock', '--lock',
type=str,
default=[0,'Auger_BandMuons'],
nargs=2,
help='name of dataset of which we\'ll lock the set of selected \
    events; so that the analysis of other datasets are made with \
    the restriction of these "locked" events.',
action=str_to_other_ii,
metavar=('BOOL','NAME'),
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
'-v', '--verb',
action='store_true',
default=False,
help='verbose mode.'
)
parser.add_argument(
'-fgap', '--fgap',
type=float,
default=0.2, # always, except for Auger scalers
help='gap fraction to tolerate (i.e. won\'t tolerate more gaps \
than a fraction `fgap`)',
)
pa = parser.parse_args()

class boundaries:
    def __init__(self):
        name = 'name'


gral                = sf.general()
day                 = 86400.
#---- cosas input
gral.fnames = fnames = {}
fnames['ACE']       = pa.inp_ACE #'%s/data_ace/64sec_mag-swepam/ace.1998-2015.nc' % HOME
fnames['ACE1sec']   = pa.inp_ACE1sec
fnames['McMurdo']   = pa.inp_McMurdo #'%s/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat' % HOME
fnames['Auger_scals']     = pa.inp_Auger_scals #'%s/data_auger/estudios_AoP/data/unir_con_presion/data_final_2006-2013.h5' % PAO
#fnames['Auger_BandMuons'] = '%s/data_auger/data_histogramas/all.array.avrs/temp.corrected/shape.ok_and_3pmt.ok/15min/test_temp.corrected.nc' % PAO
fnames['Auger_BandMuons'] = pa.inp_Auger_BandMuons #'{AUGER_REPO}/out/out.build_temp.corr/shape.ok_and_3pmt.ok/15min/histos_temp.corrected.h5'.format(**os.environ)
fnames['Auger_BandScals'] = pa.inp_Auger_BandScals #fnames['Auger_BandMuons']

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
FILTER['CorrShift']     = pa.tshift #False #True
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
fgap                    = pa.fgap #0.5

#--- bordes de estructura
bounds      = boundaries()
if pa.struct=='sh.i':
    bounds.tini = tb.tshck      
    bounds.tend = tb.tini_icme  
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
from copy import deepcopy
bounds = deepcopy(bounds)

#--- list of data-sets that have an input-filename !='0'
lnm = [nm[4:] for nm in dir(pa) if (nm.startswith('inp_') & (getattr(pa,nm)!='0') )]
print lnm

#--- reordenamos la lista, si hay q hacer un `lock_in()`
if pa.lock[0]:
    lnm.remove(pa.lock[1])
    lnm = [pa.lock[1],] + lnm
    
print lnm

gral.data_name      = lnm[0] #'ACE' #'Auger_scals' #'McMurdo' #'ACE'
emgr = sf.events_mgr(
         gral, FILTER, CUTS, bounds, nBin, fgap, tb, 
         None, structure=pa.struct, verbose=pa.verb
       )
LOW, MID1, MID2, TOP = 100., pa.Vsplit[0], pa.Vsplit[1], 3000.

#--- import lib of the i/o classes for
#    each `dname`
from shared import readers

for dname in lnm:
    print " ---> dataset: "+dname
    data_handler = getattr(readers,'_data_'+dname)
    #+++ global
    emgr.data_name = dname #'Auger_BandScals'
    emgr.FILTER['vsw_filter'] = False 
    emgr.run_all(data_handler)
    if (dname==pa.lock[1] and pa.lock[0]): 
        emgr.lock_IDs()

    #+++ split
    emgr.FILTER['vsw_filter'] = True
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = LOW, MID1 
    emgr.run_all(data_handler)
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID1, MID2 
    emgr.run_all(data_handler)
    emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = MID2, TOP 
    emgr.run_all(data_handler)

print " ---> we processed:"
for dname in lnm:
    print ' > '+dname
print """
--- output:
 data  : %s
 plots : %s
""" % (pa.dir_plot, pa.dir_data)
     

#EOF
