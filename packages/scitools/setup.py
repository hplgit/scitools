#!/usr/bin/env python
"""Install scitools with easyviz
Usage:

python setup.py install [, --prefix=$PREFIX]"""

__author__ = 'Rolv Erlend Bredsen <rolv@simula.no>'

import os, sys, socket, re, glob

if  __file__ == 'setupegg.py':
    # http://peak.telecommunity.com/DevCenter/setuptools
    from setuptools import setup, Extension
else:
    from distutils.core import setup
    
configfile = os.path.join("lib", "scitools", "scitools.cfg")

setup(
    version = "0.1", 
    author = "Hans Petter Langtangen, Rolv Erlend Bredesen, Johannes Ring",
    author_email = "<rolv@simula.no>",
    description = __doc__,
    license = "",
    name = "Scitools",
    url = "",
    package_dir = {'': 'lib'},
    packages = ["scitools",
                os.path.join("scitools", "easyviz"), 
		os.path.join("scitools", "pyPDE"),
                ],
    #py_modules = ['numpytools',], # Extra scripts to install
    data_files = [("scitools", [configfile,])],
    scripts = [os.path.join('bin', f) \
               for f in os.listdir('bin') if not f.startswith('.')],
	       )
	       
    
    
               

    
