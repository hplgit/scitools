"""
Imports and definitions for the scitools library.

  * import of numpytools:
  
    - a unified interface to Numeric, numarray, numpy
    - extra numerical utility functions
    
  * definition of variables:

    - SAFECODE:

    - OPTIMIZATION:

"""

# avoid integer division (for safety):
from __future__ import division  # must appear in each application file too

# unified interface to Numeric, numarray, and numpy:
from numpytools import *  
# numpytools imports os, sys, operator, math, StringFunction
from glob import glob   # nice to have

# plotting/graphics:
#import easyviz
# if gnuplot is available (check that)
#from easyviz.gnuplot_ import *
#from easyviz import *


# for safety checks:
SAFECODE = True
if os.environ.get('SCITOOLS_SAFECODE', '1') == '0':
    SAFECODE = False
elif not __debug__:  # python -O (optimized mode)
    SAFECODE = False

# for implementing different types of optimizations:
OPTIMIZATION = os.environ.get('SCITOOLS_OPTIMIZATION', False)
# if OPTIMIZATION == 'vectorization', 'f77', 'C' etc.

def debug(comment, var):
    if os.environ.get('PYDEBUG', '0') == '1':
        print comment, var

def check(variable_name, variable):
    print '%s, type=%s' % (variable_name, type(variable)),
    print variable

# *** try to import SciPy if it is installed ***
#print '....before from scipy import *.....'
scipy_is_installed = False
# can turn the somewhat time consuming "from scipy import *"
# on and off by setting an environment variable:
if os.environ.get('SCITOOLS_AUTOIMPORT_SCIPY', '1') != '0':
    if basic_NumPy == 'numpy':   # modern scipy works with numpy
        try:
            from scipy import *
            scipy_is_installed = True
            from numpy.lib.scimath import *    # will be part of scipy import
        except ImportError:
            # no SciPy package
            pass

#print '....after from scipy import *.....'

