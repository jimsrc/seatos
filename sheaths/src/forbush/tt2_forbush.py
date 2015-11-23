#!/usr/bin/env ipython
import os
from rebineo_forbush import *
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import console_colors as ccl

def makefig(medVAR, avrVAR, stdVAR, nVAR, tnorm, 
        dTday, SUBTITLE, YLIMS, YLAB, fname_fig):
    fig     = figure(1, figsize=(13, 6))
    ax      = fig.add_subplot(111)

    ax.plot(tnorm, avrVAR, 'o-', c='black', markersize=5, label='mean')
    ax.plot(tnorm, medVAR, 'o-', c='red', alpha=.5, markersize=5, markeredgecolor='none', label='median')
    inf     = avrVAR + stdVAR/sqrt(nVAR)
    sup     = avrVAR - stdVAR/sqrt(nVAR)
    ax.fill_between(tnorm, inf, sup, facecolor='gray', alpha=0.5)
    trans   = transforms.blended_transform_factory(
            ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((0., 0.), width=1.0, height=1,
            transform=trans, color='orange',
            alpha=0.3)
    ax.add_patch(rect1)

    ax.legend(loc='upper right')
    ax.grid()
    #ax.set_ylim(YLIMS)
    TITLE = SUBTITLE
    ax.set_title(TITLE)
    ax.set_xlabel('time normalized to sheath passage time [1]')
    ax.set_ylabel(YLAB)
    savefig(fname_fig, format='png', dpi=180, bbox_inches='tight')
    close()

def wangflag(ThetaThres):
    if ThetaThres<0:
        return 'NaN'
    else:
        return str(ThetaThres)

#-------------------- para figuras:
#Nsh     = dVARS[0][0]
WangFlag = wangflag(ThetaThres) #'NaN' #wangflag(ThetaThres)

# prefijo gral para los nombres de los graficos:
if CorrShift:
    prexShift =  'wShiftCorr'
else:
    prexShift = 'woShiftCorr'
DIR_FIGS    = '../../plots/MCflag%s/%s' % (MCwant['alias'], prexShift)
DIR_ASCII   = '../../ascii/MCflag%s/%s' % (MCwant['alias'], prexShift)
os.system('mkdir -p %s' % DIR_FIGS)
os.system('mkdir -p %s' % DIR_ASCII)
print ccl.On + " -------> creando: %s" % DIR_FIGS + ccl.W
print ccl.On + " -------> creando: %s" % DIR_ASCII + ccl.W

FNAMEs = 'MCflag%s_%dbefore.%dafter_Wang%s_fgap%1.1f_vlo.%3.1f.vhi.%4.1f_forbush' % (MCwant['alias'], nbefore, nafter, WangFlag, fgap, v_lo, v_hi)
FNAME_ASCII = '%s/%s' % (DIR_ASCII, FNAMEs)
FNAME_FIGS  = '%s/%s' % (DIR_FIGS, FNAMEs)

fname_nro   = DIR_ASCII+'/'+'n.events_'+FNAMEs+'.txt'
fnro        = open(fname_nro, 'w')

#------------------------------------------------------------------------------------
for i in range(nvars):
    fname_fig = '%s_%s.png' % (FNAME_FIGS, VARS[i][1])
    print ccl.Rn+ " ------> %s" % fname_fig
    varname = VARS[i][1]
    ylims   = VARS[i][2]
    ylabel  = VARS[i][3]
    mediana = dVARS[i][4]
    average = dVARS[i][3]
    std_err = dVARS[i][5]
    nValues = dVARS[i][6]       # nmbr of good values aporting data
    binsPerTimeUnit = nbin/(1+nbefore+nafter)
    N_selec = dVARS[i][0]
    N_final = nEnough[i]

    SUBTITLE = '# of selected events: %d \n\
        events w/80%% of data: %d \n\
        bins per time unit: %d \n\
        MCflag: %s \n\
        WangFlag: %s' % (N_selec, N_final, binsPerTimeUnit, MCwant['alias'], WangFlag)

    makefig(mediana, average, std_err, nValues, tnorm,
            dTday, SUBTITLE, ylims, ylabel, fname_fig)

    fdataout = '%s_%s.txt' % (FNAME_ASCII, varname)
    dataout = np.array([tnorm, mediana, average, std_err, nValues])
    print " ------> %s\n" % fdataout + ccl.W
    np.savetxt(fdataout, dataout.T, fmt='%12.5f')

    #-------- grabamos nro de eventos selecc para esta variable
    line = '%s %d %d\n' % (varname, N_final, N_selec)
    fnro.write(line)

print ccl.Rn + " --> nro de eventos seleccionados: " + fname_nro + ccl.W
fnro.close()


#---------------------------------------------- begin: NC_FILE
print "\n**************************************** begin: NC_FILE"
#------- generamos registro de id's de los 
#        eventos q entraron en los promedios. 
#        Nota: un registro por variable.
fname_out   = DIR_ASCII+'/'+'_stuff_'+FNAMEs+'.nc' #'./test.nc'
fout        = netcdf_file(fname_out, 'w')
print "\n ----> generando: %s\n" % fname_out
for i in range(nvars):
    varname  = VARS[i][1]
    print " ----> " + varname
    n_events = len(IDs[varname])
    dimname  = 'nevents_'+varname
    fout.createDimension(dimname, n_events)
    prom     = dVARS[i][7]
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
    dt       = np.zeros(len(ids))
    for i in range(len(ids)):
        id  = ids[i]
        dt[i] = dt_sheath[id]
    vname    = 'dt_sh_'+varname
    write_variable(fout, vname, dims, dt, 'd', '[days]')

fout.close()
print "**************************************** end: NC_FILE"
#---------------------------------------------- end: NC_FILE



##
