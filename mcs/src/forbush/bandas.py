from numpy import *
from pylab import *
from scipy.io.netcdf import netcdf_file
from datetime import datetime, time
from read_table import t_shck
from funcs import *

fname_inp_murdo = "../../../../../actividad_solar/neutron_monitors/mcmurdo/mcmurdo_utc_correg.dat"
fname_inp_evs   = "../../data_317events_iii.nc"
data_murdo              = loadtxt(fname_inp_murdo, unpack=True)
f_events        = netcdf_file(fname_inp_evs, 'r')

Afd             = f_events.variables['A_FD'].data
MC              = f_events.variables["MC_sig"].data
t_onset         = f_events.variables['t_onset'].data
taufd           = f_events.variables['tau_FD'].data
rate_pre        = f_events.variables['rate_pre'].data
cond_wTau       = f_events.variables['cond_wTau'].data    # perfiles exp "bonitos"

cond_wTau       = array(cond_wTau, bool)

THRES   = 0.51
ratio   = t_onset / taufd
nonans  = ~isnan(ratio)

cond    = []
cond    += [ ((MC==0) & nonans) & cond_wTau ]           # irregular icme
cond    += [ ((MC==1) & nonans) & cond_wTau ]           # B-field rotation
cond    += [ ((MC==2) & nonans) & cond_wTau ]           # MCs only
cond    += [ ((MC>=1) & nonans) & cond_wTau ]           # MCs & B-field rotation
cond    += [ ((MC>=0) & nonans) & cond_wTau ]           # all ICMEs
cond    += [ ((MC<=1) & nonans) & cond_wTau ]           # all ICMEs, except MCs

#--- filtramos por ratio:
cond[0] = cond[0] & (ratio<THRES)
cond[1] = cond[1] & (ratio<THRES)
cond[2] = cond[2] & (ratio<THRES)
cond[3] = cond[3] & (ratio<THRES)
cond[4] = cond[4] & (ratio<THRES)
cond[5] = cond[5] & (ratio<THRES)
n_selec	= len(cond)

labels	= []
labels	+= ["irregular ICMEs"]
labels	+= ["B-field rotation"]
labels	+= ["MCs only"]
labels	+= ["MCs & B-field rotation"]
labels	+= ["all ICMEs"]
labels	+= ["all ICMEs, exluding MCs"]

ind     = []
ind     += [find(cond[0])]                      # irregular icme
ind     += [find(cond[1])]                      # B-field rotation
ind     += [find(cond[2])]                      # MCs only
ind     += [find(cond[3])]                      # MCs & B-field rotation
ind     += [find(cond[4])]                      # all ICMEs
ind     += [find(cond[5])]                      # all ICMEs, excluding MCs

n	= zeros(n_selec)
n[0]    = len(ind[0])
n[1]    = len(ind[1])
n[2]    = len(ind[2])
n[3]    = len(ind[3])
n[4]    = len(ind[4])
n[5]    = len(ind[5])
print "n0, n1, n2, n3, n4: %d, %d, %d, %d, %d, %d" % (n[0], n[1], n[2], n[3], n[4], n[5])
adap	= []

for j in range(n_selec):
	taumin  = min(taufd[cond[j]])
	taumax  = max(taufd[cond[j]])
	print " ==== partial selection #%d (n=%d): '%s' ====" % (j, n[j], labels[j])
	print " ---> tau [days] (min/max): %2.1f / %2.1f" % (taumin, taumax)
	print " ---> nro of events: %d" % n[j]
	dt	= (1./24.) / taumin
	print " dt: ", dt
	adap	= []

	for i in ind[j]:
		print "    id: ", i
		t, r            = selecc_data(data_murdo, t_shck[i])
		t               = t / taufd[i]
		r               = 100.*(r - rate_pre[i]) / rate_pre[i]
		r               = r / (-Afd[i])

		adap		+= [ adaptar(dt, t, r) ]

	adap	= array(adap)	# (nro eventos) x (2) x (nro de puntos de rejilla adaptada)
	nn	= len(adap.T)	# nro de puntos en la rejilla adaptada
	avr_t	= zeros(nn)
	avr_r	= zeros(nn)
	std_r	= zeros(nn)
	sup_r	= zeros(nn)
	inf_r	= zeros(nn)
	for i in range(nn):
		avr_t[i], avr_r[i]	= mean(adap.T[i], axis=1)
		std_r[i]		= std(adap.T[i], axis=1)[1]
		sup_r[i]		= avr_r[i] + std_r[i]
		inf_r[i]		= avr_r[i] - std_r[i]
	#-----------------------------------------------------
	fig	= figure(1, figsize=(6, 4))
	ax	= fig.add_subplot(111)

	ax.plot(avr_t, avr_r, lw=6., c='black')
	ax.fill_between(avr_t, inf_r, sup_r, facecolor='gray', alpha=0.5)

	text    = "%s\n$t_{onset}/\\tau \leq$ %2.1f\n%d events" % (labels[j], THRES, n[j])
	ax.text(-.8, 1.2, text, fontsize=13.)

	ax.set_xlabel("[$\\tau_{FD}$]", fontsize=15)
	ax.set_ylabel("[$A_{FD}$]", fontsize=15)
	ax.grid()
	ax.set_xlim(-1., 4.)
	ax.set_ylim(-2., 2.)
	fname_png	= "bandas_tonset.o.tau_%2.1f_%d.png" % (THRES, j)
	fig.savefig(fname_png, format='png', dpi=300, bbox_inches='tight')
	print " hemos creado %s" % fname_png
	close()
	#-----------------------------------------------------
# cerramos archivo
f_events.close()
##
