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

import time as _time   # measure how much time various imports take
_t0 = _time.clock()

# load configuration file
import ConfigParser, os, sys
scitools_config = ConfigParser.ConfigParser()

_default_config_file = os.path.join(os.path.dirname(__file__),
                                    'scitools.cfg.py')
scitools_config.readfp(open(_default_config_file))
_files = scitools_config.read(['.scitools.cfg',
                               os.path.expanduser('~/.scitools.cfg')])

# for safety checks:
SAFECODE = scitools_config.getboolean('modes', 'SAFECODE')
if not __debug__:  # python -O (optimized mode)
    SAFECODE = False

# for implementing different types of optimizations:
OPTIMIZATION = scitools_config.get('modes', 'OPTIMIZATION')
# if OPTIMIZATION == 'vectorization', 'f77', 'C' etc.

VERBOSE = int(scitools_config.get('modes', 'VERBOSE'))

_load_scipy = scitools_config.getboolean('scipy', 'load')

_t1 = _time.clock()
_config_time = _t1 - _t0

# unified interface to Numeric, numarray, and numpy:
# NO, restrict scitools to numpy, split numpytools into numpyload and numpyutils, update script in py4cs must be changed; numpyutils must also have arrmin, arrmax (?) or...? check numpy.min/max if they are sufficient
#from numpytools import *
# could avoid numpy import if there is a scipy import!!!
from numpy import *
basic_NumPy = 'numpy'
# numpytools imports os, sys, operator, math, StringFunction
from glob import glob   # nice to have

_t2 = _time.clock()
_numpytools_time = _t2 - _t1

# *** try to import SciPy if it is installed ***
has_scipy = False
#print '....before from scipy import *.....'
if _load_scipy:
    if basic_NumPy == 'numpy':   # modern scipy works with numpy
        try:
            from scipy import *
            has_scipy = True
            from numpy.lib.scimath import *    # will be part of scipy import
        except ImportError:
            # no SciPy package
            pass

#print '....after from scipy import *.....'

_t3 = _time.clock()
_scipy_time = _t3 - _t2

if VERBOSE >= 2:
    print 'from numpytools import *'
    print 'Numerical Python implementation:', basic_NumPy
    if has_scipy:
        print 'from scipy import *'
if VERBOSE >= 3:
    print 'Import time: config=%.3f, numpytools=%.3f, scipy=%.3f' \
          % (_config_time, _numpytools_time, _scipy_time)


# ------------ utility functions ---------------

def debug(comment, var):
    if os.environ.get('PYDEBUG', '0') == '1':
        print comment, var

def check(variable_name, variable):
    print '%s, type=%s' % (variable_name, type(variable)),
    print variable

