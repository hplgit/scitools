from scitools import *
from scitools.easyviz.gnuplot_ import *

def pic(fname):
    #os.system('import %s' % fname)
    pass
    

x = seq(-3, 3, 0.05)
y = exp(-x**2)*cos(pi*x)

plot(x, y)

# wait 3 seconds before we update the plot on the screen
# (enabled by the sleep(3) command)
from time import sleep
sleep(3)
pic('plot11.ps')

# specify a blue line:
plot(x, y, 'b-')
sleep(3)
pic('plot12.ps')

# specify a red line with circles at each coordinate point in x and y:
plot(x, y, 'r-o')
sleep(3)
pic('plot13.ps')

# specify a red circles at the coordinates only:
plot(x, y, 'ro')
sleep(3)
pic('plot14.ps')


# add legend, title, axis ranges, and axis labels:
plot(x, y, 'b-')
legend('exp(-x**2)*cos(pi*x)')
title('plot demo 1')
axis(-2.5, 2.5, -1.2, 1.2)
show()
sleep(3)
pic('plot15.ps')

xlabel('x values')
ylabel('y values')
show()
sleep(3)
pic('plot16.ps')

# alternative syntax:
plot(x, y, 'b-', legend='x*sin(x)', title='plot demo 2',
     axis=(-2.5, 2.5, -1.2, 1.2), xlabel='X', ylabel='Y')

hardcopy('tmp1.ps')



