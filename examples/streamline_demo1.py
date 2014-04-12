#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/streamline.html

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
sx,sy,sz = ndgrid([80]*4,seq(20,50,10),seq(0,15,5),sparse=False)
sl = streamline(x,y,z,u,v,w,sx,sy,sz)
sl.setp(linecolor='r')
view(3)
axis([60,140,10,60,-5,20])
setp(show=True)
show()


figure()
# alternative syntax:
sl = streamline(x,y,z,u,v,w,sx,sy,sz,
                linecolor='r',
                view=3,
                axis=[60,140,10,60,-5,20])


raw_input('Press Return key to quit: ')
