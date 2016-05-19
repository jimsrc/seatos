#!/usr/bin/env ipython
# cython: boundscheck=False, cdivision=True, initializedcheck=False, wraparound=False
"""# cython: profile=True
# cython: linetrace=True"""
import numpy as np
from lmfit import minimize, Parameters, Parameter, report_errors
from numpy import array, ones, zeros, sum, power, min, max
import sys
from scipy.optimize import brute, fmin
#--- cython stuff
cimport numpy as np
# Numpy must be initialized. When using numpy from C or Cython you must
# _always_ do that, or you will have segfaults
np.import_array()
#--- some datatypes 
ctypedef np.int_t       Int
ctypedef np.float32_t   Float32
ctypedef np.ndarray     NDarray


"""
cdef nCR2(data, double tau, double q, double off, double bp, double bo):
    cdef:
        int i, no
        double t, fc, b, to
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
"""

#cdef struct nCR_par:
#    """ structure for parameters of fit_forbush::nCR2()
#    """
#    Float32 tau, q, off, bp, bo


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

cdef class fit_forbush(object):
    #cdef nCR_par par
    cdef NDarray t, rms, b, dt, fcc, bc, crs
    cdef NDarray sum0, sum1, sems
    #cdef Float32[:] fcc, bc#, t, fc, b, dt
    cdef Float32 to
    #cdef Float32[:] nCR # output
    cdef NDarray nCR # output
    cdef Int[:] cx, cy
    cdef NDarray cc
    cdef Int ncx, ncy, no, nt

    """def __init__(self, data, sems):"""
    def __cinit__(s, NDarray[Float32, ndim=2, mode="c"] data, NDarray[Int, ndim=1] sems):
        s.sems = sems
        s.nt  = data.shape[1]
        s.t   = np.ndarray(shape=s.nt, dtype=np.float32)
        s.dt  = np.ndarray(shape=s.nt, dtype=np.float32)
        s.rms = np.ndarray(shape=s.nt, dtype=np.float32)
        s.b   = np.ndarray(shape=s.nt, dtype=np.float32)
        s.crs = np.ndarray(shape=s.nt, dtype=np.float32)
        s.fcc = np.ndarray(shape=s.nt, dtype=np.float32)
        s.bc  = np.ndarray(shape=s.nt, dtype=np.float32)
        s.cc  = np.ndarray(shape=s.nt, dtype=np.int)
        s.nCR = np.zeros(s.nt, dtype=np.float32) # allocate memory

        s.t[:]     = data[0,:]    # time
        s.rms[:]   = data[1,:]    # rms(B)
        s.crs[:]   = data[2,:]    # GCRs
        s.b[:]     = data[3,:]    # campo B

        #--- process inputs
        cdef Int i, j
        s.to  = 1.0           # to=1.0 : sheath trailing edge
        s.cc  = s.t[1:s.nt]<=s.to # la recuperacion ocurre despues de 'to'
        s.cx  = s.cc.nonzero()[0] # should be equivalent to 'cx=find(cc)'!
        s.cy  = (~s.cc).nonzero()[0] # antes 'find(~cc)'
        s.ncx = len(s.cx)
        s.ncy = len(s.cy)
        s.dt  = s.t[1:s.nt] - s.t[0:s.nt-1]
        s.fcc = s.rms[1:s.nt]
        s.no  = s.cx[s.ncx-1]
        #--- auxiliary sumatory terms
        s.sum0  = np.zeros(shape=s.ncx, dtype=np.float32)
        s.sum1  = np.zeros(shape=s.ncy, dtype=np.float32)
        #--- 1st summatory
        for i, j in zip(s.cx, range(s.ncx)):
            s.sum0[j] = np.sum(s.fcc[:(i+1)]*s.dt[:(i+1)])
        #--- 2nd summatory
        for i, j in zip(s.cy, range(s.ncy)):
            # termino rms
            s.sum1[j] = np.sum(s.fcc[:(i+1)]*s.dt[:(i+1)])


    #@cython.boundscheck(False)
    cdef void nCR2(s, double tau, double q, double off, double bp, double bo):
        cdef Int i#, no

        s.bc = s.b[1:s.nt] - bo
        s.bc[s.bc<=0.0] = 0.0
        #---- zona sheath
        for i, j in zip(s.cx, range(s.ncx)):
            #s.ind      = s.cx[:(i+1)]
            #s.nCR[i+1] = q*np.sum(s.fcc[:(i+1)]*s.dt[:(i+1)])
            s.nCR[i+1] = q*s.sum0[j]

        #---- despues de sheath
        for i, j in zip(s.cy, range(s.ncy)):
            # termino rms
            s.nCR[i+1] = q*s.sum1[j]
            # termino recovery-after-sheath
            s.nCR[i+1] += (-1.0/tau)*np.sum(s.nCR[1:s.nt][s.no:i]*s.dt[s.no:i])
            s.nCR[i+1] += 1.0*off    # offset
            s.nCR[i+1] += bp*np.sum(s.bc[s.no:i]*s.dt[s.no:i])
        #return s.nCR
        #END


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
        #model = nCR2([t, self.rms, self.b], tau, q, off, bp, bo)
        self.nCR2(tau, q, off, bp, bo)
        model = self.nCR
        sqr   = np.square(crs - model)
        diff  = np.nanmean(sqr)
        #print " diff---> %f, tau:%g, q:%g, bp:%g" % (diff, tau, q, bp)
        #LINE = "%g   %g  %g  %g %g  %g\n" % (tau, q, bp, off, bo, diff)
        #sys.stderr.write(LINE)
        return diff


    def make_fit_brute(self, rranges):
        rb = brute(self.residuals, rranges, full_output=False, finish=None)
        # este orden va acorde con self.residuals()
        result = { 
            'tau':  rb[0],
            'q':    rb[1],
            'off':  rb[2],
            'bp':   rb[3],
            'bo':   rb[4],
        }
        return result


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
        result = {}
        for name in result.params.keys():
            self.result[name] = result.params[name].value
        print result
        return result

#EOF
