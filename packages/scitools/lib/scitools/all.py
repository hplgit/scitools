"""
Quick import of easyviz and basic scitools modules.

This module just contains two import statements::

  from scitools.easyviz import *
  from scitools.basics  import *

The latter import also does a from numpy or scipy import.
See documentation of scitools.easyviz and scitools.basics
for more documentation (and information in what is imported).
"""

# import easyviz first to make sure scipy or numpy overwrites
# what easyviz imports:
from scitools.easyviz import *
from scitools.basics  import *

