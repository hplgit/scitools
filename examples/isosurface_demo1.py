#!/usr/bin/env python

# Examples taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/isosurface.html and
# http://www.mathworks.com/access/helpdesk/help/techdoc/visualize/f5-3653.html

from scitools.easyviz import *
from time import sleep

setp(interactive=False)

x, y, z, v = flow()

h = isosurface(x,y,z,v,-3)
#setp(h,'FaceColor','red','EdgeColor','none');
h.setp(opacity=0.5)
shading('interp')
daspect([1,1,1])
view(3)
axis('tight')
#camlight()
#lighting('gouraud')
show()

#hardcopy('tmp_isosurf1a.eps')
#hardcopy('tmp_isosurf1a_lq.eps', vector_file=False)
#hardcopy('tmp_isosurf1a.png')

figure()
h = isosurface(x,y,z,v,0)
#setp(hpatch,'FaceColor','red','EdgeColor','none')
shading('interp')
daspect([1,4,4])
view([-65,20])
axis('tight')
#camlight('left')
#setp(gcf,'Renderer','zbuffer');
#lighting('phong')
show()
#sleep(3)
raw_input('Press Return key to quit: ')

#hardcopy('tmp_isosurf1b.eps')
#hardcopy('tmp_isosurf1b_lq.eps', vector_file=False)
#hardcopy('tmp_isosurf1b.png')
