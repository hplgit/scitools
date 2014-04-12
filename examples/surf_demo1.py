#!/usr/bin/env python

"""Demonstration on how to use the surf command."""

from scitools.std import *

xv, yv = ndgrid(linspace(-2,2,21),linspace(-1,1,11))
values = xv**2*yv-2*yv
setp(show=False)
subplot(221);  surf(values)
subplot(222);  surf(xv,yv,values,shading='flat')
subplot(223);  surf(values,shading='interp')
subplot(224);  surfc(values,clevels=10)  # add contours beneath the surface
setp(show=True)
show()

#hardcopy('surf1a.eps')
#hardcopy('surf1a.png')

figure()
# Create a surface plot of a sphere:
n = 32
theta = pi*linspace(-n,n,n)/n
theta = reshape(theta, (n,1))
phi = (pi/2)*linspace(-n,n,n)/n
phi = reshape(phi, (1,n))
x = cos(phi)*cos(theta)
y = cos(phi)*sin(theta)
z = sin(phi)*ones(shape(theta))
surf(x,y,z,axis='equal')

#hardcopy('surf1b.eps')
#hardcopy('surf1b.png')

figure()
xv, yv = ndgrid(linspace(-2,2,41),linspace(-2,2,41))
values = xv*exp(-xv**2-yv**2)
dx, dy = gradient(values)
c = dx + dy
surf(xv,yv,values,c,colorbar='on',axis=[-2,2,-2,2,-0.5,0.5])

#hardcopy('surf1c.eps')
#hardcopy('surf1c.png')

figure()
xv, yv = ndgrid(seq(-2.5,2.5,0.15),seq(-5,5,0.15))
values = 70*yv**2*exp(-xv**2-0.2*yv**2)
surf(xv,yv,values)

#hardcopy('surf1d.eps')
#hardcopy('surf1d.png')

raw_input('Press Return key to quit: ')
