#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.fr/access/helpdesk/help/techdoc/ref/streamparticles.html

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

set(show=False)
sx, sy, sz = meshgrid([80]*36,seq(20,55,1),[5]*36)
sl = streamline(x,y,z,u,v,w,sx,sy,sz)
axis('tight')
view(30,30)
daspect([1,1,.125])
camproj('perspective')
camva(8)
box('on')
set(show=True)
show()
sleep(3)

# alternative syntax:
sl = streamline(x,y,z,u,v,w,sx,sy,sz,
                axis='tight',
                view=(30,30),
                daspect=[1,1,.125],
                camproj='perspective',
                camva=8,
                box='on')
sleep(3)

