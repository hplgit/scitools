"""Test text in plot."""
from scitools.std import *

def f1(t):
    return t**2*exp(-t**2)

def f2(t):
    return t**2*f1(t)

t = linspace(0, 3, 51)
y1 = f1(t)
y2 = f2(t)

plot(t, y1, 'r-', legend='t**2*exp(-t**2)')
text(1.5, 0.3, 'A text')
savefig('tmp1.eps')

raw_input('Press Return key to quit: ')
