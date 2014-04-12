#!/usr/bin/env python
import glob, os, sys

demos = glob.glob('*.py')
avoid = 'runall.py',
for filename in avoid:
    demos.remove(filename)

from scitools.std import backend
try:
    backend = sys.argv[1]
except IndexError:
    pass

for filename in sorted(demos):
    answer = raw_input(filename + '? ')
    if answer.lower() == 'n':
        continue
    if 'matlab' in filename and not backend.startswith('matlab'):
        continue
    if ('isosurf' in filename or 'streamtube' in filename or \
        'slice' in filename or 'contourslice' in filename) and \
       backend in ('gnuplot', 'grace', 'matplotlib',):
        continue
    cmd = 'python %s --SCITOOLS_easyviz_backend %s' % (filename, backend)
    failure = os.system(cmd)

# surf_demo2

