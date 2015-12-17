from pylab import *
import os
import matplotlib.patches as patches
import matplotlib.transforms as transforms

def makefig(medVAR, avrVAR, stdVAR, nVAR, tnorm, 
        SUBTITLE, YLIMS, YLAB, fname_fig):
    fig     = figure(1, figsize=(13, 6))
    ax      = fig.add_subplot(111)

    ax.plot(tnorm, avrVAR, 'o-', color='black', markersize=5, label='mean')
    ax.plot(tnorm, medVAR, 'o-', color='red', alpha=.5, markersize=5, markeredgecolor='none', label='median')
    inf     = avrVAR + stdVAR/np.sqrt(nVAR)
    sup     = avrVAR - stdVAR/np.sqrt(nVAR)
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
    ax.set_xlabel('time normalized to MC passage time [1]', fontsize=14)
    ax.set_ylabel(YLAB, fontsize=20)
    savefig(fname_fig, format='png', dpi=180, bbox_inches='tight')
    close()

