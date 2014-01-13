"""Plot rows of a matrix object."""
from scitools.std import *

m = mat([[1,2,5], [3,-1,0], [4, 5, 5]])
x = range(m.shape[0])
for i in range(m.shape[0]):
    y = m[i,:]
    plot(x, array(y), 'r-', legend='row %d' % i)
    hold('on')
title('Plot of the rows of a matrix object')
plot([1,3,5],[4,4,4],'b-')
hardcopy('tmp5.eps')
raw_input('Press Return key to quit: ')

