from pylab import *
from numpy import *
import read_table as r1
import read_NewTable as r2

nok=0
for i in range(r1.n_icmes):
	nokk = nok
	for j in range(r2.n_icmes):
		cc = r1.t_shck[i]==r2.tshck[j]
		if cc:
			print " ok, i:%d, j:%d" % (i, j)
			nok+=1
	if nokk==nok:
		print " ausent?, i:%d" % i
		pause(2)
