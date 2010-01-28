#!/usr/bin/env python

"""
Demonstration of the quiver command in combination with other plotting
commands.
"""

from scitools.std import *

setp(interactive=False)

xv, yv = ndgrid(linspace(-5,5,81), linspace(-5,5,81))
values = sin(sqrt(xv**2 + yv**2))

pcolor(xv, yv, values, shading='interp')

# create a coarser grid for the gradient field:
xv, yv = ndgrid(linspace(-5,5,21), linspace(-5,5,21), sparse=True)
values = sin(sqrt(xv**2 + yv**2))

# compute the gradient field:
uu, vv = gradient(values)

hold('on')
quiver(xv, yv, uu, vv, 'filled', 'k', axis=[-6,6,-6,6])
show()

#hardcopy('quiver2a.eps')
#hardcopy('quiver2a.png')


figure()
contour(xv, yv, values, 15, hold=True)
quiver(xv, yv, uu, vv, axis=[-6,6,-6,6])
show()

#hardcopy('quiver2b.eps')
#hardcopy('quiver2b.png')

raw_input("Press Return key to quit: ")
