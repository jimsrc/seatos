#
from nCR_models import func_data as fd
from nCR_models.share import funcs as ff
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np

"""
dir_inp_sh      = '../../../../sheaths/ascii/MCflag2/wShiftCorr/_test_Vmc_'
dir_inp_mc      = '../../../../mcs/ascii/MCflag2/wShiftCorr/_test_Vmc_'
fname_inp_part  = 'MCflag2_2before.4after_fgap0.2_Wang90.0'
"""
def build_plot(dirs, par, ax):
    dir_inp_sh      = dirs['sheath']
    dir_inp_mc      = dirs['mc']
    fname_inp_part  = dirs['fname_inputs']
    dir_figs        = dirs['figs']
    mgr             = fd.mgr_data(dir_inp_sh, dir_inp_mc, fname_inp_part)
    #sh, mc, cr      = mgr.run(vlo=100.0, vhi=450.0)
    sh, mc, cr      = mgr.run(vlo=par['vlo'], vhi=par['vhi'])

    fname_fig = '%s/nCR_vlo.%4.1f.vhi.%4.1f.png' % (dir_figs, mgr.vlo, mgr.vhi)
    #++++++++++++++++++++++++++++++++++++++++++++++++++++
    #-- mc:
    mc.cc   = (mc.t>0.0) & (mc.t<=2.0)
    mc.tout = 3.0*mc.t[mc.cc]+1.0
    mc.rms  = mc.rmsB[mc.cc]
    mc.B    = mc.B[mc.cc]
    cr.mc.crs   = cr.mc.avr[mc.cc]

    #-- sheath
    sh.cc   = sh.t<1.0
    sh.tout = sh.t[sh.cc]
    sh.rms  = sh.rmsB[sh.cc]
    sh.B    = sh.B[sh.cc]
    cr.sh.crs   = cr.sh.avr[sh.cc]

    tpre    = 0.0 #-1.0  # tiempo antes del cual se toma data para el rms-del-quiet-SW
    rms_o   = np.mean(sh.rms[sh.t<tpre]) #0.06 #0.025 #np.mean(sh.rms[sh.t<-1.0]) #0.03
    t       = np.concatenate([sh.tout, mc.tout])
    rms     = np.concatenate([sh.rms, mc.rms])
    B       = np.concatenate([sh.B, mc.B])
    crs     = np.concatenate([cr.sh.crs, cr.mc.crs])
    org_t   = t.copy()
    org_crs = crs.copy()
    t, rms, crs, B  = t[t>=0.0], rms[t>=0.0], crs[t>=0.0], B[t>=0.0]
    dt      = t[1:-1] - t[0:-2]
    cte     = 0.0
    #q       = -390.0 #-350.0 #-385.01000158 #-440.0 #-170.0

    #--- 'fc' es la version trozos de 'rms'
    cc      = ((rms-rms_o)>=0.0) & (t<5.0)
    fc      = np.zeros(rms.size)
    fc[cc]  = (rms-rms_o)[cc]
    b       = B

    #++++++++++++++++++++++++++++++++++++++++++++++++ figura
    #fig     = figure(1, figsize=(6,3.))
    #ax     = fig.add_subplot(111)
    #ax1     = ax.twinx()
    #--- plot der
    #ax1.plot(t[1:-1], fc[1:-1], c='gray')      # rmsB
    #ax1.plot(t[1:-1], b[1:-1], c='gray')       # B field

    tau, bp     = par['tau'], par['bp']
    q, off, bo  = par['q'], par['off'], par['bo']
    """
    tau, bp     = 2.36, 0.0
    q, off, bo  = -9.373, 0.89, 16.15
    """

    ncr     = ff.nCR2([t, fc, b], tau, q, off, bp, bo)
    #sqr     = np.nanmean(np.power(crs - ncr, 2.0))

    #--- plot izq
    ax.plot(org_t, org_crs, '-o', c='gray', ms=3)
    ax.plot(t, ncr, '-', c='red', lw=5, alpha=0.8, label='$\\tau=%3.3g$'%tau)

    #++++ region sheath (naranja)
    trans   = transforms.blended_transform_factory(ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((0., 0.), width=1, height=1, 
                transform=trans, color='orange',
                alpha=0.3)
    ax.add_patch(rect1)
    #++++ region mc (blue)
    trans   = transforms.blended_transform_factory(ax.transData, ax.transAxes)
    rect1   = patches.Rectangle((1., 0.), width=3, height=1, 
                transform=trans, color='blue',
                alpha=0.3)
    ax.add_patch(rect1)

    ax.plot(t, crs, '-o', c='k', ms=1)
    #ax.axhline(y=0.0, c='g')
    ax.grid()
    ax.set_xlabel('time normalized to\nsheath/MC passage [1]', fontsize=11)
    #ax.set_ylabel('$n_{CR}$ [%]', fontsize=21)
    ax.set_ylim(-8., 2.)

    return ax

"""
savefig(fname_fig, dpi=135, bbox_inches='tight')
close()
"""
#EOF
