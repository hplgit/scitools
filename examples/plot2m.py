"""Test LaTeX syntax in legends and titles."""
from scitools.std import *

def f1(t):
    return t**2*exp(-t**2)

def f2(t):
    return t**2*f1(t)

t = linspace(0, 3, 51)
y1 = f1(t)
y2 = f2(t)

plot(t, y1, 'r-', legend='t**2*exp(-t**2)',
     title='Testing legend with double mult for power')
savefig('tmp1.eps')
raw_input('Press Return key to quit: ')
import sys; sys.exit(0)
savefig('tmp1.eps')
savefig('tmp1.png')

figure()
plot(t, y1, 'r-', legend='t^2*exp(-t^2)',
     title='Testing legend with hat for power')
savefig('tmp2.eps')
savefig('tmp2.png')

figure()
plot(t, y1, 'r-.',
     t, y2, 'b--',
     legend=(r'$t^2\exp{(-t^2)}$', r'$t^4\exp{(-t^2)}$'),
     title=r'Testing real LaTeX syntax w/dollars: $\alpha$, $\beta + \Omega$')
savefig('tmp3.eps')
savefig('tmp3.png')

figure()
plot(t, y1, 'r-.',
     t, y2, 'b--',
     legend=(r't^2\exp{(-t^2)}', r't^4\exp{(-t^2)}'),
     title=r'Testing real LaTeX syntax (no dollars): \alpha, \beta + \Omega')
savefig('tmp4.eps')
savefig('tmp4.png')

raw_input('Press Return key to quit: ')
