"""

"""
import common
__doc__ += common._idea

__author__ = "Rolv Erlend Bredesen, Hans Petter Langtangen, Johannes H. Ring"
__version__ = "0.1"

from common import *
from utils import *
from movie import movie

# ----
# which backend? load config file, check command line
import sys
if '--easyviz' in sys.argv:
    try:
        backend = sys.argv[sys.argv.index('--easyviz') + 1]
    except:
        print '--easyviz option must be followed by backend name\n'\
              '(gnuplot_, vtk_, matplotlib_, etc.)'
else:
    import scitools.basics as _st
    backend = _st.scitools_config.get('easyviz', 'backend')

exec('from %s import *' % backend)
# ----

if _st.VERBOSE >= 1:
    print "Easyviz backend is %s" % backend
if _st.VERBOSE >= 3:
    import time as _time
    print "Import time %s=%g" % (backend, _time.clock())


# add plot doc string to package doc string:
#__doc__ += plot.__doc__

def get_backend():
    """Return the current backend object (used for direct access
    to the underlying plotting package when there is need for
    advanced plotting beyond the plain easyplot functionality).
    """
    return plt._g
