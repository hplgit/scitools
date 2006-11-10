#!/usr/bin/env python

# Examples taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/isosurface.html and
# http://www.mathworks.com/access/helpdesk/help/techdoc/visualize/f5-3653.html

from scitools.easyviz import *
from time import sleep

x, y, z, v = flow()

set(show=False)
h = isosurface(x,y,z,v,-3)
#set(h,'FaceColor','red','EdgeColor','none');
h.set(opacity=0.5)
shading('interp')
daspect([1,1,1])
view(3)
axis('tight')
#camlight()
#lighting('gouraud')
set(show=True)
show()
sleep(3)

set(show=False)
h = isosurface(x,y,z,v,0)
#set(hpatch,'FaceColor','red','EdgeColor','none')
shading('interp')
daspect([1,4,4])
view([-65,20])
axis('tight')
#camlight('left')
#set(gcf,'Renderer','zbuffer');
#lighting('phong')
set(show=True)
show()
sleep(3)
