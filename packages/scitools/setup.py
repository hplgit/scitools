#!/usr/bin/env python
"""Install scitools with easyviz
Usage:

python setup.py install [, --prefix=$PREFIX]"""

__author__ = 'Rolv Erlend Bredsen <rolv@simula.no>'

import os, sys, socket, re, glob

BOOTSTRAP = False # Bootstrap setuptools

if BOOTSTRAP:
    from ez_setup import use_setuptools
    use_setuptools()
    
if  __file__ == 'setupegg.py':
    # http://peak.telecommunity.com/DevCenter/setuptools
    from setuptools import setup, Extension
else:
    if BOOTSTRAP:
	from setuptools import setup
    else:
	from distutils.core import setup

# The scitools.cfg.py config file is treated as a Python file...
#configfile = os.path.join("lib", "scitools", "scitools.cfg.py")
ver = sys.version[:3]

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
    # Force configfile to reside with the scitools python package
    #data_files = [('lib/python'+ver+'/site-packages/scitools', [configfile,])],
    #data_files = [("scitools", [configfile,])], # easier to use bootstrap
    
    scripts = [os.path.join('bin', f) \
               for f in os.listdir('bin') if not f.startswith('.')],
	       )
	    
    
               

    
