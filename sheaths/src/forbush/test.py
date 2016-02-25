from numpy import *
from pylab import *
from Scientific.IO.NetCDF import NetCDFFile
from datetime import datetime, time
from read_table import t_shck
from funcs import *

fname_inp_murdo	= "../../../../actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat"
fname_inp_evs	= "../data_317events_iii.nc"
data_murdo		= loadtxt(fname_inp_murdo, unpack=True)
f_events    	= NetCDFFile(fname_inp_evs, 'r')

Afd     	= f_events.variables['A_FD'].getValue()
MC  		= f_events.variables["MC_sig"].getValue()
t_onset 	= f_events.variables['t_onset'].getValue()
taufd   	= f_events.variables['tau_FD'].getValue()
rate_pre   	= f_events.variables['rate_pre'].getValue()
cond_wTau	= f_events.variables['cond_wTau'].getValue()	# perfiles exp "bonitos"

cond_wTau	= array(cond_wTau, bool)

THRES	= 0.33
ratio	= t_onset / taufd
nonans	= ~isnan(ratio)

cond	= []
cond	+= [ ((MC==0) & nonans) & cond_wTau ]		# irregular icme
cond	+= [ ((MC==1) & nonans) & cond_wTau ]	 	# B-field rotation
cond	+= [ ((MC==2) & nonans) & cond_wTau ]		# MCs only

#--- filtramos por ratio:
cond[0]	= cond[0] & (ratio<THRES)
cond[1]	= cond[1] & (ratio<THRES)
cond[2]	= cond[2] & (ratio<THRES)

ind	= []
ind	+= [find(cond[0])]			# irregular icme
ind	+= [find(cond[1])]			# B-field rotation
ind	+= [find(cond[2])]			# MCs only

n0	= len(ind[0])
n1	= len(ind[1])
n2	= len(ind[2])
print "n0, n1, n2: %d, %d, %d" % (n0, n1, n2)

import time
for j in range(3):
	taumin	= min(taufd[cond[j]])
	taumax	= max(taufd[cond[j]])
	print " partial selection #", j
	print " tau [days] (min/max): %2.1f / %2.1f" % (taumin, taumax)
	fig0     = figure(1, figsize=(6, 4))
	fig1     = figure(2, figsize=(6, 4))
	ax0      = fig0.add_subplot(111)
	ax1      = fig1.add_subplot(111)
	dt		= (1./24.) / taumin				# [1]
	print " dt: ", dt

	for i in ind[j]:
		print "    id: ", i
		t, r		= selecc_data(data_murdo, t_shck[i])		# [days], [cnts/s]
		t		= t / taufd[i]
		r		= 100.*(r - rate_pre[i]) / rate_pre[i]
		r		= r / (-Afd[i])

		fig0, ax0	= plotear_perfil_i (fig0, ax0, i, j, [t, r])

		fig1, ax1	= plotear_perfil_ii(fig1, ax1, i, j, [t, r], dt)
		#a, b		= plotear_perfil_ii(fig1, ax1, i, j, [t, r], dt)
		#time.sleep(1)
	close(fig0)
	close(fig1)
#
##
