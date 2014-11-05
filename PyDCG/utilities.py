# -*- coding: utf-8 -*-

'''This module contains some definitions for some constants and the wapper for
    C++ functions used in various modules.'''

import pickle
import os
import warnings

warnings.filterwarnings('always', '.*PyDCG.*',)

__config_file = open(os.path.join(os.path.dirname(__file__),
                                  "config/config.cfg"), "rb")
__config = pickle.load(__config_file)
__config_file.close()


def safe_val(n):
    """True if the it is safe to speed up with the given integer."""
    return __config["MAX_INT"] >= abs(n)
    
def safe_point(p):
    """True if the it is safe to speed up with the given integer."""
    return __config["MAX_INT"] >= abs(p[0]) and __config["MAX_INT"] >= abs(p[1])


def safe_point_set(pts):
    """True if it's safe to speed up with the given point set."""
    for p in pts:
        if not safe_point(p):
            return False
    return True

#TODO: Decide whether the bounds are going to be checked here or on the C++ side. I think currently
#there C wrappers are also checking this

def cppWrapper(pyf, cppf, speedup, checkPoints=None, checkPointSets=None, **kwargs):
    if __config['PURE_PYTHON'] or not speedup:
        return pyf(**kwargs)

    if speedup == 'try':
        safePoints = True
        if checkPoints is not None:
            for p in checkPoints:
                safePoints = safePoints and safe_point(p)
                
        safePointSets = True
        if checkPointSets is not None:
            for pts in checkPointSets:
                safePointSets = safePointSets and safe_point_set(pts)
                
        if safePoints and safePointSets:
            return cppf(**kwargs)
        else:
            return pyf(**kwargs)

    if speedup:
        return cppf(**kwargs)

    raise ValueError("Invalid value for parameter 'speedup':" + str(speedup))

def loadData(filename):
    f = open(filename, "rb")
    data = pickle.load(f)
    f.close()
    return data
    
def saveData(filename, data):
    f = open(filename, "wb")
    pickle.dump(data, f)
    f.close()