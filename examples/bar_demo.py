#!/usr/bin/env python

from scitools.std import *
from numpy.random import rand, seed
seed(12)  # fix to ensure same results each time this program is run

# simple example:
data = rand(4,3)
print data
bar(data)
title('Bars from a matrix: 4 groups of 3 bars each')
# alternative:
figure()
bar(data,
    barticks=['group 1', 'group 2', 'group 3', 'group 4'],
    legend=['bar 1', 'bar 2', 'bar 3'],
    axis=[-1, data.shape[0], 0, 1.3],
    ylabel='Normalized CPU time',
    title='Bars from a matrix, now with more annotations')


# example with a vector:
figure()
x = linspace(-3,3,15)
y = exp(-x**2)
if backend in ['gnuplot', 'matplotlib']:
    w = 7   # increase width of bars
else:
    w = 0.8 # default
bar(y, width=w)
title('Bars at 15 points for the exp(-x**2) functions')

# draw a bar graph from a dicitonary:
figure()
data = {'method1': {'thing1': 3, 'thing2': 2, 'thing3': 4},
        'method2': {'thing1': 4, 'thing2': 4.5, 'thing3': 2},
        'method3': {'thing1': 1, 'thing2': 4, 'thing3': 2},}
bar(data,
    rotated_barticks=True,
    hardcopy='tmp_bar1a.eps', color=True,
    ylabel='response',
    axis=[-1, len(data), 0, 5],
    title='Bars from nested dictionary')

# red bars with borders turned off:
figure()
bar(rand(5,4), 'r', shading='interp',
    title='Red bars with borders turned off')

# specify face and edge color:
figure()
bar(rand(3,3), facecolor='b', edgecolor='r',
    title='Bars with specified face and edge colors')

raw_input('Press Return key to quit: ')
