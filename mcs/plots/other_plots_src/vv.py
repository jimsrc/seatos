from pylab import *
import funcs as ff
from scipy.io.netcdf import netcdf_file
import numpy as np 
import os

dir_ascii   = '../../ascii/MCflag2/wShiftCorr'


fname_inp   = dir_ascii + '/_stuff_MCflag2_2before.4after_fgap0.2_WangNaN.nc'
f           = netcdf_file(fname_inp, 'r')

print os.path.isfile(fname_inp)


varname     = 'B'
nevents     = f.dimensions['nevents_%s' % varname]

