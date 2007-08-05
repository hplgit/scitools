#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/streamtube.html

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

sx,sy,sz = meshgrid([80]*4,seq(20,50,10),seq(0,15,5),sparse=False)

setp(show=False)
streamtube(x,y,z,u,v,w,sx,sy,sz)
daspect([1,1,1])
view(3)
axis('tight')
shading('interp')
#camlight(); lighting('gouraud')
setp(show=True)
show()
#sleep(3)

figure()
# alternative syntax:
streamtube(x,y,z,u,v,w,sx,sy,sz,
           daspect=[1,1,1],
           view=3,
           axis='tight',
           shading='interp')
#sleep(3)
raw_input('press enter')

#hardcopy('tmp_streamtube1.eps')
#hardcopy('tmp_streamtube1.png')
