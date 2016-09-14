#!/usr/bin/env ipython
from pylab import *
import numpy as np
import load_avrs as p


#------------------------------funcion promedio corrido
def running_average(temp, n, m): 
    """ 
    Calculates centered running average from -n to +m points (total of n+m+1 points).
    Example 1: if n=m=6 and the data is monthly, then the result is a centered 13 month running average.
    Example 2: if n=5, m=6 and the data is monthly, then the result is a "centered" 12 month moving average
                (another way to center it is with n=6, m=5).
    """
    avg = temp.copy()
    if temp.size > min(m,n): # pido q tenga suficientes elementos para q tenga sentido hacer running avr
        for i in range(n, size(temp)-m):
            window  = temp[i-n:i+m+1]
            cc  = ~np.isnan(window)     # filtro los nans
            if len(find(cc))>0:
                avg[i]  = np.mean(window[cc])
            else:
                avg[i]  = np.nan
        avg[:n] = np.nan
        avg[-m:]= np.nan
    return avg


def get_histogram(var, nbins):
    # quitamos nans                                                 
    no_nans = ~np.isnan(var)
    var     = var[no_nans]
    # histograma
    h       = np.histogram(var, bins=nbins)
    h_cnts  = h[0]      # counts    n elementos
    h_bound = h[1]      # boundaries    n+1 elementos
    #   
    n   = len(h_cnts)
    h_x = zeros(n)
    for i in range(n):
        h_x[i]  = .5*(h_bound[i] + h_bound[i+1])
    #   
    return [h_cnts, h_x]


v       = np.concatenate([p.v0, p.v1, p.v2])
sigs    = np.concatenate([p.sigma_p0, p.sigma_p1, p.sigma_p2])
#sigss   = running_average(sigs, 7, 7)
m, b    = np.polyfit(x=v, y=sigs, deg=1)

hc, hx  = get_histogram(sigs, nbins=15)

fig     = figure(1, figsize=(6,4))
ax0     = fig.add_subplot(121, position=(0.1 , 0.1, .45, .5))
ax1     = fig.add_subplot(122, position=(0.55, 0.1, .2, .5))
#ax1     = ax1p.twiny()
#ax1.set_position((0.55, 0.1, .2, .5))
#ax0.set_position((0.1, 0.1, .45, .5))

#--- scatter plot
ax0.scatter(v, sigs/(1e14), edgecolor='None') 
#--- version suavizada
#ax0.scatter(v, sigss, c='red')
#--- ajuste
#ax0.plot(v, m*v+b, c='b', alpha=.7)  # linear fit

ax0.axvline(x=450., ls='--', c='k', lw=2, alpha=.8) 
ax0.axvline(x=550., ls='--', c='k', lw=2, alpha=.8)
ax0.grid()
ax0.set_xlabel('$V_{mc}$', fontsize=17)
ax0.set_ylabel('$\sigma_{sh}$ $[cm^{-2}]$ ($\\times 10^{14}$)', fontsize=17)
ax0.set_ylim(-1.0, 14) #(-.1e14, 1.4e14)
#ax0.tick_params(labeltop=True)
"""
XTICKS = [300., 450., 600., 750., 900.]
ax0.set_xticks(XTICKS)
ax0.set_xticklabels(XTICKS, visible=True)
"""

#--- histograma
ax1.barh(hx, hc, align='center', height=0.8e14)
ax1.grid()
ax1.set_yticklabels([], visible=False)
ax1.tick_params(labeltop=True, labelbottom=False)
ax1.set_ylim(-.1e15, 1.4e15)
#ax1.set_xlabel('#')

fname_fig = '../figs/Vmc__vs__sigma.png'
savefig(fname_fig, dpi=100, bbox_inches='tight')
print " ---> "+ fname_fig
close()
#EOF
