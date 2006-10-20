#!/usr/bin/env python
"""Install Scitools with easyviz and numpytools
Usage:

python setup[_egg].py install [, --prefix=$PREFIX]"""

__author__ = 'Rolv Erlend Bredsen <rolv@simula.no>'

import os, sys, socket, re, glob

if  __file__ == 'setupegg.py':
    """Usage:
    python setupegg.py bdist_egg
    easy_install --prefix=$PREFIX dist/Scitools-0.1-py2.4.egg"""
    from setuptools import setup, Extension
else:
    from distutils.core import setup
    
setup(
    version = "0.1", 
    author = "Hans Petter Langtangen, Rolv Erlend Bredesen, Johannes Ring",
    author_email = "<rolv@simula.no>",
    description = __doc__,
    license = "Well",
    name = "Scitools",
    url = "",
    package_dir = {'': 'lib'},
    # Packages to install
    packages = ["scitools",],
    # Extra scripts to install
    #py_modules = ['numpytools',],
    # Install data 
    #data_files = [(os.path.join('easyviz', 'data'), glob.glob('data/*')),
    #              ],
    scripts = [os.path.join('bin', 'subst.py'),
               ],
    )

    
