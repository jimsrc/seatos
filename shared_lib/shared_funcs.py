#!/usr/bin/env ipython
# -*- coding: utf-8 -*- 
from datetime import datetime, time, timedelta
import numpy as np
import console_colors as ccl
from scipy.io.netcdf import netcdf_file
from ShiftTimes import ShiftCorrection, ShiftDts
import os, argparse
import h5py
from h5py import File as h5
from numpy import (
    mean, median, nanmean, nanmedian, std, nan, 
    isnan, min, max, zeros, ones, size, loadtxt
)
from os.path import isfile, isdir
if 'DISPLAY' in os.environ: # to avoid crash when running remotely
    from pylab import figure, savefig, close, find, pause
    import matplotlib.patches as patches
    import matplotlib.transforms as transforms

#from read_NewTable import tshck, tini_icme, tend_icme, tini_mc, tend_mc, n_icmes, MCsig
#from z_expansion_gulisano import z as z_exp
_ERROR_ = ccl.Rn+' ### ERROR ###: '+ccl.W

def flags2nan(VAR, FLAG):
        cond            = VAR < FLAG
        VAR             = np.array(VAR)
        VAR[~cond]      = np.nan
        return VAR


def date_to_utc(fecha):
    utc = datetime(1970, 1, 1, 0, 0, 0, 0)
    sec_utc = (fecha - utc).total_seconds()
    return sec_utc


def selecc_data(data, tshk):
    time    = data[0]       #[s] utc sec
    rate    = data[1]

    day      = 86400.        # [seg]
    utc      = datetime(1970, 1, 1, 0, 0, 0, 0)
    tshk_utc = (tshk - utc).total_seconds()

    ti      = tshk_utc - 10.*day        # [seg] utc
    tf      = tshk_utc + 30.*day
    cond    = (time > ti) & (time < tf)

    time    = (time[cond] - tshk_utc) / day     # [days] since shock
    rate    = rate[cond]
    return (time, rate)

def selecc_window(data, tini, tend):
    time    = data[0]       #[s] utc sec
    y       = data[1]

    day         = 86400.                # [seg]
    utc         = datetime(1970, 1, 1, 0, 0, 0, 0)
    tini_utc    = (tini - utc).total_seconds()      # [s] utc sec
    tend_utc    = (tend - utc).total_seconds()      # [s] utc sec

    ti      = tini_utc              # [seg] utc
    tf      = tend_utc
    cond    = (time > ti) & (time < tf)

    time    = (time[cond] - tini_utc) / day     # [days] since 'ti'
    y       = y[cond]
    return (time, y)


def enoughdata(var, fgap):
    n       = len(var)
    ngood   = len(find(~isnan(var)))
    fdata   = 1.*ngood/n        # fraccion de data sin gaps
    if fdata>=(1.-fgap):
        return True
    else:
        return False


def averages_and_std(n_icmes, t_shck, ti_icme, dTday, nbin, t_utc, VAR, fgap):
        day = 86400.
        nok=0; nbad=0
        adap = []
        for i in range(n_icmes):
            dT      = (ti_icme[i] - t_shck[i]).total_seconds()/day  # [day]
            if dT>dTday:
                dt      = dT/nbin
                t, var  = selecc_window(
                                [t_utc, VAR],
                                t_shck[i], ti_icme[i]
                                )
                if enoughdata(var, fgap):           # pido q haya mas del 80% NO sean gaps
                    adap    += [adaptar(nbin, dt, t, var)]
                    nok     +=1
                else:
                    continue
            else:
                print " i:%d ---> Este evento es muy chico!, dT/day:%g" % (i, dT)
                nbad +=1

        VAR_adap = zeros(nbin*nok).reshape(nok, nbin)
        for i in range(nok):
                VAR_adap[i,:] = adap[i][1]

        VAR_avrg = zeros(nbin)
        VAR_std = zeros(nbin)
        ndata = zeros(nbin)
        for i in range(nbin):
            cond = ~isnan(VAR_adap.T[i,:])
            ndata[i] = len(find(cond))      # nro de datos != flag
            VAR_avrg[i] = mean(VAR_adap.T[i,cond])  # promedio entre los valores q no tienen flag
            VAR_std[i] = std(VAR_adap.T[i,cond])    # std del mismo conjunto de datos

        tnorm   = adap[0][0]
        return [nok, nbad, tnorm, VAR_avrg, VAR_std, ndata]

def adaptar(n, dt, t, r):
    #n  = int(5./dt)        # nro de puntos en todo el intervalo de ploteo
    tt  = zeros(n)
    rr  = zeros(n)
    for i in range(n):
        tmin    = i*dt
        tmax    = (i+1.)*dt
        cond    = (t>tmin) & (t<tmax)
        tt[i]   = mean(t[cond])
        rr[i]   = mean(r[cond])
    return [tt/(n*dt), rr]


def adaptar(nwndw, dT, n, dt, t, r):
    #n  = int(5./dt)        # nro de puntos en todo el intervalo de ploteo
    tt  = zeros(n)
    rr  = zeros(n)
    _nbin_  = n/(1+nwndw[0]+nwndw[1])   # nro de bins en la sheath
    for i in range(n):
        tmin    = (i-nwndw[0]*_nbin_)*dt
        tmax    = tmin + dt
        cond    = (t>tmin) & (t<tmax)
        tt[i]   = mean(t[cond])#; print "tt:", t[i]; pause(1)
        rr[i]   = mean(r[cond])
    return [tt/dT, rr]          # tiempo normalizado x la duracion de la sheath

#@profile
def adaptar_ii(nwndw, dT, n, dt, t, r, fgap):
    tt      = zeros(n)
    rr      = zeros(n)
    _nbin_  = n/(1+nwndw[0]+nwndw[1])   # nro de bins en la sheath/mc
    cc      = (t>0.) & (t<dT)           # intervalo de la sheath/mc
    #print " r[cc]: ", r[cc]
    if len(r[cc])==0:           # no hay data en esta ventana
        rr      = nan*ones(n)
        enough  = False
    else:
        enough  = enoughdata(r[cc], fgap)   # [bool] True si hay mas del 80% de data buena.

    if not(enough): 
        rr  = nan*ones(n)   # si no hay suficiente data, este evento no aporta

    for i in range(n):
        tmin    = (i-nwndw[0]*_nbin_)*dt
        tmax    = tmin + dt
        cond    = (t>=tmin) & (t<=tmax)
        #tt[i]   = mean(t[cond])#; print "tt:", t[i]; pause(1) # bug
        tt[i]   = tmin + .5*dt          # bug corregido
        if enough:
            #cc    = ~isnan(r[cond])    # no olvidemos filtrar los gaps
            #rr[i] = mean(r[cond][cc])
            rr[i] = nanmean(r[cond])

    return enough, [tt/dT, rr]          # tiempo normalizado x la duracion de la sheath/mc/etc

#@profile
def selecc_window_ii(nwndw, data, tini, tend):
    time = data[0]       #[s] utc sec
    y    = data[1]

    day     = 86400.                # [seg]
    utc     = datetime(1970, 1, 1, 0, 0, 0, 0)
    tini_utc = (tini - utc).total_seconds()  # [s] utc sec
    tend_utc = (tend - utc).total_seconds()  # [s] utc sec

    dt   = tend_utc - tini_utc
    ti   = tini_utc - nwndw[0]*dt            # [seg] utc
    tf   = tend_utc + nwndw[1]*dt
    cond = (time > ti) & (time < tf)

    time = (time[cond] - tini_utc) / day     # [days] since 'ti'
    y    = y[cond]
    return (time, y)


def averages_and_std_ii(nwndw,
        SELECC, #MCsig, MCwant,
        n_icmes, tini, tend, dTday, nbin, t_utc, VAR):
        day = 86400.
        nok=0; nbad=0
        adap = []
        for i in range(n_icmes):
            dT      = (tend[i] - tini[i]).total_seconds()/day  # [day]
            if ((dT>dTday) & SELECC[i]):# (MCsig[i]>=MCwant)):
                dt      = dT*(1+nwndw[0]+nwndw[1])/nbin
                t, var  = selecc_window_ii(
                            nwndw,              # nro de veces hacia atras y adelante
                            [t_utc, VAR],
                            tini[i], tend[i]
                            )
                adap    += [adaptar(nwndw, dT, nbin, dt, t, var)]       # rebinea usando 'dt' como el ancho de nuevo bineo
                nok     +=1
            else:
                print " i:%d ---> Filtramos este evento!, dT/day:%g" % (i, dT)
                nbad +=1

        VAR_adap = zeros(nbin*nok).reshape(nok, nbin)
        for i in range(nok):
            VAR_adap[i,:] = adap[i][1]

        VAR_avrg = zeros(nbin)
        VAR_medi = zeros(nbin)
        VAR_std  = zeros(nbin)
        ndata    = zeros(nbin)
        for i in range(nbin):
            cond = ~isnan(VAR_adap.T[i,:])
            ndata[i] = len(find(cond))      # nro de datos != flag
            VAR_avrg[i] = mean(VAR_adap.T[i,cond])  # promedio entre los valores q no tienen flag
            VAR_medi[i] = median(VAR_adap.T[i,cond])# mediana entre los valores q no tienen flag
            VAR_std[i] = std(VAR_adap.T[i,cond])    # std del mismo conjunto de datos

        tnorm   = adap[0][0]
        return [nok, nbad, tnorm, VAR_avrg, VAR_medi, VAR_std, ndata]


def mvs_for_each_event(VAR_adap, nbin, nwndw, Enough, verbose=False):
    nok         = size(VAR_adap, axis=0)
    mvs         = zeros(nok)            # valores medios por cada evento
    binsPerTimeUnit = nbin/(1+nwndw[0]+nwndw[1])    # nro de bines por u. de tiempo
    start       = nwndw[0]*binsPerTimeUnit  # en este bin empieza la estructura (MC o sheath)
    for i in range(nok):
        aux = VAR_adap[i, start:start+binsPerTimeUnit]  # (*)
        cc  = ~isnan(aux)                   # pick good-data only
        #if len(find(cc))>1:
        if Enough[i]:       # solo imprimo los q tienen *suficiente data*
            if verbose:
                print ccl.G + "id %d/%d: %r"%(i+1, nok, aux[cc]) + ccl.W

            mvs[i] = mean(aux[cc])
        else:
            mvs[i] = nan
    #(*): esta es la serie temporal (de esta variable) para el evento "i"
    pause(1)
    return mvs


def diff_dates(tend, tini):
    n       = len(tend)
    diffs   = np.nan*np.ones(n)
    for i in range(n):
        ok  = type(tend[i]) == type(tini[i]) == datetime    # ambos deben ser fechas!
        if ok:
            diffs[i] = (tend[i] - tini[i]).total_seconds()
        else:
            diffs[i] = np.nan

    return diffs    #[sec]


def write_variable(fout, varname, dims, var, datatype, comments):
    dummy           = fout.createVariable(varname, datatype, dims)
    dummy[:]        = var
    dummy.units     = comments


def calc_beta(Temp, Pcc, B):
    # Agarramos la definicion de OMNI, de:
    # http://omniweb.gsfc.nasa.gov/ftpbrowser/magnetopause/Reference.html
    # http://pamela.roma2.infn.it/index.php
    # Beta = [(4.16*10**-5 * Tp) + 5.34] * Np/B**2 (B in nT)
    #
    beta = ((4.16*10**-5 * Temp) + 5.34) * Pcc/B**2
    return beta


def thetacond(ThetaThres, ThetaSh):
    """
    Set a lower threshold for shock orientation, using Wang's
    catalog of shocks.
    NOTE: Near 180Â means very close to the nose!
    """
    if ThetaThres<=0.:
        print ccl.Rn + ' ----> BAD WANG FILTER!!: ThetaThres<=0.'
        print ' ----> Saliendo...' + ccl.Rn
        raise SystemExit
        #return ones(len(ThetaSh), dtype=bool)
    else:
        return (ThetaSh > ThetaThres)


def wangflag(ThetaThres):
    if ThetaThres<0:
        return 'NaN'
    else:
        return str(ThetaThres)


def makefig(medVAR, avrVAR, stdVAR, nVAR, tnorm,
        SUBTITLE, YLIMS, YLAB, fname_fig):
    fig     = figure(1, figsize=(13, 6))
    ax      = fig.add_subplot(111)

    ax.plot(tnorm, avrVAR, 'o-', color='black', markersize=5, label='mean')
    ax.plot(tnorm, medVAR, 'o-', color='red', alpha=.5, markersize=5, markeredgecolor='none', label='median')
    inf     = avrVAR + stdVAR/np.sqrt(nVAR)
    sup     = avrVAR - stdVAR/np.sqrt(nVAR)
    ax.fill_between(tnorm, inf, sup, facecolor='gray', alpha=0.5)
    trans   = transforms.blended_transform_factory(
                ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((0., 0.), width=1.0, height=1,
                transform=trans, color='blue',
                alpha=0.3)
    ax.add_patch(rect1)

    ax.legend(loc='upper right')
    ax.grid()
    ax.set_ylim(YLIMS)
    TITLE = SUBTITLE
    ax.set_title(TITLE)
    ax.set_xlabel('time normalized to MC passage time [1]', fontsize=14)
    ax.set_ylabel(YLAB, fontsize=20)
    savefig(fname_fig, format='png', dpi=180, bbox_inches='tight')
    close()


def makefig_ii(mc, sh, YLIMS, YLAB, **kws):
    """
    - ftext{bool}:
    if False, we put the text in the title. Otherwise, we put
    the text inside the figure, using `TEXT_LOC`{dict} as positions
    - TEXT_LOC{dict}:
    coordinates for the text inside the figure. The `TEXT_LOC['sh']`{2-tuple} are
    the positions for the left part, and `TEXT_LOC['mc']`{2-tuple} for the right
    part.
    """
    #--- kws
    ftext       = kws.get('ftext', False)
    TEXT        = kws.get('TEXT', None)
    TEXT_LOC    = kws.get('TEXT_LOC', None)
    fname_fig   = kws.get('fname_fig', None)
    #-------------------------------------
    fmc,fsh = 3.0, 1.0      # escaleos temporales

    #--- if figure is not given, create one
    if 'fig' in kws:
        fig, ax = kws['fig'], kws['ax']
    else:
        fig     = figure(1, figsize=(13, 6))
        ax      = fig.add_subplot(111)

    # catch the name of the observable
    if 'varname' in kws:
        varname = kws['varname']
    else:
        varname = fname_fig[:-4].split('_')[-1]

    if(varname == 'Temp'):
        mc.med      /= 1.0e4; sh.med      /= 1.0e4
        mc.avr      /= 1.0e4; sh.avr      /= 1.0e4
        mc.std_err  /= 1.0e4; sh.std_err  /= 1.0e4
        YLIMS[0]    /= 1.0e4; YLIMS[1] /= 1.0e4
        if ftext:
            TEXT_LOC['mc'][1] /= 1.0e4
            TEXT_LOC['sh'][1] /= 1.0e4

    # curvas del mc
    time = fsh+fmc*mc.tnorm
    cc = time>=fsh
    ax.plot(time[cc], mc.avr[cc], 'o-', color='black', markersize=5)
    ax.plot(time[cc], mc.med[cc], 'o-', color='red', alpha=.8, markersize=5, markeredgecolor='none')
    # sombra del mc
    inf     = mc.avr + mc.std_err/np.sqrt(mc.nValues)
    sup     = mc.avr - mc.std_err/np.sqrt(mc.nValues)
    ax.fill_between(time[cc], inf[cc], sup[cc], facecolor='gray', alpha=0.5)
    trans   = transforms.blended_transform_factory(
                ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((fsh, 0.), width=fmc, height=1,
                transform=trans, color='blue',
                alpha=0.3)
    ax.add_patch(rect1)

    # curvas del sheath
    time = fsh*sh.tnorm
    cc = time<=fsh
    ax.plot(time[cc], sh.avr[cc], 'o-', color='black', markersize=5)
    ax.plot(time[cc], sh.med[cc], 'o-', color='red', alpha=.8, markersize=5, markeredgecolor='none')
    # sombra del sheath
    inf     = sh.avr + sh.std_err/np.sqrt(sh.nValues)
    sup     = sh.avr - sh.std_err/np.sqrt(sh.nValues)
    ax.fill_between(time[cc], inf[cc], sup[cc], facecolor='gray', alpha=0.5)
    #trans   = transforms.blended_transform_factory(
    #            ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((0., 0.), width=fsh, height=1,
                transform=trans, color='orange',
                alpha=0.3)
    ax.add_patch(rect1)

    ax.tick_params(labelsize=17)
    ax.grid()
    ax.set_ylim(YLIMS)
    if ftext:
        ax.text(TEXT_LOC['mc'][0], TEXT_LOC['mc'][1], TEXT['mc'], fontsize=22)
        ax.text(TEXT_LOC['sh'][0], TEXT_LOC['sh'][1], TEXT['sh'], fontsize=22)
    else:
        if TEXT is not None:
            ax.set_title(
                'left:  '+TEXT['sh']+'\n'
                'right: '+TEXT['mc']
            )
        else:
            pass # no text anywhere

    ax.set_ylabel(YLAB, fontsize=27)

    # if `varname` has any of these strings, plot in log-scale.
    if any([(nm in varname) for nm in \
        ('beta','Temp', 'rmsB', 'rmsBoB', 'ratio')]):
        ax.set_yscale('log')
    else:
        ax.set_yscale('linear')

    ax.legend(loc='best', fontsize=20)
    if 'fig' not in kws: # if figure not given, save to disk
        ax.set_xlim(-2.0, 7.0)
        ax.set_xlabel('time normalized to sheath/MC passage [1]', fontsize=25)
        savefig(fname_fig, format='png', dpi=100, bbox_inches='tight')
        close()
        return None
    else:
        # return changes of passed figure
        return fig, ax

#--- chekea q el archivo no repita elementos de la 1ra columna
def check_redundancy(fname, name):
    f = open(fname, 'r')
    dummy   = {}
    for line in f:
        ll          = line.split(' ')
        varname     = ll[0]
        dummy[varname] = 0

    dummy_names = dummy.keys()
    dummy_set   = set(dummy_names)
    redundancy  = len(dummy_set)<len(dummy_names)

    overwriting = name in dummy_set

    if redundancy or overwriting:
        return True
    else:
        return False

class general:
    def __init__(self):
        self.name = 'name'

class dummy1:
    def __init__(self,):
        pass

class dummy2 (object):
    """
    can be used:
    >>> dd = dummy2()
    >>> dd['name'] = [3,4,5]
    >>> dd['name2'].time = [0,1,2,3,4]
    """
    def __init__(self):
        self.this = {}

    def __getitem__(self, idx):
        if not idx in self.this.keys():
            self.this[idx] = dummy1()
        return self.this[idx]

    def set(self, name, attname, value):
        if not name in self.this.keys():
            self.this[name] = dummy1()
        setattr(self.this[name], attname, value)

    def keys(self,):
        return self.this.keys()


class boundaries:
    def __init__(self):
        print self.__dict__
        print dict(self)
    def ff(self):
        self.fg = 0.2


def nans(sh):
    return np.nan*np.ones(sh)


def grab_time_domain(adap, check=False):
    """
    Search for a valid time domain for 
    this `varname` and return.
    If `check`==True, it checks that all time domains
    are the same (for all `varname`s) unless a difference
    of 10 times the numerical epsilon.
    """
    na = len(adap)
    # grab all posible time domains
    found = False
    for i in range(na):
        for name in adap[i].keys():
            if not(found):
                tarr = adap[i][name][0]
                if tarr is not None:
                    found = True

    if found:
        # we found a valid time domain (`tarr`)
        if check:
            # assume time array is 'np.float32'
            eps32 = np.finfo(np.float32).eps
            for i in range(na):
                for name in adap[i].keys():
                    tarr_ = adap[i][name][0]
                    if tarr_ is not None:
                        # they differ at most in its
                        # numerical epsilon
                        ok = (tarr_-tarr<=eps32)
                        assert ok.prod(),\
                        " we have more than 1 valid time domain!!:\n%r\n\n%r"%(
                        tarr_, tarr)
        return tarr

    #--- didn't find any valid time domain
    try:
        # hung in debug mode
        import pdb; pdb.set_trace()
    except ImportError:
        # ok, get out!
        raise SystemExit(
            'shut! none are valid time domains:\n %r'%t_array
            )


class events_mgr(object):
    def __init__(self, gral, FILTER, CUTS, bd, nBin, fgap, tb, z_exp, structure='mc', verbose=True):
        """
        structure: can be 'sh.mc', 'sh.i', 'mc', 'i', refering to sheath-of-mc,
                   sheath-of-icme, mc, and icme, respectively. This is to
                   use the proper mean values calculated in each structure.
        """
        self.structure  = structure
        self.data_name  = gral.data_name
        self.FILTER     = FILTER
        self.CUTS       = CUTS
        self.bd         = bd
        self.nBin       = nBin
        self.fgap       = fgap
        self.tb         = tb
        self.z_exp      = z_exp
        self.dir_plots  = gral.dirs['dir_plots']
        self.dir_ascii  = gral.dirs['dir_ascii']
        self.gral       = gral
        self._dirs_     = gral.dirs
        self.verbose    = verbose

        #self.f_sc       = netcdf_file(gral.fnames[gral.data_name], 'r')
        self.f_events   = netcdf_file(gral.fnames['table_richardson'], 'r')
        print " -------> archivos input leidos!"

        #--- put False to all possible data-flags (all CR detector-names must be included in 'self.CR_observs')
        self.names_ok   = ('Auger_BandMuons', 'Auger_BandScals',  'Auger_scals', 'McMurdo', 'ACE', 'ACE_o7o6', 'ACE1sec')
        for name in self.names_ok:
            read_flag   = 'read_'+name
            setattr(self, read_flag, False) # True: if files are already read

        #--- names of CR observatories
        self.CR_observs = ( #debe *incluir* a los metodos 'load_data_..()'
            'Auger_scals', 'Auger_BandMuons', 'Auger_BandScals',\
            'McMurdo')

        #--- just a check for load_data_.. methods
        for att_name in dir(events_mgr): # iterate on all methods
            if att_name.startswith('load_data_'):
                att_suffix = att_name.replace('load_data_', '')
                assert att_suffix in self.names_ok,\
                    " ---> uno de los metodos '%s' no esta tomando en cuenta en 'self.CR_observs' (%s) " % (att_name, att_suffix)

        self.data_name_ = str(self.data_name) # nombre de la data input inicial (*1)
        self.IDs_locked = False      # (*2)
        """
        (*1):   si despues cambia 'self.data_name', me voy a dar
                cuenta en la "linea" FLAG_001.
        (*2):   lock in lock_IDs().
                True: if the id's of the events have been
                fixed/locked, so that later analysis is
                resctricted only with theses locked id's.
        """
        #++++++++++ CORRECTION OF BORDERS ++++++++++
        # IMPORTANTE:
        # Solo valido para los "63 eventos" (MCflag='2', y visibles en ACE)
        # NOTA: dan saltos de shock mas marcados con True.
        # TODO: make a copy/deepcopy of `tb` and `bd`, so that we don't 
        # bother the rest of data_names (i.e. Auger_scals, Auger_BandMuons, 
        # etc.)
        if FILTER['CorrShift']:
            ShiftCorrection(ShiftDts, tb.tshck)
            ShiftCorrection(ShiftDts, tb.tini_icme)
            ShiftCorrection(ShiftDts, tb.tend_icme)
            ShiftCorrection(ShiftDts, tb.tini_mc)
            ShiftCorrection(ShiftDts, tb.tend_mc)
            ShiftCorrection(ShiftDts, bd.tini)
            ShiftCorrection(ShiftDts, bd.tend)

    def run_all(self, _data_handler):
        #----- seleccion de eventos
        self.filter_events()
        print "\n ---> filtrado de eventos (n:%d): OK\n" % (self.n_SELECC)
        #----- load data y los shiftimes "omni"
        self.load_files_and_timeshift_ii(_data_handler)
        #----- rebineo y promedios
        self.rebine()
        self.rebine_final()
        #----- hacer ploteos
        self.make_plots()
        #----- archivos "stuff"
        self.build_params_file()

    #@profile
    def rebine(self, collect_only=False):
        """
        rebineo de c/evento
        """
        nvars   = self.nvars #len(VARS)
        n_icmes = self.tb.n_icmes
        bd      = self.bd
        VARS    = self.VARS
        nbin    = self.nBin['total']
        nwndw   = [self.nBin['before'], self.nBin['after']]
        day     = 86400.

        #---- quiero una lista de los eventos-id q van a incluirse en c/promedio :-)
        IDs     = {}
        Enough, nEnough = {}, {}
        self.__ADAP__ = ADAP    = []   # conjunto de varios 'adap' (uno x c/variable)
        for varname in VARS.keys():
            IDs[varname]        = []
            Enough[varname]     = []
            nEnough[varname]    = 0     # counter

        # recorremos los eventos:
        nok, nbad = 0, 0
        nnn     = 0     # nro de evento q pasan el filtro a-priori
        self.out  = {}
        if collect_only:
            self.out['events_data'] = {} # bag to save data from events

        ok = np.zeros(n_icmes,dtype=np.bool) # all `False` by default
        for i in range(n_icmes):
            try: #no todos los elementos de 'tend' son fechas (algunos eventos no tienen fecha definida)
                # this 'i'-event must be contained in our data-base
                ok[i]  =  date_to_utc(bd.tini[i]) >= self.t_utc[0] #True
                ok[i]  &= date_to_utc(bd.tend[i]) <= self.t_utc[-1]
                if self.IDs_locked:
                    ok[i] &= i in self.restricted_IDs
            except: # e.g. if `bd.{tini,tend}[i]` is NaN
                ok[i] = False

        for i in range(n_icmes):
            #np.set_printoptions(4) # nro de digitos a imprimir al usar numpy.arrays
            if not (ok[i] & self.SELECC[i]):   #---FILTRO--- (*1)
                print ccl.Rn, " id:%d ---> ok, SELECC: "%i, ok[i], self.SELECC[i], ccl.W
                nbad +=1
                continue

            dT = (bd.tend[i] - bd.tini[i]).total_seconds()/day  # [day]
            ADAP += [ {} ] # agrego un diccionario a la lista
            nnn += 1
            print ccl.Gn + " id:%d ---> dT/day:%g" % (i, dT) + ccl.W
            print self.tb.tshck[i]
            nok +=1
            if collect_only:
                # evdata is just a pointer
                evdata = self.out['events_data']['id_%03d'%i] = dummy2() #{} 

            # recorremos las variables:
            for varname in VARS.keys():
                dt      = dT*(1+nwndw[0]+nwndw[1])/nbin
                t, var  = self.grab_window(
                    nwndw=nwndw, #rango ploteo
                    data=[self.t_utc, VARS[varname]['value']],
                    tini=bd.tini[i],
                    tend=bd.tend[i],
                    vname=varname, # for ACE 1sec
                )
                if collect_only:
                    evdata.set(varname, 'time', t)
                    evdata.set(varname, 'data', var)

                #--- read average CR rates before shock/disturbance
                if self.data_name in self.CR_observs:   # is it CR data?
                    rate_pre = getattr(self, 'rate_pre_'+self.data_name)
                    var = 100.*(var - rate_pre[i]) / rate_pre[i]

                #--- rebinea usando 'dt' como el ancho de nuevo bineo
                out = adaptar_ii(
                    nwndw = nwndw, 
                    dT = dT, 
                    n = nbin, 
                    dt = dt, 
                    t = t, 
                    r = var, 
                    fgap = self.fgap
                )
                enough    = out[0]    # True: data con menos de 100*'fgap'% de gap
                Enough[varname]         += [ enough ]
                ADAP[nok-1][varname]    = out[1] # out[1] = [tiempo, variable]

                if enough:
                    #import pdb; pdb.set_trace()
                    IDs[varname]     += [i]
                    nEnough[varname] += 1

        #NOTE: `ADAP` points to `self.__ADAP__`
        print " ----> len.ADAP: %d" % len(ADAP)
        self.__nok__    = nok
        self.__nbad__   = nbad
        self.out['nok']     = nok
        self.out['nbad']    = nbad
        self.out['IDs']     = IDs
        self.out['nEnough'] = nEnough
        self.out['Enough']  = Enough

    def lock_IDs(self):
        """
        This assumes that 'IDs' has only *one* key.
        That is, len(IDs)=1 !!
        """
        IDs = self.out['IDs']
        varname = IDs.keys()[0]
        self.restricted_IDs = IDs[varname]
        self.IDs_locked = True

    def rebine_final(self):
        """
        rebineo de c/evento ... PARTE FINAL
        """
        nvars   = self.nvars #len(VARS)
        VARS    = self.VARS
        nbin    = self.nBin['total']
        nwndw   = [self.nBin['before'], self.nBin['after']]
        day     = 86400.
        ## salidas del 'self.rebine()'
        ADAP    = self.__ADAP__
        Enough  = self.out['Enough']
        nEnough = self.out['nEnough']
        IDs     = self.out['IDs']
        nok     = self.out['nok']
        nbad    = self.out['nbad']
        stuff   = {} #[]

        # Hacemos un lugar para la data rebineada (posible uso post-analisis)
        if self.data_name==self.data_name_:
            self.rebined_data = {} # creamos el diccionario UNA sola vez

        for varname in VARS.keys():
            if self.verbose:
                print ccl.On + " -------> procesando: %s" % VARS[varname]['label']
                print " nEnough/nok/(nok+nbad): %d/%d/%d " % (nEnough[varname], nok, nok+nbad) + ccl.W
            VAR_adap = zeros((nok, nbin))    # perfiles rebineados (*)
            # (*): uno de estos por variable
            # recorro los 'nok' eventos q pasaron el filtro de arriba:
            for i in range(nok):
                VAR_adap[i,:] = ADAP[i][varname][1] # valores rebineados de la variable "j" para el evento "i"

            self.rebined_data[varname] = VAR_adap

            # valores medios de esta variable para c/evento
            avrVAR_adap = mvs_for_each_event(VAR_adap, nbin, nwndw, Enough[varname], self.verbose)
            if self.verbose: 
                print " ---> (%s) avrVAR_adap[]: \n" % varname, avrVAR_adap

            VAR_avrg        = zeros(nbin)
            VAR_avrgNorm    = zeros(nbin)
            VAR_medi        = zeros(nbin)
            VAR_std         = zeros(nbin)
            ndata           = zeros(nbin)

            # recorremos bin a bin, para calular media, mediana, error, etc...
            for i in range(nbin):
                cond = ~np.isnan(VAR_adap.T[i,:])  # filtro eventos q no aportan data en este bin
                ndata[i] = len(find(cond))      # nro de datos != nan
                VAR_avrg[i] = np.mean(VAR_adap.T[i,cond])  # promedio entre los valores q no tienen flag
                VAR_avrgNorm[i] = np.mean(VAR_adap.T[i,cond]/avrVAR_adap[cond])
                VAR_medi[i] = np.median(VAR_adap.T[i,cond])# mediana entre los valores q no tienen flag
                VAR_std[i] = np.std(VAR_adap.T[i,cond])    # std del mismo conjunto de datos

            stuff[varname] = [VAR_avrg, VAR_medi, VAR_std, ndata, avrVAR_adap]
            # NOTA: chekar q 'ADAP[j][varname][0]' sea igual para TODOS los
            #       eventos 'j', y para TODOS los 'varname'.

        self.out['dVARS']    = stuff
        self.out['tnorm']    = grab_time_domain(ADAP, check=True)

    """def __getattr__(self, attname):
        if attname[:10]=='load_data_':
            return self.attname"""

    def load_files_and_timeshift_ii(self, _data_handler, obs_check=None):
        """
        INPUT
        -----
        * _data_handler:
        class that handles the i/o of the database related to 'data_name'.

        * obs_check: 
        if not None, is a list of strings related to the names of
        the observables of our interest. The idea is to make
        sure that we are asking for variables that are included
        in our database `self.VARS`.
        """
        read_flag = 'read_'+self.data_name # e.g. self.read_Auger
        if not(read_flag in self.__dict__.keys()): # do i know u?
            setattr(self, read_flag, False) #True: if files are already read

        #--- read data and mark flag as read!
        if not( getattr(self, read_flag) ):
            attname = 'load_data_'+self.data_name
            dh = _data_handler(
                    input=self.gral.fnames[self.data_name], 
                 )

            # point to the method that selects data from
            # a given window
            self.grab_window = dh.grab_block # {method}

            # grab/point-to data from disk
            #NOTE: if self.FILTER['CorrShift']==True, then `self.tb` and
            # `self.bd` will be shifted!
            out = dh.load(data_name=self.data_name, tb=self.tb, bd=self.bd)

            # attribute data pointers to `self`
            for nm, value in out.iteritems():
                # set `t_utc` and `VAR` to `self`
                setattr(self,nm,value)
    
            # check that we are grabbing observables of our 
            # interest
            if obs_check is not None:
                for nm in obs_check:
                    nm_ = nm+'.'+self.data_name
                    assert nm_ in self.VARS.keys(),\
                    " %s is not database list: %r"%(nm_, self.VARS.keys())

            self.nvars = len(self.VARS.keys())
            # mark as read
            self.read_flag = True       # True: ya lei los archivos input

        #--- check weird case
        assert self.data_name in self.names_ok,\
            _ERROR_+" not on my list!: %s" % self.data_name+\
            "\n Must be one of these: %r" % [self.names_ok]
        
    def make_plots(self):
        """
        #---- generar figuras y asciis de los perfiles promedio/mediana
        """
        nBin        = self.nBin
        fgap        = self.fgap
        MCwant      = self.FILTER['MCwant']

        ThetaThres  = self.CUTS['ThetaThres']
        if self.FILTER['vsw_filter']:
            v_lo, v_hi = self.CUTS['v_lo'], self.CUTS['v_hi']
        else:
            v_lo, v_hi = 0.0, 0.0   #estos valores significan q no hay filtro

        if self.FILTER['z_filter_on']:
            z_lo, z_hi = self.CUTS['z_lo'], self.CUTS['z_hi']
        else:
            z_lo, z_hi = 0.0, 0.0

        if self.FILTER['B_filter']:
            B_lo, B_hi = self.CUTS['B_lo'], self.CUTS['B_hi']
        else:
            B_lo, B_hi = 0.0, 0.0   #estos valores significan q no hay filtro

        if self.FILTER['filter_dR.icme']:
            dR_lo, dR_hi = self.CUTS['dR_lo'], self.CUTS['dR_hi']
        else:
            dR_lo, dR_hi = 0.0, 0.0   #estos valores significan q no hay filtro

        nbin        = (1+nBin['before']+nBin['after'])*nBin['bins_per_utime']  # [1] nro de bines q quiero en mi perfil promedio


        #-------------------- prefijos:
        # prefijo para filtro Wang:
        if self.FILTER['wang']:
            WangFlag = str(ThetaThres)
        else:
            WangFlag = 'NaN'

        # prefijo gral para los nombres de los graficos:
        if self.FILTER['CorrShift']:
            prexShift =  'wShiftCorr'
        else:
            prexShift = 'woShiftCorr'

        #-------------------------------
        # nombres genericos...
        DIR_FIGS    = '%s/MCflag%s/%s' % (self.dir_plots, MCwant['alias'], prexShift)
        DIR_FIGS    += '/' + self._dirs_['suffix']
        DIR_ASCII   = '%s/MCflag%s/%s' % (self.dir_ascii, MCwant['alias'], prexShift)
        DIR_ASCII   += '/' + self._dirs_['suffix']
        os.system('mkdir -p %s' % DIR_FIGS)     # si no existe, lo creamos
        os.system('mkdir -p %s' % DIR_ASCII)    # (bis)
        print ccl.On + " -------> creando: %s" % DIR_FIGS + ccl.W
        print ccl.On + " -------> creando: %s" % DIR_ASCII + ccl.W

        FNAMEs = 'MCflag%s_%dbefore.%dafter_fgap%1.1f' % (MCwant['alias'], nBin['before'], nBin['after'], fgap)
        FNAMEs += '_Wang%s' % (WangFlag)
        if self.FILTER['vsw_filter']:       FNAMEs += '_vlo.%03.1f.vhi.%04.1f' % (v_lo, v_hi)
        if self.FILTER['z_filter_on']:      FNAMEs += '_zlo.%2.2f.zhi.%2.2f' % (z_lo, z_hi)
        if self.FILTER['B_filter']:         FNAMEs += '_Blo.%2.2f.Bhi.%2.2f' % (B_lo, B_hi)
        if self.FILTER['filter_dR.icme']:   FNAMEs += '_dRlo.%2.2f.dRhi.%2.2f' % (dR_lo, dR_hi)
        if not self.FILTER['vsw_filter']:
            FNAMEs += '_' # flag for post-processing, indicating
                          # there was no splitting

        FNAME_ASCII = '%s/%s' % (DIR_ASCII, FNAMEs)
        FNAME_FIGS  = '%s/%s' % (DIR_FIGS, FNAMEs)

        fname_nro   = DIR_ASCII+'/'+'n.events_'+FNAMEs+'.txt'
        #'w': write mode #'a': append mode
        #---FLAG_001
        if self.data_name==self.data_name_:
            fnro = open(fname_nro, 'w')
        else:
            fnro = open(fname_nro, 'a') # si uso otra data input, voy anotando el nro
                                        # de eventos al final del archivo 'fname_nro'

        #-------------------------------------------------------------------
        nvars = len(self.VARS)
        for varname in self.VARS.keys():
            fname_fig = '%s_%s.png' % (FNAME_FIGS, varname) #self.VARS[i][1])
            print ccl.Rn+ " ------> %s" % fname_fig
            ylims   = self.VARS[varname]['lims'] #self.VARS[i][2]
            ylabel  = self.VARS[varname]['label'] #self.VARS[i][3]
            average = self.out['dVARS'][varname][0]
            mediana = self.out['dVARS'][varname][1] #self.out['dVARS'][i][4]
            std_err = self.out['dVARS'][varname][2]
            nValues = self.out['dVARS'][varname][3] # number of values aporting to each data bin
            N_selec = self.out['nok'] #self.out['dVARS'][varname][0]
            N_final = self.out['nEnough'][varname] #nEnough[i]

            SUBTITLE = '# of selected events: %d \n\
                events w/80%% of data: %d \n\
                bins per time unit: %d \n\
                MCflag: %s \n\
                WangFlag: %s' % (N_selec, N_final, nBin['bins_per_utime'], MCwant['alias'], WangFlag)

            makefig(mediana, average, std_err, nValues, self.out['tnorm'], 
                    SUBTITLE, ylims, ylabel, fname_fig)

            fdataout = '%s_%s.txt' % (FNAME_ASCII, varname) #self.VARS[i][1])
            dataout = np.array([self.out['tnorm'] , mediana, average, std_err, nValues])
            print " ------> %s\n" % fdataout + ccl.W
            np.savetxt(fdataout, dataout.T, fmt='%12.5f')

            #-------- grabamos nro de eventos selecc para esta variable
            line = '%s %d %d\n' % (varname, N_final, N_selec)
            fnro.write(line)

        print ccl.Rn + " --> nro de eventos seleccionados: " + fname_nro + ccl.W
        fnro.close()

        #--- salidas (a parte de los .png)
        self.DIR_ASCII  = DIR_ASCII
        self.FNAMEs     = FNAMEs

    def build_params_file(self):
        """
        Construye archivo q tiene cosas de los eventos seleccionados:
        - valores medios de los observables (B, Vsw, Temp, beta, etc)
        - los IDs de los eventos
        - duracion de los MCs y las sheaths
        """
        DIR_ASCII   = self.DIR_ASCII
        FNAMEs      = self.FNAMEs
        #-------------------------------------------- begin: NC_FILE
        print "\n*********************************** begin: NC_FILE"
        #------- generamos registro de id's de los
        #        eventos q entraron en los promedios.
        #        Nota: un registro por variable.
        fname_out = DIR_ASCII+'/'+'_stuff_'+FNAMEs+'.nc' #'./test.nc'
        #---FLAG_001
        if self.data_name==self.data_name_:
            fout        = netcdf_file(fname_out, 'w')
            print "\n ----> generando: %s\n" % fname_out
        else:
            fout        = netcdf_file(fname_out, 'a')
            # modo 'a': si uso otra data input, voy anotando el nro
            # de eventos al final del archivo 'fname_out'
            print "\n ----> anexando en: %s\n" % fname_out


        IDs = self.out['IDs']
        for varname in self.VARS.keys():
            print " ----> " + varname
            n_events = len(IDs[varname])
            dimname  = 'nevents_'+varname
            fout.createDimension(dimname, n_events)
            print " n_events: ", n_events
            prom     = self.out['dVARS'][varname][4]
            cc       = np.isnan(prom)
            print " nprom (all)    : ", prom.size
            prom     = prom[~cc]
            print " nprom (w/o nan): ", prom.size
            dims     = (dimname,)
            write_variable(fout, varname, dims, prom, 'd', 
                'average_values per event')
            #---------- IDs de esta variable
            ids      = map(int, IDs[varname])
            vname    = 'IDs_'+varname
            write_variable(fout, vname, dims, ids, 'i',
                'event IDs that enter in this parameter average')
            #---------- duracion de la estructura
            dtsh     = np.zeros(len(ids))
            dtmc     = np.zeros(len(ids))
            for i in range(len(ids)):
                id      = ids[i]
                dtsh[i] = self.dt_sh[id]
                dtmc[i] = self.dt_mc[id]

            vname    = 'dt_sheath_'+varname
            write_variable(fout, vname, dims, dtsh, 'd', '[days]')
            vname    = 'dt_mc_'+varname
            write_variable(fout, vname, dims, dtmc, 'd', '[days]')

        fout.close()
        print "**************************************** end: NC_FILE"
        #---------------------------------------------- end: NC_FILE

    def filter_events(self):
        structure       = self.structure
        tb              = self.tb
        FILTER          = self.FILTER
        dTday           = self.CUTS['dTday']
        day             = 86400.
        AU_o_km         = 1./(150.0e6)
        sec_o_day       = 86400.
        #------------------------------------ EVENTS's PARAMETERS
        #MCsig  = array(f_events.variables['MC_sig'].data)# 2,1,0: MC, rotation, irregular
        #Vnsh   = array(f_events.variables['wang_Vsh'].data) # veloc normal del shock
        ThetaSh     = np.array(self.f_events.variables['wang_theta_shock'].data) # orientacion de la normal del shock
        i_V         = self.f_events.variables[structure+'_V'].data.copy() # velocidad de icme
        i_B         = self.f_events.variables[structure+'_B'].data.copy() # B del icme
        i_dt        = self.f_events.variables[structure+'_dt'].data.copy() # B del icme
        i_dR            = i_dt*(i_V*AU_o_km*sec_o_day)

        #RatePre_Names = []
        #--- seteamos miembros de 'self' q se llamen 'rate_pre_...'
        for vname in self.f_events.variables.keys():
            if vname.startswith('rate_pre_'):
                #RatePre_Names += [ vname ] # save them to make checks later
                var = self.f_events.variables[vname].data.copy()
                setattr(self, vname, var)  # asignamos 'rate_pre_...' a 'self'

        """
        self.rate_pre   = self.f_events.variables['rate_pre_McMurdo'].data.copy()
        self.rate_pre_Auger=self.f_events.variables['rate_pre_Auger'].data.copy()
        """
        self.Afd        = self.f_events.variables['A_FD'].data.copy()
        #------------------------------------

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++++++++++ begin: SELECCION DE EVENTOS ++++++++++++++++++++++
        #------- fechas
        BETW1998_2006   = np.ones(tb.n_icmes, dtype=bool)
        if FILTER['choose_1998-2006']:
            _until_2006 = range(294) # all events up to Jan/2006
            for i in _until_2006:
                BETW1998_2006[i]=False # 'False' para excluir eventos

        #------- seleccionamos MCs con label-de-catalogo (lepping=2, etc)
        MC_FLAG = np.ones(tb.n_icmes, dtype=bool)
        for i in range(tb.n_icmes):
                MC_FLAG[i]  = tb.MCsig[i] in FILTER['MCwant']['flags']

        #------- excluimos eventos de 2MCs
        EVENTS_with_2MCs= (26, 148, 259, 295)
        MCmultiple      = FILTER['Mcmultiple'] #False #True para incluir eventos multi-MC
        MCmulti         = np.ones(tb.n_icmes, dtype=bool)  # False para eventos multi-MC (SI, escribi bien)
        if(~FILTER['Mcmultiple']):
            for i in EVENTS_with_2MCs:
                MCmulti[i] &= False

        #------- orientacion del shock (catalogo Wang)
        if FILTER['wang']:
            ThetaThres  = self.CUTS['ThetaThres']
            ThetaCond   = thetacond(ThetaThres, ThetaSh) # set lower threshold

        #------- duration of sheaths
        self.dt_mc      = diff_dates(tb.tend_mc, tb.tini_mc)/day     # [day]
        self.dt_sh      = diff_dates(tb.tini_mc, tb.tshck)/day     # [day]
        dt              = diff_dates(self.bd.tend, self.bd.tini)/day
        DURATION        = dt > dTday    # sheaths>0

        #------- speed of icmes
        if FILTER['vsw_filter']:
            v_lo        = self.CUTS['v_lo']
            v_hi        = self.CUTS['v_hi']
            SpeedCond   = (i_V>=v_lo) & (i_V<v_hi)

        #------- z expansion (a. gulisano)
        z_exp   = self.z_exp
        if FILTER['z_filter_on']:
            z_lo    = self.CUTS['z_lo']
            z_hi    = self.CUTS['z_hi']
            z_cond  = (z_exp>=z_lo) & (z_exp<z_hi)

        #------- <B> of icmes
        if FILTER['B_filter']:
            B_lo        = self.CUTS['B_lo']
            B_hi        = self.CUTS['B_hi']
            BfieldCond  = (i_B>=B_lo) & (i_B<B_hi)

        #------- size of icmes
        if FILTER['filter_dR.icme']:
            dR_lo        = self.CUTS['dR_lo']
            dR_hi        = self.CUTS['dR_hi']
            """print " ---> i_dR: \n", i_dR
            print " ---> i_dt: \n", i_dt
            raw_input()"""
            dRicmeCond   = (i_dR>=dR_lo) & (i_dR<dR_hi)

        #------- filtro total
        SELECC  = np.ones(tb.n_icmes, dtype=bool)
        SELECC  &= BETW1998_2006    # nos mantenemos en este periodo de anios
        SELECC  &= MCmulti          # nubes multiples
        SELECC  &= MC_FLAG          # catalogo de nubes
        SELECC  &= DURATION         # no queremos sheaths q duran 1hr xq solo aportan ruido
        if FILTER['wang']:           SELECC &= ThetaCond # cerca a 180 es nariz del shock
        if FILTER['vsw_filter']:     SELECC &= SpeedCond
        if FILTER['z_filter_on']:    SELECC &= z_cond
        if FILTER['B_filter']:       SELECC &= BfieldCond
        if FILTER['filter_dR.icme']: SELECC &= dRicmeCond

        self.SELECC     = SELECC
        self.n_SELECC   = len(find(SELECC))
        #self.aux['SELECC']    = self.SELECC
        #+++++++++++++++++ end: SELECCION DE EVENTOS ++++++++++++++++++++
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.n_SELECC<=0:
            print ccl.Rn + "\n --------> FATAL ERROR!!!: self.n_SELECC=<0"
            print " exiting....... \n" + ccl.W
            raise SystemExit


class RichTable(object):
    def __init__(s, fname_rich):
        s.fname_rich = fname_rich
        s.tshck 	= []
        s.tini_icme, s.tend_icme	= [], []
        s.tini_mc,   s.tend_mc      = [], []
        s.Qicme		= []
        s.MCsig		= []
        s.Dst		= []

    def read(s):
        print "\n ---> reading Richardson's table: %s" % s.fname_rich
        frich = open(s.fname_rich, 'r')
        print " file read."
        ll, n = [], 0
        for line in frich:
            ll 	+= [line.split(',')]
            n +=1
        print " lineas leidas: %d" % n
        for i in range(1,n):
            #------ fecha shock
            s.tshck += [datetime.strptime(ll[i][1][1:20],"%Y-%m-%d %H:%M:%S")]
            #------ fecha ini icme
            ss	= ll[i][2][1:11].split()  # string de la fecha ini-icme
            HH	= int(ss[1][0:2])
            MM	= int(ss[1][2:4])
            mm	= int(ss[0].split('/')[0])
            dd	= int(ss[0].split('/')[1])
            if mm==s.tshck[i-1].month:
                yyyy = s.tshck[i-1].year
            else:
                yyyy = s.tshck[i-1].year + 1
            s.tini_icme += [datetime(yyyy, mm, dd, HH, MM)]
            #------ fecha fin icme
            ss      = ll[i][3][1:11].split()
            HH      = int(ss[1][0:2])
            MM      = int(ss[1][2:4])
            mm      = int(ss[0].split('/')[0])
            dd      = int(ss[0].split('/')[1])
            if mm==s.tshck[i-1].month:
                yyyy = s.tshck[i-1].year
            elif s.tshck[i-1].month==12:
                yyyy = s.tshck[i-1].year + 1

            s.tend_icme += [datetime(yyyy, mm, dd, HH, MM)]
            #------ fechas MCs
            if ll[i][6]=='':
                s.tini_mc += [nan]
                s.tend_mc += [nan]
            else:
                hrs_ini	= int(ll[i][6])			# col6 es inicio del MC
                dummy = ll[i][7].split('(')		# col7 es fin del MC
                ndummy = len(dummy)
                if ndummy==1:
                    hrs_end = int(ll[i][7])
                else:
                    hrs_end	= int(ll[i][7].split('(')[0][1:])
                s.tini_mc += [ s.tini_icme[i-1] + timedelta(hours=hrs_ini) ]
                s.tend_mc += [ s.tend_icme[i-1] + timedelta(hours=hrs_end) ]
            # calidad de ICME boundaries
            s.Qicme 	+= [ ll[i][10] ]		# quality of ICME boundaries
            # flag de MC
            s.MCsig	+= [ ll[i][15] ]
            #if ll[i][15]=='2H':
            #	MCsig   += [ 2 ]
            #else:
            #	MCsig	+= [ int(ll[i][15]) ]	# MC flag
            #
            s.Dst	+= [ int(ll[i][16]) ]		# Dst

        #--------------------------------------
        s.MCsig   = np.array(s.MCsig)
        s.Dst	  = np.array(s.Dst)
        s.n_icmes = len(s.tshck)
        #
        """
        col0 : id
        col1 : disturbance time
        col2 : ICME start
        col3 : ICME end
        col4 : Composition start
        col5 : Composition end
        col6 : MC start
        col7 : MC end
        col8 : BDE
        col9 : BIF
        col10: Quality of ICME boundaries (1=best)
        col11: dV --> 'S' indica q incluye shock
        col12: V_ICME
        col13: V_max
        col14: B
        col15: MC flag --> '0', '1', '2', '2H': irregular, B-rotation, MC, or MC of "Huttunen etal05" respectively.
        col16: Dst
        col17: V_transit
        col18: LASCO_CME --> time of associated event, generally the CME observed by SOHO/LASCO.
               A veces tiene 'H' por Halo. 
        """

def Add2Date(date, days, hrs=0, BadFlag=np.nan):
    """
    Mapping to add `days` and `hrs` to a given
    `datetime` object.
    NOTE: `days` can be fractional.
    """
    if type(date) is not datetime:
        return BadFlag
    return date + timedelta(days=days, hours=hrs)

def utc2date(t):
    date_utc = datetime(1970, 1, 1, 0, 0, 0, 0)
    date = date_utc + timedelta(days=(t/86400.))
    return date


def date2utc(date):
    date_utc = datetime(1970, 1, 1, 0, 0, 0, 0)
    utcsec = (date - date_utc).total_seconds() # [utc sec]
    return utcsec

def ACEepoch2utc(AceEpoch):
    return AceEpoch + 820454400.0

class arg_to_datetime(argparse.Action):
    """
    argparse-action to handle command-line arguments of 
    the form "dd/mm/yyyy" (string type), and converts
    it to datetime object.
    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(arg_to_datetime, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        #print '%r %r %r' % (namespace, values, option_string)
        dd,mm,yyyy = map(int, values.split('/'))
        value = datetime(yyyy,mm,dd)
        setattr(namespace, self.dest, value)

class arg_to_utcsec(argparse.Action):
    """
    argparse-action to handle command-line arguments of 
    the form "dd/mm/yyyy" (string type), and converts
    it to UTC-seconds.
    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(arg_to_utcsec, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        #print '%r %r %r' % (namespace, values, option_string)
        dd,mm,yyyy = map(int, values.split('/'))
        value = (datetime(yyyy,mm,dd)-datetime(1970,1,1)).total_seconds()
        setattr(namespace, self.dest, value)

class My2DArray(object):
    """
    wrapper around numpy array with:
    - flexible number of rows
    - records the maximum nrow requested
    NOTE:
    This was test for 1D and 2D arrays.
    """
    def __init__(self, shape, dtype=np.float32):
        self.this = np.empty(shape, dtype=dtype)
        setattr(self, '__array__', self.this.__array__)

    def resize_rows(self, nx_new=None):
        """ Increment TWICE the size of axis=0, **without**
        losing data.
        """
        sh_new = np.copy(self.this.shape)
        nx     = self.this.shape[0]
        if nx_new is None:
            sh_new[0] = 2*sh_new[0]
        elif nx_new<=nx:
            return 0 # nothing to do
        else:
            sh_new[0] = nx_new

        tmp    = self.this.copy()
        #print "----> tmp: ", tmp.shape
        new    = np.zeros(sh_new)
        new[:nx] = tmp
        self.this = new
        """
        for some reason (probably due to numpy 
        implementation), if we don't do this, the:
        >>> print self.__array__()
        
        stucks truncated to the original size that was
        set in __init__() time.
        So we need to tell numpy our new resized shape!
        """
        setattr(self, '__array__', self.this.__array__)

    def __get__(self, instance, owner):
        return self.this

    def __getitem__(self, i):
        return self.this[i]

    def __setitem__(self, i, value):
        """ 
        We can safely use:
        >>> ma[n:n+m,:] = [...]

        assuming n+m is greater than our size in axis=0.
        """
        stop = i
        if type(i)==slice:
            stop = i.stop
        elif type(i)==tuple:
            if type(i[0])==slice:
                """
                in case:
                ma[n:n+m,:] = ...
                """
                stop = i[0].stop
            else:
                stop = i[0]

        #--- if requested row exceeds limits, duplicate
        #    our size in axis=0
        if stop>=self.this.shape[0]:
            nx_new = self.this.shape[0]
            while nx_new<=stop:
                nx_new *= 2
            self.resize_rows(nx_new)

        self.this[i] = value
        #--- register the maximum nrow requested.
        # NOTE here we are referring to size, and *not* row-index.
        self.max_nrow_used = stop+1 # (row-size, not row-index)

    def __getattr__(self, attnm):
        return getattr(self.this, attnm)

def ACEepoch2date(ace_epoch):
    """
    ace_epoch: seconds since 1/1/96
    """
    date = datetime(1996,1,1) + timedelta(seconds=ace_epoch)
    return date

def date2ACEepoch(date):
    ace_o = datetime(1996,1,1)
    return (date - ace_o).total_seconds()

#+++++++++++++++++++++++++++++++++
if __name__=='__main__':
    print " ---> this is a library!\n"

#EOF
