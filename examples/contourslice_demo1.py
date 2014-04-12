#!/usr/bin/env python

# Example taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/contourslice.html

from scitools.easyviz import *
from time import sleep

setp(show=False)
x, y, z, v = flow()
h = contourslice(x,y,z,v,seq(1,9),[],[0],linspace(-8,2,10))
axis([0,10,-3,3,-3,3])
daspect([1,1,1])
camva(24)
camproj('perspective')
campos([-3,-15,5])
ax = gca()
ax.setp(fgcolor=(1,1,1), bgcolor=(0,0,0))
box('on')
view(3) # because camva, camproj, and campos currently not working
setp(show=True)
show()

#hardcopy('tmp_contourslice1a.eps')
#hardcopy('tmp_contourslice1a.png')

figure()
# alternative syntax:
h = contourslice(x,y,z,v,seq(1,9),[],[0],linspace(-8,2,10),
                 axis=[0,10,-3,3,-3,3], daspect=[1,1,1],
                 camva=24, camproj='perspective', campos=[-3,-15,5], 
                 fgcolor=(1,1,1), bgcolor=(0,0,0),
                 box='on')

#hardcopy('tmp_contourslice1b.eps')
#hardcopy('tmp_contourslice1b.png')

#sleep(3)
raw_input('Press Return key to quit: ')
