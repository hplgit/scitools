"""
%s

%s
"""

import os, sys, operator, math


# copied into this file by preprocess.py:
#  #include "_numpyload.py"
#  #include "numpyutils.py"

#---- build doc string from _numpyload/util doc strings ----

from . import _numpyload as _load
_load.__doc__ += """

Example on what gets imported
-----------------------------

(basic_NumPy holds the name of the Numeric
Python module after import of numpytools (or _numpyload):

# default:
unix/DOS> python -c "from numpytools import *; print basic_NumPy"
numpy

# set the NUMPYARRAY environment variable:
unix/DOS> python -c "import os; os.environ['NUMPYARRAY']='Numeric'; from numpytools import *; print basic_NumPy"
Numeric

# import a Numerical Python module (precedence over NUMPYARRAY variable):
unix/DOS> python -c "import numpy; import os; os.environ['NUMPYARRAY']='Numeric'; from numpytools import *; print basic_NumPy"
numpy

# add flag on the command line (precedence over import):
unix/DOS> python -c "import numpy; import os; os.environ['NUMPYARRAY']='Numeric'; from numpytools import *; print basic_NumPy" --numarray
numarray
"""

from . import numpyutils as _utils
# insert numpyutils and _numpyload documentation into the
# doc string of this numpytools module:
__doc__ = __doc__ % (_load.__doc__, _utils.__doc__)
# clean up:
# import numpyutils may import numpy and we remove this entry
# in sys.modules
if basic_NumPy != 'numpy':
    if 'numpy' in sys.modules:
        del sys.modules['numpy']
del _load, _utils
#---------

if __name__ == '__main__':

    def _doctest():
        import doctest, numpytools
        return doctest.testmod(numpytools)

    def verify(N, namecheck = ['fft','mlab','ma','ra','la']):
        """
        Verify that some packages imported by numpytools
        works for Numeric, numarray, or numpy.
        """
        print "\nUsing %s in %s" % (N.basic_NumPy, N.__name__)
        for name in namecheck:
            if hasattr(N, name):
                print "%s.%s : %s " % (
                    N.__name__,
                    name,
                    eval("N.%s.__name__" % name))
        print ""

    def _test1():
        """Call verify function for N as Numeric, numarray, and numpy."""
        sys.argv.append('--Numeric')
        from . import numpytools as N
        verify(N)
        sys.argv[-1] = '--numarray'
        reload(N)
        verify(N)
        sys.argv[-1] = '--numpy'
        reload(N)
        verify(N)

    #_test1()

    #test_ArrayGen()
    #_doctest()  # does not work properly with wrap2callable

    # Test meshgrid function
    import unittest
    from . import numpytools as N

    class numpytoolsTest(unittest.TestCase):
        def setUp(self):
            pass

        def testMeshgrid(self):
            #print 'testing Meshgrid'
            x = N.arange(10)
            y = N.arange(4)
            z = N.arange(3)
            X, Y, Z = N.meshgrid(x, y, z, sparse=False)
            assert N.rank(X) == 3

        def testMeshgrid_DenseFromMixedArrayTypes(self):
            # Other combination of arrays
            #print 'testing Meshgrid with mixed array implementations'
            y = N.arange(4)
            z = N.arange(3)

            import Numeric
            x = Numeric.arange(10)
            X, Y, Z = N.meshgrid(x, y, z, sparse=False)
            if not  N.rank(X) == 3:
                raise AssertionError(
                    "Meshgrid failed with arraytype mix of  Numeric and %s"\
                    %N.basic_NumPy)
            import numarray
            x = numarray.arange(10)
            X, Y, Z = N.meshgrid(x, y, z, sparse=False)

            if not  N.rank(X) == 3:
                raise AssertionError(
                    "Meshgrid failed with arraytype mix of numarray and %s"\
                    %N.basic_NumPy)

            import numpy
            x = numpy.arange(10)
            X, Y, Z = N.meshgrid(x, y, z, sparse=False)
            #assert N.rank(X) == 3
            if not  N.rank(X) == 3:
                raise AssertionError(
                    "Meshgrid failed with arraytype mix of numpy and %s"\
                    %N.basic_NumPy)

        def testMeshGrid_DenseFromNodenseMeshgridOutput(self):
            # sparse fails for dense output when input has singleton dimensions
            x = seq(-2,2,0.1)
            y = seq(-4,4,1)
            xx, yy = meshgrid(x,y) # xx and yy now has singleton dimension
            self.assertEqual(rank(xx), 2)
            self.assertEqual(rank(yy), 2)
            self.assertEqual(multiply.reduce(xx.shape), size(xx))
            self.assertEqual(multiply.reduce(yy.shape), size(yy))
            # This one should fail when xx and yy is not flat as well
            xx, yy = meshgrid(xx.flat, yy.flat, sparse=False) # no singleton
            self.assertEqual(shape(xx), (size(y), size(x)))
            self.assertEqual(shape(yy), (size(y), size(x)))

            xx, yy = meshgrid(x,y) # Add singleton dimensions
            xx, yy = meshgrid(xx, yy, sparse=False)
            self.assertEqual(shape(xx), (size(y), size(x)))
            self.assertEqual(shape(yy), (size(y), size(x)))

            #from IPython.Shell import IPythonShellEmbed as magic
            #magic()('from unittest')

    sys.argv.append('')  # extra argument for the test below
    for arg in ['--Numeric', '--numarray', '--numpy']:
        try:
            __import__(arg[2:])
        except:
            print "You don't have %s installed" %arg[2:]
            continue

        sys.argv[-1] = arg
        print '\nNow testing with system arg %10s\n%s' %(arg, '='*38)
        print N, dir(N)
        reload(N);  verify(N)
        suite = unittest.makeSuite(numpytoolsTest)
        unittest.TextTestRunner(verbosity=2).run(suite)
