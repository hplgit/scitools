from scitools.std import *
# Clean up tmp_*.eps files:
import glob, os
for name in glob.glob('tmp_*.png'):
    os.remove(name)
# Clean up movie files
for name in glob.glob('tmpmovie*.*'):
    os.remove(name)

def f(x, t):
    return exp(-(x-3*t)**2)*sin(3*pi*(x-t))

xmax = 6
x = linspace(-xmax, xmax, 1001)


t_values = linspace(-1, 1, 61)
counter = 1
for t in t_values:
    y = f(x, t)
    plot(x, y, hardcopy='tmp_%04d.png' % counter)
    counter += 1

# Make movie file the simplest possible way
movie('tmp_*.png')
import glob, os
print 'generated the file', glob.glob('movie.*')[0]
#os.remove(glob.glob('movie.*')[0])

# Make animated GIF movie in the file tmpmovie.gif
movie('tmp_*.png', encoder='convert', fps=2,
      output_file='tmpmovie.gif')

# Show movie (os.system runs an operating system command)
os.system('animate tmpmovie.gif &')

# Other formats
movie('tmp_*.png', encoder='html', fps=3,
      output_file='tmpmovie.html')  # play in HTML file

movie('tmp_*.png', encoder='ppmtompeg', fps=24,
      output_file='tmpmovie1.mpeg') # requires netpbm package

movie('tmp_*.png', encoder='ffmpeg', fps=4,
      output_file='tmpmovie1b.mpeg') # requires ffmpeg package

movie('tmp_*.png', encoder='ffmpeg', fps=4,
      output_file='tmpmovie1.avi') # requires ffmpeg package

movie('tmp_*.png', encoder='ffmpeg',
      output_file='tmpmovie1c.mpeg', vodec='mpeg2video')
