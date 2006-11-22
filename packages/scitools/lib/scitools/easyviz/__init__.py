"""
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
