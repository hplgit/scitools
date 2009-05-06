#!/usr/bin/env python
"""
Install scitools with easyviz

Usage:

python setup.py install [, --prefix=$PREFIX]
"""

import os, sys, socket, re, glob, platform

scripts = [os.path.join("bin", "scitools"), os.path.join("bin", "pyreport")]

if platform.system() == "Windows" or "bdist_wininst" in sys.argv:
    # In the Windows command prompt we can't execute Python scripts 
    # without a .py extension. A solution is to create batch files
    # that runs the different scripts.
    batch_files = []
    for script in scripts:
        batch_file = script + ".bat"
        f = open(batch_file, "w")
        f.write('python "%%~dp0\%s" %%*\n' % os.path.split(script)[1])
        f.close()
        batch_files.append(batch_file)
    scripts.extend(batch_files)

# make sure we import from scitools in this package, not an installed one:
sys.path.insert(0, os.path.join('lib'))
import scitools
    
if  __file__ == 'setupegg.py':
    # http://peak.telecommunity.com/DevCenter/setuptools
    from setuptools import setup, Extension
else:
    from distutils.core import setup

setup(
    version = str(scitools.version), 
    author = ', '.join(scitools.author),
    #version = '0.6',
    #author = 'Hans Petter Langtangen',
    author_email = "<hpl@simula.no>",
    description = scitools.__doc__,
    license = "BSD",
    name = "SciTools",
    url = "http://scitools.googlecode.com",
    package_dir = {'': 'lib'},
    packages = ["scitools",
                os.path.join("scitools", "easyviz"), 
		],
    package_data = {'': ['scitools.cfg']},
    scripts = scripts,
    data_files=[(os.path.join("share", "man", "man1"),
                 [os.path.join("doc", "man", "man1", "scitools.1.gz"),
                  os.path.join("doc", "man", "man1", "pyreport.1.gz")])],
    )
