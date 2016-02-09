#!/usr/bin/env ipython
# -*- coding: utf-8 -*-

import sys
sys.path.append('../../../shared_lib')
import read_NewTable as tb
import ShiftTimes as st

st2 = st.ShiftCorrection(st.ShiftDts, tb.tshck)

ss = len(tb.tshck)

# NOTA IMPORTANTE: los shifts estan hechos a los 5min mas cercanos
for i in range(ss):
    dt  = st2['dates_shifted'][i] - st2['dates_original'][i]
    dtt = dt.total_seconds()
    if dtt!=0.0:
        print i, dtt, (dtt/60.0)%5. # el ultimo es el resto de 5min
