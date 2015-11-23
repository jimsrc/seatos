from pylab import *
from numpy import *
from scipy.io.netcdf import netcdf_file
from datetime import datetime, time
from funcs import *
from read_NewTable import tshck, tini_icme, tend_icme, tini_mc, tend_mc, n_icmes, MCsig
from ShiftTimes import *

def thetacond(ThetaThres, ThetaSh):
	if ThetaThres<0.:
		return ones(len(ThetaSh), dtype=bool)
	else:
		return (ThetaSh > ThetaThres)

day		= 86400.
#fname_omni	= '../../../../../../data_omni/jan1996_jan2010/binary_format/omni_1996-2010.nc'
#fname_ace       = '../../../../../../../data_ace/64sec_mag-swepam/ace.1998-2014.nc'
fname_aceMulti  = '../../../../../../../data_ace/1hr_multi/ace.1998-2013.nc'
fname_events	= '../../../../data_317events_iii.nc'
#f_ace		= netcdf_file(fname_ace, 'r')
f_aceMulti	= netcdf_file(fname_aceMulti, 'r')
f_events	= netcdf_file(fname_events, 'r')
print " -------> archivos leidos!"
#----------------------------------------------------------
DayInMin= 24*60.
dtmin	= 2.88		# [min] ventana minima en q voy a promediar
dTmin	= 0.1*DayInMin	# [min] (*) duracion minima q pido para las sheaths
			# q entran en mi promedio.
			# (*) esto debe dar 0.1days para nbin=50, y dtmin=2.88.
dTday	= dTmin*60./day	# [day] lo mismo q 'dTmin' pero en dias
print " leyendo tiempo..."
t_utc	= utc_from_omni(f_aceMulti)
print " Ready."
#------------------------------------ EVENTOS
#MCsig	= array(f_events.variables['MC_sig'].data)  # 2,1,0: MC, rotation, irregular
#Vnsh	= array(f_events.variables['wang_Vsh'].data) # veloc normal del shock
#ThetaSh	= array(f_events.variables['wang_theta_shock'].data) # veloc normal del shock
#------------------------------------
#++++++++++++++++++++ SELECCION DE EVENTOS +++++++++++++++++++++++++
#ThetaThres     = 130 #-1 #130.
#ThetaCond      = thetacond(ThetaThres, ThetaSh)
BETW1998_2006   = ones(n_icmes, dtype=bool)
for i in range(307, n_icmes)+range(0, 26):
        BETW1998_2006[i]=False # 'False' para excluir eventos
SELECC  = BETW1998_2006
# seleccionamos solo los de flag>'MCwant'
#MCwant  = {'flags':     ('2', '2H'),
#           'alias':     '2.2H'}            # para "flagear" el nombre/ruta de las figuras
MCwant  = {'flags':     ('2',),
           'alias':     '2'}            # para "flagear" el nombre/ruta de las figuras
for i in range(n_icmes):
        cc         = MCsig[i] in MCwant['flags']
        SELECC[i] &= cc
#SELECC                 = ((MCsig>=MCwant) & (BETW1998_2006)) #& (ThetaCond)
# excluimos eventos de 2MCs
EVENTS_with_2MCs= (26, 148, 259, 295)
MCmultiple      = False                 # para "flagear" el nombre/ruta de las figuras
for i in EVENTS_with_2MCs:
        if(~MCmultiple): SELECC[i] &= False
#++++++++++++++++++++ CORRECCION DE BORDES +++++++++++++++++++++++++++++
# IMPORTANTE:
# Solo valido para los "63 eventos" (MCflag='2', y visibles en ACE)
CorrShift = False#True
if CorrShift:
	ShiftCorrection(ShiftDts, tshck)
	ShiftCorrection(ShiftDts, tini_icme)
	ShiftCorrection(ShiftDts, tend_icme)
	ShiftCorrection(ShiftDts, tini_mc)
	ShiftCorrection(ShiftDts, tend_mc)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""B       = array(f_ace.variables['Bmag'].data)
Vsw     = array(f_ace.variables['Vp'].data)
Temp    = array(f_ace.variables['Tp'].data)
Pcc     = array(f_ace.variables['Np'].data)
rmsB	= array(f_ace.variables['dBrms'].data)
alphar	= array(f_ace.variables['Alpha_ratio'].data)
beta	= calc_beta(Temp, Pcc, B)
rmsBoB	= rmsB/B"""
O7O6	= array(f_aceMulti.variables['O7toO6'].data)

print " -------> variables leidas!"
#------------------------------------ VARIABLES
VARS = []
# variable, nombre archivo, limite vertical, ylabel
VARS += [[O7O6, 'o7o6', [0., 1.5], 'O7/O6 [1]']]
"""VARS += [[B, 'B', [5., 18.], 'B [nT]']]
VARS += [[Vsw, 'V', [380., 650.], 'Vsw [km/s]']]
VARS += [[beta, 'beta', [0.001, 5.], '$\\beta$ [1]']]
VARS += [[Pcc, 'Pcc', [2, 17.], 'proton density [#/cc]']]
VARS += [[Temp, 'Temp', [1e4, 4e5], 'Temp [K]']]
VARS += [[rmsBoB, 'rmsBoB', [0.01, 0.1], 'rms($\hat B$/|B|) [1]']]
VARS += [[alphar, 'AlphaRatio', [0.02, 0.1], 'alpha ratio [1]']]"""
nvars = len(VARS)
#---------
nbefore	= 1
nafter	= 1
nbin	= (1 + nbefore + nafter)*50  # [1] nro de bines q quiero en mi perfil promedio
fgap	= 0.2 	# fraccion de gap que tolero
# nEnough: nmbr of events aporting good data in 80% of the window
dVARS, nEnough, Enough = avrs_and_stds([nbefore, nafter], 
			SELECC,
			n_icmes, tini_mc, tend_mc, dTday, nbin, t_utc, VARS, fgap)
#------------------------------------
tnorm = dVARS[0][2]
#-------------------------------------------------------------
##
