#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
from pylab import find
import numpy as np
from lmfit import minimize, Parameters, Parameter, report_errors
from numpy import array, ones, zeros, sum, power, min, max
import sys
from scipy.optimize import brute, fmin


def get_histogram(var, nbins):
    # quitamos nans
    no_nans = ~isnan(var)
    var = var[no_nans]
    # histograma
    h   = hist(var, bins = nbins); close()
    close()         # para no generar figura
    h_cnts  = h[0]      # counts    n elementos
    h_bound = h[1]      # boundaries    n+1 elementos
    #
    n   = len(h_cnts)
    h_x = zeros(n)
    for i in range(n):
        h_x[i]  = .5*(h_bound[i] + h_bound[i+1])
    #
    return [h_cnts, h_x]


def nCR2(data, tau, q, off, bp, bo):
    t, fc, b = data
    to  = 1.0           # to=1.0 : sheath trailing edge
    cc  = t[1:-1]<=to   # la recuperacion ocurre despues de 'to'
    cx  = find(cc)
    dt  = t[1:-1] - t[0:-2]
    nCR = np.nan*np.ones(t.size)
    fcc = fc[1:-1]
    bc          = b[1:-1] - bo
    bc[bc<=0.0] = 0.0
    #---- zona sheath
    for i in cx:
        ind      = cx[:(i+1)]
        nCR[i+1] = q*np.sum(fcc[:(i+1)]*dt[:(i+1)])

    cy  = find(~cc)
    no  = cx[-1]
    #---- despues de sheath
    for i in cy:
        # termino rms
        nCR[i+1] = q*sum(fcc[:(i+1)]*dt[:(i+1)])
        # termino recovery-after-sheath
        nCR[i+1] += (-1.0/tau)*sum( nCR[1:-1][no:i]*dt[no:i] )
        nCR[i+1] += 1.0*off    # offset
        nCR[i+1] += bp*sum(bc[no:i]*dt[no:i])

    return nCR


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class fit_forbush():
    def __init__(self, data, sems):
        self.sems = sems
        self.data = data
        self.t      = data[0] # time
        self.rms    = data[1] # rms(B)
        self.crs    = data[2] # GCRs
        self.b      = data[3] # campo B


    def residuals(self, params):
        if hasattr(params, 'keys'):
            tau   = params['tau'].value
            q     = params['q'].value
            off   = params['off'].value
            bp    = params['bp'].value
            bo    = params['bo'].value
        elif hasattr(params, '__len__'):
            tau, q, off, bp, bo = params
        else:
            print " ---> params is WEIRD!"
            raise SystemExit

        t     = self.t
        crs   = self.crs
        model = nCR2([t, self.rms, self.b], tau, q, off, bp, bo)
        sqr   = np.square(crs - model)
        diff  = np.nanmean(sqr)
        #print " diff---> %f, tau:%g, q:%g, bp:%g" % (diff, tau, q, bp)
        #LINE = "%g   %g  %g  %g %g  %g\n" % (tau, q, bp, off, bo, diff)
        #sys.stderr.write(LINE)
        return diff


    def make_fit_brute(self, rranges):
        """
        rranges = ( 
            slice(0., pi, pi/20),
            slice(-2.*pi, +2.*pi, 4.*pi/20),
            slice(1., 2.*pi, 2.*pi/20),
        )
        """
        rb = brute(self.residuals, rranges, full_output=False, finish=None)
        # este orden va acorde con self.residuals()
        self.par = { 
            'tau':  rb[0],
            'q':    rb[1],
            'off':  rb[2],
            'bp':   rb[3],
            'bo':   rb[4],
        }

        


    def make_fit(self):
        sems    = self.sems
        #x   = self.t #data[0]
        #y   = self.crs #data[1]
        # create a set of Parameters
        params = Parameters()
        params.add('q')
        params.add('tau')
        params.add('off')
        params.add('bp')
        params.add('bo')

        SEM_tau   = sems[0]
        SEM_q     = sems[1]
        SEM_off   = sems[2]
        SEM_bp    = sems[3]
        SEM_bo    = sems[4]

        # recuperacion dsps del MC leading edge
        params['tau'].value = SEM_tau
        params['tau'].vary  = True
        params['tau'].min   = 0.2 #1.0
        params['tau'].max   = 20.0

        # termino rmsB
        params['q'].value   = SEM_q
        params['q'].vary    = True #False #True
        params['q'].min     = -20.0 #-800.0 #-1.0e3
        params['q'].max     = -0.1 #-200.0 #-1.0e1

        # salto / discontinuidad
        params['off'].value = SEM_off
        params['off'].vary  = True #False #True
        params['off'].min   = 0.0
        params['off'].max   = 1.0 #2.0

        # termino del campo magnetico (i)
        params['bp'].value  = SEM_bp
        params['bp'].vary   = True
        params['bp'].min    = -1.0
        params['bp'].max    = 0.0

        # termino del campo magnetico (ii)
        params['bo'].value  = SEM_bo
        params['bo'].vary   = True #False #True
        params['bo'].min    = 0.0
        params['bo'].max    = 20.0

        METHOD  = "lbfgsb"#"leastsq"#"lbfgsb"
        result = minimize(self.residuals, params, method=METHOD)

        # write error report
        print " --------> METODO_FITEO: %s" % METHOD
        #print " --------> funcion: %s" % func_name
        #report_errors(params)
        self.par = {}
        for name in result.params.keys():
            self.par[name] = result.params[name].value

#EOF
