#!/usr/bin/env python

"""
Shows several ways of how one can create a movie file from a series of
images by using the movie function in scitools.easyviz.
"""

from scitools.std import *
import os, time, glob

x = seq(0, 15, 0.1)

def f(x, t):
    return exp(-0.1*t)*exp(-(x-t)**2)

def f2(x, t):
    return exp(-(x-t)**2)

dt = 0.1    # time step
tstop = 3   # end time

# make hardcopy of the animation:
# (first clean up old tmp_*.png and tmp_*.eps files)
for file in glob.glob('tmp_*.png') + glob.glob('tmp_*.eps'):
    os.remove(file)

t = 0
dt = 0.25
xtop = []; ytop = []
frame_counter = 0
files = []
while t <= tstop:
    y = f(x, t)
    y2 = f2(x, t)
    xtop.append(t)  # top point corresponds to x=t
    ytop.append(f(t,t))
    filename = 'tmp_%04d.eps' % frame_counter
    files.append(filename)
    frame_counter += 1
    plot(x, y, 'r-', x, y2, 'b-', xtop, ytop, 'y--',
         axis=[0, 15, -0.1, 1.1], show=False)
    hardcopy(filename)
    print 't=%s' % t
    t += dt
    if backend == 'matlab':
        close()
    elif backend == 'gnuplot':
        time.sleep(0.1)
# make a sample file with numbers for testing in verify.sh:
f = open('tmp.dat', 'w')
for yi in y:
    f.write('%.12f\n' % yi)
f.close()

