#!/usr/bin/env python

"""Demonstration on how to place arbitrary axes in some backends."""

from scitools.all import *

x = linspace(0,1,51)
y1 = sin(2*pi*x)
y2 = cos(4*pi*x)

plot(x, y1, 'rd-', xlabel='x-axis', ylabel='y-axis', legend='test')

if backend == 'veusz':
    pos = ['9cm', '9cm', '1cm', '2cm']
elif backend == 'gnuplot':
    pos = [.6, .52, .33, .33]
elif backend in ['matplotlib', 'matlab', 'matlab2']:
    pos = [.62, .56, .2, .2]
else:
    print "The '%s' backend has currently no support for placement of " \
          "arbitrary axes." % backend
    sys.exit(1)

ax = axes(viewport=pos)
plot(ax, x, y2, 'b--')

hardcopy('axes1a.eps')
hardcopy('axes1a.png')

if backend == 'matlab2':
    save('test_axes.m')
elif backend == 'veusz':
    save('test_axes.vsz')

raw_input('press enter to continue')
