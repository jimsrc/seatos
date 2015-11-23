from numpy import *
from pylab import *
from datetime import datetime, time, timedelta
import numpy as np
import console_colors as ccl
from scipy.io.netcdf import netcdf_file
from ShiftTimes import *
import os
import matplotlib.patches as patches
import matplotlib.transforms as transforms

#from read_NewTable import tshck, tini_icme, tend_icme, tini_mc, tend_mc, n_icmes, MCsig
#from z_expansion_gulisano import z as z_exp

def flags2nan(VAR, FLAG):
        cond            = VAR < FLAG
        VAR             = np.array(VAR)
        VAR[~cond]      = np.nan 
        return VAR


def date_to_utc(fecha):
    utc = datetime(1970, 1, 1, 0, 0, 0, 0)
    time = (fecha - utc).total_seconds()
    return time


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


def utc_from_omni(file):
    t = np.array(file.variables['time'].data)
    dates = dates_from_omni(t)
    n = len(dates)
    time = np.zeros(n)
    for i in range(n):
        time[i] = date_to_utc(dates[i])

    return time

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
    n   = len(var)
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


def adaptar_ii(nwndw, dT, n, dt, t, r, fgap):
    #n  = int(5./dt)            # nro de puntos en todo el intervalo de ploteo
    tt  = zeros(n)
    rr  = zeros(n)
    _nbin_  = n/(1+nwndw[0]+nwndw[1])   # nro de bins en la sheath/mc
    cc  = (t>0.) & (t<dT)       # intervalo de la sheath/mc
    enough  = enoughdata(r[cc], fgap)   # [bool] True si hay mas del 80% de data buena.
    if not(enough): rr  = nan*ones(n)   # si no hay suficiente data, este evento no aporta
    for i in range(n):
        tmin    = (i-nwndw[0]*_nbin_)*dt
        tmax    = tmin + dt
        cond    = (t>tmin) & (t<tmax)
        tt[i]   = mean(t[cond])#; print "tt:", t[i]; pause(1)
        if enough:
            cc    = ~isnan(r[cond])     # no olvidemos filtrar los gaps
            rr[i] = mean(r[cond][cc])

    return enough, [tt/dT, rr]          # tiempo normalizado x la duracion de la sheath/mc/etc


def selecc_window_ii(nwndw, data, tini, tend):
    time    = data[0]       #[s] utc sec
    y   = data[1]

    day     = 86400.                # [seg]
    utc     = datetime(1970, 1, 1, 0, 0, 0, 0)
    tini_utc    = (tini - utc).total_seconds()      # [s] utc sec
    tend_utc    = (tend - utc).total_seconds()      # [s] utc sec

    dt  = tend_utc - tini_utc
    ti  = tini_utc - nwndw[0]*dt            # [seg] utc
    tf  = tend_utc + nwndw[1]*dt
    cond    = (time > ti) & (time < tf)

    time    = (time[cond] - tini_utc) / day     # [days] since 'ti'
    y   = y[cond]
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


def mvs_for_each_event(VAR_adap, nbin, nwndw, Enough):
    nok         = size(VAR_adap, axis=0)
    mvs         = np.zeros(nok)            # valores medios por cada evento
    binsPerTimeUnit = nbin/(1+nwndw[0]+nwndw[1])    # nro de bines por u. de tiempo
    start       = nwndw[0]*binsPerTimeUnit  # en este bin empieza la MC
    #print " ----> binsPerTimeUnit: ", binsPerTimeUnit
    #print " ----> nok:  ", nok
    #print " ----> VAR_adap.shape: ", VAR_adap.shape
    #print " ----> VAR_adap: \n", VAR_adap
    #raw_input()

    for i in range(nok):
        aux = VAR_adap[i, start:start+binsPerTimeUnit]  # (*)
        cc  = ~isnan(aux)                   # pick good-data only
        #if len(find(cc))>1: 
        if Enough[i]:       # solo imprimo los q tienen *suficiente data*
            print ccl.G
            print "id %d/%d: "%(i+1, nok), aux[cc] 
            print ccl.W
            mvs[i] = np.mean(aux[cc])
        else: 
            mvs[i] = np.nan
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
    # http://pamela.roma2.infn.it/index.php
    # Beta = [(4.16*10**-5 * Tp) + 5.34] * Np/B**2 (B in nT)
    #
    beta = ((4.16*10**-5 * Temp) + 5.34) * Pcc/B**2
    return beta


def thetacond(ThetaThres, ThetaSh):
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


class general:
    def __init__(self):
        name='name'


class events_mgr:
    def __init__(self, gral, FILTER, CUTS, bd, nBin, fgap, tb, z_exp):
        #self.fnames     = fnames
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

        self.f_sc       = netcdf_file(gral.fnames['ACE'], 'r')
        self.f_events   = netcdf_file(gral.fnames['table_richardson'], 'r')
        print " -------> archivos input leidos!"


    def run_all(self):
        #----- seleccion de eventos
        self.filter_events()
        print "\n ---> filtrado de eventos (n:%d): OK\n" % (self.n_SELECC)
        #----- load data y los shiftimes "omni"
        self.load_data_and_timeshift()
        #----- rebineo y promedios
        self.rebine_and_avr()
        #----- hacer ploteos
        self.make_plots()
        #----- archivos "stuff"
        self.build_params_file()


    def rebine_and_avr(self):
        """def avrs_and_stds(nwndw, 
            SELECC, #MCsig, MCwant,
            n_icmes, tini, tend, dTday, nbin, t_utc, VARS, fgap):"""
        nvars   = self.nvars #len(VARS)
        n_icmes = self.tb.n_icmes
        bd      = self.bd
        VARS    = self.VARS
        nbin    = self.nBin['total']
        nwndw   = [self.nBin['before'], self.nBin['after']]
        day     = 86400.

        """print " ---> nbin: ", nbin
        print " ---> t_utc[0]: ", self.t_utc[0]
        print " ---> t_utc[-1]: ", self.t_utc[-1]
        print " ---> fgap: ", self.fgap
        print " ---> VARS[-1][1]: ", self.VARS[-1][1]
        print " ---> nwndw: ", nwndw
        print " ---> dTday: ", self.CUTS['dTday']
        print " ---> tini[0]: ", bd.tini[0]
        print " ---> tend[-110]: ", bd.tend[-110]"""
        #raw_input()

        ADAP    = []   # conjunto de varios 'adap' (uno x c/variable)
        # recorremos los eventos:
        nok=0; nbad=0; 
        nEnough = np.zeros(nvars)
        Enough  = np.zeros(n_icmes*nvars, dtype=bool).reshape(n_icmes, nvars)
        Enough  = []
        nnn     = 0     # nro de evento q pasan el filtro a-priori

        #---- quiero una lista de los eventos-id q van a incluirse en c/promedio :-)
        IDs     = {}
        for j in range(nvars): 
            varname      = VARS[j][1]
            IDs[varname] = []

        for i in range(n_icmes):
            #nok=0; nbad=0; 
            ok=False
            try:    #no todos los elementos de 'tend' son fechas (algunos eventos no tienen fecha definida)
                dT      = (bd.tend[i] - bd.tini[i]).total_seconds()/day  # [day]
                ok = True
            except:
                continue    # saltar al sgte evento 'i'

            #np.set_printoptions(4)         # nro de digitos a imprimir cuando use numpy.arrays
            if (ok & self.SELECC[i]):# (MCsig[i]>=MCwant)):  ---FILTRO--- (*1)
                nnn += 1
                print ccl.Gn + " id:%d ---> dT/day:%g" % (i, dT) + ccl.W
                nok +=1
                Enough += [ np.zeros(nvars, dtype=bool) ]   # todo False por defecto
                # recorremos las variables:
                for j in range(nvars):
                    varname = VARS[j][1]
                    dt      = dT*(1+nwndw[0]+nwndw[1])/nbin
                    t, var  = selecc_window_ii(
                            nwndw, #rango ploteo
                            [self.t_utc, VARS[j][0]],
                            bd.tini[i], bd.tend[i]
                            )
                    # rebinea usando 'dt' como el ancho de nuevo bineo
                    out       = adaptar_ii(nwndw, dT, nbin, dt, t, var, self.fgap)
                    enough    = out[0]       # True: data con menos de 100*'fgap'% de gap
                    Enough[nok-1][j] = enough
                    ADAP             += [ out[1] ] 
                    #print " out01: ", out[1]; raw_input()
                    if enough:
                        IDs[varname]    += [i]
                        nEnough[j]      += 1
            else:
                print ccl.Rn + " id:%d ---> dT/day:%g" % (i, dT) + ccl.W
                nbad +=1 

        print " ----> len.ADAP: %d" % len(ADAP)
        Enough      = np.array(Enough)
        stuff       = []
        #nok = len(ADAP)/nvars  # (*)
        # (*) la dim de 'ADAP' es 'nvars' por el nro de eventos q pasaro el filtro en (*1)
        for j in range(nvars):
            print ccl.On + " -------> procesando: %s" % VARS[j][3] + "  (%d/%d)" % (j+1,nvars)
            print " nEnough/nok/(nok+nbad): %d/%d/%d " % (nEnough[j], nok, nok+nbad) + ccl.W
            VAR_adap = np.zeros((nok, nbin))    # perfiles rebineados (*)
            # (*): uno de estos por variable
            # recorro los 'nok' eventos q pasaron el filtro de arriba:
            for i in range(nok):
                VAR_adap[i,:] = ADAP[i*nvars+j][1] # valores rebineados de la variable "j" para el evento "i"
            # valores medios de esta variable para c/evento
            avrVAR_adap = mvs_for_each_event(VAR_adap, nbin, nwndw, Enough.T[j])
            print " ---> (%d/%d) avrVAR_adap[]: \n" % (j+1,nvars), avrVAR_adap

            VAR_avrg        = np.zeros(nbin)
            VAR_avrgNorm    = np.zeros(nbin)
            VAR_medi        = np.zeros(nbin)
            VAR_std         = np.zeros(nbin)
            ndata           = np.zeros(nbin)
            for i in range(nbin):
                cond = ~np.isnan(VAR_adap.T[i,:])  # filtro eventos q no aportan data en este bin
                ndata[i] = len(find(cond))      # nro de datos != nan
                VAR_avrg[i] = np.mean(VAR_adap.T[i,cond])  # promedio entre los valores q no tienen flag
                VAR_avrgNorm[i] = np.mean(VAR_adap.T[i,cond]/avrVAR_adap[cond])
                VAR_medi[i] = np.median(VAR_adap.T[i,cond])# mediana entre los valores q no tienen flag
                VAR_std[i] = np.std(VAR_adap.T[i,cond])    # std del mismo conjunto de datos
                #--- calculo perfil normalizado por c/variable
                #ii = nwndw[0]*binsPerTimeUnit
                #AvrInWndw = mean(VAR_avrg[ii:ii+binsPerTimeUnit])
            tnorm   = ADAP[0][0]
            stuff += [[nok, nbad, tnorm, VAR_avrg, VAR_medi, VAR_std, ndata, avrVAR_adap]]

        #return stuff, nEnough, Enough, IDs
        self.out = OUT  = {}
        OUT['dVARS']    = stuff
        OUT['nEnough']  = nEnough
        OUT['Enough']   = Enough
        OUT['IDs']      = IDs
        OUT['tnorm']    = OUT['dVARS'][0][2]


    def load_data_and_timeshift(self):
        if self.data_name=='ACE':
            self.load_data_ACE()
        elif self.data_name=='McMurdo':
            self.load_data_McMurdo()
        else:
            print " --------> BAD 'self.data_name'!!!"
            print " exiting.... "
            raise SystemExit



    def load_data_McMurdo(self):
        tb          = self.tb
        nBin        = self.nBin
        bd          = self.bd
        day         = 86400.


    def load_data_ACE(self):
        tb          = self.tb
        nBin        = self.nBin
        bd          = self.bd
        day         = 86400.

        #----------------------------------------------------------
        print " leyendo tiempo..."
        t_utc   = utc_from_omni(self.f_sc)
        print " Ready."

        #++++++++++++++++++++ CORRECCION DE BORDES +++++++++++++++++++++++++++++
        # IMPORTANTE:
        # Solo valido para los "63 eventos" (MCflag='2', y visibles en ACE)
        # NOTA: dan saltos de shock mas marcados con True.
        if self.FILTER['CorrShift']:
            ShiftCorrection(ShiftDts, tb.tshck)
            ShiftCorrection(ShiftDts, tb.tini_icme)
            ShiftCorrection(ShiftDts, tb.tend_icme)
            ShiftCorrection(ShiftDts, tb.tini_mc)
            ShiftCorrection(ShiftDts, tb.tend_mc)
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        B       = np.array(self.f_sc.variables['Bmag'].data)
        Vsw     = np.array(self.f_sc.variables['Vp'].data)
        Temp    = np.array(self.f_sc.variables['Tp'].data)
        Pcc     = np.array(self.f_sc.variables['Np'].data)
        rmsB    = np.array(self.f_sc.variables['dBrms'].data)
        alphar  = np.array(self.f_sc.variables['Alpha_ratio'].data)
        beta    = calc_beta(Temp, Pcc, B)
        rmsBoB  = rmsB/B

        print " -------> variables leidas!"
        #------------------------------------ VARIABLES
        self.t_utc  = t_utc
        self.VARS = VARS = []
        # variable, nombre archivo, limite vertical, ylabel
        VARS += [[B, 'B', [5., 18.], 'B [nT]']]
        VARS += [[Vsw, 'V', [380., 650.], 'Vsw [km/s]']]
        VARS += [[rmsBoB, 'rmsBoB', [0.01, 0.2], 'rms($\hat B$/|B|) [1]']]
        VARS += [[beta, 'beta', [0.001, 5.], '$\\beta$ [1]']]
        VARS += [[Pcc, 'Pcc', [2, 17.], 'proton density [#/cc]']]
        VARS += [[Temp, 'Temp', [1e4, 4e5], 'Temp [K]']]
        VARS += [[alphar, 'AlphaRatio', [1e-3, 0.1], 'alpha ratio [1]']]
        self.nvars = len(VARS)
        #---------
        #nbin    = (1+nBin['before']+nBin['after'])*nBin['bins_per_utime']  # [1] nro de bines q quiero en mi perfil promedio
        #fgap    = 0.2   # fraccion de gap que tolero
        # nEnough: nmbr of events aporting good data in 80% of the window

        self.aux = aux = {}
        aux['SELECC']    = self.SELECC
        """aux['BETW1998_2006'] = BETW1998_2006
        aux['DURATION']  = DURATION
        if wang_filter: aux['ThetaCond'] = ThetaCond
        if vsw_filter:  aux['SpeedCond'] = SpeedCond
        if z_filter_on: aux['z_cond']    = z_cond
        aux['dt_mc']     = dt_mc
        aux['dt_sh']     = dt_sh"""

        #---- SALIDA:
        #self.VARS   = VARS
        #self.out    = out
        #self.aux    = aux


    #---- generar figuras y asciis de los perfiles promedio/mediana
    def make_plots(self):
        nBin        = self.nBin
        fgap        = self.fgap
        MCwant      = self.FILTER['MCwant']

        #dt_mc       = self.aux['dt_mc']
        #dt_sh       = self.aux['dt_sh']
        ThetaThres  = self.CUTS['ThetaThres']
        v_lo        = self.CUTS['v_lo']
        v_hi        = self.CUTS['v_hi']
        z_lo        = self.CUTS['z_lo']
        z_hi        = self.CUTS['z_hi']
        nbin        = (1+nBin['before']+nBin['after'])*nBin['bins_per_utime']  # [1] nro de bines q quiero en mi perfil promedio


        #-------------------- prefijos:
        # prefijo para filtro Wang:
        #WangFlag = wangflag(ThetaThres) #'NaN' #wangflag(ThetaThres)
        if self.FILTER['wang']:
            WangFlag = str(ThetaThres)
        else:
            WangFlag = 'NaN'

        # prefijo gral para los nombres de los graficos:
        if self.FILTER['CorrShift']:
            prexShift =  'wShiftCorr'
        else:
            prexShift = 'woShiftCorr'

        # filtro z-expansion
        if not(self.FILTER['z_filter_on']):
            z_lo = z_hi = 0.0 # estos valores significan q no hay filtro por z

        # filtro por Vmc (veloc del MC)
        if not(self.FILTER['vsw_filter']):
            v_lo = v_hi = 0.0 # estos valores significan q no hay filtro por Vmc

        #-------------------------------
        # nombres genericos...
        DIR_FIGS    = '%s/MCflag%s/%s' % (self.dir_plots, MCwant['alias'], prexShift)
        DIR_ASCII   = '%s/MCflag%s/%s' % (self.dir_ascii, MCwant['alias'], prexShift)
        os.system('mkdir -p %s' % DIR_FIGS)
        os.system('mkdir -p %s' % DIR_ASCII)
        print ccl.On + " -------> creando: %s" % DIR_FIGS + ccl.W
        print ccl.On + " -------> creando: %s" % DIR_ASCII + ccl.W

        FNAMEs = 'MCflag%s_%dbefore.%dafter_fgap%1.1f' % (MCwant['alias'], nBin['before'], nBin['after'], fgap)
        FNAMEs += '_Wang%s' % (WangFlag)
        FNAMEs += '_vlo.%03.1f.vhi.%04.1f' % (v_lo, v_hi)
        FNAMEs += '_zlo.%2.2f.zhi.%2.2f' % (z_lo, z_hi)

        FNAME_ASCII = '%s/%s' % (DIR_ASCII, FNAMEs)
        FNAME_FIGS  = '%s/%s' % (DIR_FIGS, FNAMEs)

        fname_nro   = DIR_ASCII+'/'+'n.events_'+FNAMEs+'.txt'
        fnro        = open(fname_nro, 'w')

        #--------------------------------------------------------------------------------
        nvars = len(self.VARS)
        for i in range(nvars):
            fname_fig = '%s_%s.png' % (FNAME_FIGS, self.VARS[i][1])
            print ccl.Rn+ " ------> %s" % fname_fig
            varname = self.VARS[i][1]
            ylims   = self.VARS[i][2]
            ylabel  = self.VARS[i][3]
            mediana = self.out['dVARS'][i][4]
            average = self.out['dVARS'][i][3]
            std_err = self.out['dVARS'][i][5]
            nValues = self.out['dVARS'][i][6] # nmbr of good values aporting data
            #binsPerTimeUnit = nbin  #nbin/(1+nbefore+nafter)
            N_selec = self.out['dVARS'][i][0]
            N_final = self.out['nEnough'][i] #nEnough[i]

            SUBTITLE = '# of selected events: %d \n\
                events w/80%% of data: %d \n\
                bins per time unit: %d \n\
                MCflag: %s \n\
                WangFlag: %s' % (N_selec, N_final, nBin['bins_per_utime'], MCwant['alias'], WangFlag)

            makefig(mediana, average, std_err, nValues, self.out['tnorm'], SUBTITLE, 
                    ylims, ylabel, fname_fig)

            fdataout = '%s_%s.txt' % (FNAME_ASCII, self.VARS[i][1])
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


    #---- construye archivo q contiene cosas de los eventos seleccionados:
    # - valores medios de los observables (B, Vsw, Temp, beta, etc)
    # - los IDs de los eventos
    # - duracion de los MCs y las sheaths
    def build_params_file(self):
        DIR_ASCII   = self.DIR_ASCII
        FNAMEs      = self.FNAMEs
        #---------------------------------------------- begin: NC_FILE
        print "\n**************************************** begin: NC_FILE"
        #------- generamos registro de id's de los 
        #        eventos q entraron en los promedios. 
        #        Nota: un registro por variable.
        fname_out   = DIR_ASCII+'/'+'_stuff_'+FNAMEs+'.nc' #'./test.nc'
        fout        = netcdf_file(fname_out, 'w')
        print "\n ----> generando: %s\n" % fname_out

        IDs = self.out['IDs']
        for i in range(len(self.VARS)):
            varname  = self.VARS[i][1]
            print " ----> " + varname
            n_events = len(IDs[varname])
            dimname  = 'nevents_'+varname
            fout.createDimension(dimname, n_events)
            prom     = self.out['dVARS'][i][7]
            cc       = np.isnan(prom)
            prom     = prom[~cc]
            dims     = (dimname,)
            write_variable(fout, varname, dims, 
                    prom, 'd', 'average_values per event')
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
        tb              = self.tb
        FILTER          = self.FILTER
        ThetaThres      = self.CUTS['ThetaThres']
        dTday           = self.CUTS['dTday']
        v_lo            = self.CUTS['v_lo'] 
        v_hi            = self.CUTS['v_hi']
        z_lo            = self.CUTS['z_lo']
        z_hi            = self.CUTS['z_hi']
        day             = 86400.
        #------------------------------------ EVENTS's PARAMETERS
        #MCsig  = array(f_events.variables['MC_sig'].data)  # 2,1,0: MC, rotation, irregular
        #Vnsh   = array(f_events.variables['wang_Vsh'].data) # veloc normal del shock
        ThetaSh = np.array(self.f_events.variables['wang_theta_shock'].data) # orientacion de la normal del shock
        i_V     = np.array(self.f_events.variables['i_V'].data) # velocidad de icme
        #------------------------------------

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++++++++++ begin: SELECCION DE EVENTOS ++++++++++++++++++++++
        #------- fechas
        BETW1998_2006   = np.ones(tb.n_icmes, dtype=bool)
        for i in range(307, tb.n_icmes)+range(0, 26):
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
            ThetaCond   = thetacond(ThetaThres, ThetaSh)

        #------- duration of sheaths
        self.dt_mc      = diff_dates(tb.tend_mc, tb.tini_mc)/day     # [day]
        self.dt_sh      = diff_dates(tb.tini_mc, tb.tshck)/day     # [day]
        dt              = diff_dates(self.bd.tend, self.bd.tini)/day
        DURATION        = dt > dTday    # sheaths>0

        #------- speed of icmes
        if (FILTER['vsw_filter']) & (v_lo<v_hi):
            SpeedCond   = (i_V>=v_lo) & (i_V<v_hi)

        #------- z expansion (a. gulisano)
        z_exp   = self.z_exp
        if (FILTER['z_filter_on']) & (z_lo<z_hi):
            z_cond      = (z_exp>=z_lo) & (z_exp<z_hi)

        #------- filtro total
        SELECC  = np.ones(tb.n_icmes, dtype=bool)
        SELECC  &= BETW1998_2006    # nos mantenemos en este periodo de anios
        SELECC  &= MCmulti          # nubes multiples
        SELECC  &= MC_FLAG          # catalogo de nubes
        SELECC  &= DURATION         # no queremos sheaths q duran 1hr xq solo aportan ruido
        if FILTER['wang']:        SELECC &= ThetaCond # cerca a 180 es nariz del shock
        if FILTER['vsw_filter']:  SELECC &= SpeedCond
        if FILTER['z_filter_on']: SELECC &= z_cond # para desactivar este filtro, comentar esta linea
        """print "+++ eventos +++++++++++++++++++++++++++++++++++++++"
        for i in range(tb.n_icmes):
            if SELECC[i]:
                print i
        raw_input()"""
        self.SELECC     = SELECC
        self.n_SELECC   = len(find(SELECC))
        #+++++++++++++++++ end: SELECCION DE EVENTOS +++++++++++++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.n_SELECC<=0:
            print " --------> FATAL ERROR!!!: self.n_SELECC=<0"
            print " exiting....... \n"
            raise SystemExit


##
