from scitools.std import *   # for curve plotting

def f(t):
    return exp(-t**2)

t = linspace(0, 3, 51)    # 51 points between 0 and 3
y = f(t)
plot(t, y, 'r-2',
     log='y',
     xlabel='t',
     ylabel='y',
     legend='exp(-t^2)',
     title='Logarithmic scale on the y axis',
     savefig='plot1e.png',  # or hardcopy='plot1e.eps'
     show=True)

savefig('plot1e.eps')

raw_input('Press Return key to quit: ')
