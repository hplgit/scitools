#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.fr/access/helpdesk/help/techdoc/visualize/f5-3558.html

import os
os.environ['EASYVIZ_BACKEND'] = 'vtk_'

from time import sleep
from scitools.easyviz import *

BUG = 0.0001 # bug somewhere in _add_slice in vtk_.py
x,y,z = meshgrid(seq(-2,2,.2),seq(-2,2,.25),seq(-2,2,.16),sparse=True)
v = x*exp(-x**2-y**2-z**2)
xslice = [-1.2,.8,2-BUG]
yslice = 2
zslice = [-2+BUG,0]
slice_(x,y,z,v,xslice,yslice,zslice,
       colormap=hsv(),grid='off')
sleep(3)
