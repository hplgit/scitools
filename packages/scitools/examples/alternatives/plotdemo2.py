from scitools import *
from scitools.easyviz.gnuplot_ import *

x = seq(-3, 3, 0.05)
y = exp(-x**2)*cos(pi*x)

# plot in batch (i.e., no plot on the screen, only make hardcopy):
plot(x, y, 'b-', legend='y', title='plot demo 2 (in batch)',
     show=False)
hardcopy('tmp1.ps')

# or
axis(ymin=-1.2, ymax=1.2)
plot(x, y, 'b-', legend='y', title='plot demo 2 (in batch)',
     show=False, hardcopy='tmp2.ps')



