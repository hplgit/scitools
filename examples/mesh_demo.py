#!/usr/bin/env python

from scitools.std import *

from numpy import MachAr
eps = MachAr().eps

mesh(peaks())
title('Wireframe mesh of the peaks function')

#hardcopy('mesh1a.eps', color=True)
#hardcopy('mesh1a.png', color=True)

figure()
x = linspace(-8,8,51)
xv, yv = ndgrid(x,x)
r = sqrt(xv**2 + yv**2) + eps
values = sin(r)/r
mesh(xv, yv, values, xlabel='x', ylabel='y', zlabel='z',
     title='f(x,y)=sqrt(x**2+y**2)/(x**2+y**2)')

#hardcopy('mesh1b.eps', color=True)
#hardcopy('mesh1b.png', color=True)

figure()
x = y = linspace(0,pi,32)
xv, yv = ndgrid(x,y)
values = sin(yv**2 + xv) - cos(yv - xv**2)
setp(interactive=False)
subplot(221);  mesh(values);
subplot(222);  mesh(x, y, values, hidden='off')
subplot(223);  mesh(xv, yv, values)
subplot(224);  meshc(values)  # contour lines beneath the mesh
show()

#hardcopy('mesh1c.eps', color=True)
#hardcopy('mesh1c.png', color=True)

raw_input('Press Return key to quit: ')
