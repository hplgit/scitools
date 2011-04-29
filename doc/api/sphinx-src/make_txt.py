#!/usr/bin/env python
"""Grab all SciTools modules and make .txt files for sphinx."""
import os, glob

scitools_dir = os.path.join(os.pardir, os.pardir, os.pardir, 'lib', 'scitools')
easyviz_dir = os.path.join(scitools_dir, 'easyviz')
this_dir = os.getcwd()
os.chdir(scitools_dir)
modules_scitools = glob.glob('*.py')
os.chdir('easyviz')
modules_easyviz = glob.glob('*.py')
os.chdir(this_dir)
# strip off .py and remove tmp* and __init__:
modules_scitools = ['scitools.' + m[:-3] for m in modules_scitools \
                    if not m.startswith('tmp') and m != '__init__.py' \
                        and m[-5:] != '.p.py' and not m.startswith('_')]
modules_easyviz  = ['scitools.easyviz.' + m[:-3] for m in modules_easyviz \
                    if not m.startswith('tmp') and m != '__init__.py' \
                        and m[-5:] != '.p.py' and not m.startswith('_')]
modules_scitools.sort()
modules_easyviz.sort()
modules_scitools.insert(0, 'scitools')
modules_easyviz.insert(0, 'easyviz')
modules = modules_scitools + modules_easyviz

for m in modules:
    f = open(m.split('.')[-1] + '.txt', 'w')
    f.write("""
:mod:`%s`
===========================================================

.. automodule:: %s
   :members:
   :undoc-members:
   :show-inheritance:
""" % (m, m))
    f.close()

print 'List of modules for generate.sh:'
print r"""scitools subst ':maxdepth: 2' ":maxdepth: 2\n\n""",
for m in modules:
    print '  ' + m.split('.')[-1] + r'\n',
print '" index.txt'

