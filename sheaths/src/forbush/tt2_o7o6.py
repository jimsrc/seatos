import os
from rebineo_o7o6 import *
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import console_colors as ccl

def makefig(medVAR, avrVAR, stdVAR, nVAR, tnorm, 
		dTday, SUBTITLE, YLIMS, YLAB, fname_fig):
	fig     = figure(1, figsize=(13, 6))
	ax      = fig.add_subplot(111)

	ax.plot(tnorm, avrVAR, 'o-', c='black', markersize=5, label='mean')
	ax.plot(tnorm, medVAR, 'o-', c='red', alpha=.5, markersize=5, markeredgecolor='none', label='median')
	inf     = avrVAR + stdVAR/sqrt(nVAR)
	sup     = avrVAR - stdVAR/sqrt(nVAR)
	ax.fill_between(tnorm, inf, sup, facecolor='gray', alpha=0.5)
	trans   = transforms.blended_transform_factory(
			ax.transData, ax.transAxes)
	rect1   = patches.Rectangle((0., 0.), width=1.0, height=1,
			transform=trans, color='blue',
			alpha=0.3)
	ax.add_patch(rect1)

	ax.legend(loc='upper right')
	ax.grid()
	ax.set_ylim(YLIMS)
	TITLE = SUBTITLE
	ax.set_title(TITLE)
	ax.set_xlabel('time normalized to MC passage time [1]')
	ax.set_ylabel(YLAB)
	savefig(fname_fig, format='png', dpi=180, bbox_inches='tight')
	close()

def wangflag(ThetaThres):
	if ThetaThres<0:
		return 'NaN'
	else:
		return str(ThetaThres)

#-------------------- para figuras:
Nsh = dVARS[0][0]
WangFlag = 'NaN'#wangflag(ThetaThres)
SUBTITLE = 'number of sheaths: %d \n\
		%dbins per time unit \n\
		sheaths w/ dT>%gdays \n\
		MCflags: %s \n\
		WangFlag: %s' % (Nsh, nbin/(1+nbefore+nafter), dTday, MCwant['alias'], WangFlag)

# prefijo gral para los nombres de los graficos:
if CorrShift:
	prexShift =  'wShiftCorr'
else:
	prexShift = 'woShiftCorr'
DIR_FIGS 	= '../plots/MCflag%s/%s' % (MCwant['alias'], prexShift)
DIR_ASCII 	= '../ascii/MCflag%s/%s' % (MCwant['alias'], prexShift)
try:
	os.system('mkdir -p %s' % DIR_FIGS)
	os.system('mkdir -p %s' % DIR_ASCII)
	print ccl.On + " -------> creando: %s" % DIR_FIGS + ccl.W
	print ccl.On + " -------> creando: %s" % DIR_ASCII + ccl.W
except:
	print ccl.On +  " Ya existe: %s" %DIR_FIGS + ccl.W
	print ccl.On +  " Ya existe: %s" %DIR_ASCII + ccl.W

FNAMEs = 'MCflag%s_%dbefore.%dafter_Wang%s_fgap%1.1f' % (MCwant['alias'], nbefore, nafter, WangFlag, fgap)
FNAME_ASCII = '%s/%s' % (DIR_ASCII, FNAMEs)
FNAME_FIGS  = '%s/%s' % (DIR_FIGS, FNAMEs)

#----------------------------------------------------------------------------------------------------
for i in range(nvars):
	fname_fig = '%s_%s.png' % (FNAME_FIGS, VARS[i][1])
	print ccl.Rn+ " ------> %s" % fname_fig
	ylims	= VARS[i][2]
	ylabel	= VARS[i][3]
	mediana = dVARS[i][4]
	average = dVARS[i][3]
	std_err	= dVARS[i][5]
	nValues	= dVARS[i][6]		# nmbr of good values aporting data
	binsPerTimeUnit = nbin/(1+nbefore+nafter)
	SUBTITLE = '# of selected events: %d \n\
		events w/80%% of data: %d \n\
		bins per time unit: %d \n\
		MCflag: %s \n\
		WangFlag: %s' % (dVARS[i][0], nEnough[i], binsPerTimeUnit, MCwant['alias'], WangFlag)

	makefig(mediana, average, std_err, nValues, tnorm,
			dTday, SUBTITLE, ylims, ylabel, fname_fig)

	fdataout = '%s_%s.txt' % (FNAME_ASCII, VARS[i][1])
	dataout = array([tnorm, mediana, average, std_err, nValues])
	print " ------> %s\n" % fdataout + ccl.W
	savetxt(fdataout, dataout.T, fmt='%12.5f')
##
