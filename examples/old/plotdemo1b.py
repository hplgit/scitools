from scitools.std import *

x = seq(0, 15, 0.2)
y1 = sin(x)*x
y2 = sin(x)*sqrt(x)

plot(x, y1, 'b-', x, y2, 'ro', legend='x*sin(x)', title='plot demo 2',
     axis=(0, 15, -25, 25), xlabel='X', ylabel='Y')

hardcopy('tmp1.ps')



