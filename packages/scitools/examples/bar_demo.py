#!/usr/bin/env python

from scitools.all import *
from numpy.random import rand

# simple example:
bar(rand(4,3))

# example with a vector:
figure()
x = linspace(-3,3,15)
y = exp(-x*x)
if backend == 'gnuplot':
    bar(y,0.7)  # increase width of bars
else:
    bar(y)

# draw a bar graph from a dicitonary:
figure()
data = {'method1': {'thing1': 3, 'thing2': 2, 'thing3': 4},
        'method2': {'thing1': 4, 'thing2': 4.5, 'thing3': 2},
        'method3': {'thing1': 1, 'thing2': 4, 'thing3': 2},}
bar(data,rotated_barticks=False,
    hardcopy='bar1a.eps',color=True,
    ymin=0,ymax=5)

# border turned off:
figure()
bar(rand(5,4),shading='interp')


raw_input('press enter')
