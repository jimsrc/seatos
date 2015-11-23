from pylab import *
import numpy as np
from lmfit import minimize, Parameters, Parameter, report_errors


def get_histogram(var, nbins, lims=None):
    # quitamos nans
    no_nans = ~np.isnan(var)
    var     = var[no_nans]
    # histograma
    h   = np.histogram(var, bins=nbins, range=lims)
    #close()         # para no generar figura
    h_cnts  = h[0]      # counts    n elementos
    h_bound = h[1]      # boundaries    n+1 elementos
    #
    n   = len(h_cnts)
    h_x = np.zeros(n)
    for i in range(n):
        h_x[i]  = 0.5*(h_bound[i] + h_bound[i+1])
    #
    return [h_cnts, h_x]


def lognormal(x, A, mu, sig):
    potenc  = ((log(x) - mu)**2.) / (2.*sig**2.)
    denom   = x * sig * sqrt(2.*pi)
    f   = A * exp(-potenc) / denom
    return f


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


def make_fit(data, sems, func_name):
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
    params['A'].min     = 0.1*SEM_A
    params['A'].max     = 2.0*SEM_A

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


def ajustar_lognormal(data, sems):
    x   = data[0]
    y   = data[1]
    SEM_mu  = sems[0]
    SEM_sig = sems[1] 



