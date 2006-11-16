#!/usr/bin/env python
"""Install SciTools
Usage:

python setup.py install [, --prefix=...]
"""

__author__ = 'Hans Petter Langtangen <hpl@simula.no>, Rolv E. Bredesen <rolv@simula.no>'

from distutils.core import setup
import os, glob

external_packages = ['epydoc', 'Gnuplot', 'IPython', 'Pmw', 'Scientific']

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
    packages = ["scitools", "scitools.easyviz", "scitools.pyPDE",] + \
               external_packages,
    py_modules = ["preprocess",],
    # standalone scripts :
    scripts = [os.path.join('bin', f) \
               for f in os.listdir('bin') if not f.startswith('.')],
    )
    
    
