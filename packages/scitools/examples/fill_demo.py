#!/usr/bin/env python

"""Examples taken from fill_demo.py and fill_demo2.py in Matplotlib."""

from scitools.all import *

t = linspace(0.0, 1.0, 101)
s = sin(2*2*pi*t)

fill(t, s*exp(-5*t), 'r', grid=True)

figure()
t = linspace(0.0,3.0,301)
s = sin(2*pi*t)
c = sin(4*pi*t)
fill(t, s, 'b', t, c, 'g', opacity=0.2)

raw_input('press enter')

