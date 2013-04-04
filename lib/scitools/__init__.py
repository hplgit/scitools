"""
SciTools is a Python package containing lots of useful tools for
scientific computing in Python. The package is built on top of other
widely used packages such as NumPy, SciPy, ScientificPython, Gnuplot,
Matplotlib, VTK, and others. SciTools can be downloaded from
code.google.com/p/scitools.

The SciTools package contains a lot of modules:

  - easyviz: package for unified Matlab-like plotting syntax
  - basics: imports from numpy, scipy, scitools.numpyutils
  - std: imports of basics and easyviz
  - misc: many non-numerical convenience functions
  - numpyutils: many numerical convenience functions
  - StringFunction: turns string formulas into callable functions
  - configdata: user-friendly access to Python config files
  - filetable: read/write tabular data in files into/from arrays
  - debug: useful functions for debugging
  - pprint2: improvement of pprint for formatting control of floats
  - multipleloop: makes a loop from all combinations of a set of parameters
  - EfficiencyTable: nice table report from efficiency experiments
  - globaldata: holds all global data in the scitools package
  - sound: tools for easy sound generation and manipulation
  - aplotter: curve plotting in pure ASCII
  - Lumpy: visualization of the data structures in a Python program

Some modules and classes are closely related to and explained in the
text in the book "Python Scripting for Computational Science", by
H. P. Langtangen, 3rd edition, 2nd printing, Springer, 2009:

  - NumPyDB: a simple database for holding NumPy arrays
  - Regression: module for performing regression tests (also with floats)
  - CanvasCoord: transformations between canvas and physical coordinates
  - DrawFunction: enables users to draw a function (in Pmw.Blt plotting widget)
  - FunctionSelector: Tk/Pmw-based widgets for selecting functions
  - FuncDependenceViz: visualization of how functions vary with parameters
  - ParameterInterface: a simplified GUI generator for simulation programs
  - PrmDictBase: module for holding parameters in simulation programs

Some preliminary modules include
  - BoxGrid: a structured grid in 1D, 2D, or 2D
  - BoxField: a scalar or vector field over a BoxGrid

See the different modules for more detailed information.

The most convenient SciTools import statement reads::

  from scitools.std import *

This statement imports from numpy, scipy (if available),
scitools.numpyutils (many numerical convenince functions), and all
Easyviz plotting capabilities. (See the documentation of
scitools.std for a precise list of imports implied by the
above statement.)

Many programmers prefer to avoid the "star import" above, which
has the disadvantage of filling up the global namespace with
a large number of names. The key import statement is then::

  import scitools.std as st

All functions and modules must then be prefixed by ``st``:
``st.float_eq``, ``st.StringFunction``, ``st.plot``, etc.
"""

__version__ = '0.9.0'
version = __version__
__author__ = 'Johannes H. Ring', 'Hans Petter Langtangen', \

author = __author__

__acknowledgments__ = 'Joachim Berdal Haga', 'Mario Pernici', \
                      'Allen B. Downey', 'Imri Goldberg', \
                      'Fred L. Drake', 'Gael Varoquaux', \
                      'Rolv E. Bredesen', 'Ilmar Wilbers'

try:
    # for backward compatibility:
    import sys, std
    sys.modules['scitools.all'] = std
    try:
        from . import TkGUI
        sys.modules['scitools.CanvasCoords'] = TkGUI
        sys.modules['scitools.DrawFunction'] = TkGUI
        sys.modules['scitools.FuncDependenceViz'] = TkGUI
        sys.modules['scitools.FunctionSelector'] = TkGUI
        sys.modules['scitools.ParameterInterface'] = TkGUI
    except ImportError:
        pass  # Pmw and other graphics might be missing - this is not crucial

except ImportError:
    pass
