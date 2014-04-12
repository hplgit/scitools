"""
Import modules and definitions for the scitools library.

Import of Numerical Python
--------------------------

  - If scipy is installed, a from scipy import * is executed.
    scipy requires numpy as basic array library, and scipy replaces
    numpy functionality (at some cost of speed since scipy functions
    are more general).

    The user can turn off import of scipy in the configuration file
    (see below).

  - If scipy is not available or not wanted, two options are possible,
    depending on what is set in the "numpy" section of the configuration
    file:

      1. from numpy import *
         (configuration file: numpytools = no)

      2. from numpytools import *
         which allows the user to transparently use Numeric, numarray,
         and numpy
         (configuration file: numpytools = yes)

To make numpy/scipy and math more similar (and thereby ease
vectorization of user-defined functions), we introduce the math
function names asin, acos, and atan for numpy/scipy's arcsin,
arccos, and arctan.


Other modules
-------------

The from scitools.basics import * statement performs a
from numpy (or scipy) import * as explained above, plus an import
of the modules os, sys, operator, and math. The modules
StringFunction and glob are also imported.


Definition of variables
-----------------------

  - SciTools defines a series of variables to monitor execution of
    programs: SAFECODE, OPTIMIZATION, backend (for Easyviz),
    VERBOSE, DEBUG, has_scipy. Many of these are set in a configuration
    file (see below) or in environment variables (SCITOOLS_SAFECODE,
    SCITOOLS_VERBOSE, SCITOOLS, SCITOOLS_DEBUG, SCITOOLS_easyviz_backend).

All these variables are contained in basics.py.


Debug functions
---------------

The following functions are imported from the debug module:

  - watch(var): print out the name, type, and value of a variable and
    where in a program this output was requested (used to monitor variables).

  - trace(message): print a message and where in the program this
    message was requested (used to trace the execution).

These debug functions require the DEBUG variable to be different from 0.


Default configuration file
--------------------------
"""
# Collect all import statements done by this module
_import_list = []
# Measure CPU time for various import statements
_import_times = 'scitools import times: '
import time as _time
_t0 = _time.clock()

import os
# Add the configuration file as part of the doc string
__doc__ += open(os.path.join(os.path.dirname(__file__), 'scitools.cfg')).read()

# Load configuration file through import of the globaldata module
from .globaldata import *   # read-only import of global variables
_import_list.append("from globaldata import *")
from . import globaldata as _globaldata
#import pprint; pprint.pprint(_globaldata._config_data)

_t1 = _time.clock(); _import_times += 'config=%g ' % (_t1 - _t0)

# *** try to import SciPy if it is installed ***
# idea: load scipy, if not, load numpy or numpytools

has_scipy = False   # indicates for all application scripts if one has scipy
if _globaldata._load_scipy:
    try:
        from .numpyutils import *   # loads numpy too
        from math import factorial # override
        _import_list.append("from numpy import *")
        _import_list.append("from numpyutils import *")
        from scipy import *        # overrides some numpy functions
        has_scipy = True
        from numpy.lib.scimath import *    # will be part of scipy import
        del _import_list[-2]       # del the numpy entry (scipy overrides)
        _import_list.append("from scipy import *")
    except ImportError:
        # ImportError is likely due to missin scipy
        if VERBOSE >= 2: print 'tried to import scipy, but could not find it'
        pass
    _t2 = _time.clock(); _import_times += 'scipy=%g ' % (_t2 - _t1)

# didn't want, or couldn't load, scipy:
if not has_scipy:
    if _globaldata._load_numpytools:
        from .numpytools import *
        _t2 = _time.clock(); _import_times += 'numpytools=%g ' % (_t2 - _t1)
        _import_list.append("from .numpytools import *")
    else:
        # load numpy and numpyutils
        try:
            from .numpyutils import *   # loads numpy too
            _import_list.append("from numpy import *\nfrom .numpyutils import *")
            from numpy.lib.scimath import *   # more general sin, cos etc

        except ImportError:
            raise ImportError('numpy was requested, but it could not be found')
        _t2 = _time.clock(); _import_times += 'numpy=%g ' % (_t2 - _t1)

# nice to have imports:
import sys, operator, math
from scitools.StringFunction import StringFunction
from glob import glob
_import_list.append("import sys, operator, math")
_import_list.append("from StringFunction import StringFunction")
_import_list.append("from glob import glob")

# nice to have symbols (for math/numpy/scipy equivalence/vectorization):
asin = arcsin
acos = arccos
atan = arctan

from . import debug
debug.DEBUG = DEBUG
from .debug import watch, trace
_import_list.append("from debug import watch, trace")

if VERBOSE >= 2:
    for i in _import_list:
        print i

if VERBOSE >= 3:
    print _import_times

__doc__ += '\nImport statements in this module:\n' + '\n'.join(_import_list)
