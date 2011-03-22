#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/slice.html

from scitools.easyviz import *
from time import sleep

BUG = 0.0001 # bug somewhere in _add_slice in vtk_.py
x,y,z = ndgrid(seq(-2,2,.2),seq(-2,2,.25),seq(-2,2,.16),sparse=True)
v = x*exp(-x**2-y**2-z**2)
xslice = [-1.2,.8,2-BUG]
yslice = 2
zslice = [-2+BUG,0]
slice_(x,y,z,v,xslice,yslice,zslice,grid='off')

#hardcopy('tmp_slice1.eps')
#hardcopy('tmp_slice1.png')

raw_input('Press Return key to quit: ')
