from pylab import *
from numpy import *
import matplotlib.patches as patches
import matplotlib.transforms as transforms

#------------------------------
Nsh		= 90#47 #100	# revisar a ojo
dTdays		= 0.1		# revisar a ojo
nbins 		= 50		# (revisar a ojo) bine por unidad de tiempo normalizado
MCwant 		= 2
WangFlag 	= 'NaN'
#------------------------------
VARstf = []
VARstf += [['B', [5., 18.], 'B [nT]']]
VARstf += [['V', [380., 650.], 'Vsw [km/s]']]
VARstf += [['rmsBoB', [0.02, 0.2], 'rms($\hat B$/|B|) [1]']]
VARstf += [['beta', [0.001, 5.], '$\\beta$ [1]']]
VARstf += [['Pcc', [2, 17.], 'proton density [#/cc]']]
VARstf += [['Temp', [1e4, 4e5], 'Temp [K]']]
nvars = len(VARstf)
#------------------------------
for i in range(nvars):
	varname = VARstf[i][0]
	ylims	= VARstf[i][1]
	ylabel 	= VARstf[i][2]
	fname_sh = '../../sheaths/ascii/MCflag%d/MCflag%d_2before.4after_Wang%s_%s.txt' % (MCwant, MCwant, WangFlag, varname)
	fname_mc = '../../mcs/ascii/MCflag%d/MCflag%d_2before.4after_Wang%s_%s.txt' % (MCwant, MCwant, WangFlag, varname)

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
	t_mc		= varmc[0][cond_mc] + 1.0
	var_med_mc	= varmc[1][cond_mc]
	var_avr_mc	= varmc[2][cond_mc]
	var_std_mc	= varmc[3][cond_mc]
	var_n_mc	= varmc[4][cond_mc]

	#---------------------------------------------------
	fig	= figure(1, figsize=(11, 5.5))
	ax 	= fig.add_subplot(111)

	ax.plot(t_sh, var_avr_sh, '-', alpha=.9, c='black', markeredgecolor='none', label='average')
	ax.plot(t_mc, var_avr_mc, '-', alpha=.9, c='black', markeredgecolor='none')
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
	# pinta ventana de sheath
	rect1   = patches.Rectangle((1., 0.), width=1.0, height=1,
			transform=trans, color='blue',
			alpha=0.1)
	ax.add_patch(rect1)

	ax.plot(t_sh, var_med_sh, '-o', markersize=3 ,alpha=.8, c='red', markeredgecolor='none', label='median')
	ax.plot(t_mc, var_med_mc, '-o', markersize=3 ,alpha=.8, c='red', markeredgecolor='none')
	ax.grid()
	ax.set_ylim(ylims)
	ax.legend(loc='upper right')
	ax.set_xlabel('mixed time scale [1]')
	ax.set_ylabel(ylabel)
	TITLE = 'nmbr of sheaths: %d \n\
			%dbins per time unit \n\
			sheaths w/ dT>%gdays \n\
			MCflag>=%d \n\
			WangFlag: %s' % (Nsh, nbins, dTdays, MCwant, WangFlag)
	ax.set_title(TITLE)

	#show()
	fname_fig = '../plots/MCflag%d/MCflag%d_2before.4after_Wang%s_%s.png' % (MCwant, MCwant, WangFlag, varname)
	savefig(fname_fig, dpi=200, format='png', bbox_inches='tight')
	close()
