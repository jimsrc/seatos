from read_NewTable import *
import numpy as np

#for i in range(n_icmes):
#    print " id: %02d    tini_mc: " % i, tini_mc[i]

# NOTA: estos valores son sacados de la tabla del .docx q mando Adri en su mail del 21.jul.2015, con asunto:"Paper on typical profiles in magnetic clouds and density peaks".
z       = np.nan*np.ones(n_icmes)
z[34]   = 0.69
z[68]   = 0.86
z[83]   = 0.43
z[97]   = 0.01
z[125]  = 1.88
z[131]  = 1.21
z[139]  = 1.77
z[195]  = 0.79
z[197]  = 0.60
z[199]  = 0.62
z[207]  = 0.69
z[229]  = 0.34
z[241]  = 1.14
z[246]  = 0.82
z[250]  = -3.88         # WTF!!!!?
z[251]  = 1.27
z[255]  = 0.47
z[273]  = 0.89
z[278]  = 1.02
z[281]  = 0.86
z[293]  = 0.86
z[299]  = 0.98
