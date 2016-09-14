#!/usr/bin/env ipython
# -*- coding: utf-8 -*-

import sys
from tabulate import tabulate
sys.path.append('../../../shared_lib')
import read_NewTable as tb
import ShiftTimes as st

st2 = st.ShiftCorrection(st.ShiftDts, tb.tshck) # shift the shock
ss = len(tb.tshck)

# NOTA IMPORTANTE: los shifts estan hechos a los 5min mas cercanos
string = []; c=0
string += [['shock date [yyyy-mm-dd HH:MM]', 'shifted-original [min]']]
for i in range(ss):
    dt  = st2['dates_shifted'][i] - st2['dates_original'][i]
    ts  = st2['dates_original'][i]
    dtt = dt.total_seconds()
    if dtt!=0.0:
        #c +=1; print i, dtt, (dtt/60.0)%5. # el ultimo es el resto de 5min
        yyyy, mm, dd = ts.year, ts.month, ts.day
        HH, MM       = ts.hour, ts.minute
        str_date = '%04d-%02d-%02d %02d:%02d' % (yyyy, mm, dd, HH, MM)
        string += [[ str_date, dtt/60.0 ]]

tab = tabulate(string, tablefmt='latex', headers='firstrow')
tab2 = tabulate(string, tablefmt='grid', headers='firstrow')

