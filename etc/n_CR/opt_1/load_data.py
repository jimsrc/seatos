#!/usr/bin/env ipython
import numpy as np
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class gral():
    def __init__(self):
        self.name = ''

sh, mc          = gral(), gral()
cr              = gral()
cr.sh, cr.mc    = gral(), gral()

fname_sh = '../../sheaths/ascii/MCflag2/wShiftCorr/_test_Vmc_/MCflag2_2before.4after_fgap0.2_Wang90.0_vlo.550.0.vhi.3000.0_rmsBoB.txt'
fname_mc = '../../mcs/ascii/MCflag2/wShiftCorr/_test_Vmc_/MCflag2_2before.4after_fgap0.2_Wang90.0_vlo.550.0.vhi.3000.0_rmsBoB.txt'

sh.data = np.loadtxt(fname_sh).T
mc.data = np.loadtxt(fname_mc).T

sh.t, sh.avr    = sh.data[0], sh.data[2]
mc.t, mc.avr    = mc.data[0], mc.data[2]

#++++++++++++++++++++++++++++++++++++++++++++++++++++
fname_sh = '../../sheaths/ascii/MCflag2/wShiftCorr/_test_Vmc_/MCflag2_2before.4after_fgap0.2_Wang90.0_vlo.550.0.vhi.3000.0_CRs.txt'
fname_mc = '../../mcs/ascii/MCflag2/wShiftCorr/_test_Vmc_/MCflag2_2before.4after_fgap0.2_Wang90.0_vlo.550.0.vhi.3000.0_CRs.txt'

cr.sh.data = np.loadtxt(fname_sh).T
cr.mc.data = np.loadtxt(fname_mc).T

cr.sh.t, cr.sh.avr    = cr.sh.data[0], cr.sh.data[2]
cr.mc.t, cr.mc.avr    = cr.mc.data[0], cr.mc.data[2]
