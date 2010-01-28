#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/visualize/f5-3796.html

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

# Determine the Range of the Coordinates:
xmin = arrmin(x)
xmax = arrmax(x)
ymax = arrmax(y)
zmin = arrmin(z)
ymax = ymax - 0.1
zmin = 0 # bug in slice_ and contourslice

setp(interactive=False)

# Add Slice Planes for Visual Context:
wind_speed = sqrt(u**2 + v**2 + w**2)
hsurfaces = slice_(x,y,z,wind_speed,[xmin,100,xmax],ymax,zmin)
#set(hsurfaces,'FaceColor','interp','EdgeColor','none')
hold('on')
shading('interp')

# Add Contour Lines to Slice Planes:
hcont = contourslice(x,y,z,wind_speed,[xmin,100,xmax],ymax,zmin,8)
# What is the default number of contour lines in contourslice? 8?
#set(hcont,'EdgeColor',[.7,.7,.7],'LineWidth',.5)
hcont.setp(linecolor=[.7,.7,.7], linewidth=2)

# Define the Starting Points for the Stream Lines:
sx,sy,sz = ndgrid([80]*4,seq(20,50,10),seq(0,15,5), sparse=False)
hlines = streamline(x,y,z,u,v,w,sx,sy,sz)
#set(hlines,'LineWidth',2,'Color','r')
hlines.setp(linewidth=3, linecolor='r')

# Define the View:
view(3)
daspect([2,2,1])
axis('tight')

show()

raw_input('Press Return key to quit: ')
