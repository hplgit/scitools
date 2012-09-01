#!/usr/bin/env python

"""
Example on how to work with references to objects and the setp command.
"""

from scitools.std import *

setp(interactive=False)

x = linspace(0,2*pi,51)

a1 = subplot(211)
l1 = plot(x,sin(x),'x')

a2 = subplot(212)
l2 = plot(x,cos(x)*sin(x))
show()

raw_input('Press Return key to continue')

setp(a1,box='off',grid='on')
setp(l1,linemarker='<')
show()

raw_input('Press Return key to continue')

setp(a2,xmin=pi/2,xmax=2*pi)
setp(a2,fontsize=12)
setp(a2,log='x')
setp(l2,linewidth=4,linecolor='g')
show()

raw_input('Press Return key to quit')
