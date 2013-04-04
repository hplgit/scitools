"""
Note:
This module stems from the days when there were three (almost) competing
Numerical Python implementations around and people wanted to be able
to switch between these implementations in their Python programs.
Nowadays, numpy is the dominating module, and the use of _numpyload and
numpytools is no longer particularly fruitful. For backward compatibility
of scitools, the two modules still exist.


Unified array computing interface
=================================

Numeric, numarray, and numpy can be viewed as three different
implementations of Numerical Python functionality.  The present module
enables writing scripts that are independent of the particular choice
of Numeric, numarray, or numpy. That is, the idea is that any of these
modules can be replaced by one of the alternatives, and the script
should still work. This requires the script to only use the set of
instructions that are common to Numeric, numarray, and numpy.

One reason for wanting the flexibility is that the different
implementations may exhibit different computational efficiency in
different applications. It also makes it trivial to adopt new versions
of Numerical Python in old scripts.


Basic Usage
-----------

To achieve a script that makes transparent use of Numeric, numarray, and
numpy, one needs to do one of the following imports::

  from scitools.numpytools import *
  # or
  import scitools.numpytools as N

Then one should never explicitly import Numeric, numarray, or numpy,
and explicitly use functions in these modules as this may cause
different array types to be mixed in the same application. Only call
the functions that were imported by the star or prefix functions by
the N symbol.


What Gets Imported?
-------------------

All symbols from either Numeric, numarray, or numpy are imported
into the global namespace of this numpytools module::

  from Numeric import *
  #or
  from numarray import *
  #or
  from numpy import *

Also the modules for random arrays, linear algebra, Matlab functions,
and FFT are imported. One problem with switching between Numeric,
numarray, and numpy is the additional modules for random arrays, etc.,
have different names in the three packages. For example::

  Numeric has LinearAlgebra
  numarray has numarray.linear_algebra.LinearAlgebra2
  numpy has numpy.linalg

The Numeric names are always available in addition to the native names.
For example, an import numpy.linalg is associated with a::

  LinearAlgebra = numpy.linalg

Note that the MA module is not imported since it redefines
the repr function (array([1,2]) becomes [1,2] as for a list) if
the Numeric is used. The user must always explicitly import this package
if Numeric is used as basic array module.

Note that the numpytools module also makes some extensions of Numerical
Python available, see the section "Functionality of this module that
extends Numerical Python" (below).


What to use: Numeric, numarray, or numpy?
-----------------------------------------

The present module defines a global variable basic_NumPy holding
either "Numeric", "numarray", or "numpy", depending on which module
that was actually imported.

To determine whether Numeric, numarray, or numpy is to be imported,
the following procedure is applied:

  1. The command line arguments are checked for a --numarray,
     --Numeric, or --numpy option.

  2. If the user has already imported Numeric, numarray, or numpy by an::

     import Numeric
     #or
     import numarray
     #or
     import numpy

     statement, the present module continues to import from the same
     module (module in sys.modules is used to check whether it should
     be Numeric, numarray, or numpy). If the user has imported more than
     one of the three module alternatives, numpy is used.

  3. The environment variable NUMPYARRAY is checked.
     If this variable contains "numarray", "Numeric", or "numpy" the
     corresponding module is imported.

If neither 1., 2., nor 3. determines the import, i.e., the user has not
explicitly indicated what to use, the new numpy is the default choice.

Some Functions for Unified Usage
--------------------------------

Some operations, like finding the maximum and minimum values in an array,
or controlling the output format when printing arrays, have different
syntax in the different Numerical Python implementations. The functions
below attempt to provide a uniform syntax to functionality with
different names in Numeric, numarray, and numpy:

 - NumPyArray:
           the type used in isinstance(a,NumPyArray) for
           checking if a is a NumPy array

 - arrmin, arrmax:
           compute maximum and minimum of all array entries
           (same as amin(a,None) and amax(a,None) in scipy)

 - array_output_precision(n):
           print arrays with n decimals

 - NumPy_type:
           returns the type of an array, i.e., "Numeric", "numarray",
           or "numpy"

 - NumPy_dtype:
           returns the type of the data in an array, i.e., 'd', 'i', etc.

 - fortran_storage:
           transparent transform of an array to column major (Fortran) storage
           that preserves the nature (Numeric, numarray, numpy) of the array

Some frequently standard modules like sys, os, and operator are
imported into the namespace of the present module.
"""
import sys, os
import collections
import numbers

# The first task to accomplish in this module is to determine
# whether to use Numeric, numarray, or numpy

basic_NumPy = None  # will later hold 'Numeric', 'numarray', or 'numpy'

# check the command line (this code is similar to matplotlib.numerix):
if basic_NumPy is None:
    if hasattr(sys, 'argv'):  # Apache mod_python has no argv
        for _a in sys.argv:
            if _a in ["--Numeric", "--numeric", "--NUMERIC"]:
                basic_NumPy = 'Numeric'
                break
            if _a in ["--Numarray", "--numarray", "--NUMARRAY"]:
                basic_NumPy = 'numarray'
                break
            if _a in ["--NumPy", "--numpy", "--NUMPY"]:
                basic_NumPy = 'numpy'
                break
        del _a  # don't pollute the global namespace

# check if the user has already done an import Numeric, import numarray,
# or import numpy; use the module that was imported

if basic_NumPy is None:
    if 'numpy' in sys.modules:
        basic_NumPy = 'numpy'
    elif 'numarray' in sys.modules:
        basic_NumPy = 'numarray'
    elif 'Numeric' in sys.modules:
        basic_NumPy = 'Numeric'

# check the environment variable NUMPYARRAY:
if basic_NumPy is None:
    if 'NUMPYARRAY' in os.environ:
        if   os.environ['NUMPYARRAY'] == 'numpy':
            basic_NumPy = 'numpy'
        elif os.environ['NUMPYARRAY'] == 'numarray':
            basic_NumPy = 'numarray'
        elif os.environ['NUMPYARRAY'] == 'Numeric':
            basic_NumPy = 'Numeric'

if basic_NumPy is None:  basic_NumPy = 'numpy' # final default choice

if basic_NumPy not in ('Numeric', 'numarray', 'numpy'):
    raise ImportError('cannot decide which Numerical Python '\
          'implementation to use (ended up with "%s")' % basic_NumPy)

#print 'from', basic_NumPy, 'import *'

# table of equivalent names of Numerical Python modules:
# (used to import modules under Numeric, numarray, or numpy name)

_NumPy_modules = (
    ('Numeric', 'numarray', 'numpy'),
    # umath and Precision are included as part of Numeric, numarray, numpy
    ('LinearAlgebra', 'numarray.linear_algebra.LinearAlgebra2',
     'numpy.linalg'),
    ('RandomArray', 'numarray.random_array.RandomArray2', 'numpy.random'),
    ('RNG', '', 'numpy.random'),
    ('FFT', 'numarray.fft', 'numpy.fft'),
    ('MLab', 'numarray.linear_algebra.mlab', 'numpy.oldnumeric.mlab'),
    ('MA', 'numarray.ma.MA', 'numpy.ma'),
    )

if basic_NumPy == 'numpy':
    try:
        # fix backward compatibility with Numeric names:
	import numpy
	oldversion = (numpy.version.version[0] == '0')
        majorversion = int(numpy.version.version[0])
        minorversion = int(numpy.version.version[2])
	for _Numeric_name, _dummy1, _numpy_name in _NumPy_modules[1:]:
	    if oldversion and (_Numeric_name in ['RNG', 'FFT']):
		n, module = _numpy_name.split('.')
		exec("from %s import %s as %s" %(n, module, _Numeric_name))
	    elif oldversion and (_Numeric_name == 'MLab'):
		from numpy.lib import mlab as MLab
            elif (oldversion or (majorversion == 1 and minorversion < 1)) \
                     and (_Numeric_name == 'MA'):
                import numpy.core.ma; MA = numpy.core.ma
	    elif _numpy_name != '':
		exec('import %s; %s = %s' %
                     (_numpy_name, _Numeric_name, _numpy_name))

	del _Numeric_name, _dummy1, _numpy_name, _NumPy_modules

	from numpy import *
	if not oldversion:
	    # get the old names too (NewAxis, Float, etc.):
	    from numpy.oldnumeric import *
	del oldversion
        # define new names compatible with Numeric:
        LinearAlgebra.solve_linear_equations = linalg.solve
        LinearAlgebra.inverse = linalg.inv
        LinearAlgebra.determinant = linalg.det
        LinearAlgebra.eigenvalues = linalg.eigvals
        LinearAlgebra.eigenvectors = linalg.eig

    except ImportError as e:
        raise ImportError('%s\nnumpy import failed!\n'\
              'see doc of %s module for how to choose Numeric instead' % \
              (e, __name__))


    def array_output_precision(no_of_decimals):
        """Set no of decimals in printout of arrays."""
        arrayprint.set_precision(no_of_decimals)

    def arrmax(a):
        """Compute the maximum of all the entries in a."""
        try:
            return a.max()
        except AttributeError:
            # not a NumPy array
            if isinstance(a, collections.Sequence):
                return max(a)  # does not work for nested sequences
            elif isinstance(a, numbers.Number):
                return a
            else:
                raise TypeError('arrmax of %s not supported' % type(a))

    def arrmin(a):
        """Compute the minimum of all the entries in a."""
        try:
            return a.min()
        except AttributeError:
            # not a NumPy array
            if isinstance(a, collections.Sequence):
                return min(a)  # does not work for nested sequences
            elif isinstance(a, numbers.Number):
                return a
            else:
                raise TypeError('arrmin of %s not supported' % type(a))

    NumPyArray = ndarray

if basic_NumPy == 'numarray':
    try:
        for _Numeric_name, _numarray_name, _dummy1 in _NumPy_modules[1:]:
            if _numarray_name:
                exec('import %s; %s = %s' %
                     (_numarray_name, _Numeric_name, _numarray_name))

        # RNG is not supported, make an object that gives an error message:
        class __Dummy:
            def __getattr__(self, name):
                raise ImportError('You have chosen the numarray package, '\
                'but it does not have the functionality of the RNG module')
        RNG = __Dummy()
        del _Numeric_name, _numarray_name, _dummy1, __Dummy, _NumPy_modules

        from numarray import *

    except ImportError as e:
        raise ImportError('%s\nnumarray import failed!\n'\
        'see doc of %s module for how to choose Numeric instead' % \
        (e, __name__))

    def array_output_precision(no_of_decimals):
        """Set no of decimals in printout of arrays."""
        arrayprint.set_precision(no_of_decimals)

    def arrmax(a):
        """Compute the maximum of all the entries in a."""
        try:
            return a.max()
        except AttributeError:
            # not a NumPy array
            if isinstance(a, collections.Sequence):
                return max(a)  # does not work for nested sequences
            elif isinstance(a, numbers.Number):
                return a
            else:
                raise TypeError('arrmax of %s not supported' % type(a))

    def arrmin(a):
        """Compute the minimum of all the entries in a."""
        try:
            return a.min()
        except AttributeError:
            # not a NumPy array
            if isinstance(a, collections.Sequence):
                return min(a)  # does not work for nested sequences
            elif isinstance(a, numbers.Number):
                return a
            else:
                raise TypeError('arrmin of %s not supported' % type(a))

    NumPyArray = NumArray

if basic_NumPy == 'Numeric':
    try:
        for _Numeric_name, _dummy1, _dummy2 in _NumPy_modules[1:]:
            if _Numeric_name != 'MA':  # exclude MA, see comment above
                exec('import %s' % _Numeric_name)
        del _Numeric_name, _dummy1, _dummy2, _NumPy_modules

        from Numeric import *

        # the following is perhaps not a good idea;
        # Numeric.UserArray and numarray.NumArray have different
        # data attributes!
        from UserArray import UserArray as NumArray

        # define new numpy names:
        newaxis = NewAxis
        def linspace(start, stop, num=50, endpoint=True, retstep=False):
            return asarray(numpy.linspace(start, stop, num, endpoint, retstep))


        # hack if LinearAlgebra.eigenvalues hang (because of trouble
        # with gcc and Numeric and -ffloat-store flag):

        _problems = False
        if _problems:
            def numpy_eigenvalues(A):
                """
                Temporary wrapper for Numeric's LinearAlgebra.eigenvalues.
                Convert A to numpy, call numpy's eigenvalues,
                convert back to Numeric.
                """
                import numpy
                A = numpy.array(A)
                E = numpy.linalg.eigenvalues(A)
                import Numeric
                E = Numeric.array(E)
                return E

            def numpy_eigenvectors(A):
                """
                Temporary wrapper for Numeric's LinearAlgebra.eigenvectors.
                Convert A to numpy, call numpy's eigenvalues,
                convert back to Numeric.
                """
                import numpy
                A = numpy.array(A)
                E, V = numpy.linalg.eigenvectors(A)
                import Numeric
                E = Numeric.array(E)
                V = Numeric.array(V)
                return E, V

            LinearAlgebra.eigenvalues = numpy_eigenvalues
            LinearAlgebra.eigenvectors = numpy_eigenvectors
        del _problems

    except ImportError as e:
        raise ImportError('%s\nNumeric import failed!\n'\
        'see doc of %s module for how to choose numarray instead' % \
        (e, __name__))


    # fix of matrixmultiply bug in Numeric (according to Fernando Perez,
    # SciPy-dev mailing list, Sep 28, 2004:
    # http://www.scipy.net/pipermail/scipy-dev/2004-September/002267.html,
    # matrixmultiply is dot if not dotblas is used, otherwise dot is
    # imported from dotblas, and matrixmultiply becomes the unoptimized
    # version (Perez timed the difference to be 0.55 vs 122.6 on his
    # computer)):
    matrixmultiply = dot

    def array_output_precision(no_of_decimals):
        """Set no of decimals in printout of arrays."""
        sys.float_output_precision = no_of_decimals

    def arrmax(a):
        """Compute the maximum of all the entries in a."""
        # could set arrmax = amax in scipy if scipy is installed
        try:
            return max(a.flat)  # use Python's list min
        except AttributeError:
            # not a NumPy array
            if isinstance(a, collections.Sequence):
                return max(a)
            elif isinstance(a, numbers.Number):
                return a
            else:
                raise TypeError('arrmax of %s not supported' % type(a))

    def arrmin(a):
        """Compute the minimum of all the entries in a."""
        # could set arrmin = amin in scipy if scipy is installed
        try:
            return min(a.flat)
        except AttributeError:
            # not a NumPy array
            if isinstance(a, collections.Sequence):
                return min(a)
            elif isinstance(a, numbers.Number):
                return a
            else:
                raise TypeError('arrmin of %s not supported' % type(a))

    NumPyArray = ArrayType

    # support numpy types:
    int_ = Int
    int0 = Int0
    int8 = Int8
    int16 = Int16
    int32 = Int32
    float_ = Float
    float32 = Float32
    float64 = Float64
    complex_ = Complex
    complex64 = Complex64


_N = __import__(basic_NumPy)
NumPy_version = _N.__version__
del _N

# Short forms:
fft = FFT
mlab = MLab
try:
    ma = MA
except NameError:
    # for Numeric we do not import MA since it affects output format
    pass
ra = RandomArray
la = LinearAlgebra

def NumPy_type(a):
    """
    @param a: NumPy array
    @return:  "Numeric", "numarray", or "numpy", depending on which
    module that was used to generate the a array

    If type is list or tuple then the corresponding typename will be returned
    """

    # check basic_NumPy type first to avoid possible import errors
    types = {'Numeric': 'Numeric.ArrayType',
             'numarray': 'numarray.NumArray',
             'numpy': 'numpy.ndarray'}

    # Check for non NumPy types first
    if isinstance(a, tuple):
	return "tuple"
    elif isinstance(a, list):
	return "list"
    exec("import %s" % basic_NumPy) # Why isn't basic_NumPy imported?
    if isinstance(a, eval(types[basic_NumPy])):
        return basic_NumPy

    # not the main NumPy type, try the others:
    import numpy
    if isinstance(a, numpy.ndarray):
        return 'numpy'
    import Numeric
    if isinstance(a, Numeric.ArrayType):
        return 'Numeric'
    import numarray
    if isinstance(a, numarray.NumArray):
        return 'numarray'

def NumPy_dtype(a):
    """
    @param a: NumPy array
    @return:  array data type, as a character,
    depending on which module that was
    used to generate the a array (a.typecode() for Numeric and
    numarray, a.dtype for numpy).
    """
    if NumPy_type(a) == 'Numeric':
        return a.typecode()
    elif NumPy_type(a) == 'numarray':
        return a.typecode()
    elif NumPy_type(a) == 'numpy':
        return a.dtype
    else:
        raise TypeError("array should be NumPy array, not %s" % type(a))

def fortran_storage(a):
    """
    Transparent transform of a NumPy array to Fortran (column major)
    storage.

    @param a:  NumPy array (generated in Python or C with C storage)
    @return: a new NumPy array with column major storage.

    Method: If a is of numpy type, numpy.asarray(a, fortran=True)
    is used to produce the new array.
    If a is of Numeric or numarray type, we want to preserve the array type
    and use a simple (and slower) transpose(transpose(a).copy()) instead.
    """
    if NumPy_type(a) == 'Numeric' or NumPy_type(a) == 'numarray':
        return transpose(transpose(a).copy())
    else:
        import numpy
        return numpy.asarray(a, fortran=True)

