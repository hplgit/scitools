from scitools.std import *   # for curve plotting

def f(t):
    return t**2*exp(-t**2)

t = linspace(0, 3, 31)    # 31 points between 0 and 3
y = zeros(len(t), 'd')    # 31 doubles ('d')
for i in xrange(len(t)):
    y[i] = f(t[i])

plot(t, y)
savefig('plot1a.png')
savefig('plot1a.eps')
show()
raw_input('Press Return key to quit: ')
