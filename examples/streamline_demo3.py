#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.fr/access/helpdesk/help/techdoc/ref/streamparticles.html

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

setp(show=False)
sx, sy, sz = ndgrid([80]*36,seq(20,55,1),[5]*36)
sl = streamline(x,y,z,u,v,w,sx,sy,sz)
axis('tight')
view(30,30)
daspect([1,1,.125])
camproj('perspective')
camva(8)
box('on')
setp(show=True)
show()


figure()
# alternative syntax:
sl = streamline(x,y,z,u,v,w,sx,sy,sz,
                axis='tight',
                view=(30,30),
                daspect=[1,1,.125],
                camproj='perspective',
                camva=8,
                box='on')

raw_input('Press Return key to quit: ')

