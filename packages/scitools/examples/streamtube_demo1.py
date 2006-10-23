#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.fr/access/helpdesk/help/techdoc/ref/streamline.html

import os
os.environ['EASYVIZ_BACKEND'] = 'vtk_'

from time import sleep
from scitools.easyviz import *
from scipy import io

wind = io.loadmat('wind_matlab_v6.mat')
x = wind['x']
y = wind['y']
z = wind['z']
u = wind['u']
v = wind['v']
w = wind['w']

sx,sy,sz = meshgrid([80]*4,seq(20,50,10),seq(0,15,5),sparse=False)

set(show=False)
streamtube(x,y,z,u,v,w,sx,sy,sz)
view(3)
axis([60,140,10,60,-5,20])
shading('interp')
#camlight(); lighting('gouraud')
set(show=True)
show()
sleep(3)

# alternative syntax:
streamtube(x,y,z,u,v,w,sx,sy,sz,view=3,axis=[60,140,10,60,-5,20])
sleep(3)
