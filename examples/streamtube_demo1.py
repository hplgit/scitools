#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/streamtube.html

from scitools.easyviz import *
from scipy import io

wind = io.loadmat('wind_matlab_v6.mat')
x = wind['x']
y = wind['y']
z = wind['z']
u = wind['u']
v = wind['v']
w = wind['w']

sx,sy,sz = ndgrid([80]*4,seq(20,50,10),seq(0,15,5),sparse=False)

setp(show=False)
streamtube(x,y,z,u,v,w,sx,sy,sz)
daspect([1,1,1])
view(3)
axis('tight')
shading('interp')
#camlight(); lighting('gouraud')
setp(show=True)
show()

figure()
# alternative syntax:
streamtube(x,y,z,u,v,w,sx,sy,sz,
           daspect=[1,1,1],
           view=3,
           axis='tight',
           shading='interp')

raw_input('Press Return key to quit: ')

#hardcopy('tmp_streamtube1.eps')
#hardcopy('tmp_streamtube1.png')
