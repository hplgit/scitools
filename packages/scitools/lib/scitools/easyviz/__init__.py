"""

"""
import common
__doc__ += common._idea

__author__ = "Rolv Erlend Bredesen, Hans Petter Langtangen, Johannes H. Ring"
__version__ = "0.1"

from scitools import *    # nice to have
from common import *
from utils import *
from movie import movie
# gnuplot is default:
backend = 'gnuplot_'
#backend = 'vtk_'
#backend = 'pyx_'
#backend = 'blt_'

# Try to set backend from environment variable
import os
backend = os.environ.get('EASYVIZ_BACKEND', backend)
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
