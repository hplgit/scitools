"""
Imports and definitions for the scitools library.

* import of numpytools:
  
  - a unified interface to Numeric, numarray, numpy
  - extra numerical utility functions
    
* definition of variables:

  - SciTools defines a series of variables to monitor execution of
    programs: SAFECODE, OPTIMIZATION, backend (for Easyviz),
    VERBOSE, has_scipy, load_scipy. These are set in a configuration
    file. 

* default configuration file::

  [modes]
  SAFECODE = on        ; boolean: safety checks or not
  OPTIMIZATION = off   ; 'F77', 'C', 'vectorization', 'on', etc.
  VERBOSE = 0          ; an int for the level of verbosity

  [scipy]
  load = yes           ; true: from scipy import * (may have side effects)

  [easyviz]
  backend = gnuplot_

      
"""

# avoid integer division (for safety):
from __future__ import division  # must appear in each application file too

_import_times = 'scitools import times: '
import time as _time   # measure how much time various imports take
_t0 = _time.clock()

# load configuration file:
from misc import load_config_file
scitools_config = load_config_file('scitools')

# for safety checks:
SAFECODE = scitools_config.getboolean('modes', 'SAFECODE')
if not __debug__:  # python -O (optimized mode)
    SAFECODE = False

# for implementing different types of optimizations:
OPTIMIZATION = scitools_config.get('modes', 'OPTIMIZATION')
# if OPTIMIZATION == 'vectorization', 'f77', 'C' etc.

VERBOSE = int(scitools_config.get('modes', 'VERBOSE'))

_load_scipy = scitools_config.getboolean('scipy', 'load')
_load_numpytools = scitools_config.getboolean('numpy', 'numpytools')

_t1 = _time.clock(); _import_times += 'config=%g ' % (_t1 - _t0)


# *** try to import SciPy if it is installed ***
# idea: load scipy, if not, load numpy or numpytools

has_scipy = False   # indicates for all application scripts if one has scipy
if _load_scipy:
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
    if _load_numpytools:
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

import os, sys, operator, math, StringFunction
if VERBOSE >= 2: print 'import os, sys, operator, math, StringFunction'
from glob import glob   # nice to have

if VERBOSE >= 3:
    print _import_times


# ------------ utility functions ---------------

def debug(comment, var):
    if os.environ.get('PYDEBUG', '0') == '1':
        print comment, var

def check(variable_name, variable):
    print '%s, type=%s' % (variable_name, type(variable)),
    print variable

