from scitools.std import *   # for curve plotting

def f(t):
    return exp(-t**2)

t = linspace(0, 3, 51)    # 51 points between 0 and 3
y = f(t)
semilogy(t, y, 'r-2')

xlabel('t')
ylabel('y')
legend('exp(-t^2)')
title('Logarithmic scale on the y axis')
savefig('plot1d.eps')
savefig('plot1d.png')
raw_input('Press Return key to quit: ')
