#!/usr/bin/env python
"""Install Scitools with easyviz and numpytools
Usage:

python setup.py install [, --prefix=$PREFIX]"""

__author__ = 'Rolv Erlend Bredsen <rolv@simula.no>'

import os, sys, socket, re, glob

if  __file__ == 'setupegg.py':
    # Using easy_install and ezsetup to package as eggs (zipfiles) instead
    url = "http://peak.telecommunity.com/DevCenter/setuptools"+ \
          "#bdist-egg-create-a-python-egg-for-the-project"
    """Normal build
    ~~~~~~~~~~~~
    python setupegg.py bdist_egg 
    easy_install --prefix=$PREFIX dist/Scitools-0.1-py2.4.egg

    Developer build and install
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    python setupegg.py egg_info --tag-svn-revision bdist_egg
    easy_install --prefix=$PREFIX dist/Scitools-0.1_r90-py2.4.egg"""
    from setuptools import setup, Extension
else:
    from distutils.core import setup
    
setup(
    version = "0.1", 
    author = "Hans Petter Langtangen, Rolv Erlend Bredesen, Johannes Ring",
    author_email = "<rolv@simula.no>",
    description = __doc__,
    license = "",
    name = "Scitools",
    url = "",
    package_dir = {'': 'lib'},
    # Packages to install
    packages = ["scitools",
                os.path.join("scitools", "easyviz"), 
                os.path.join("scitools", "pyPDE"),
                ],
    # Extra scripts to install
    #py_modules = ['numpytools',],
    # Install data 
    #data_files = [(os.path.join('easyviz', 'data'), glob.glob('data/*')),
    #              ],
    scripts = [os.path.join('bin', bin) for bin in ['_gnuplot.py',
                                                    'floatdiff.py',
                                                    'pdb',
                                                    'regression.py',
                                                    'timer.py',
                                                    'file2interactive.py',
                                                    'locate_pdb.py',
                                                    'ps2mpeg.py',
                                                    'subst.py']],
    )


               

    
