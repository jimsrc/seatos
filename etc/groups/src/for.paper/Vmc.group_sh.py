#!/usr/bin/env ipython
from wdir.funcs import *
# NOTE: the 'wdir' is the *working*/*analysis* directory!!

nBin                            = {}
nBin['before'], nBin['after']   = 2, 4
FILTER                          = {}
FILTER['fgap']                  = 0.2
FILTER['MCwant']                = '2'
FILTER['WangFlag']              = '90.0'
FILTER['vsw_filter']            = True #False
FILTER['z_filter_on']           = False
FILTER['B_filter']              = False #True
FILTER['filter_dR.icme']        = False #False

CUTS                         = {}
#CUTS['v_lo'], CUTS['v_hi']   = 0.0, 0.0
#CUTS['z_lo'], CUTS['z_hi']   = 0.0, 0.0
#CUTS['B_lo'], CUTS['B_hi']   = 0.0, 0.0
#CUTS['dR_lo'], CUTS['dR_hi'] = 0.0, 0.0

DIR_ASCII = '../../../../sheaths/ascii/MCflag%s/wShiftCorr' % (FILTER['MCwant']) + '/_test_Vmc_'
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
proms = []

CUTS['v_lo'], CUTS['v_hi'] = 100.0, 450.0
proms += [make_plot(DIR_ASCII, FILTER, CUTS, nBin)]

CUTS['v_lo'], CUTS['v_hi'] = 450.0, 550.0
proms += [make_plot(DIR_ASCII, FILTER, CUTS, nBin)]

CUTS['v_lo'], CUTS['v_hi'] = 550.0, 3000.0
proms += [make_plot(DIR_ASCII, FILTER, CUTS, nBin)]

VARNAMES    = proms[0].keys()
VARNAMES.remove('AlphaRatio')   # no lo queremos para el paper
avr         = {}

fig     = figure(1, figsize=(3.5, 3.5))
ax      = fig.add_subplot(111)
i       = 0
# hallamos valores medios de los 3 conjuntos
for varname in VARNAMES:
    v0, v1, v2      = proms[0][varname], proms[1][varname], proms[2][varname]
    print " --> " + varname + ': ', v0, v1, v2
    vals            = np.array([v0, v1, v2])
    avr[varname]    = np.mean(vals)
    #dummy           = i*np.ones(3)
    ax.plot(i, v0/avr[varname], 'v--', color='blue')
    ax.plot(i, v1/avr[varname], 'o--', color='green')
    ax.plot(i, v2/avr[varname], '^--', color='red')
    i               += 1

ax.grid()
ax.text(1.0, 1.6, 'sheaths', fontsize=15.)
ax.text(5.5, 1.8, 'b)', fontsize=15.)
ax.set_xlim(-.5, 6.5)
ax.set_ylim(0.3, 2.1)
XTICKS = range(len(VARNAMES))
ax.set_xticks(XTICKS)
ax.set_xticklabels(VARNAMES, fontsize=12, rotation='40')
ax.set_yticklabels([], visible=False)
ax.plot(XTICKS, np.ones(len(VARNAMES)), '-', color='black', lw=3 ,alpha=0.3)


fname_fig = '../../plots/__paper__deviations_sh_Vmc.group.png'
#if FILTER['vsw_filter']:        fname_fig += '_Vmc.group' #'_vsw.group'
#if FILTER['B_filter']:          fname_fig += '_Bmc.group' #'_B.group'
#if FILTER['filter_dR.icme']:    fname_fig += '_dRmc.group' #'_dR.icme.group'
#fname_fig += '.png'

savefig(fname_fig, format='png', dpi=135, bbox_inches='tight')
print " ---> " + fname_fig
close()
##
