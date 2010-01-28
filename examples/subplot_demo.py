#!/usr/bin/env python

from scitools.std import *

setp(interactive=False)

x = linspace(-5,5,201)
subplot(2,2,1)
plot(x, x-sin(pi*x), xlabel='x', ylabel='y', title='subplot(2,2,1)')
subplot(2,2,2)
plot(x, x-cos(x**2), xlabel='x', ylabel='y', title='subplot(2,2,2)')
subplot(2,2,3)
plot(cos(3*pi*x), cos(0.5*pi*x), x=x, grid='on', axis=[-3,3,-3,3],
     xlabel='x', ylabel='y', title='subplot(2,2,3)')
subplot(2,2,4)
plot(x, cos(pi*x), xlabel='x', ylabel='y', title='subplot(2,2,4)')
show()

#hardcopy('subplot1a.eps', color=True)
#hardcopy('subplot1a.png', color=True)

figure()
t = linspace(0,1,51)
y1 = sin(2*pi*t)
y2 = cos(2*pi*3*t)
subplot(2,1,1)
plot(t, y1, 'ro-')
hold('on')
plot(t, y2, 'b--')
title('This is the title')
ylabel('voltage (mV)')
axis([0, 1, -1.5, 1.5])

subplot(2,1,2)
plot(t, y1+y2, 'm:')
axis([0, 1, -3, 3])
grid('on')
xlabel('time (sec)')
ylabel('voltage (mV)')
show()

#hardcopy('subplot1b.eps', color=True)
#hardcopy('subplot1b.png', color=True)

raw_input("Press Return key to quit: ")

