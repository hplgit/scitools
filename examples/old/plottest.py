from scitools import *
from scitools.easyviz.gnuplot_ import *
from time import sleep
x = seq(0, 15, 0.2)
y = sin(x)*x
v = sin(x)*sqrt(x)
w = sin(x)*x**0.33333333

plot(x, y, 'r-', x, v, 'b-', x, w, 'g-',
     legend=('sin(x)*x', 'sin(x)*sqrt(x)', 'sin(x)*x**0.33333333'),
     title='An easyviz demo', xlabel='X', ylabel='Y')
"""
plot(x, y, 'r-')
hold('on')
#plot(x, v)
plot(x, v, 'b-o')
legend('sin(x)*x', 'sin(x)*sqrt(x)', 'sin(x)*x**0.33333333')
title('An easyviz demo')
xlabel('x coordinate'); ylabel('function value')
plot(x, w, 'g-')
"""
