#!/usr/bin/env ipython
from pylab import *
from numpy import *
from scipy.io.netcdf import netcdf_file
from datetime import datetime, time, timedelta
#------------ shared libraries:
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

#---- cosas input
day             = 86400.
fnames              = {}
fnames['ACE']       = '../../../../../../../data_ace/64sec_mag-swepam/ace.1998-2014.nc'
fnames['table_richardson']    = '../../../../data_317events_iii.nc'

#---- directorios de salida
dirs                = {}
dirs['dir_plots']   = '../plots'
dirs['dir_ascii']   = '../ascii'

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
FILTER['wang']          = True
FILTER['vsw_filter']    = True
FILTER['z_filter_on']   = False
FILTER['CorrShift']     = True
FILTER['MCwant']        = MCwant

CUTS                    = {}
CUTS['ThetaThres']      = 90.0
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


class boundaries:
    def __init__(self):
        name = 'name'

bounds      = boundaries()
bounds.tini = tb.tshck #tb.tini_mc #tb.tshck 
bounds.tend = tb.tini_mc #tb.tend_mc #tb.tini_mc

FILTER['vsw_filter']    = False
CUTS['v_lo'], CUTS['v_hi'] = 550.0, 3000.0
emgr    = events_mgr(dirs, fnames, FILTER, CUTS, bounds, nBin, fgap, tb, z_exp)
emgr.run_all()

FILTER['vsw_filter']    = True
CUTS['v_lo'], CUTS['v_hi'] = 100.0, 450.0
emgr    = events_mgr(dirs, fnames, FILTER, CUTS, bounds, nBin, fgap, tb, z_exp)
emgr.run_all()

FILTER['vsw_filter']    = True
CUTS['v_lo'], CUTS['v_hi'] = 450.0, 550.0
emgr    = events_mgr(dirs, fnames, FILTER, CUTS, bounds, nBin, fgap, tb, z_exp)
emgr.run_all()

FILTER['vsw_filter']    = True
CUTS['v_lo'], CUTS['v_hi'] = 550.0, 3000.0
emgr    = events_mgr(dirs, fnames, FILTER, CUTS, bounds, nBin, fgap, tb, z_exp)
emgr.run_all()
##
