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


def safe_point_set(pts):
    """True if it's safe to speed up with the given point set."""
    for p in pts:
        if (not safe_val(p[0])) or (not safe_val(p[1])):
            return False
    return True


def cppWrapper(name, pyf, cppf, speedup, **kwargs):
    if not speedup:
        return pyf(**kwargs)

    if __config['PURE_PYTHON'] and (speedup == 'try' or speedup):
        warnings.warn(
            "PyDCG:PURE_PYTHON option set to True. The Python version of '" +
            name +
            "' will be used.",
            stacklevel=3)
        return pyf(**kwargs)

    if speedup == 'try':
        safepts = safe_point_set(kwargs['points'])
        safep = True if 'p' not in kwargs else safe_val(kwargs['p'])
        if safepts and safep:
            return cppf(**kwargs)
        else:
            return pyf(**kwargs)

    if speedup:
        return cppf(**kwargs)

    raise ValueError("Invalid value for parameter 'speedup':" + str(speedup))
