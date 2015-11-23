from numpy import *
from pylab import *
from datetime import datetime, time

def selecc_data(data, tshk):
	time	= data[0]
	rate	= data[1]

	day		= 86400.		# [seg]
	utc		= datetime(1970, 1, 1, 0, 0, 0, 0)
	tshk_utc	= (tshk - utc).total_seconds()

	ti	= tshk_utc - 10.*day		# [seg] utc
	tf	= tshk_utc + 30.*day
	cond 	= (time > ti) & (time < tf)

	time	= (time[cond] - tshk_utc) / day		# [days] since shock
	rate	= rate[cond]
	return (time, rate)

def plotear_perfil_i(fig, ax, i, j, data):
	time 	= data[0]
	rate	= data[1]
	ax.plot(time, rate, lw=.8, alpha=.3, label=i)
	leg = ax.legend(loc='center left', bbox_to_anchor=(1, 0.6), numpoints=1, fontsize=6)

	ax.set_xlim( -1., +4.)
	ax.set_ylim(-1.2, +1.)

	fname_png	= "profiles.norm.%d.png" % j
	fig.savefig(fname_png, format='png', dpi=300, bbox_extra_artists=(leg,), bbox_inches='tight')
	return fig, ax

def adaptar(dt, t, r):
	n 	= int(5./dt)		# nro de puntos en todo el intervalo de ploteo
	tt	= zeros(n)
	rr	= zeros(n)
	for i in range(n):
		tmin	= -1. + (i-.5)*dt
		tmax	= -1. + (i+.5)*dt
		cond	= (t>tmin) & (t<tmax)
		tt[i]	= mean(t[cond])
		rr[i]	= mean(r[cond])
	return [tt, rr]


def plotear_perfil_ii(fig, ax, i, j, data, dt):
	t	= data[0]		# [tau]
	r	= data[1]
	"""cond	= (t>-1.) & (t<4.)
	t	= t[cond]
	r	= data[1][cond]		# [Afd]"""

	t, r	= adaptar(dt, t, r)
	ax.scatter(t, r, alpha=.1, edgecolor='none', s=6.)
	ax.plot(t, r, alpha=.3, lw=.8, label=i)
	leg = ax.legend(loc='center left', bbox_to_anchor=(1, 0.6), numpoints=1, fontsize=6)

	ax.set_xlim( -1., +4.)
	ax.set_ylim(-1.2, +1.)

	fname_png	= "adapted.%d.png" % j
	fig.savefig(fname_png, format='png', dpi=300, bbox_extra_artists=(leg,), bbox_inches='tight')
	return fig, ax

