"""
Import modules and definitions for the scitools library
=======================================================

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

      1. from numpytools import *
         which allows the user to transparently use Numeric, numarray,
         and numpy, plus lots of utility functions from numpyutils
         (configuration file: numpytools = yes)

      2. from numpy import * and from numpyutils import *
         (configuration file: numpytools = no)
    
Definition of variables
-----------------------

  - SciTools defines a series of variables to monitor execution of
    programs: SAFECODE, OPTIMIZATION, backend (for Easyviz),
    VERBOSE, DEBUG, has_scipy. Many of these are set in a configuration
    file (see below) or in environment variables (SCITOOLS_SAFECODE,
    SCITOOLS_VERBOSE, SCITOOLS, SCITOOLS_DEBUG, SCITOOLS_easyviz_backend).

Debug functions 
---------------

  - watch(var): print out the name, type, and value of a variable and
    where in a program this output was requested (used to monitor variables).

  - trace(message): print a message and where in the program this
    message was requested (used to trace the execution).

These debug functions require the DEBUG variable to be different from 0.

    
Default configuration file
--------------------------
"""
# avoid integer division (for safety):
from __future__ import division  # must appear in each application file too

_import_times = 'scitools import times: '
import time as _time   # measure how much time various imports take
_t0 = _time.clock()

import os
__doc__ += open(os.path.join(os.path.dirname(__file__), 'scitools.ini')).read()

from globaldata import *   # read-only import of global variables
import globaldata as _globaldata
#import pprint; pprint.pprint(_globaldata._config_data)

_t1 = _time.clock(); _import_times += 'config=%g ' % (_t1 - _t0)

# *** try to import SciPy if it is installed ***
# idea: load scipy, if not, load numpy or numpytools

has_scipy = False   # indicates for all application scripts if one has scipy
if _globaldata._load_scipy:
    try:
        from scipy import *
        has_scipy = True
        from numpy.lib.scimath import *    # will be part of scipy import
        if VERBOSE >= 2: print 'from scipy import *'
    except ImportError:
        # no SciPy package, NumPy only
        if VERBOSE >= 2: print 'tried to import scipy, but could not find it'
        pass
    _t2 = _time.clock(); _import_times += 'scipy=%g ' % (_t2 - _t1)

# didn't want our couldn' load scipy:
if not has_scipy:
    if _globaldata._load_numpytools:
        from numpytools import *
        if VERBOSE >= 2: print 'from numpytools import *'
        _t2 = _time.clock(); _import_times += 'numpytools=%g ' % (_t2 - _t1)
    else:
        # load numpy and numpyutils
        try:
            from numpyutils import *   # loads numpy too
            if VERBOSE >= 2: print 'from numpy import *'
            if VERBOSE >= 2: print 'from numpyutils import *'
        except ImportError:
            raise ImportError, \
                  'numpy was requested, but it could not be found'
        _t2 = _time.clock(); _import_times += 'numpy=%g ' % (_t2 - _t1)

# nice to have imports:
import sys, operator, math, StringFunction
from glob import glob

if VERBOSE >= 2: print 'import os, sys, operator, math, StringFunction'
if VERBOSE >= 3:
    print _import_times

import debug
debug.DEBUG = DEBUG
from debug import watch, trace
