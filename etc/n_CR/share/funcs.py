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



def residuals(params, x, y_data):
    mu  = params['mu'].value
    sig = params['sig'].value
    A   = params['A'].value
    fun_name = params['function'].value
    #
    """if fun_name=="log-normal":
        diff    = (lognormal(x, A, mu, sig) - y_data)**2.
    elif fun_name=="gauss":
        diff    = (gauss(x, A, mu, sig)  - y_data)**2."""
    diff = np.power(fun_name(x, A, mu, sig)  - y_data, 2.0)
    #print " diff---> %f" % mean(diff)
    return diff



def make_fit(data, sems, func):
    x   = data[0]
    y   = data[1]
    # create a set of Parameters
    params = Parameters()
    params.add('A')
    params.add('mu')
    params.add('sig')
    params.add('function')

    SEM_A   = sems[0]
    SEM_mu  = sems[1]
    SEM_sig = sems[2]

    params['A'].value   = SEM_A
    params['A'].vary    = True
    """params['A'].min      =
    params['A'].max     = """

    params['mu'].value  = SEM_mu
    params['mu'].vary   = True
    """params['mu'].min =
    params['mu'].max    = """

    params['sig'].value = SEM_sig
    params['sig'].vary  = True
    """params['sig'].min    =
    params['sig'].max   ="""

    params['function'].value= func_name
    params['function'].vary = False

    METHOD  = "lbfgsb"#"leastsq"#"lbfgsb"
    result = minimize(residuals, params, args=(x, y), method=METHOD)

    # write error report
    print " --------> METODO_FITEO: %s" % METHOD
    #print " --------> funcion: %s" % func_name
    #report_errors(params)

    par = zeros(3)
    par[0]  = result.values['A']
    par[1]  = result.values['mu']
    par[2]  = result.values['sig']
    return par



def func_nCR(data, rms_o, tau, q):
    cte     = 0.0
    t, rms  = data[0], data[1]
    dt      = t[1:-1] - t[0:-2]
    integ   = np.nan*np.ones(dt.size)
    for i in range(dt.size):
        integ[i] = np.sum(np.exp(t[1:i+2]/tau) * (rms[1:i+2]-rms_o) * dt[:(i+1)])

    ncr         = np.nan*np.ones(t.size)
    ncr[1:-1]   = np.exp(-t[1:-1]/tau) * (q*integ + cte)
    return ncr



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

class fit_forbush(object):
    def __init__(s, data, sems):
        s.sems = sems
        s.data = data
        nt     = data.shape[1]
        s.t      = data[0,:] # time
        s.rms    = data[1,:] # rms(B)   ['fc'--->'rms']
        s.crs    = data[2,:] # GCRs
        s.b      = data[3,:] # campo B

        #--- process input fot self.nCR2()
        s.to  = 1.0           # to=1.0 : sheath trailing edge
        s.cc  = s.t[1:-1]<=s.to # la recuperacion ocurre despues de 'to'
        s.cx  = s.cc.nonzero()[0] # should be equivalent to 'cx=find(cc)'!
        s.cy  = (~s.cc).nonzero()[0] # antes 'find(~cc)'
        s.dt  = s.t[1:-1] - s.t[0:-2] # permite resolucion des-uniforme
        s.fcc = s.rms[1:-1]
        s.no  = s.cx[-1]
        #--- auxiliary sumatory terms
        s.ncx   = len(s.cx)
        s.ncy   = len(s.cy)
        s.sum0  = np.zeros(shape=s.ncx, dtype=np.float32)
        s.sum1  = np.zeros(shape=s.ncy, dtype=np.float32)
        s.nCR   = np.zeros(shape=nt, dtype=np.float32)
        #--- 1st summatory
        for i, j in zip(s.cx, range(s.ncx)):
            s.sum0[j] = np.sum(s.fcc[:(i+1)]*s.dt[:(i+1)])
        #--- 2nd summatory
        for i, j in zip(s.cy, range(s.ncy)):
            # termino rms
            s.sum1[j] = np.sum(s.fcc[:(i+1)]*s.dt[:(i+1)])

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
        #print params; raw_input()
        if self.monit:
            self.niter += 1
            for nm in params.keys():
                self.foll[nm] += [ params[nm].value ]

        t     = self.t
        crs   = self.crs
        #model = nCR2([t, self.rms, self.b], tau, q, off, bp, bo)
        model = self.nCR2(tau, q, off, bp, bo)
        #sqr   = np.square(crs - model)
        sqr   = np.square(crs - model) # mas rapido q el np.square()
        diff  = np.nanmean(sqr)
        return diff

    def nCR2(s, tau, q, off, bp, bo):
        s.bc = s.b[1:-1] - bo
        s.bc[s.bc<=0.0] = 0.0
        #---- zona sheath
        for i, j in zip(s.cx, range(s.ncx)):
            #s.ind      = s.cx[:(i+1)]
            s.nCR[i+1] = q*s.sum0[j]

        #---- despues de sheath
        for i, j in zip(s.cy, range(s.ncy)):
            # termino rms
            s.nCR[i+1] = q*s.sum1[j]
            # termino recovery-after-sheath
            s.nCR[i+1] += (-1.0/tau)*np.sum(s.nCR[1:-1][s.no:i]*s.dt[s.no:i])
            s.nCR[i+1] += 1.0*off    # offset
            s.nCR[i+1] += bp*np.sum(s.bc[s.no:i]*s.dt[s.no:i])
        return s.nCR
        #END

    def make_fit_brute(self, rranges):
        """
        rranges: slices that define the boundaries && step-size
        """
        rb = brute(self.residuals, rranges, full_output=False, finish=None)
        # este orden va acorde con residuals()
        self.par = { 
            'tau':  rb[0],
            'q':    rb[1],
            'off':  rb[2],
            'bp':   rb[3],
            'bo':   rb[4],
        }

    def make_fit(self, monit=False):
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
        self.monit = monit
        if monit:
            self.niter = 0
            self.foll = {}
            for nm in params.keys():
                self.foll[nm] = []  
                self.foll[nm] += [ params[nm].value ]

        print " --------> METODO_FITEO: %s" % METHOD
        result = minimize(self.residuals, params, method=METHOD)

        # write error report
        #print " --------> funcion: %s" % func_name
        #report_errors(params)
        self.par = {}
        for name in result.params.keys():
            self.par[name] = result.params[name].value

        if monit:
            self.resid = self.residuals(result.params)

#EOF
