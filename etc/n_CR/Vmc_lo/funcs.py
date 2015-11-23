from pylab import find
import numpy as np
from lmfit import minimize, Parameters, Parameter, report_errors

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



def nCR2(data, tau, q):
    t, fc = data
    to  = 1.0          # to=1.0 : sheath trailing edge
    cc  = t[1:-1]<=to   # la recuperacion ocurre despues de 'to'
    cx  = find(cc)
    dt  = t[1:-1] - t[0:-2]
    nCR = np.nan*np.ones(t.size)
    fcc = fc[1:-1]
    for i in cx:
        ind      = cx[:(i+1)]
        nCR[i+1] = q*np.sum(fcc[:(i+1)]*dt[:(i+1)]) 

    cy  = find(~cc)
    no  = cx[-1]
    for i in cy:
        # termino rms
        nCR[i+1] = q*np.sum(fcc[:(i+1)]*dt[:(i+1)]) 
        # termino recovery-after-sheath
        nCR[i+1] += (-1.0/tau)*np.sum( nCR[1:-1][no:i]*dt[no:i] )

    return nCR



#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class fit_forbush():
    def __init__(self, data, sems):
        self.sems = sems
        self.data = data
        self.t      = data[0]
        self.rms    = data[1]
        self.crs    = data[2]


    def residuals(self, params):
        tau    = params['tau'].value
        q      = params['q'].value
        #diff = np.power(fun_name(x, A, mu, sig)  - y_data, 2.0)
        t    = self.t
        crs  = self.crs
        #sqr  = np.power(crs - func_nCR([t,self.rms], rms_o, tau, q), 2.0)
        sqr  = np.power(crs - nCR2([t,self.rms], tau, q), 2.0)
        diff = np.nanmean(sqr)
        print " diff---> %f, tau:%g, q:%g" % (diff, tau, q)
        return diff


    def make_fit(self):
        sems    = self.sems
        #x   = self.t #data[0]
        #y   = self.crs #data[1]     
        # create a set of Parameters
        params = Parameters()
        params.add('q')
        params.add('tau')

        SEM_tau   = sems[0]
        SEM_q     = sems[1]

        params['tau'].value  = SEM_tau
        params['tau'].vary   = True
        params['tau'].min     = 1.0
        params['tau'].max     = 16.0

        params['q'].value = SEM_q
        params['q'].vary  = True
        params['q'].min    = -800.0 #-1.0e3 
        params['q'].max    = -200.0 #-1.0e1

        METHOD  = "lbfgsb"#"leastsq"#"lbfgsb"
        result = minimize(self.residuals, params, method=METHOD)

        # write error report
        print " --------> METODO_FITEO: %s" % METHOD
        #print " --------> funcion: %s" % func_name
        #report_errors(params)

        par = np.zeros(2)
        par[0]  = result.values['tau']
        par[1]  = result.values['q']
        self.par = par
        
