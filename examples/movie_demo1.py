from scitools.std import *
import time, glob, os

# clean up old frames:
for name in glob.glob('tmp_*.eps'):
    os.remove(name)

def f(x, m, s):
    return (1.0/(sqrt(2*pi)*s))*exp(-0.5*((x-m)/s)**2)

m = 0
s_start = 2
s_stop = 0.2
s_values = linspace(s_start, s_stop, 30)
x = linspace(m -3*s_start, m + 3*s_start, 1000)
# f is max for x=m; smaller s gives larger max value
max_f = f(m, m, s_stop)

# show the movie, and make hardcopies of frames simulatenously:
counter = 0
for s in s_values:
    y = f(x, m, s)
    plot(x, y, axis=[x[0], x[-1], -0.1, max_f],
         xlabel='x', ylabel='f', legend='s=%4.2f' % s,
         hardcopy='tmp_%04d.png' % counter)
    counter += 1
    #time.sleep(0.2)  # can insert a pause to control movie speed

# make movie file the simplest possible way:
movie('tmp_*.png')
import glob, os
print 'generated the file', glob.glob('movie.*')[0]
#os.remove(glob.glob('movie.*')[0])

# make animated GIF movie in the file tmpmovie.gif:
movie('tmp_*.png', encoder='convert', fps=2,
      output_file='tmpmovie.gif')

# show movie (os.system runs an operating system command):
os.system('animate tmpmovie.gif &')

# make MPEG movie:
movie('tmp_*.png', encoder='mpeg_encode', fps=24,
      output_file='tmpmovie1.mpeg',
      vcodec='mpeg2video', vbitrate=2400, qscale=4)

# requires netpbm package:
movie('tmp_*.png', encoder='ppmtompeg', fps=24,
      output_file='tmpmovie2.mpeg')

# requires ffmpeg package:
movie('tmp_*.png', encoder='ffmpeg', fps=4,
      output_file='tmpmovie3.mpeg')

