#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/contourslice.html

import os
os.environ['EASYVIZ_BACKEND'] = 'vtk_'

from time import sleep
from scitools.easyviz import *
from scitools import linspace

set(show=False)
x, y, z, v = flow()
h = contourslice(x,y,z,v,seq(1,9),[],[0],linspace(-8,2,10))
axis([0,10,-3,3,-3,3])
daspect([1,1,1])
camva(24)
camproj('perspective')
campos([-3,-15,5])
ax = gca()
ax.set(fgcolor=(1,1,1), bgcolor=(0,0,0))
box('on')
view(3) # because camva, camproj, and campos currently not working
set(show=True)
show()
sleep(3)

# alternative syntax:
h = contourslice(x,y,z,v,seq(1,9),[],[0],linspace(-8,2,10),
                 axis=[0,10,-3,3,-3,3], daspect=[1,1,1],
                 camva=24, camproj='perspective', campos=[-3,-15,5], 
                 fgcolor=(1,1,1), bgcolor=(0,0,0),
                 box='on')
sleep(3)
