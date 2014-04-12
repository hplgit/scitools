#!/usr/bin/env python
"""
Install scitools with easyviz

Usage:

python setup.py install [, --prefix=$PREFIX --easyviz_backend backendname]
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

# NOTE: now we force matplotlib as default backend if it is installed:
# (previously gnuplot was always default)
try:
    import matplotlib
    default_easyviz_backend = 'matplotlib'
except:  # cannot accept any error here
    try:
        import Gnuplot
        default_easyviz_backend = 'gnuplot'
    except:
        # Neither Gnuplot nor Matplotlib is installed. Matplotlib is now set
        # as default backend for Easyviz.
        default_easyviz_backend = 'matplotlib'

# modify config file so that it sets the wanted backend for easyviz
config_file = os.path.join('lib', 'scitools', 'scitools.cfg')
if '--easyviz_backend' in sys.argv:
    try:
        i = sys.argv.index('--easyviz_backend')
        default_easyviz_backend = \
            sys.argv[i+1]
        del sys.argv[i:i+2]
    except IndexError:
        print '--easyviz_backend must be followed by a name like '\
            '\ngnuplot, matplotlib, etc.'
        sys.exit(1)
print 'default scitools.easyviz backend becomes', default_easyviz_backend
print '(could be set by the --easyviz_backend option to setup.py)\n'
# write new config file and change backend line
os.rename(config_file, config_file + '.old~~')
infile = open(config_file + '.old~~', 'r')
outfile = open(config_file, 'w')
for line in infile:
    if line.lstrip().startswith('['):
        section = line.lower().strip()[1:-1]
    if line.lstrip().startswith('backend') and section == 'easyviz':
        outfile.write('backend     = %s  ; default backend\n' % \
                      default_easyviz_backend)
    else:
        outfile.write(line)
infile.close();  outfile.close()

if  __file__ == 'setupegg.py':
    # http://peak.telecommunity.com/DevCenter/setuptools
    from setuptools import setup, Extension
else:
    from distutils.core import setup

# make sure we import from scitools in this package, not an installed one:
sys.path.insert(0, os.path.join('lib')); import scitools

setup(
    version = str(scitools.version), 
    author = ', '.join(scitools.author),
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

if os.path.isfile(config_file + '.cop'):
    os.rename(config_file + '.cop', config_file)

