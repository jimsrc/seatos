#!/usr/bin/env ipython
import numpy as np
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class gral():
    def __init__(self):
        self.name = ''


class mgr_data():
    def __init__(self, dir_inp_sh, dir_inp_mc, fname_inp_part):
        self.dir_inp_sh     = dir_inp_sh
        self.dir_inp_mc     = dir_inp_mc
        self.fname_inp_part = fname_inp_part
        #self.vlo, self.vhi  = vlo, vhi

    def run(self, vlo, vhi):
        """
        Antes de correr esto, hay q definir las 
        variables miembro "self.vlo, self.vhi" desde
        afuera
        """
        dir_inp_sh      = self.dir_inp_sh
        dir_inp_mc      = self.dir_inp_mc
        fname_inp_part  = self.fname_inp_part
        sh, mc, cr      = gral(), gral(), gral()
        cr.sh, cr.mc    = gral(), gral()
        fname_inp       = fname_inp_part+'_vlo.%4.1f.vhi.%4.1f'%(vlo, vhi)
        self.vlo, self.vhi = vlo, vhi

        #--- rmsB
        fname_sh = dir_inp_sh + '/%s_rmsB.txt' % fname_inp
        fname_mc = dir_inp_mc + '/%s_rmsB.txt' % fname_inp
        sh.data = np.loadtxt(fname_sh).T
        mc.data = np.loadtxt(fname_mc).T
        sh.t, sh.rmsB    = sh.data[0], sh.data[2]
        mc.t, mc.rmsB    = mc.data[0], mc.data[2]

        #--- B
        fname_sh = dir_inp_sh + '/%s_B.txt' % fname_inp
        fname_mc = dir_inp_mc + '/%s_B.txt' % fname_inp
        sh.data = np.loadtxt(fname_sh).T
        mc.data = np.loadtxt(fname_mc).T
        sh.t, sh.B    = sh.data[0], sh.data[2]
        mc.t, mc.B    = mc.data[0], mc.data[2]

        #++++++++++++++++++++++++++++++++++++++++++++++++++++
        fname_sh = dir_inp_sh + '/%s_CRs.txt' % fname_inp
        fname_mc = dir_inp_mc + '/%s_CRs.txt' % fname_inp

        cr.sh.data = np.loadtxt(fname_sh).T
        cr.mc.data = np.loadtxt(fname_mc).T

        cr.sh.t, cr.sh.avr    = cr.sh.data[0], cr.sh.data[2]
        cr.mc.t, cr.mc.avr    = cr.mc.data[0], cr.mc.data[2]

        self.sh = sh
        self.mc = mc
        self.cr = cr
        return sh, mc, cr

"""
vlo, vhi        = 550.0, 3000.0 #100.0, 450.0 #550.0, 3000.0
dir_inp_sh      = '../../../sheaths/ascii/MCflag2/wShiftCorr/_test_Vmc_'
dir_inp_mc      = '../../../mcs/ascii/MCflag2/wShiftCorr/_test_Vmc_'
fname_inp_part  = 'MCflag2_2before.4after_fgap0.2_Wang90.0_vlo.%4.1f.vhi.%4.1f' % (vlo, vhi)
"""
