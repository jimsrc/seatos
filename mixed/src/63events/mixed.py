import os
from pylab import *
from numpy import *
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import console_colors as ccl

#------------------------------
Nsh		= 63#47 #100	# revisar a ojo
nbins 		= 50		# (revisar a ojo) bine por unidad de tiempo normalizado
MCwant 		= '2'		# '2', '2.2H'
WangFlag 	= 'NaN'
CorrShift	= True
#dTdays		= 0.1		# revisar a ojo
if CorrShift==True:
	prexShift = 'wShiftCorr'
else:
	prexShift = 'woShiftCorr'
#------------------------------
# varname, range-for-plot, label, N-mcs, N-sheaths
VARstf = []
VARstf += [['B', [5., 19.], 'B [nT]', 63, 57]]
VARstf += [['V', [380., 600.], 'Vsw [km/s]', 59, 57]]
VARstf += [['rmsBoB', [0.015, 0.14], 'rms($\hat B$/|B|) [1]', 63, 57]]
VARstf += [['beta', [0.1, 10.], '$\\beta$ [1]', 52, 50]]
VARstf += [['Pcc', [3., 19.], 'proton density [#/cc]', 52, 50]]
VARstf += [['Temp', [1e4, 3e5], 'Temp [K]', 53, 50]]
VARstf += [['AlphaRatio', [0.02, 0.09], 'alpha ratio [K]', 45, 19]]
nvars = len(VARstf)
dir_figs	= '../plots/%s/MCflag%s/' % (prexShift, MCwant)
try:
	os.system('mkdir -p %s' % dir_figs)
except:
	print ccl.On+ " ---> Ya existe: %s" % dir_figs + ccl.W
print ccl.On+" generando figuras en: %s"%dir_figs + ccl.W
fgap=0.2        # fraccion-de-gap-tolerado que escojo plotear
#------------------------------
for i in range(nvars):
	varname = VARstf[i][0]
	ylims	= VARstf[i][1]
	ylabel 	= VARstf[i][2]
	Nmc	= VARstf[i][3]
	Nsh	= VARstf[i][4]
	fname_sh = '../../../sheaths/ascii/MCflag%s/%s/MCflag%s_2before.4after_Wang%s_fgap%1.1f_%s.txt' % (MCwant, prexShift, MCwant, WangFlag, fgap, varname)
	fname_mc =     '../../../mcs/ascii/MCflag%s/%s/MCflag%s_2before.4after_Wang%s_fgap%1.1f_%s.txt' % (MCwant, prexShift, MCwant, WangFlag, fgap, varname)

	varsh 	= loadtxt(fname_sh, unpack=True)
	varmc 	= loadtxt(fname_mc, unpack=True)
	cond_sh	= varsh[0]<1.0
	cond_mc = varmc[0]>0.0
	#------ sheath
	t_sh		= varsh[0][cond_sh]
	var_med_sh 	= varsh[1][cond_sh]
	var_avr_sh 	= varsh[2][cond_sh]
	var_std_sh 	= varsh[3][cond_sh]
	var_n_sh 	= varsh[4][cond_sh]
	#------ mc
	t_mc		= varmc[0][cond_mc]*3. + 1.0
	var_med_mc	= varmc[1][cond_mc]
	var_avr_mc	= varmc[2][cond_mc]
	var_std_mc	= varmc[3][cond_mc]
	var_n_mc	= varmc[4][cond_mc]

	#---------------------------------------------------
	fig	= figure(1, figsize=(11, 5.5))
	ax 	= fig.add_subplot(111)

	ax.plot(t_sh, var_avr_sh, '-o', alpha=.9, c='black', markeredgecolor='none', label='average', markersize=5)
	ax.plot(t_mc, var_avr_mc, '-o', alpha=.9, c='black', markeredgecolor='none', markersize=5)
	# bandas de errores en sheath
	inf = var_avr_sh-var_std_sh/sqrt(var_n_sh)
	sup = var_avr_sh+var_std_sh/sqrt(var_n_sh)
	ax.fill_between(t_sh, inf, sup, facecolor='gray', alpha=0.5)
	# bandas de errores en MC
	inf = var_avr_mc - var_std_mc/sqrt(var_n_mc)
	sup = var_avr_mc + var_std_mc/sqrt(var_n_mc)
	ax.fill_between(t_mc, inf, sup, facecolor='gray', alpha=0.5)
	# pinta ventana de sheath
	trans   = transforms.blended_transform_factory(
			ax.transData, ax.transAxes)
	rect1   = patches.Rectangle((0., 0.), width=1.0, height=1,
			transform=trans, color='orange',
			alpha=0.3)
	ax.add_patch(rect1)
	# pinta ventana de mc
	rect1   = patches.Rectangle((1., 0.), width=3.0, height=1,
			transform=trans, color='blue',
			alpha=0.2)
	ax.add_patch(rect1)

	ax.plot(t_sh, var_med_sh, '-o', markersize=5 ,alpha=.8, c='red', markeredgecolor='none', label='median')
	ax.plot(t_mc, var_med_mc, '-o', markersize=5 ,alpha=.8, c='red', markeredgecolor='none')
	ax.grid()
	ax.set_ylim(ylims);
	ax.set_xlim(-2., 7.)
	ax.legend(loc='upper right')
	ax.set_xlabel('mixed time scale [1]')
	ax.set_ylabel(ylabel)
	TITLE = '# of MCs: %d \n\
			# of sheaths: %d \n\
			%dbins per time unit \n\
			MCflag: %s \n\
			WangFlag: %s' % (Nmc, Nsh, nbins, MCwant, WangFlag)
	ax.set_title(TITLE)
	if varname=='beta':
		ax.set_yscale('log')
	#show()
	fname_fig = '%s/MCflag%s_2before.4after_Wang%s_fgap%1.1f_%s' % (dir_figs, MCwant, WangFlag, fgap, varname)
	savefig('%s.png'%fname_fig, dpi=200, format='png', bbox_inches='tight')
	savefig('%s.pdf'%fname_fig, dpi=200, format='pdf', bbox_inches='tight')
	savefig('%s.eps'%fname_fig, dpi=200, format='eps', bbox_inches='tight')
	close()
