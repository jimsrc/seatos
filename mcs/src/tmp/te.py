from pylab import *

def func(tt):
    if tt=='aa':
        print " ----> hell!"
        raise SystemExit
    else:
        return 999.

print func('uu')
print func('aa')
