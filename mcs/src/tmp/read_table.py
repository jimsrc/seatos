#
from numpy import *
from pylab import *
from datetime import datetime, time
#
# recibe un arhivo, para leer fechas/horas cuyo formato es "string", de 
# la forma: 1997/02/09/1321
def leer_fechas(FILE, ncol):
	t_ini	= []
	for line in FILE:
		date			= line.split()[ncol]	# [string] fecha del shock
		fecha			= date.split('/')	# [string] vector de strings tipo ['2009', '12', '19', '1000']
		# obtenemos la fecha
		yy, mm, dd, hora_mix	= map(int, fecha)
		# la ultima parte, la hora, hay q "splitearlo":
		HH			= hora_mix/100
		MM			= mod(hora_mix, 100)

		shock_time		= datetime(yy, mm, dd, HH, MM, 0, 0)
		t_ini.append(shock_time)

	return t_ini
#---------------------------------------------
fname_tabla	= "../../../../../icmes_richardson10.txt"

# fechas de shocks
file		= open(fname_tabla, 'r')	# abrimos para lectura
t_shck		= leer_fechas(file, 0)

# inicio del ICME
file		= open(fname_tabla, 'r')	# abrimos para lectura
ti_icme		= leer_fechas(file, 1)

# fin del ICME
file		= open(fname_tabla, 'r')	# abrimos para lectura
tf_icme		= leer_fechas(file, 2)
#
n_icmes		= size(t_shck)
