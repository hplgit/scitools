from scitools.all import *
from time import sleep
backend = get_backend()
if backend == 'blt_':
    set(interactive=True, color=True)

x = seq(0, 15, 0.2)
y = sin(x)*x
v = sin(x)*sqrt(x)
w = sin(x)*x**0.33333333

plot(x, y, 'b-')
hold('on')
plot(x, v, 'r-')
plot(x, w, 'y-')
plot([0,15],[0,15])
plot([0,15],[0,-15])
sleep(3)

# add legend and title:
legend('y curve', 'v curve', 'w curve', '', '')
title('plot demo 3')
show()

sleep(3)

hold('off')  # do not add the next curves

# alternative syntax:
plot(x, y, 'r-', x, v, 'b--', x, w, 'g--',
     legend=('sin(x)*x', 'sin(x)*sqrt(x)', 'sin(x)*x**(1/3)'),
     title='plot demo 3', xlabel='X', ylabel='Y',
     axis=(0, 15, -15, 25))
sleep(3)

# test default lines:
axis(ymin=-15, ymax=25)
plot(x, y, x, v, x, w, 
     legend=('sin(x)*x', 'sin(x)*sqrt(x)', 'sin(x)*x**(1/3)'),
     title='default lines styles', xlabel='X', ylabel='Y')
sleep(3)

plot(x, y, 'b-')



