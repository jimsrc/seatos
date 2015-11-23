#!/usr/bin/env ipython
import numpy as np
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class gral():
    def __init__(self):
        self.name = ''

sh, mc          = gral(), gral()
cr              = gral()
cr.sh, cr.mc    = gral(), gral()

vlo, vhi        = 550.0, 3000.0  #550., 3000. #100.0, 450.0 #550.0, 3000.0
dir_inp_sh      = '../../../sheaths/ascii/MCflag2/wShiftCorr/_test_Vmc_'
dir_inp_mc      = '../../../mcs/ascii/MCflag2/wShiftCorr/_test_Vmc_'
fname_inp_part  = 'MCflag2_2before.4after_fgap0.2_Wang90.0_vlo.%4.1f.vhi.%4.1f' % (vlo, vhi)

fname_sh = dir_inp_sh + '/%s_V.txt' % fname_inp_part
fname_mc = dir_inp_mc + '/%s_V.txt' % fname_inp_part

sh.data = np.loadtxt(fname_sh).T
mc.data = np.loadtxt(fname_mc).T

sh.t, sh.avr    = sh.data[0], sh.data[2]
mc.t, mc.avr    = mc.data[0], mc.data[2]

#++++++++++++++++++++++++++++++++++++++++++++++++++++
fname_sh = dir_inp_sh + '/%s_CRs.txt' % fname_inp_part
fname_mc = dir_inp_mc + '/%s_CRs.txt' % fname_inp_part

cr.sh.data = np.loadtxt(fname_sh).T
cr.mc.data = np.loadtxt(fname_mc).T

cr.sh.t, cr.sh.avr    = cr.sh.data[0], cr.sh.data[2]
cr.mc.t, cr.mc.avr    = cr.mc.data[0], cr.mc.data[2]
