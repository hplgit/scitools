"""
"""

__author__ = "Johannes H. Ring, Rolv Erlend Bredesen, Hans Petter Langtangen"
__version__ = "0.1"

import time as _time; _t0 = _time.clock();
_import_times = 'easyviz import time: '

from scitools.globaldata import backend, VERBOSE   # read-only import

_t1 = _time.clock(); _import_times += 'config: %s ' % (_t1 - _t0)

exec('from %s import *' % backend)
_t2 = _time.clock(); _import_times += '%s: %s ' % (backend, _t2 - _t1)

from utils import *
from movie import movie

_t3 = _time.clock(); _import_times += 'utils: %s ' % (_t3 - _t2)

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
