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
'-inp', '--input',
type=str,
default='{HOME}/data_ace/64sec_mag-swepam/ace.1998-2014.nc'.format(**os.environ),
help='input filename of ACE data',
)
parser.add_argument(
'-in', '--inp_name',
type=str,
default='ACE',
help='name/flag of input data. Must be one of these: ACE, ACE_o7o6, Auger_BandMuons, Auger_BandScals, McMurdo.',
)
parser.add_argument(
'-rich', '--rich_csv',
type=str,
default='{ASO}/icmes_richardson/RichardsonList_until.2016.csv'.format(**os.environ),
help='.csv file for Richardson catalog of ICMEs',
)
parser.add_argument(
'-avr', '--avr',
type=str,
default='{ASO}/icmes_richardson/data/rich_events2_ace.nc'.format(**os.environ),
help='.csv file for Richardson catalog of ICMEs',
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
default=[None,None], # no filter by default
help='limits for the values of the Vsw (SW speed), to define\
 a filter of events. Recommended partition: 100, 450, 550, 3000.'
)
parser.add_argument(
'-obs', '--obs',
type=str,
nargs='+',
default=['B','rmsB'],
help="""
keyname of the variables to extract. 
For ACE, use:
B, rmsB, rmsBoB, V, beta, Pcc, Temp, AlphaRatio.
For Auger_..., use:
CRs.
""",
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
type=float,
default=None,
help="""
If not used, ignores Wang's catalog. Otherwise, set a lower 
threshold value to filter events according to its shock orientation, 
using Wang's catalog.
NOTE: the orientation is 180 degrees close to the nose!
""",
metavar=('THRESHOLD',),
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
fnames[pa.inp_name]       = pa.input #'%s/data_ace/64sec_mag-swepam/ace.1998-2014.nc' % HOME
fnames['McMurdo']   = '%s/actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat' % HOME
fnames['table_richardson']  = pa.avr # .nc file w/ average values

#---- directorios de salida
gral.dirs =  dirs   = {}
dirs['dir_plots']   = pa.dir_plot #'../plots'
dirs['dir_ascii']   = pa.dir_data #'../ascii'
dirs['suffix']      = '_test_Vmc_'    # sufijo para el directorio donde guardare


#------- seleccionamos MCs con label-de-catalogo (lepping=2, etc)
MCwant  = {'flags':     pa.icme_flag.split('.'), #('2',),
           'alias':     pa.icme_flag } #'2'}            # para "flagear" el nombre/ruta de las figuras

FILTER                  = {}
FILTER['Mcmultiple']    = False # True para incluir eventos multi-MC
FILTER['CorrShift']     = pa.tshift #True
FILTER['wang']          = pa.wang if pa.wang is not None else False #False/True
FILTER['vsw_filter']    = True
FILTER['z_filter_on']   = False
FILTER['MCwant']        = MCwant
FILTER['B_filter']      = False
FILTER['filter_dR.icme'] = False #True
FILTER['choose_1998-2006'] = False

CUTS                    = {}
CUTS['ThetaThres']      = 90.0      # all events with theta>ThetaThres
CUTS['dTday']           = 0.0
CUTS['v_lo']            = 550.0
CUTS['v_hi']            = 3000.0
CUTS['z_lo']            = -50.0
CUTS['z_hi']            = 0.65

nBin                    = {}
nBin['before']          = pa.BefAft[0] #2
nBin['after']           = pa.BefAft[1] #4
nBin['bins_per_utime']  = 50    # bins por unidad de tiempo
nBin['total']           = (1+nBin['before']+nBin['after'])*nBin['bins_per_utime']
fgap                    = 0.2

#--- bordes de estructura
tb = sf.RichTable(pa.rich_csv)
tb.read()

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
from copy import deepcopy
bounds = deepcopy(bounds)

from shared import readers
#+++++++++++++++++++++++++++++++++++++++++++++++++
gral.data_name      = pa.inp_name #'ACE'

FILTER['vsw_filter']    = False
emgr    = sf.events_mgr(gral, FILTER, CUTS, bounds, nBin, fgap, tb, None, structure=pa.struct, verbose=True)

#++++ limites
emgr.FILTER['vsw_filter'] = False if pa.limits==[None,None] else True
emgr.CUTS['v_lo'], emgr.CUTS['v_hi'] = pa.limits
emgr.filter_events()
emgr.load_files_and_timeshift_ii(
    _data_handler = getattr(readers,'_data_'+emgr.data_name),
    obs_check = pa.obs
)
emgr.rebine(collect_only=True)

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
nobs    = len(pa.obs)

for id, i in zip(events, range(n_evnts)):
    myid = int(id[3:])
    #--- construct header/footer
    dtsh = emgr.dt_sh[myid]  # [days] sheath duration
    dtmc = emgr.dt_mc[myid]  # [days] MC duration
    dt   = (bounds.tend[myid]-bounds.tini[myid]).total_seconds()/86400.
    HEADER=''+\
    'ini ({struct}) : {date}'.format(
        struct=pa.struct,
        date=emgr.bd.tini[myid].strftime('%d %B %Y %H:%M'),
    )+'\n'+\
    'end ({struct}) : {date}'.format(
        struct=pa.struct,
        date=emgr.bd.tend[myid].strftime('%d %B %Y %H:%M'),
    )
    FOOTER=''+\
    'dt [days]: %g\n' % dt +\
    'dt_sheath [days]: %g\n' % dtsh +\
    'dt_MC [days]: %g' % dtmc
    #--- get the data
    for obs, io in zip(pa.obs, range(nobs)):
        buffer = emgr.out['events_data'][id][obs+'.'+emgr.data_name] # [dummy1]
        data_out = np.array([buffer.time, buffer.data]).T
        fname_out = '%s/event.data_%s_vlo.%04d_vhi.%04d_id.%03d.txt' % (dir_dst, obs+'.'+emgr.data_name, emgr.CUTS['v_lo'], emgr.CUTS['v_hi'], myid)
        np.savetxt(fname_out,data_out,header=HEADER,footer=FOOTER,fmt='%g')

print " --> saved in: "+dir_dst

#EOF
