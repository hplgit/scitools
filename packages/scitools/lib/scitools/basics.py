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

# load configuration file:
from misc import load_config_file as _load_config_file
scitools_config = _load_config_file('scitools')

# for safety checks:
SAFECODE = scitools_config.getboolean('modes', 'SAFECODE')
SAFECODE = bool(os.environ.get('SCITOOLS_SAFECODE', SAFECODE))
if not __debug__:  # python -O (optimized mode)
    SAFECODE = False

VERBOSE = int(scitools_config.get('modes', 'VERBOSE'))
VERBOSE = int(os.environ.get('SCITOOLS_VERBOSE', VERBOSE))
DEBUG = int(scitools_config.get('modes', 'DEBUG'))
DEBUG = int(os.environ.get('SCITOOLS_DEBUG', DEBUG))
if not __debug__:
    DEBUG = 0  # always turn off debugging if we run python -O

# for implementing different types of optimizations:
OPTIMIZATION = scitools_config.get('modes', 'OPTIMIZATION')
OPTIMIZATION = os.environ.get('SCITOOLS_OPTIMIZATION', OPTIMIZATION)
# usage: if OPTIMIZATION == 'vectorization', 'f77', 'C' etc.


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

# nice to have imports:
import sys, operator, math, StringFunction
from glob import glob

if VERBOSE >= 2: print 'import os, sys, operator, math, StringFunction'
if VERBOSE >= 3:
    print _import_times


# ------------ utility functions ---------------

from traceback import extract_stack as _extract_stack

def watch(variable, output_medium=sys.stdout):
    """
    Print out the name, type, and value of a variable and
    where in a program this output was requested.
    Used to monitor variables during debugging.
    As an example, watch(myprm) may lead to this output::

      File "myscript.py", line 56, in myfunction
        myprm, type "int" = 3

    Taken from the online Python Cookbook::

      http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52314/index_txt
      
    (original code written by Olivier Dagenais)
    """
    if DEBUG:
        stack = _extract_stack()[-2:][0]
        actual_call = stack[3]
        if actual_call is None:
            actual_call = "watch([unknown])"
        left = string.find(actual_call, '(' )
        right = string.rfind(actual_call, ')')
        prm = {}
        # get variable name is extracted from actual_call:
        # everything between '(' and ')'
        prm["variable_name"] = string.strip(actual_call[left+1:right])  
        prm["variable_type"] = str(type(variable))[7:-2]
        prm["value"]       = repr(variable)
        prm["methodName"]  = stack[2]
        prm["line_number"] = stack[1]
        prm["filename"]    = stack[0]
        outstr = 'File "%(filename)s", line %(line_number)d, '\
                 'in %(methodName)s\n  %(variable_name)s, '\
                 'type "%(variable_type)s" = %(value)s\n\n'
        output_medium.write(outstr % prm)

def trace(message='', output_medium=sys.stdout):
    """
    Print a message and where in the program this
    message was requested (as in the function watch).
    Used to trace the program flow during debugging.
    """
    if DEBUG:
        stack = _extract_stack()[-2:][0]
        prm = {}
        prm["method_name"] = stack[2]
        prm["line_number"] = stack[1]
        prm["filename"]    = stack[0]
        prm["message"]     = message
        outstr = 'File "%(filename)s", line %(line_number)d, in %(method_name)s: %(message)s\n\n'
        output_medium.write(outstr % prm)

