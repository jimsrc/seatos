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

#++++++++++++++++++++++ SHEATHS +++++++++++++++++++++++++++++++++++++++
DIR_ASCII = '../../../../sheaths/ascii/MCflag%s/wShiftCorr' % (FILTER['MCwant']) + '/_test_Vmc_'
sh = []

CUTS['v_lo'], CUTS['v_hi'] = 100.0, 450.0
sh += [make_plot(DIR_ASCII, FILTER, CUTS, nBin)]

CUTS['v_lo'], CUTS['v_hi'] = 450.0, 550.0
sh += [make_plot(DIR_ASCII, FILTER, CUTS, nBin)]

CUTS['v_lo'], CUTS['v_hi'] = 550.0, 3000.0
sh += [make_plot(DIR_ASCII, FILTER, CUTS, nBin)]

#++++++++++++++++++++++ MCs +++++++++++++++++++++++++++++++++++++++
DIR_ASCII = '../../../../mcs/ascii/MCflag%s/wShiftCorr' % (FILTER['MCwant']) + '/_test_Vmc_'
mc = []

CUTS['v_lo'], CUTS['v_hi'] = 100.0, 450.0
mc += [make_plot(DIR_ASCII, FILTER, CUTS, nBin)]

CUTS['v_lo'], CUTS['v_hi'] = 450.0, 550.0
mc += [make_plot(DIR_ASCII, FILTER, CUTS, nBin)]

CUTS['v_lo'], CUTS['v_hi'] = 550.0, 3000.0
mc += [make_plot(DIR_ASCII, FILTER, CUTS, nBin)]

VARNAMES    = sh[0].keys()
VARNAMES.remove('AlphaRatio')   # no lo queremos para el paper
avr         = {}

#VNAMES  =  ['rmsB', 'CRs', 'B', 'Temp', 'rmsBoB', 'beta', 'V', 'Pcc']
VNAMES  =  ['B', 'V', 'Pcc', 'Temp', 'beta', 'rmsBoB', 'rmsB', 'CRs']

fig     = figure(1, figsize=(7, 3.5))
ax      = fig.add_subplot(111)
i, di   = 0, 0.1
S       = 8
# hallamos valores medios de los 3 conjuntos
#for varname in VARNAMES:
for varname in VNAMES:
    sh0, sh1, sh2      = sh[0][varname], sh[1][varname], sh[2][varname]
    mc0, mc1, mc2      = mc[0][varname], mc[1][varname], mc[2][varname]

    #--- sheaths
    vals            = np.array([sh0, sh1, sh2])
    avr[varname]    = np.mean(vals)
    print " --> " + varname + 'SH: ', sh0, sh1, sh2, avr[varname]
    ax.plot(i-di, sh0/avr[varname], 'v--', mec='blue', mfc='None', mew=1.5, ms=S)
    ax.plot(i-di, sh1/avr[varname], 'o--', mec='green', mfc='None', mew=1.5, ms=S)
    ax.plot(i-di, sh2/avr[varname], '^--', mec='red', mfc='None', mew=1.5, ms=S)
    #--- mcs
    vals            = np.array([mc0, mc1, mc2])
    avr[varname]    = np.mean(vals)
    print " --> " + varname + 'MC: ', mc0, mc1, mc2, avr[varname], '\n'
    ax.plot(i+di, mc0/avr[varname], 'v--', color='blue', ms=S)
    ax.plot(i+di, mc1/avr[varname], 'o--', color='green', ms=S)
    ax.plot(i+di, mc2/avr[varname], '^--', color='red', ms=S)

    i               += 1

#ax.text(1.0, 1.6, 'MCs', fontsize=15.)
#ax.text(5.5, 1.8, 'a)', fontsize=15.)
ax.grid()
ax.set_xlim(-.5, 7.5)
ax.set_ylim(0.3, 2.1)
#XTICKS = range(len(VARNAMES))
XTICKS = range(len(VNAMES))
ax.set_xticks(XTICKS)
#ax.set_xticklabels(VARNAMES, fontsize=12, rotation='40')
VNAMES2 = ['B', 'V', '$n_p$', '$T_p$', '$\\beta$', 'rmsBoB', 'rmsB', '$n_{GCR}$']
ax.set_xticklabels(VNAMES2, fontsize=12, rotation='40')

#ax.plot(XTICKS, np.ones(len(VARNAMES)), '-', color='black', lw=3 ,alpha=0.3)
ax.plot(XTICKS, np.ones(len(VNAMES)), '-', color='black', lw=3 ,alpha=0.3)
ax.set_ylabel('normalized values')

fname_fig = '../../plots/__paper__deviations_mix_Vmc.group.png'
#if FILTER['vsw_filter']:        fname_fig += '_Vmc.group' #'_vsw.group'
#if FILTER['B_filter']:          fname_fig += '_Bmc.group' #'_B.group'
#if FILTER['filter_dR.icme']:    fname_fig += '_dRmc.group' #'_dR.icme.group'
#fname_fig += '.png'

savefig(fname_fig, format='png', dpi=135, bbox_inches='tight')
print " ---> " + fname_fig
close()

##
