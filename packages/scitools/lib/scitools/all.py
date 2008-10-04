"""
Quick import of easyviz and basic scitools modules.

This module just contains two import statements::

  from scitools.easyviz import *
  from scitools.basics  import *

The former imports plot, movie, legend, title, and most other
convienient functions from the Easyviz plotting tool.
The latter performs a from numpy import * (or from scipy
import *) statement as well as an import of the modules
os, sys, math, StringFunction, operator, and glob.
See documentation of scitools.easyviz and scitools.basics
for more detailed documentation of what is actually imported.
"""

# import easyviz first to make sure scipy or numpy overwrites
# what easyviz imports:
from scitools.easyviz import *
from scitools.basics  import *

