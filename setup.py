#!/usr/bin/env python
"""
Install scitools with easyviz

Usage:

sudo python setup.py install

python setup.py install --prefix=$PREFIX --easyviz_backend gnuplot

python setup.py install --prefix=$PREFIX --easyviz_backend matplotlib
"""

import os, sys, socket, re, glob, platform

scripts = [os.path.join("bin", "scitools"),]

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
try:
    import matplotlib
    default_easyviz_backend = 'matplotlib'
except ImportError:
    try:
        import Gnuplot
        default_easyviz_backend = 'gnuplot'
    except:
        # Neither Gnuplot nor Matplotlib is installed. Matplotlib is still set
        # as default backend for Easyviz.
        default_easyviz_backend = 'matplotlib'
        print 'NOTE: matplotlib is not installed on this system, but scitools.easyviz\nwill still use matplotlib as the default plotting engine!'

# Modify config file so that it sets the wanted backend for easyviz
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
# Write new config file and change backend line
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
os.remove(config_file + '.old~~')

if  __file__ == 'setupegg.py':
    # http://peak.telecommunity.com/DevCenter/setuptools
    from setuptools import setup, Extension
else:
    from distutils.core import setup

# Make sure we import from the source code in lib/scitools,
# not an installed scitools package
sys.path.insert(0, os.path.join('lib')); import scitools

setup(
    version = str(scitools.version),
    author = ', '.join(scitools.author),
    author_email = "<hpl@simula.no>",
    description = scitools.__doc__,
    license = "BSD",
    name = "SciTools",
    url = "https://github.com/hplgit/scitools",
    package_dir = {'': 'lib'},
    # Must specify package directories and not individual module files
    # (py_modules) since package_data= only works with packages=
    packages = ["scitools",
                os.path.join("scitools", "easyviz"),
                os.path.join("scitools", "pyreport"),
		],
    package_data = {'': ['scitools.cfg']},
    scripts = scripts,
    data_files=[(os.path.join("share", "man", "man1"),
                 [os.path.join("doc", "man", "man1", "scitools.1.gz"),])],
    )

if os.path.isfile(config_file + '.cop'):
    os.rename(config_file + '.cop', config_file)

