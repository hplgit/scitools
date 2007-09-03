#!/usr/bin/env python

from scitools.all import *
from numpy.random import rand

bar(rand(4,3))

figure()
x = seq(-2.9,2.9,0.2)
data = exp(-x*x)

if backend == 'gnuplot':
    bar(data,0.7)
else:
    bar(data)


figure()
g = get_backend()
h = bar(rand(3,2))
if backend == 'gnuplot':
    g('set xtics ("A" 1, "B" 2, "C" 3)')
    g.replot()

raw_input('press enter')
