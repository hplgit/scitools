from scitools.all import *
from time import sleep

x = seq(0, 15, 0.1)

def f(x, t):
    return exp(-0.1*t)*exp(-(x-t)**2)

dt = 0.1    # time step
tstop = 15  # end time
# animation requires axis keyword in plot command, not separate axis
# function call

t = 0
while t <= tstop:
    y = f(x, t)
    plot(x, y, axis=[0, 15, -0.1, 1.1])
    t += dt
    sleep(0.2) # control speed

# animate two curves
def f2(x, t):
    return exp(-(x-t)**2)

t = 0
while t <= tstop:
    y = f(x, t)
    y2 = f2(x, t)
    plot(x, y, 'r-', x, y2, 'b-', axis=[0, 15, -0.1, 1.1])
    t += dt

# draw a line for the top of the f curve:
t = 0
xtop = []; ytop = []
while t <= tstop:
    y = f(x, t)
    y2 = f2(x, t)
    xtop.append(t)  # top point corresponds to x=t
    ytop.append(f(t,t))
    plot(x, y, 'r-', x, y2, 'b-', xtop, ytop, 'y--', axis=[0, 15, -0.1, 1.1])
    t += dt

# make hardcopy of the animation:
# (first clean up old tmp_*.ps files)
import os, glob
for file in glob.glob('tmp_*.ps'): os.remove(file)
t = 0
dt = 0.25
frame_counter = 0
while t <= tstop:
    y = f(x, t)
    y2 = f2(x, t)
    filename = 'tmp_%04d.ps' % frame_counter
    frame_counter += 1
    plot(x, y, 'r-', x, y2, 'b-', hardcopy=filename, axis=[0, 15, -0.1, 1.1])
    t += dt

cmd1 = 'ps2mpeg.py tmp_*.ps tmp.mpeg'
print 'make MPEG move:\n', cmd1
cmd2 = 'convert -delay 20 tmp_0*.ps tmp.gif'
print 'make animated GIF file:\n', cmd2
#os.system(cmd1)
#os.system(cmd2)


