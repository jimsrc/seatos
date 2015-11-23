from numpy import *
from pylab import *
from datetime import datetime, time
import numpy as np
import console_colors as ccl

def flags2nan(VAR, FLAG):
        cond            = VAR < FLAG
        VAR             = array(VAR)
        VAR[~cond]      = nan 
        return VAR

def mask_with_nans(VAR, FLAG, SCflag, SCwant):
    print " ---> seleccionando s/c con flag: %s" % str(SCwant)
    if SCwant=='AnySC':
        VAR         = flags2nan(VAR, FLAG)
    else:
        VAR         = flags2nan(VAR, FLAG)
        nbef        = len(find(~isnan(VAR)))# nro de datos q no son NaNs, ANTES del filtro
        cond        = SCflag==SCwant
        VAR[~cond]  = nan           # todo lo q NO es del s/c 'SCwant', pongo NaNs
        naft        = len(find(~isnan(VAR)))# nro de datos q no son NaNs, DESPUES del filtro
        print " ----> (aft-bef)/bef [%%]: %2.2f" % (100.*(naft-nbef)/nbef)  # porcentaje de data filtrada
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

    day     = 86400.        # [seg]
    utc     = datetime(1970, 1, 1, 0, 0, 0, 0)
    tshk_utc    = (tshk - utc).total_seconds()

    ti  = tshk_utc - 10.*day        # [seg] utc
    tf  = tshk_utc + 30.*day
    cond    = (time > ti) & (time < tf)

    time    = (time[cond] - tshk_utc) / day     # [days] since shock
    rate    = rate[cond]
    return (time, rate)

def selecc_window(data, tini, tend):
    time    = data[0]       #[s] utc sec
    y   = data[1]

    day     = 86400.                # [seg]
    utc     = datetime(1970, 1, 1, 0, 0, 0, 0)
    tini_utc    = (tini - utc).total_seconds()      # [s] utc sec
    tend_utc    = (tend - utc).total_seconds()      # [s] utc sec

    ti  = tini_utc              # [seg] utc
    tf  = tend_utc
    cond    = (time > ti) & (time < tf)

    time    = (time[cond] - tini_utc) / day     # [days] since 'ti'
    y   = y[cond]
    return (time, y)

def plotear_perfil_i(fig, ax, i, j, data):
    time    = data[0]
    rate    = data[1]
    ax.plot(time, rate, lw=.8, alpha=.3, label=i)
    leg = ax.legend(loc='center left', bbox_to_anchor=(1, 0.6), numpoints=1, fontsize=6)

    ax.set_xlim( -1., +4.)
    ax.set_ylim(-1.2, +1.)

    fname_png   = "profiles.norm.%d.png" % j
    fig.savefig(fname_png, format='png', dpi=300, bbox_extra_artists=(leg,), bbox_inches='tight')
    return fig, ax




def plotear_perfil_ii(fig, ax, i, j, data, dt):
    t   = data[0]       # [tau]
    r   = data[1]
    """cond = (t>-1.) & (t<4.)
    t   = t[cond]
    r   = data[1][cond]     # [Afd]"""

    t, r    = adaptar(dt, t, r)
    ax.scatter(t, r, alpha=.1, edgecolor='none', s=6.)
    ax.plot(t, r, alpha=.3, lw=.8, label=i)
    leg = ax.legend(loc='center left', bbox_to_anchor=(1, 0.6), numpoints=1, fontsize=6)

    ax.set_xlim( -1., +4.)
    ax.set_ylim(-1.2, +1.)

    fname_png   = "adapted.%d.png" % j
    fig.savefig(fname_png, format='png', dpi=300, bbox_extra_artists=(leg,), bbox_inches='tight')
    return fig, ax

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
        #tt[i]   = mean(t[cond])#; print "tt:", t[i]; pause(1)
        tt[i]   = tmin + .5*dt
        if enough:
            cc    = ~isnan(r[cond])     # no olvidemos filtrar los gaps
            rr[i] = mean(r[cond][cc])

    return enough, [tt/dT, rr]          # tiempo normalizado x la duracion de la sheath/mc/etc

def selecc_window_ii(nwndw, data, tini, tend):
    time        = data[0]       #[s] utc sec
    y           = data[1]

    day         = 86400.                # [seg]
    utc         = datetime(1970, 1, 1, 0, 0, 0, 0)
    tini_utc    = (tini - utc).total_seconds()      # [s] utc sec
    tend_utc    = (tend - utc).total_seconds()      # [s] utc sec

    dt  = tend_utc - tini_utc
    ti  = tini_utc - nwndw[0]*dt            # [seg] utc
    tf  = tend_utc + nwndw[1]*dt
    cond    = (time > ti) & (time < tf)

    time    = (time[cond] - tini_utc) / day     # [days] since 'ti'
    y       = y[cond]
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


def avrs_and_stds(nwndw, 
        SELECC, #MCsig, MCwant,
        n_icmes, tini, tend, dTday, nbin, t_utc, VARS, fgap, rate_pre, Afd):
    nvars   = len(VARS)
    day     = 86400.
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
            dT      = (tend[i] - tini[i]).total_seconds()/day  # [day]
            ok = True
        except:
            continue    # saltar al sgte evento

        #np.set_printoptions(4)         # nro de digitos a imprimir cuando use numpy.arrays
        if (ok & SELECC[i]):# (MCsig[i]>=MCwant)):  ---FILTRO--- (*1)
            nnn += 1
            print ccl.Gn + " id:%d ---> dT/day:%g" % (i, dT) + ccl.W
            nok +=1
            Enough += [ np.zeros(nvars, dtype=bool) ]   # todo False por defecto
            # recorremos las variables:
            for j in range(nvars):
                varname = VARS[j][1]
                dt      = dT*(1+nwndw[0]+nwndw[1])/nbin
                t, var  = selecc_window_ii(
                        nwndw,       #nro de veces hacia atras y adelante
                        [t_utc, VARS[j][0]],
                        tini[i], tend[i]
                        )
                var = 100.*(var - rate_pre[i]) / rate_pre[i]
                #var = var / (-Afd[i])
                # rebinea usando 'dt' como el ancho de nuevo bineo
                out              = adaptar_ii(nwndw, dT, nbin, dt, t, var, fgap)
                enough           = out[0]       # True: data con menos de 100*'fgap'% de gap
                Enough[nok-1][j] = enough
                ADAP             += [ out[1] ] 
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
            cond = ~isnan(VAR_adap.T[i,:])  # filtro eventos q no aportan data en este bin
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
        print ccl.R + "\n >>> VAR_avrg:", VAR_avrg
        print "\n >>>tnorm:\n", tnorm, ccl.W, '\n'

    return stuff, nEnough, Enough, IDs

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
##
