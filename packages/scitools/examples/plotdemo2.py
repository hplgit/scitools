from scitools.all import *

x = seq(0, 15, 0.2)
y = sin(x)*x

# plot in batch (i.e., no plot on the screen, only make hardcopy):
plot(x, y, 'b-', legend='y', title='plot demo 2 (in batch)',
     show=False)
hardcopy('tmp1.ps')

# or
axis(ymin=-20,ymax=20)
plot(x, y, 'b-', legend='y', title='plot demo 2 (in batch)',
     show=False, hardcopy='tmp2.ps')



