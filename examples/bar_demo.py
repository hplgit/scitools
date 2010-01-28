#!/usr/bin/env python

from scitools.std import *
from numpy.random import rand

# simple example:
bar(rand(4,3))

# example with a vector:
figure()
x = linspace(-3,3,15)
y = exp(-x*x)
if backend in ['gnuplot', 'matplotlib']:
    bar(y,7)  # increase width of bars
else:
    bar(y)

# draw a bar graph from a dicitonary:
figure()
data = {'method1': {'thing1': 3, 'thing2': 2, 'thing3': 4},
        'method2': {'thing1': 4, 'thing2': 4.5, 'thing3': 2},
        'method3': {'thing1': 1, 'thing2': 4, 'thing3': 2},}
bar(data, rotated_barticks=True,
    hardcopy='bar1a.eps', color=True,
    ymin=0, ymax=5)

# red bars with borders turned off:
figure()
bar(rand(5,4),'r',shading='interp')

# specify face and edge color:
figure()
bar(rand(3,3),facecolor='b',edgecolor='r')

raw_input('Press Return key to quit: ')
