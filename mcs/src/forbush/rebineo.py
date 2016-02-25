from pylab import *
from numpy import *
from scipy.io.netcdf import netcdf_file
from datetime import datetime, time
from funcs import *
from read_NewTable import tshck, tini_icme, tend_icme, tini_mc, tend_mc, n_icmes, MCsig
from ShiftTimes import *
import numpy as np

def thetacond(ThetaThres, ThetaSh):
    if ThetaThres<0.:
        return ones(len(ThetaSh), dtype=bool)
    else:
        return (ThetaSh > ThetaThres)

day             = 86400.
fname_ace       = '../../../../../../../data_ace/64sec_mag-swepam/ace.1998-2014.nc'
fname_events    = '../../../../data_317events_iii.nc'
f_ace           = netcdf_file(fname_ace, 'r')
f_events        = netcdf_file(fname_events, 'r')
print " -------> archivos leidos!"
#----------------------------------------------------------
DayInMin= 24*60.
dtmin   = 2.88      # [min] ventana minima en q voy a promediar
dTmin   = 0.1*DayInMin  # [min] (*) duracion minima q pido para las sheaths
                        # q entran en mi promedio.
                        # (*) esto debe dar 0.1days para nbin=50, y dtmin=2.88.
dTday   = dTmin*60./day # [day] lo mismo q 'dTmin' pero en dias
print " leyendo tiempo..."
t_utc   = utc_from_omni(f_ace)
print " Ready."
#------------------------------------ EVENTOS
#MCsig  = array(f_events.variables['MC_sig'].data)  # 2,1,0: MC, rotation, irregular
#Vnsh   = array(f_events.variables['wang_Vsh'].data) # veloc normal del shock
ThetaSh    = np.array(f_events.variables['wang_theta_shock'].data) # orientacion de la normal del shock
i_V         = np.array(f_events.variables['i_V'].data) # velocidad de icme
#------------------------------------

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++ begin: SELECCION DE EVENTOS ++++++++++++++++++++++
#------- fechas
BETW1998_2006   = np.ones(n_icmes, dtype=bool)
for i in range(307, n_icmes)+range(0, 26):
        BETW1998_2006[i]=False # 'False' para excluir eventos

#------- seleccionamos MCs con label-de-catalogo (lepping=2, etc)
#MCwant  = {'flags':     ('0', '1', '2', '2H'),
#           'alias':     '0.1.2.2H'}       # para "flagear" el nombre/ruta de las figuras
#MCwant  = {'flags':     ('1', '2', '2H'),
#           'alias':     '1.2.2H'}         # para "flagear" el nombre/ruta de las figuras
#MCwant  = {'flags':     ('2', '2H'),
#           'alias':     '2.2H'}           # para "flagear" el nombre/ruta de las figuras
MCwant  = {'flags':     ('2',),
           'alias':     '2'}            # para "flagear" el nombre/ruta de las figuras
MC_FLAG = np.ones(n_icmes, dtype=bool)
for i in range(n_icmes):
        MC_FLAG[i]  = MCsig[i] in MCwant['flags']

#------- excluimos eventos de 2MCs
EVENTS_with_2MCs= (26, 148, 259, 295)
MCmultiple      = False                         # True para incluir eventos multi-MC
MCmulti         = np.ones(n_icmes, dtype=bool)  # False para eventos multi-MC (SI, escribi bien)
if(~MCmultiple): 
    for i in EVENTS_with_2MCs: 
        MCmulti[i] &= False

#------- orientacion del shock (catalogo Wang)
ThetaThres     = -1 #90 #-1 #130.       # rango : [90:180]
ThetaCond      = thetacond(ThetaThres, ThetaSh)

#------- duration of sheaths
dt_mc       = diff_dates(tend_mc, tini_mc)/day     # [day]
DURATION    = dt_mc > dTday

#------- speed of icmes
v_lo        = 100.0      #550.0  #450.0 #100.0
v_hi        = 450.0     #3000.0 #550.0 #450.0
SpeedCond   = (i_V>=v_lo) & (i_V<v_hi)

#------- filtro total
SELECC  = np.ones(n_icmes, dtype=bool)
SELECC  &= BETW1998_2006     # nos mantenemos en este periodo de anios
SELECC  &= MCmulti          # nubes multiples
SELECC  &= MC_FLAG          # catalogo de nubes
SELECC  &= DURATION         # no queremos sheaths q duran 1hr xq solo aportan ruido
SELECC  &= ThetaCond        # cerca a 180 es nariz del shock
SELECC  &= SpeedCond
#+++++++++++++++++ end: SELECCION DE EVENTOS +++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#++++++++++++++++++++ CORRECCION DE BORDES +++++++++++++++++++++++++++++
# IMPORTANTE:
# Solo valido para los "63 eventos" (MCflag='2', y visibles en ACE)
# NOTA: dan saltos de shock mas marcados con True.
CorrShift = True #False #True 
if CorrShift:
    ShiftCorrection(ShiftDts, tshck)
    ShiftCorrection(ShiftDts, tini_icme)
    ShiftCorrection(ShiftDts, tend_icme)
    ShiftCorrection(ShiftDts, tini_mc)
    ShiftCorrection(ShiftDts, tend_mc)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
B       = np.array(f_ace.variables['Bmag'].data)
Vsw     = np.array(f_ace.variables['Vp'].data)
Temp    = np.array(f_ace.variables['Tp'].data)
Pcc     = np.array(f_ace.variables['Np'].data)
rmsB    = np.array(f_ace.variables['dBrms'].data)
alphar  = np.array(f_ace.variables['Alpha_ratio'].data)
beta    = calc_beta(Temp, Pcc, B)
rmsBoB  = rmsB/B

print " -------> variables leidas!"
#------------------------------------ VARIABLES
VARS = []
# variable, nombre archivo, limite vertical, ylabel
VARS += [[B, 'B', [5., 18.], 'B [nT]']]
VARS += [[Vsw, 'V', [380., 650.], 'Vsw [km/s]']]
VARS += [[rmsBoB, 'rmsBoB', [0.01, 0.2], 'rms($\hat B$/|B|) [1]']]
VARS += [[beta, 'beta', [0.001, 5.], '$\\beta$ [1]']]
VARS += [[Pcc, 'Pcc', [2, 17.], 'proton density [#/cc]']]
VARS += [[Temp, 'Temp', [1e4, 4e5], 'Temp [K]']]
VARS += [[alphar, 'AlphaRatio', [1e-3, 0.1], 'alpha ratio [1]']]
nvars = len(VARS)
#---------
nbefore = 2
nafter  = 4
nbin    = (1 + nbefore + nafter)*50  # [1] nro de bines q quiero en mi perfil promedio
fgap    = 0.2   # fraccion de gap que tolero
# nEnough: nmbr of events aporting good data in 80% of the window
dVARS, nEnough, Enough, IDs = avrs_and_stds(
            [nbefore, nafter], 
            SELECC,
            n_icmes, tini_mc, tend_mc, dTday, nbin, t_utc, VARS, fgap)
#------------------------------------
tnorm = dVARS[0][2]
#-------------------------------------------------------------
##
