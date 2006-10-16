"""
Imports and definitions for the scitools library.

  a unified interface to Numeric, numarray, numpy
  extra numerical utility functions
  definition of variables: SAFECODE, OPTIMIZATION
  etc.
"""

#Idea: scitools++.tar.gz lager scitools++ som har kildekode til IPython etc
#+ scitools/

# avoid integer division (for safety):
from __future__ import division  # must appear in each application file too

sys.path.insert(0, 'core')  # much from py4cs etc. will lie here

# unified interface to Numeric, numarray, and numpy:
from numpytools import *  
# numpytools imports os, sys, operator, math, StringFunction

# plotting/graphics:
from easyviz import *
from glob import glob # nice to have

# for safety checks:
SAFECODE = True
if os.environ.get('SCITOOLS_SAFECODE', '1') == '0':
    SAFECODE = False
elif not __debug__:  # python -O (optimized mode)
    SAFECODE = False

# for implementing different types of optimizations:
OPTIMIZATION = os.environ.get('SCITOOLS_OPTIMIZATION', False)
# if OPTIMIZATION == 'vectorization', 'f77', 'C' etc.

# *** try to import SciPy if it is installed ***
scipy_is_installed = False
if basic_NumPy == 'numpy':
    try:
        from scipy import *
        scipy_is_installed = True
    except ImportError:
        # no SciPy package
        pass


def debug(comment, var):
    if os.environ.get('PYDEBUG', '0') == '1':
        print comment, var

def check(variable_name, variable):
    print '%s, type=%s' % (variable_name, type(variable)),
    print variable
