#!/usr/bin/env python
"""Install SciTools
Usage:

python setup.py install [, --prefix=...]
"""

__author__ = 'Hans Petter Langtangen <hpl@simula.no>, Rolv E. Bredesen <rolv@simula.no>'

from distutils.core import setup
import os, glob

# this script applies to a directory tree with the SciTools++ suite
external_packages = ['preprocess', 'epydoc', 'Gnuplot', 'IPython',
                     'Pmw', 'Scientific']
internal_packages = ['doconce',
                     'scitools', 'scitools.easyviz', 'scitools.pyPDE',
                     ]

setup(
    version = "1.0",
    author = "Rolv Bredesen, Hans Petter Langtangen",
    author_email = "<hpl@simula.no>",
    description = __doc__,
    license = "Well",
    name = "SciTools++",
    url = "",
    package_dir = {'': 'lib'},
    # packages to install:
    packages = internal_packages + external_packages,
    # standalone scripts :
    scripts = [os.path.join('bin', f) \
               for f in os.listdir('bin') if not f.startswith('.')],
    )
    
    
