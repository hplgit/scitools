from scitools.std import *

def f1(t):
    return t**2*exp(-t**2)

def f2(t):
    return t**2*f1(t)

t = linspace(0, 3, 51)
y1 = f1(t)
y2 = f2(t)

# Matlab-style syntax
plot(t, y1, 'r-')
hold('on')
plot(t, y2, 'bo')

axis([0, 4, -0.1, 0.7])
xlabel('t')
ylabel('y')
legend('t^2*exp(-t^2)', 't^4*exp(-t^2)', loc='upper left', fancybox=True)
title('Plotting two curves in the same plot')
savefig('plot2l.png')
savefig('plot2l.eps')
raw_input('Press Return key to quit: ')
