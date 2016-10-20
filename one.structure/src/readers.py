#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
from scipy.io.netcdf import netcdf_file
import numpy as np
from datetime import datetime, timedelta
from h5py import File as h5
import os, sys
#--- shared libs
from shared.ShiftTimes import ShiftCorrection, ShiftDts
import shared.console_colors as ccl


def calc_beta(Temp, Pcc, B):
    """
    Agarramos la definicion de OMNI, de:
     http://omniweb.gsfc.nasa.gov/ftpbrowser/magnetopause/Reference.html
     http://pamela.roma2.infn.it/index.php
    Beta = [(4.16*10**-5 * Tp) + 5.34] * Np/B**2 (B in nT)
    """
    beta = ((4.16*10**-5 * Temp) + 5.34) * Pcc/B**2
    return beta

def dates_from_omni(t):
    time = []
    n = len(t)
    for i in range(n):
        yyyy = t[i][0]
        mm = t[i][1]
        dd = t[i][2]
        HH = t[i][3]
        MM = t[i][4]
        SS = t[i][5]
        uSS = t[i][6]
        time += [datetime(yyyy, mm, dd, HH, MM, SS, uSS)]

    return time

def date_to_utc(fecha):
    utc = datetime(1970, 1, 1, 0, 0, 0, 0)
    sec_utc = (fecha - utc).total_seconds()
    return sec_utc

def utc_from_omni(file):
    t = np.array(file.variables['time'].data)
    dates = dates_from_omni(t)
    n = len(dates)
    time = np.zeros(n)
    for i in range(n):
        time[i] = date_to_utc(dates[i])

    return time


#------- data parsers -------
class _data_ACE(object):
    def __init__(self, fname_inp, tshift=False):
        """
        if tshift==True, we return shifted versions of
        the `tb` and `bd` in load() method.
        """
        self.fname_inp = fname_inp
        self.tshift    = tshift

    def load(self, data_name, tb, bd):
        f_sc   = netcdf_file(self.fname_inp, 'r')
        print " leyendo tiempo..."
        t_utc   = utc_from_omni(f_sc)
        print " Ready."

        #++++++++++ CORRECTION OF BORDERS ++++++++++
        # IMPORTANTE:
        # Solo valido para los "63 eventos" (MCflag='2', y visibles en ACE)
        # NOTA: dan saltos de shock mas marcados con True.
        if self.tshift:
            ShiftCorrection(ShiftDts, tb.tshck)
            ShiftCorrection(ShiftDts, tb.tini_icme)
            ShiftCorrection(ShiftDts, tb.tend_icme)
            ShiftCorrection(ShiftDts, tb.tini_mc)
            ShiftCorrection(ShiftDts, tb.tend_mc)
            ShiftCorrection(ShiftDts, bd.tini)
            ShiftCorrection(ShiftDts, bd.tend)

        #+++++++++++++++++++++++++++++++++++++++++++
        B       = f_sc.variables['Bmag'].data.copy()
        Vsw     = f_sc.variables['Vp'].data.copy()
        Temp    = f_sc.variables['Tp'].data.copy()
        Pcc     = f_sc.variables['Np'].data.copy()
        rmsB    = f_sc.variables['dBrms'].data.copy()
        alphar  = f_sc.variables['Alpha_ratio'].data.copy()
        beta    = calc_beta(Temp, Pcc, B)
        rmsBoB  = rmsB/B
        print " -------> variables leidas!"

        #------------------------------------ VARIABLES
        VARS = {}
        # variable, nombre archivo, limite vertical, ylabel
        VARS['B.'+data_name] = {
            'value' : B,
            'lims'  : [5., 18.],
            'label' : 'B [nT]'
        }
        VARS['V.'+data_name] = {
            'value' : Vsw,
            'lims'  : [300., 650.],
            'label' : 'Vsw [km/s]'
        }
        VARS['rmsBoB.'+data_name] = {
            'value' : rmsBoB,
            'lims'  : [0.01, 0.2],
            'label' : 'rms($\hat B$/|B|) [1]'
        }
        VARS['rmsB.'+data_name] = {
            'value' : rmsB,
            'lims'  : [0.05, 2.0],
            'label' : 'rms($\hat B$) [nT]'
        }
        VARS['beta.'+data_name] = {
            'value' : beta,
            'lims'  : [0.001, 5.],
            'label' : '$\\beta$ [1]'
        }
        VARS['Pcc.'+data_name] = {
            'value' : Pcc,
            'lims'  : [2, 17.],
            'label' : 'proton density [#/cc]'
        }
        VARS['Temp.'+data_name] = {
            'value' : Temp,
            'lims'  : [1e4, 4e5],
            'label' : 'Temp [K]'
        }
        VARS['AlphaRatio.'+data_name] = {
            'value' : alphar,
            'lims'  : [1e-3, 0.1],
            'label' : 'alpha ratio [1]'
        }

        #self.nvars = len(VARS.keys())
        #---------
        #self.aux = aux = {}
        #aux['SELECC']    = self.SELECC

        out = {
        't_utc' : t_utc,
        'VARS'  : VARS,
        }
        #--- out
        """
        NOTE: `bd` and `tb` have been shifted if
        `selg.tshift`==True.
        """
        return out
        #---- SALIDA:

#EOF
