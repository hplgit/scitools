from scitools.std import *
import time

xv, yv = ndgrid(linspace(-2,2,41),linspace(-1,1,41))
for n, t in enumerate(linspace(0, 4, 21)):
    values = exp(-0.2*t)*exp(-(2*(xv-t+1)**2 + 10*yv**2))
    surf(xv, yv, values, colormap=hot(24), colorbar='on',
         savefig='tmp_%03d.png' % n,
         zlim=[0,1], caxis=[0, 1])

# Note: this demo is very slow in matplotlib (3D)
raw_input()


