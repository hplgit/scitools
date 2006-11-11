"""
Easyviz
=======

Easyviz is a light-weight interface to visualization engines for
scientific data. The Easyviz interface is written in Python with the
purpose of making it very easy to visualize data in Python
scripts. Both curve plots and more advanced 2D/3D visualization of
scalar and vector fields are supported.  The Easyviz interface was
designed with three ideas in mind: 1) Simple, Matlab-like syntax,
2) a unified interface to lots of visualization engines
(called backends later): Gnuplot, Vtk, Matlab, Matplotlib, PyX, etc.,
and 3) the interface is minimalistic and offers only basic control of plots
(fine-tuning is done by programming in the specific backend directly).

*First principle*: Array data can be plotted with a minimal
set of keystrokes using a Matlab-like syntax. A simple::

  plot(x,y) 

plots the data in (the NumPy array) y versus the data in (the NumPy
array) x. If you need legends, control of the axis, as well as an
additional curve, this is obtained by the standard Matlab-style commands::

  legend('first curve')
  axis(0, 10, -1, 1)
  hold('on')
  plot(x, y2, 'ro-')
  legend('second curve')
  title('My first easyplot demo')
  hardcopy('tmp.ps')   # save figure in file tmp.ps

One may also use a more convenient compound plot command to achieve
the same result::

  plot(x, y, '', x, y2, 'ro--', legend=('first curve',
       'second curve'), title='My first easyplot demo',
       hardcopy='tmp.ps')

Similarly, a two-dimensional scalar function f(x,y) may be visualized
as an elevated surface with colors using these commands::

  x = seq(0, 10, 0.1)      # coordinates from 0 to 10, step 0.1
  xv, yv = meshgrid(x, x)  # define a 2D grid with points (xv,yv)
  values = f(xv, yv)       # function values
  surfc(xv, yv, values,
        zmin=0.9*arrmin(values), zmax=1.1*arrmax(values),
        shading='interp',
        clevels=15,
        clabels='on',
        hidden='on')

*Second princple*: Easyviz is just a unified interface to other plotting
packages that can be called from Python. Such plotting packages are
referred to as backends. Several backends are supported: Gnuplot,
Matplotlib, Pmw.Blt.Graph, PyX, Matlab, Vtk. In other words, scripts
that use Easyviz commands only, can work with a variety of backends,
depending on what you have installed on the machine in question and
what quality of the plots you demand. For example, swiching from
Gnuplot to Matplotlib is trivial.

Scripts with Easyviz commands will most probably run anywhere since at
least the Gnuplot package can always be installed right away on any
platform. In practice this means that when you write a script to
automate investigation of a scientific problem, you can always quickly
plot your data with Easyviz (i.e., Matlab-like) commands and postpone
to marry any specific plotting tool. Most likely, the choice of
plotting backend can remain flexible. This will also allow old scripts
to work with new fancy plotting packages in the future if Easyviz
backends are written for those packages.

*Third principle*: The Easyviz interface is minimalistic, aimed at
rapid prototyping of plots. This makes the Easyviz code easy to read
and extend (e.g., with new backends). If you need more sophisticated
plotting, like controlling tickmarks, inserting annotations, etc., you
must grab the backend object and use the backend-specific syntax to
fine-tune the plot. The idea is that you can get away with Easyviz
and a plotting package-independent script "95%" of the time - only now
and then there will be demand for package-dependent code for
fine-tuning and customization of figures.

These three principles and the Easyviz implementation make simple things
simple and unified, and complicated things are not more complicated than
they would otherwise be. You can always start out with the simple
commands - and jump to complicated fine-tuning only when strictly needed.

Controlling the Backend
-----------------------

The Easyviz backend can either be set in a config file (see Config File
below) or by a command-line option --easyviz, followed by the name
of the backend.

There are several available backends: "gnuplot_", "vtk_",
"matplotlib_", "blt_" (using Pmw.Blt.Graph), etc. Which backend
you choose depends on what you have available on your computer
system and what kind of plotting functionality you want.
"""

__author__ = "Rolv Erlend Bredesen, Hans Petter Langtangen, Johannes H. Ring"
__version__ = "0.1"

import time as _time; _t0 = _time.clock();
_import_times = 'easyviz import time: '

# ----
# which backend? load config file, check command line
backend = 'gnuplot_'
# load configuration file:
from scitools.misc import load_config_file
_scitools_config = load_config_file('scitools')
backend = _scitools_config.get('easyviz', 'backend')

import sys
if '--easyviz' in sys.argv:
    try:
        backend = sys.argv[sys.argv.index('--easyviz') + 1]
    except:
        print '--easyviz option must be followed by backend name\n'\
              '(gnuplot_, vtk_, matplotlib_, etc.)'

_t1 = _time.clock(); _import_times += 'config: %s ' % (_t1 - _t0)

exec('from %s import *' % backend)
_t2 = _time.clock(); _import_times += '%s: %s ' % (backend, _t2 - _t1)

from utils import *
from movie import movie

_t3 = _time.clock(); _import_times += 'utils: %s ' % (_t3 - _t2)

# ----

VERBOSE = int(_scitools_config.get('modes', 'VERBOSE'))
if VERBOSE >= 3:
    print _import_times
if VERBOSE >= 1:
    print "scitools.easyviz backend is %s" % backend


# add plot doc string to package doc string:
#__doc__ += plot.__doc__

def get_backend():
    """Return the current backend object (used for direct access
    to the underlying plotting package when there is need for
    advanced plotting beyond the plain easyplot functionality).
    """
    return plt._g
