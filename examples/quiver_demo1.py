#!/usr/bin/env python

"""
Demonstration of the quiver command.
"""

from scitools.std import *

setp(interactive=False)

# Plot the vector field F(x,y)=(-y,x):
xv, yv = ndgrid(linspace(-1,1,11),linspace(-1,1,11),sparse=False)
quiver(xv,yv,-yv,xv,3) 
axis('equal')
axis([-1,1,-1,1])
title('The vector field F(x,y)=(-y,x)')
show()

#hardcopy('quiver1a.eps', color=True)
#hardcopy('quiver1a.png', color=True)

figure()
# Now, turn off automatic scaling:
quiver(xv,yv,-yv,xv,0,axis=[-1,1,-1,1])
show()

#hardcopy('quiver1b.eps', color=True)
#hardcopy('quiver1b.png', color=True)

figure()
# Plot the gradient field of the function f(x,y)=x**3-3x-2y**2:
xv, yv = ndgrid(linspace(-2,2,21),linspace(-1,1,11),sparse=False)
values = xv**3 - 3*xv - 2*yv**2
dx, dy = gradient(values,.2,.1)
quiver(xv,yv,dx,dy,axis='equal',xmin=-2,xmax=2,ymin=-1,ymax=1,
       title='The gradient vector field of f(x,y)=x**3-3x-2y**2')
show()

#hardcopy('quiver1c.eps', color=True)
#hardcopy('quiver1c.png', color=True)

raw_input('Press Return key to quit: ')
