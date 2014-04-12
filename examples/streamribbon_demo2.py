#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/streamribbon.html

from scitools.easyviz import *
from time import sleep

xmin = -7; xmax = 7
ymin = -7; ymax = 7 
zmin = -7; zmax = 7 
x = linspace(xmin,xmax,30)
y = linspace(ymin,ymax,20)
z = linspace(zmin,zmax,20)
x,y,z = ndgrid(x,y,z,sparse=False)
u = y; v = -x; w = 0*x+1

setp(interactive=False)
hold('on')
daspect([1,1,1])
#cx,cy,cz = ndgrid(linspace(xmin,xmax,30),linspace(ymin,ymax,30),[-3,4])
#h2=coneplot(x,y,z,u,v,w,cx,cy,cz, 'q')
#set(h2, 'color', 'k');

# plot two sets of streamribbons:
sx,sy,sz = ndgrid([-1,0,1],[-1,0,1],[-6]*3,sparse=False)
p = streamribbon(x,y,z,u,v,w,sx,sy,sz)
sx,sy,sz = ndgrid(seq(1,6),zeros(6,float),[-6]*6,sparse=False)
p2 = streamribbon(x,y,z,u,v,w,sx,sy,sz)

# define viewing and lighting:
shading('interp')
view(-30,10); axis('off'); axis('tight')
camproj('perspective'); camva(66); camlookat()
camdolly(0,0,.5)
#camlight()

show()

raw_input('Press Return key to quit: ')
