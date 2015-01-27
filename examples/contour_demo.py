#!/usr/bin/env python

from scitools.std import *

# A simple contour plot of the peaks function (standard test function):
contour(peaks())

figure()
# Here we draw 15 red contour lines with double line width:
xv, yv = ndgrid(linspace(-3, 3, 51), linspace(-3, 3, 51))
values = xv*exp(-xv**2 - yv**2)
contour(xv, yv, values, 15, 'r', linewidth=2)

figure()
# Draw contour lines with labels at -2, 0, 2, and 5:
values = peaks(xv, yv)
contour(xv, yv, values, [-2,0,2,5])

figure()
# Here we combine a contour plot with a quiver plot
# (note: currently not working with the Gnuplot backend):
x = y = linspace(-2, 2, 21)
xv, yv = ndgrid(x, y)  # or meshgrid(x, y, indexing='ij')
values = sin(xv)*sin(yv)*exp(-xv**2 - xv**2)
dx, dy = gradient(values)
contour(xv, yv, values, 10, show=False)
hold('on')
quiver(xv, yv, dx, dy, 2, show=True)
hold('off')

figure()
# Another example with contour labels:
x = linspace(-2,2,201)
y = linspace(-1,1,51)
xv, yv = ndgrid(x,y)
values = sin(3*yv - xv**2 + 1) + cos(2*yv**2 - 2*xv)
contour(xv, yv, values, clabels='on')  # contour(x,y,values,..) also works

figure()
# The contourf command draws filled contours:
values = peaks(201)
contourf(values, 10, caxis=[-20, 20], title='Filled Contour Plot')

raw_input('Press Return key to quit: ')
