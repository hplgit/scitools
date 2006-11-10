#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/streamribbon.html

from scitools.easyviz import *
from time import sleep
from scipy import io

wind = io.loadmat('wind_matlab_v6.mat')
x = wind['x']
y = wind['y']
z = wind['z']
u = wind['u']
v = wind['v']
w = wind['w']

set(show=False)
sx,sy,sz = meshgrid([80]*4,seq(20,50,10),seq(0,15,5),sparse=False)
streamribbon(x,y,z,u,v,w,sx,sy,sz,ribbonwidth=5)
view(3)
daspect([1,1,1])
axis('tight')
shading('interp')
#camlight(); lighting('gouraud')
set(show=True)
show()
sleep(3)

# alternative syntax:
streamribbon(x,y,z,u,v,w,sx,sy,sz,
             daspect=[1,1,1],
             view=3,
             axis='tight',
             shading='interp',
             camlight='right',
             lighting='gouraud')
sleep(3)
