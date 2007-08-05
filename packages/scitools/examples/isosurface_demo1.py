#!/usr/bin/env python

# Examples taken from:
# http://www.mathworks.com/access/helpdesk/help/techdoc/ref/isosurface.html and
# http://www.mathworks.com/access/helpdesk/help/techdoc/visualize/f5-3653.html

from scitools.easyviz import *
from time import sleep

x, y, z, v = flow()

setp(show=False)
h = isosurface(x,y,z,v,-3)
#setp(h,'FaceColor','red','EdgeColor','none');
h.setp(opacity=0.5)
shading('interp')
daspect([1,1,1])
view(3)
axis('tight')
#camlight()
#lighting('gouraud')
setp(show=True)
show()

#hardcopy('tmp_isosurf1.eps')
#hardcopy('tmp_isosurf1_lq.eps', vector_file=False)
#hardcopy('tmp_isosurf1.png')

figure()
setp(show=False)
h = isosurface(x,y,z,v,0)
#setp(hpatch,'FaceColor','red','EdgeColor','none')
shading('interp')
daspect([1,4,4])
view([-65,20])
axis('tight')
#camlight('left')
#setp(gcf,'Renderer','zbuffer');
#lighting('phong')
setp(show=True)
show()
#sleep(3)
raw_input('press enter')

#hardcopy('tmp_isosurf2.eps')
#hardcopy('tmp_isosurf2_lq.eps', vector_file=False)
#hardcopy('tmp_isosurf2.png')
