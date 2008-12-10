#!/usr/bin/env python
"""
Install scitools with easyviz

Usage:

python setup.py install [, --prefix=$PREFIX]
"""

import os, sys, socket, re, glob

# make sure we import from scitools in this package, not an installed one:
sys.path.insert(0, os.path.join('lib'))
import scitools
    
if  __file__ == 'setupegg.py':
    # http://peak.telecommunity.com/DevCenter/setuptools
    from setuptools import setup, Extension
else:
    from distutils.core import setup

setup(
    #version = str(scitools.version), 
    #author = ', '.join(scitools.author),
    version = '0.4',
    author = 'Hans Petter Langtangen',
    author_email = "<hpl@simula.no>",
    description = scitools.__doc__,
    license = "BSD",
    name = "SciTools",
    url = "http://scitools.googlecode.com",
    package_dir = {'': 'lib'},
    packages = ["scitools",
                os.path.join("scitools", "easyviz"), 
		#os.path.join("scitools", "pyPDE"),
		],
    package_data = {'': ['scitools.cfg']},
    scripts = [os.path.join('bin', f)
               for f in os.listdir('bin')
               if not (f.startswith('.') or f.endswith('~') or
                       f.endswith('.old') or f.endswith('.bak'))],
    )
