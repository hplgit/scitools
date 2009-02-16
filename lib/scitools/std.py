"""
Quick import of easyviz and basic scitools modules.

This module just contains two import statements::

  from scitools.easyviz import *
  from scitools.basics  import *

The former imports plot, movie, legend, title, and most other
convienient functions from the Easyviz plotting tool.
The latter performs::

  from numpy import *    
  from scitools.numpyutils import *  # some convenience functions
  from numpy.lib.scimath import *
  from scipy import *                # if scipy is installed
  import sys, operator, math
  from scitools.StringFunction import StringFunction
  from glob import glob
  
See also the documentation of scitools.easyviz and scitools.basics.
"""

# import easyviz first to make sure scipy or numpy overwrites
# what easyviz imports:
from scitools.easyviz import *
from scitools.basics  import *

