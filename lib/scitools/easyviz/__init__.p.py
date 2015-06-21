'''
# #include "../../../doc/src/easyviz/easyviz.dst.txt"
'''

__author__ = "Johannes H. Ring, Hans Petter Langtangen, Rolv Erlend Bredesen"

_import_list = []  # used as in basics.py to keep track of what we import
import time as _time; _t0 = _time.clock();
_import_times = 'easyviz import times: '

from scitools.globaldata import backend, VERBOSE   # read-only import
_import_list.append("from scitools.globaldata import backend, VERBOSE")

_t1 = _time.clock(); _import_times += 'config: %s ' % (_t1 - _t0)

# Note: this import is always performed, also before any
# specialized import a la from scitools.easyviz.matplotlib_ import *
# For quicker import of special backends, use command-line or config
# file specification of the backend
cmd = 'from %s_ import *' % backend
exec(cmd)
_t2 = _time.clock(); _import_times += '%s: %s ' % (backend, _t2 - _t1)
_import_list.append(cmd)

from .utils import *
from .movie import movie
_import_list.append('from utils import *\nfrom movie import movie')

_t3 = _time.clock(); _import_times += 'utils: %s ' % (_t3 - _t2)

if VERBOSE >= 2:
    for i in _import_list:
        print i
if VERBOSE >= 3:
    print _import_times
if VERBOSE >= 1:
    print "scitools.easyviz backend is %s" % backend

__doc__ += '\nImport statements in this module:\n' + '\n'.join(_import_list)


# add plot doc string to package doc string:
#__doc__ += plot.__doc__
