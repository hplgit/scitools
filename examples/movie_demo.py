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
tstop = 15  # end time

# make hardcopy of the animation:
# (first clean up old tmp_*.png files)
for file in glob.glob('tmp_*.png'):
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
    filename = 'tmp_%04d.png' % frame_counter
    files.append(filename)
    frame_counter += 1
    plot(x, y, 'r-', x, y2, 'b-', xtop, ytop, 'y--',
         axis=[0, 15, -0.1, 1.1])
    hardcopy(filename, color=True, renderer='painters')
    print 't=%s' % t
    t += dt
    if backend == 'matlab':
        close()
    elif backend == 'gnuplot':
        time.sleep(0.1)

# First we create an animated gif file using convert as the encoding tool:
movie('tmp_*.png', encoder='convert', output_file='movie.gif')

# Now we create an mpeg file using the mpeg_encode tool:
files = glob.glob('tmp_*.png')
files.sort()  # this might not be necessary
movie(files, encoder='mpeg_encode', output_file='movie.mpeg')

# This last example shows how to create an mpeg4 file using MEncoder:
movie('tmp_%04d.png',
      encoder='mencoder',
      vcodec='mpeg4',
      vbitrate=2400,
      qscale=1,
      output_file='movie.avi',
      fps=10)
