from pylab import *
import numpy as np
from scipy.io.netcdf import netcdf_file

def make_plot(DIR_INP, FILTER, CUTS, nBin):
    MCwant      = FILTER['MCwant']
    fgap        = FILTER['fgap']
    WangFlag    = FILTER['WangFlag']

    FNAME   = 'MCflag%s_%dbefore.%dafter_fgap%1.1f' % (MCwant, nBin['before'], nBin['after'], fgap)
    FNAME   += '_Wang%s' % (WangFlag)
    if FILTER['vsw_filter']:
        FNAME += '_vlo.%03.1f.vhi.%04.1f' % (CUTS['v_lo'], CUTS['v_hi'])
    if FILTER['z_filter_on']:
        FNAME += '_zlo.%2.2f.zhi.%2.2f' % (CUTS['z_lo'], CUTS['z_hi'])
    if FILTER['B_filter']:
        FNAME += '_Blo.%2.2f.Bhi.%2.2f' % (CUTS['B_lo'], CUTS['B_hi'])
    if FILTER['filter_dR.icme']:
        FNAME += '_dRlo.%2.2f.dRhi.%2.2f' % (CUTS['dR_lo'], CUTS['dR_hi'])

    fname_inp = DIR_INP + '/' + '_stuff_' + FNAME + '.nc'

    finp = netcdf_file(fname_inp, 'r')
    #print finp.variables; finp.close()

    VARNAMES    = finp.variables.keys()
    prom        = {}
    for varname in VARNAMES:
        if varname[:2]=='dt' or varname[:2]=='ID':
            continue    # estos no los quiero

        mvs             = finp.variables[varname].data
        prom[varname]   = np.mean(mvs)

    del mvs             # borramos referencias al archivo
    finp.close()
    return prom


def get_prom(DIR_INP, FILTER, CUTS, nBin):
    """
    calcula promedios a partir de las variables del
    archivo en DIR_INP
    Retorna:
        prom: diccionario
    """
    MCwant      = FILTER['MCwant']
    fgap        = FILTER['fgap']
    WangFlag    = FILTER['WangFlag']

    FNAME   = 'MCflag%s_%dbefore.%dafter_fgap%1.1f' % (MCwant, nBin['before'], nBin['after'], fgap)
    FNAME   += '_Wang%s' % (WangFlag)
    if FILTER['vsw_filter']:
        FNAME += '_vlo.%03.1f.vhi.%04.1f' % (CUTS['v_lo'], CUTS['v_hi'])
    if FILTER['z_filter_on']:
        FNAME += '_zlo.%2.2f.zhi.%2.2f' % (CUTS['z_lo'], CUTS['z_hi'])
    if FILTER['B_filter']:
        FNAME += '_Blo.%2.2f.Bhi.%2.2f' % (CUTS['B_lo'], CUTS['B_hi'])
    if FILTER['filter_dR.icme']:
        FNAME += '_dRlo.%2.2f.dRhi.%2.2f' % (CUTS['dR_lo'], CUTS['dR_hi'])

    fname_inp = DIR_INP + '/' + '_stuff_' + FNAME + '.nc'

    finp = netcdf_file(fname_inp, 'r')
    #print finp.variables; finp.close()

    VARNAMES    = finp.variables.keys()
    prom        = {}
    for varname in VARNAMES:
        if varname[:2]=='dt' or varname[:2]=='ID':
            continue    # estos no los quiero

        mvs             = finp.variables[varname].data
        prom[varname]   = np.mean(mvs)

    del mvs             # borramos referencias al archivo
    finp.close()
    return prom

##
