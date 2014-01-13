"""
Holds global data %s
in the scitools package, loaded from a configuration file.
(This module also demonstrate how to work with global parameters
accross a package in Python.)

The default configuration file looks like this:

"""

__all__ = ['SAFECODE', 'VERBOSE', 'DEBUG', 'OPTIMIZATION', 'backend']
__doc__ = __doc__ % ', '.join(__all__)

# Add the configuration file to the doc string of this module
import os
__doc__ += open(os.path.join(os.path.dirname(__file__), 'scitools.cfg')).read()


if hasattr(__name__, 'VERBOSE'):  # test if we have global data present...
    if VERBOSE >= 3:
        print 'global data import: no need to initialize data'
else:
    # initialize global data from file - this is only done once

    from .configdata import config_parser_frontend
    _config_data, _files = config_parser_frontend(
        'scitools', default_file_location=os.path.dirname(__file__))
    # None implies the directory where configdata.py resides

    # make SciTools global variables:
    #import pprint; pprint.pprint(_config_data)
    SAFECODE = _config_data['globals']['SAFECODE'][0]
    # override:
    if not __debug__:  # python -O (optimized mode)
        SAFECODE = False

    VERBOSE = _config_data['globals']['VERBOSE'][0]
    OPTIMIZATION = _config_data['globals']['OPTIMIZATION'][0]
    # usage: if OPTIMIZATION == 'vectorization', 'f77', 'C' etc.
    DEBUG = _config_data['globals']['DEBUG'][0]
    if not __debug__:
        DEBUG = 0  # always turn off debugging if we run python -O

    _load_scipy = _config_data['scipy']['load'][0]
    _load_numpytools = _config_data['numpy']['numpytools'][0]
    backend = _config_data['easyviz']['backend'][0]

    if VERBOSE >= 2:
        print 'Initialized SAFECODE=%s, VERBOSE=%s, DEBUG=%s from %s' % \
              (SAFECODE, VERBOSE, DEBUG, ', '.join(_files))

