"""
Performs two imports::

  from scitools.easyviz import *
  from scitools.basics  import *

The latter import also does a from numpy or scipy import.
See documentation of scitools.easyviz and scitools.basics
for more documentation.
"""
from scitools.easyviz import *
# make sure scipy or numpy overwrites what easyviz imports:
from scitools.basics  import *
