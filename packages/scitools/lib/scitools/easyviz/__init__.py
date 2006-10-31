"""

"""
import common
__doc__ += common._idea

__author__ = "Rolv Erlend Bredesen, Hans Petter Langtangen, Johannes H. Ring"
__version__ = "0.1"

from scitools import *  # need at least config, nice to have it all for a user
from common import *
from utils import *
from movie import movie

backend = scitools_config.get('easyviz', 'backend')
if VERBOSE >= 1:
    print "Easyviz backend is %s" % backend

exec('from %s import *' % backend)

# add plot doc string to package doc string:
#__doc__ += plot.__doc__

def get_backend():
    """Return the current backend object (used for direct access
    to the underlying plotting package when there is need for
    advanced plotting beyond the plain easyplot functionality).
    """
    return plt._g
