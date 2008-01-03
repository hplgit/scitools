"""
%s

%s
"""
__id__ = '$Id$'
    
import os, sys, operator, math


# to copied into this file by preprocess.py:
"""
Unified interface to Numeric, numarray, and numpy
=================================================

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
    if os.environ.has_key('NUMPYARRAY'):
        if   os.environ['NUMPYARRAY'] == 'numpy':
            basic_NumPy = 'numpy'
        elif os.environ['NUMPYARRAY'] == 'numarray':
            basic_NumPy = 'numarray'
        elif os.environ['NUMPYARRAY'] == 'Numeric':
            basic_NumPy = 'Numeric'

if basic_NumPy is None:  basic_NumPy = 'numpy' # final default choice

if basic_NumPy not in ('Numeric', 'numarray', 'numpy'):
    raise ImportError, 'cannot decide which Numerical Python '\
          'implementation to use (ended up with "%s")' % basic_NumPy

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
    ('MA', 'numarray.ma.MA', 'numpy.core.ma'),
    )
     
if basic_NumPy == 'numpy':
    try:
        # fix backward compatibility with Numeric names:
	import numpy
	oldversion = (numpy.version.version[0] != '1')
	for _Numeric_name, _dummy1, _numpy_name in _NumPy_modules[1:]:
	    if oldversion and (_Numeric_name in ['RNG', 'FFT']):
		n, module = _numpy_name.split('.')
		exec "from %s import %s as %s" %(n, module, _Numeric_name)
	    elif oldversion and (_Numeric_name == 'MLab'):
		from numpy.lib import mlab as MLab
	    elif _numpy_name != '':
		exec 'import %s; %s = %s' % \
		(_numpy_name, _Numeric_name, _numpy_name)
		
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

    except ImportError, e:
        raise ImportError, '%s\nnumpy import failed!\n'\
              'see doc of %s module for how to choose Numeric instead' % \
              (e, __name__)


    def array_output_precision(no_of_decimals):
        """Set no of decimals in printout of arrays."""
        arrayprint.set_precision(no_of_decimals)

    def arrmax(a):
        """Compute the maximum of all the entries in a."""
        try:
            return a.max()
        except AttributeError:
            # not a NumPy array
            if operator.isSequenceType(a):
                return max(a)  # does not work for nested sequences
            elif operator.isNumberType(a):
                return a
            else:
                raise TypeError, 'arrmax of %s not supported' % type(a)        

    def arrmin(a):
        """Compute the minimum of all the entries in a."""
        try:
            return a.min()
        except AttributeError:
            # not a NumPy array
            if operator.isSequenceType(a):
                return min(a)  # does not work for nested sequences
            elif operator.isNumberType(a):
                return a
            else:
                raise TypeError, 'arrmin of %s not supported' % type(a)

    NumPyArray = ndarray

if basic_NumPy == 'numarray':
    try:
        for _Numeric_name, _numarray_name, _dummy1 in _NumPy_modules[1:]:
            if _numarray_name:
                exec 'import %s; %s = %s' % \
                     (_numarray_name, _Numeric_name, _numarray_name)

        # RNG is not supported, make an object that gives an error message:
        class __Dummy:
            def __getattr__(self, name):
                raise ImportError, 'You have chosen the numarray package, '\
                'but it does not have the functionality of the RNG module'
        RNG = __Dummy()
        del _Numeric_name, _numarray_name, _dummy1, __Dummy, _NumPy_modules
        
        from numarray import *

    except ImportError, e:
        raise ImportError, '%s\nnumarray import failed!\n'\
        'see doc of %s module for how to choose Numeric instead' % \
        (e, __name__)

    def array_output_precision(no_of_decimals):
        """Set no of decimals in printout of arrays."""
        arrayprint.set_precision(no_of_decimals)

    def arrmax(a):
        """Compute the maximum of all the entries in a."""
        try:
            return a.max()
        except AttributeError:
            # not a NumPy array
            if operator.isSequenceType(a):
                return max(a)  # does not work for nested sequences
            elif operator.isNumberType(a):
                return a
            else:
                raise TypeError, 'arrmax of %s not supported' % type(a)        

    def arrmin(a):
        """Compute the minimum of all the entries in a."""
        try:
            return a.min()
        except AttributeError:
            # not a NumPy array
            if operator.isSequenceType(a):
                return min(a)  # does not work for nested sequences
            elif operator.isNumberType(a):
                return a
            else:
                raise TypeError, 'arrmin of %s not supported' % type(a)

    NumPyArray = NumArray

if basic_NumPy == 'Numeric':
    try:
        for _Numeric_name, _dummy1, _dummy2 in _NumPy_modules[1:]:
            if _Numeric_name != 'MA':  # exclude MA, see comment above
                exec 'import %s' % _Numeric_name
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
        
    except ImportError, e:
        raise ImportError, '%s\nNumeric import failed!\n'\
        'see doc of %s module for how to choose numarray instead' % \
        (e, __name__)


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
            if operator.isSequenceType(a):
                return max(a)
            elif operator.isNumberType(a):
                return a
            else:
                raise TypeError, 'arrmax of %s not supported' % type(a)

    def arrmin(a):
        """Compute the minimum of all the entries in a."""
        # could set arrmin = amin in scipy if scipy is installed
        try:
            return min(a.flat)
        except AttributeError:
            # not a NumPy array
            if operator.isSequenceType(a):
                return min(a)
            elif operator.isNumberType(a):
                return a
            else:
                raise TypeError, 'arrmin of %s not supported' % type(a)

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
    exec "import %s" % basic_NumPy # Why isn't basic_NumPy imported?
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
    
"""
Functionality of this module that extends Numerical Python
==========================================================

The following extensions to Numerical Python are also defined:

 - seq
           seq(a,b,s, [type]) computes numbers from a up to and
           including b in steps of s and (default) type float_
           sequence = seq (for backward compatibility)

 - iseq:
           as seq, but integer counters are computed
           (iseq is an alternative to range where the
           upper limit is included in the sequence - this can
           be important for direct mapping of indices between
           mathematics and Python code)
           isequence = iseq (for backward compatibility)

 - arr:
           simplified/unified interface to creating NumPy
           arrays (see its doc string)

 - solve_tridiag_linear_system:
           returns the solution of a tridiagonal linear system

 - wrap2callable:
           tool for turning constants, discrete data, string
           formulas, function objects, or plain functions
           into an object that behaves as a function

 - NumPy_array_iterator:
           allows iterating over all array elements using
           a single, standard for loop (for value, index in iterator),
           has some additional features compared with numpy.ndenumerate
             
 - asarray_cpwarn:
           as asarray(a), but a warning or exception is issued if
           the array a is copied

 - ndgrid:
           extend one-dimensional coordinate arrays to multi-dimensional
           arrays over grids
           
 - float_eq:
           operator == for float operands with tolerance,
           float_eq(a,b,tol) means abs(a-b) < tol
           works for both scalar and array arguments

 - norm_L2, norm_l2, norm_L1, norm_l1, norm_inf: 
           norms for multi-dimensional arrays viewed as vectors

 - compute_historgram:
           return x and y arrays of a histogram, given a vector of samples

 - factorial:
           compute the factorial n! by various methods (iterative,
           recursive, reduce, functional, scipy, etc)

"""

if __name__.find('numpyutils') != -1:
    from numpy import *

#else if name is some other module name:
# this file is included in numpytools.py (through a preprocessing step)
# and the code below then relies on previously imported Numerical Python
# modules (Numeric, numpy, numarray)

import operator

def asarray_cpwarn(a, dtype=None, message='warning', comment=''):
    """
    As asarray, but a warning or exception is issued if the
    a array is copied.
    """
    a_new = asarray(a, dtype)
    # must drop numpy's order argument since it conflicts
    # with Numeric's savespace

    # did we copy?
    if a_new is not a:
        # we do not return the identical array, i.e., copy has taken place
        msg = '%s  copy of array %s, from %s to %s' % \
              (comment, a.shape, type(a), type(a_new))
        if message == 'warning':
            print 'Warning: %s' % msg
        elif message == 'exception':
            raise TypeError, msg
    return a_new


def seq(min=0.0, max=None, inc=1.0, type=float,
        return_type='NumPyArray'):
    """
    Generate numbers from min to (and including!) max,
    with increment of inc. Safe alternative to arange.
    The return_type string governs the type of the returned
    sequence of numbers ('NumPyArray', 'list', or 'tuple').
    """
    if max is None: # allow sequence(3) to be 0., 1., 2., 3.
        # take 1st arg as max, min as 0, and inc=1
        max = min; min = 0.0; inc = 1.0
    r = arange(min, max + inc/2.0, inc, type)
    if return_type == 'NumPyArray' or return_type == ndarray:
        return r
    elif return_type == 'list':
        return r.tolist()
    elif return_type == 'tuple':
        return tuple(r.tolist())


def iseq(start=0, stop=None, inc=1):
    """
    Generate integers from start to (and including) stop,
    with increment of inc. Alternative to range/xrange.
    """
    if stop is None: # allow isequence(3) to be 0, 1, 2, 3
        # take 1st arg as stop, start as 0, and inc=1
        stop = start; start = 0; inc = 1
    return xrange(start, stop+inc, inc)

sequence = seq  # backward compatibility
isequence = iseq  # backward compatibility


def arr(shape=None, element_type=float,
        interval=None, 
        data=None, copy=True,
        file_=None,
        order='C'):
    """
    Compact and flexible interface for creating NumPy arrays,
    including several consistency and error checks.

    @param shape:        length of each dimension
    @type  shape:        tuple or int
    @param data:         list, tuple, or NumPy array with data elements
    @param copy:         copy data if true, share data if false
    @type  copy:         boolean
    @param element_type: float, int, int16, float64, bool, etc.
    @param interval:     make elements from a to b (shape gives no of elms)
    @type  interval:     tuple or list
    @param file_:        filename or file object containing array data
    @type  file_:        string
    @param order:        'Fortran' or 'C' storage
    @type  order:        string
    @return:             created Numerical Python array

    The array can be created in four ways:
    
      1. as zeros (just shape specified),

      2. as uniformly spaced coordinates in an interval [a,b]

      3. as a copy of or reference to (depending on copy=True,False resp.)
         a list, tuple, or NumPy array (provided as the data argument),

      4. from data in a file (for one- or two-dimensional real-valued arrays).

    The function calls the underlying NumPy functions zeros, array and
    linspace (see the NumPy manual for the functionality of these
    functions).  In case of data in a file, the first line determines
    the number of columns in the array. The file format is just rows
    and columns with numbers, no decorations (square brackets, commas,
    etc.) are allowed.

    >>> arr((3,4))
    array([[ 0.,  0.,  0.,  0.],
           [ 0.,  0.,  0.,  0.],
           [ 0.,  0.,  0.,  0.]])

    >>> arr(4, element_type=int) + 4  # integer array
    array([4, 4, 4, 4])

    >>> arr(3, interval=[0,2])
    array([ 0.,  1.,  2.])
           
    >>> somelist=[[0,1],[5,5]]
    >>> a = arr(data=somelist)
    >>> a  # a has always float elements by default
    array([[ 0.,  1.],
           [ 5.,  5.]])
    >>> a = arr(data=somelist, element_type=int)
    >>> a
    array([[0, 1],
           [5, 5]])
    >>> b = a + 1
    
    >>> c = arr(data=b, copy=False)  # let c share data with b
    >>> b is c
    True
    >>> id(b) == id(c)
    True

    >>> # make a file with array data:
    >>> f = open('tmp.dat', 'w')
    >>> f.write('''\
    ... 1 3
    ... 2 6
    ... 3 12
    ... 3.5 20
    ... ''')
    >>> f.close()
    >>> # read array data from file:
    >>> a = arr(file_='tmp.dat')
    >>> a
    array([[  1. ,   3. ],
           [  2. ,   6. ],
           [  3. ,  12. ],
           [  3.5,  20. ]])
    """
    if data is None and file_ is None and shape is None:
        return None
    
    if data is not None:

        if not operator.isSequenceType(data):
            raise TypeError, 'arr: data argument is not a sequence type'
        
        if isinstance(shape, (list,tuple)):
            # check that shape and data are compatible:
            if reduce(operator.mul, shape) != size(data):
                raise ValueError, \
                      'arr: shape=%s is not compatible with %d '\
                      'elements in the provided data' % (shape, size(data))
        elif isinstance(shape, int):
            if shape != size(data):
                raise ValueError, \
                      'arr: shape=%d is not compatible with %d '\
                      'elements in the provided data' % (shape, size(data))
        elif shape is None:
            if isinstance(data, (list,tuple)) and copy == False:
                # cannot share data (data is list/tuple)
                copy = True
            return array(data, dtype=element_type, copy=copy, order=order)
        else:
            raise TypeError, \
                  'shape is %s, must be list/tuple or int' % type(shape)
    elif file_ is not None:
        if not isinstance(file_, (basestring, file, StringIO)):
            raise TypeError, \
                  'file_ argument must be a string (filename) or '\
                  'open file object, not %s' % type(file_)

        if isinstance(file_, basestring):
            file_ = open(file_, 'r')
        # skip blank lines:
        while True:
            line1 = file_.readline().strip()
            if line1 != '':
                break
        ncolumns = len(line1.split())
        file_.seek(0)
        # we assume that array data in file has element_type=float:
        if not (element_type == float or element_type == 'd'):
            raise ValueError, 'element_type must be float_/"%s", not "%s"' % \
                  ('d', element_type)
        
        d = array([float(word) for word in file_.read().split()])
        if isinstance(file_, basestring):
            f.close()
        # shape array d:
        if ncolumns > 1:
            suggested_shape = (int(len(d)/ncolumns), ncolumns)
            total_size = suggested_shape[0]*suggested_shape[1]
            if total_size != len(d):
                raise ValueError, \
                'found %d array entries in file "%s", but first line\n'\
                'contains %d elements - no shape is compatible with\n'\
                'these values' % (len(d), file, ncolumns)
            d.shape = suggested_shape
        if shape is not None:
            if shape != d.shape:
                raise ValueError, \
                'shape=%s is not compatible with shape %s found in "%s"' % \
                (shape, d.shape, file)
        return d

    elif interval is not None and shape is not None:
        if not isinstance(shape, int):
            raise TypeError, 'For array values in an interval, '\
                  'shape must be an integer'
        if not isinstance(interval, (list,tuple)):
            raise TypeError, 'interval must be list or tuple, not %s' % \
                  type(interval)
        if len(interval) != 2:
            raise ValueError, 'interval must be a 2-tuple (or list)'

        try:
            return linspace(interval[0], interval[1], shape)
        except MemoryError, e:
            # print more information (size of data):
            print e, 'of size %s' % shape

    else:
        # no data, no file, just make zeros

        if not isinstance(shape, (tuple, int, list)):
            raise TypeError, \
           'arr: shape (1st arg) must be tuple or int'
        if shape is None:
            raise ValueError, \
            'arr: either shape, data, or from_function must be specified'

        try:
            return zeros(shape, dtype=element_type, order=order)
        except MemoryError, e:
            # print more information (size of data):
            print e, 'of size %s' % shape
    
def meshgrid(x=None, y=None, z=None, sparse=True, indexing='xy',
             memoryorder=None):
    """
    Make 1D/2D/3D coordinate arrays for vectorized evaluations of
    1D/2D/3D scalar/vector fields over 1D/2D/3D grids, given
    one-dimensional coordinate arrays x, y, and/or, z.

    >>> x=linspace(0,1,3)        # coordinates along x axis
    >>> y=linspace(0,1,2)        # coordinates along y axis
    >>> xv, yv = meshgrid(x,y)   # extend x and y for a 2D xy grid
    >>> xv
    array([[ 0. ,  0.5,  1. ]]
    >>> yv
    array([[ 0.],
           [ 1.]])
    >>> z=5
    >>> xv, yv, zc = meshgrid(x,y,z)  # 2D slice of a 3D grid, with z=const
    >>> xv
    array([[ 0. ,  0.5,  1. ]]
    >>> yv
    array([[ 0.],
           [ 1.]])
    >>> zc
    5

    >>> meshgrid(2,y,x)  # 2D slice of a 3D grid, with x=const
    (2, array([[ 0.,  1.]]), array([[ 0. ],
           [ 0.5],
           [ 1. ]]))
    >>> meshgrid(0,1,5)  # just a 3D point
    (0, 1, 5)
    >>> meshgrid(3)
    3
    >>> meshgrid(y)      # 1D grid; y is just returned
    array([ 0.,  1.])
    >>> meshgrid(x,y,sparse=False)  # store the full 2D matrix
    (array([[ 0. ,  0.5,  1. ],
       [ 0. ,  0.5,  1. ]]), array([[ 0.,  0.,  0.],
       [ 1.,  1.,  1.]]))
    >>> meshgrid(x,y,indexing='ij')  # change to matrix indexing
    (array([[ 0. ],
           [ 0.5],
           [ 1. ]]), array([[ 0.,  1.]]))
    >>> meshgrid(x,y,sparse=False,indexing='ij')
    (array([[ 0. ,  0. ],
           [ 0.5,  0.5],
           [ 1. ,  1. ]]), array([[ 0.,  1.],
           [ 0.,  1.],
           [ 0.,  1.]]))


    Why has SciTools its own meshgrid function when NumPy has three
    similar functions, `mgrid`, `ogrid`, and `meshgrid`?
    The `meshgrid` function in NumPy is limited to two dimensions only, while
    the SciTools version can also work with 3D grids. In addition,
    the NumPy version of `meshgrid` has no option for generating sparse
    grids to conserve memory, like we have in SciTools by specifying the
    `sparse` argument:
    !bc
    >>> xv, yv = meshgrid(linspace(-2,2,5), linspace(-1,1,3), sparse=True)
    >>> xv
    array([[-2., -1.,  0.,  1.,  2.]])
    >>> yv
    array([[-1.],
           [ 0.],
           [ 1.]])
    >>>
    !ec
    Actually, this is the default behavior for the `meshgrid` function in
    SciTools. In NumPy, however, we will in this case get a full 2D grid:
    !bc
    >>> xv, yv = numpy.meshgrid(linspace(-2,2,5), linspace(-1,1,3))
    >>> xv
    array([[-2., -1.,  0.,  1.,  2.],
           [-2., -1.,  0.,  1.,  2.],
           [-2., -1.,  0.,  1.,  2.]])
    >>> yv
    array([[-1., -1., -1., -1., -1.],
           [ 0.,  0.,  0.,  0.,  0.],
           [ 1.,  1.,  1.,  1.,  1.]])
    >>> 
    !ec
    This is the same result we get by setting `sparse=False` in `meshgrid`
    in SciTools.

    The NumPy functions `mgrid` and `ogrid` does provide support for,
    respectively, full and sparse n-dimensional meshgrids, however,
    these functions uses slices to generate the meshgrids rather than
    one-dimensional coordinate arrays such as in Matlab. With slices, the
    user does not have the option to generate meshgrid with, e.g.,
    irregular spacings, like 
    !bc
    >>> x = array([-1,-0.5,1,4,5], float)
    >>> y = array([0,-2,-5], float)
    >>> xv, yv = meshgrid(x, y, sparse=False)
    >>> xv 
    array([[-1. , -0.5,  1. ,  4. ,  5. ],
           [-1. , -0.5,  1. ,  4. ,  5. ],
           [-1. , -0.5,  1. ,  4. ,  5. ]])
    >>> yv
    array([[ 0.,  0.,  0.,  0.,  0.],
           [-2., -2., -2., -2., -2.],
           [-5., -5., -5., -5., -5.]])
    >>> 
    !ec

    In addition to the reasons mentioned above, the meshgrid function in
    NumPy supports only Cartesian indexing, i.e., x and y, not matrix
    indexing, i.e., rows and columns (`mgrid` and `ogrid` supports only
    matrix indexing). The `meshgrid` function in SciTools supports both
    indexing conventions through the `indexing` keyword argument. Giving
    the string `'ij'` returns a meshgrid with matrix indexing, while
    `'xy'` returns a meshgrid with Cartesian indexing. The difference is
    illustrated by the following code snippet:
    !bc
    nx = 10
    ny = 15

    x = linspace(-2,2,nx)
    y = linspace(-2,2,ny)

    xv, yv = meshgrid(x, y, sparse=False, indexing='ij')
    for i in range(nx):
        for j in range(ny):
            # treat xv[i,j], yv[i,j]

    xv, yv = meshgrid(x, y, sparse=False, indexing='xy')
    for i in range(nx):
        for j in range(ny):
            # treat xv[j,i], yv[j,i]
    !ec

    It is not entirely true that matrix indexing is not supported by the
    `meshgrid` function in NumPy because we can just switch the order of
    the first two input and output arguments:
    !bc
    yv, xv = numpy.meshgrid(y, x)
    !ec
    is the same as
    !bc
    xv, yv = meshgrid(x, y, sparse=False, indexing='ij')
    !ec
    However, we think it is clearer to have the logical "x, y"
    sequence on the left-hand side and instead adjust a keyword argument.
    """

    import types
    def fixed(coor):
        return isinstance(coor, (float, complex, int, types.NoneType))

    if not fixed(x):
        x = asarray(x)
    if not fixed(y):
        y = asarray(y)
    if not fixed(z):
        z = asarray(z)
    
    def arr1D(coor):
        try:
            if len(coor.shape) == 1:
                return True
            else:
                return False
        except AttributeError:
            return False
    
    # if two of the arguments are fixed, we have a 1D grid, and
    # the third argument can be reused as is:

    if arr1D(x) and fixed(y) and fixed(z):
        return x
    if fixed(x) and arr1D(y) and fixed(z):
        return y
    if fixed(x) and fixed(y) and arr1D(z):
        return z

    # if x,y,z are identical, make copies:
    try:
        if y is x: y = x.copy()
        if z is x: z = x.copy()
        if z is y: z = y.copy()
    except AttributeError:  # x, y, or z not NumPy array
        pass

    if memoryorder is not None:
        import warnings
        msg = "Keyword argument 'memoryorder' is deprecated and will be " \
              "removed in the future. Please use the 'indexing' keyword " \
              "argument instead."
        warnings.warn(msg, DeprecationWarning)
        if memoryorder == 'xyz':
            indexing = 'ij'
        else:
            indexing = 'xy'
    
    # If the keyword argument sparse is set to False, the full N-D matrix
    # (not only the 1-D vector) should be returned. The mult_fact variable
    # should then be updated as necessary.
    mult_fact = 1

    # if only one argument is fixed, we have a 2D grid:
    if arr1D(x) and arr1D(y) and fixed(z):
        if indexing == 'ij':
            if not sparse:
                mult_fact = ones((len(x),len(y)))
            if z is None:
                return x[:,newaxis]*mult_fact, y[newaxis,:]*mult_fact
            else:
                return x[:,newaxis]*mult_fact, y[newaxis,:]*mult_fact, z
        else:
            if not sparse:
                mult_fact = ones((len(y),len(x)))
            if z is None:
                return x[newaxis,:]*mult_fact, y[:,newaxis]*mult_fact
            else:
                return x[newaxis,:]*mult_fact, y[:,newaxis]*mult_fact, z
        
    if arr1D(x) and fixed(y) and arr1D(z):
        if indexing == 'ij':
            if not sparse:
                mult_fact = ones((len(x),len(z)))
            if y is None:
                return x[:,newaxis]*mult_fact, z[newaxis,:]*mult_fact
            else:
                return x[:,newaxis]*mult_fact, y, z[newaxis,:]*mult_fact
        else:
            if not sparse:
                mult_fact = ones((len(z),len(x)))
            if y is None:
                return x[newaxis,:]*mult_fact, z[:,newaxis]*mult_fact
            else:
                return x[newaxis,:]*mult_fact, y, z[:,newaxis]*mult_fact
        
    if fixed(x) and arr1D(y) and arr1D(z):
        if indexing == 'ij':
            if not sparse:
                mult_fact = ones((len(y),len(z)))
            if x is None:
                return y[:,newaxis]*mult_fact, z[newaxis,:]*mult_fact
            else:
                return x, y[:,newaxis]*mult_fact, z[newaxis,:]*mult_fact
        else:
            if not sparse:
                mult_fact = ones((len(z),len(y)))
            if x is None:
                return y[newaxis,:]*mult_fact, z[:,newaxis]*mult_fact
            else:
                return x, y[newaxis,:]*mult_fact, z[:,newaxis]*mult_fact

    # or maybe we have a full 3D grid:
    if arr1D(x) and arr1D(y) and arr1D(z):
        if indexing == 'ij':
            if not sparse:
                mult_fact = ones((len(x),len(y),len(z)))
            return x[:,newaxis,newaxis]*mult_fact, \
                   y[newaxis,:,newaxis]*mult_fact, \
                   z[newaxis,newaxis,:]*mult_fact
        else:
            if not sparse:
                mult_fact = ones((len(y),len(x),len(z)))
            return x[newaxis,:,newaxis]*mult_fact, \
                   y[:,newaxis,newaxis]*mult_fact, \
                   z[newaxis,newaxis,:]*mult_fact

    # at this stage we assume that we just have scalars:
    l = []
    if x is not None:
        l.append(x)
    if y is not None:
        l.append(y)
    if z is not None:
        l.append(z)
    if len(l) == 1:
        return l[0]
    else:
        return tuple(l)


def ndgrid(*args,**kwargs):
    """
    Same as calling meshgrid with indexing='ij' (see meshgrid for
    documentation).
    """
    kwargs['indexing'] = 'ij'
    return meshgrid(*args,**kwargs)


def float_eq(a, b, rtol=1.0e-14, atol=1.0e-14):
    """
    Approximate test a==b for float variables.
    Returns true if abs(a-b) < atol + rtol*abs(b).
    atol comes into play when abs(b) is large.
    When a and b are NumPy arrays, NumPy's allclose function is called
    (but float_eq's default tolerances are much stricter than those of
    allclose).
    """
    if isinstance(a, float):
        return math.fabs(a-b) < atol + rtol*math.fabs(b)
    elif isinstance(a, complex):
        return float_eq(a.real, b.real, rtol, atol) and \
               float_eq(a.imag, b.imag, rtol, atol)
    else: # assume NumPy array
        try:
            return allclose(a, b, rtol, atol)
        except:
            raise TypeError, 'Illegal types: a is %s and b is %s' % \
                  (type(a), type(b))
    

def norm_l2(u):
    """
    l2 norm of a multi-dimensional array u viewed as a vector
    (norm=sqrt(dot(u.flat,u.flat))).
    """
    return math.sqrt(innerproduct(u.flat, u.flat))

def norm_L2(u):
    """
    L2 norm of a multi-dimensional array u viewed as a vector
    (norm=sqrt(dot(u.flat,u.flat)/n)).

    If u holds function values and the norm of u is supposed to
    approximate an integral (L2 norm) of the function, this (and
    not norm_l2) is the right norm function to use.
    """
    return norm_l2(u)/sqrt(float(size(u)))

def norm_l1(u):
    """
    l1 norm of a multi-dimensional array u viewed as a vector
    (norm=sum(abs(u.flat))).
    """
    return sum(abs(u.flat))

def norm_L1(u):
    """
    L1 norm of a multi-dimensional array u viewed as a vector
    (norm=sum(abs(u.flat))).

    If u holds function values and the norm of u is supposed to
    approximate an integral (L1 norm) of the function, this (and
    not norm_l1) is the right norm function to use.
    """
    return norm_l1(u)/float(size(u))

def norm_inf(u):
    """Infinity/max norm of a multi-dimensional array u viewed as a vector."""
    return abs(u).max()


def solve_tridiag_linear_system(A, b):
    """
    Solve a tridiagonal linear system of the form::
    
     A[0,1]*x[0] + A[0,2]*x[1]                                        = 0
     A[1,0]*x[0] + A[1,1]*x[1] + A[1,2]*x[2]                          = 0
     ...
     ...
              A[k,0]*x[k-1] + A[k,1]*x[k] + A[k,2]*x[k+1]             = 0
     ...
                  A[n-2,0]*x[n-3] + A[n-2,1]*x[n-2] + A[n-2,2]*x[n-1] = 0
     ...
                                    A[n-1,0]*x[n-2] + A[n-1,1]*x[n-1] = 0

    That is, the diagonal is stored in A[:,1], the subdiagonal
    is stored in A[1:,0], and the superdiagonal is stored in A[:n-2,2].
    """

    #The storage is not memory friendly in Python/C (diagonals stored
    #columnwise in A), but if A is sent to F77 for high-performance
    #computing, a copy is taken and the F77 routine works with the
    #same algorithm and hence optimal (columnwise traversal)
    #Fortran storage.
    
    n = len(b)
    x = zeros(n, 'd')  # solution
    # scratch arrays:
    d = zeros(n, 'd');  c = zeros(n, 'd');  m = zeros(n, 'd')

    d[0] = A[0,1]
    c[0] = b[0]

    for k in iseq(start=1, stop=n-1, inc=1):
        m[k] = A[k,0]/d[k-1]
        d[k] = A[k,1] - m[k]*A[k-1,2]
        c[k] = b[k] - m[k]*c[k-1]
    x[n-1] = c[n-1]/d[n-1]

    # back substitution:
    for k in iseq(start=n-2, stop=0, inc=-1):
        x[k] = (c[k] - A[k,2]*x[k+1])/d[k]

    return x




try:
    import Pmw
    class NumPy2BltVector(Pmw.Blt.Vector):
        """
        Copy a NumPy array to a BLT vector:
        # a: some NumPy array
        b = NumPy2BltVector(a)  # b is BLT vector
        g = Pmw.Blt.Graph(someframe)
        # send b to g for plotting
        """
        def __init__(self, array):
            Pmw.Blt.Vector.__init__(self, len(array))
            self.set(tuple(array))  # copy elements
except:
    class NumPy2BltVector:
        def __init__(self, array):
            raise ImportError, "Python is not compiled with BLT"

try:
    from scitools.StringFunction import StringFunction
except:
    pass  # wrap2callable may not work


class WrapNo2Callable:
    """Turn a number (constant) into a callable function."""
    def __init__(self, constant):
        self.constant = constant
        self._array_shape = None

    def __call__(self, *args):
        """
        >>> w = WrapNo2Callable(4.4)
        >>> w(99)
        4.4000000000000004
        >>> # try vectorized computations:
        >>> x = linspace(1, 4, 4)
        >>> y = linspace(1, 2, 2)
        >>> xv = x[:,NewAxis]; yv = y[NewAxis,:]
        >>> xv + yv
        array([[ 2.,  3.],
               [ 3.,  4.],
               [ 4.,  5.],
               [ 5.,  6.]])
        >>> w(xv, yv)
        array([[ 4.4,  4.4],
               [ 4.4,  4.4],
               [ 4.4,  4.4],
               [ 4.4,  4.4]])

        If you want to call such a function object with space-time
        arguments and vectorized expressions, make sure the time
        argument is not the first argument. That is,
        w(xv, yv, t) is fine, but w(t, xv, yv) will return 4.4,
        not the desired array!
        """
        if isinstance(args[0], (float, int, complex)):
            # scalar version:
            # (operator.isNumberType(args[0]) cannot be used as it is
            # true also for NumPy arrays
            return self.constant
        else: # assume NumPy array
            if self._array_shape is None:
                self._set_array_shape()
            else:
                r = self.constant*ones(self._array_shape, 'd')
                # could store r (allocated once) and just return reference
                return r

    def _set_array_shape(self, arg):
        # vectorized version:
        r = arg.copy()
        # to get right dimension of the return array,
        # compute with args in a simple formula (sum of args)
        for a in args[1:]:
            r = r + a  # in-place r+= won't work
            # (handles x,y,t - the last t just adds a constant)
            # an argument sequence t, x, y  will fail (1st arg
            # is not a NumPy array)
        self._array_shape = r.shape

    # The problem with this class is that, in the vectorized version,
    # the array shape is determined in the first call, i.e., later
    # calls may return an array with the wrong shape if the shape of
    # the input arguments change! Sometimes, when called along boundaries
    # of grids, the shape may change so the next implementation is
    # slower and safer.
    
class WrapNo2Callable:
    """Turn a number (constant) into a callable function."""
    def __init__(self, constant):
        self.constant = constant

    def __call__(self, *args):
        """
        >>> w = WrapNo2Callable(4.4)
        >>> w(99)
        4.4000000000000004
        >>> # try vectorized computations:
        >>> x = linspace(1, 4, 4)
        >>> y = linspace(1, 2, 2)
        >>> xv = x[:,NewAxis]; yv = y[NewAxis,:]
        >>> xv + yv
        array([[ 2.,  3.],
               [ 3.,  4.],
               [ 4.,  5.],
               [ 5.,  6.]])
        >>> w(xv, yv)
        array([[ 4.4,  4.4],
               [ 4.4,  4.4],
               [ 4.4,  4.4],
               [ 4.4,  4.4]])

        If you want to call such a function object with space-time
        arguments and vectorized expressions, make sure the time
        argument is not the first argument. That is,
        w(xv, yv, t) is fine, but w(t, xv, yv) will return 4.4,
        not the desired array!
               
        """
        if isinstance(args[0], (float, int, complex)):
            # scalar version:
            return self.constant
        else:
            # vectorized version:
            r = args[0].copy()
            # to get right dimension of the return array,
            # compute with args in a simple formula (sum of args)
            for a in args[1:]:
                r = r + a  # in-place r+= won't work
                # (handles x,y,t - the last t just adds a constant)
            r[:] = self.constant
            return r


class WrapDiscreteData2Callable:
    """
    Turn discrete data on a uniform grid into a callable function,
    i.e., equip the data with an interpolation function.

    >>> x = linspace(0, 1, 11)
    >>> y = 1+2*x
    >>> f = WrapDiscreteData2Callable((x,y))
    >>> # or just use the wrap2callable generic function:
    >>> f = wrap2callable((x,y))
    >>> f(0.5)   # evaluate f(x) by interpolation
    1.5
    >>> f(0.5, 0.1)  # discrete data with extra time prm: f(x,t)
    1.5
    """
    def __init__(self, data):
        self.data = data  # (x,y,f) data for an f(x,y) function
        from Scientific.Functions.Interpolation \
             import InterpolatingFunction # from ScientificPython
        self.interpolating_function = \
             InterpolatingFunction(self.data[:-1], self.data[-1])
        self.ndims = len(self.data[:-1])  # no of spatial dim.
        
    def __call__(self, *args):
        # allow more arguments (typically time) after spatial pos.:
        args = args[:self.ndims]
        # args can be tuple of scalars (point) or tuple of vectors
        if isinstance(args[0], (float, int, complex)):
            return self.interpolating_function(*args)
        else:
            # args is tuple of vectors; Interpolation must work
            # with one point at a time:
            r = [self.interpolating_function(*a) for a in zip(*args)]
            return array(r)  # wrap in NumPy array

        
def wrap2callable(f, **kwargs):
    """
    Allow constants, string formulas, discrete data points,
    user-defined functions and (callable) classes to be wrapped
    in a new callable function. That is, all the mentioned data
    structures can be used as a function, usually of space and/or
    time.
    (kwargs is used for string formulas)

    >>> f1 = wrap2callable(2.0)
    >>> f1(0.5)
    2.0
    >>> f2 = wrap2callable('1+2*x')
    >>> f2(0.5)
    2.0
    >>> f3 = wrap2callable('1+2*t', independent_variable='t')
    >>> f3(0.5)
    2.0
    >>> f4 = wrap2callable('a+b*t')
    >>> f4(0.5)
    Traceback (most recent call last):
    ...
    NameError: name 'a' is not defined
    >>> f4 = wrap2callable('a+b*t', independent_variable='t', \
                           a=1, b=2)
    >>> f4(0.5)
    2.0

    >>> x = linspace(0, 1, 3); y=1+2*x
    >>> f5 = wrap2callable((x,y))
    >>> f5(0.5)
    2.0
    >>> def myfunc(x):  return 1+2*x
    >>> f6 = wrap2callable(myfunc)
    >>> f6(0.5)
    2.0
    >>> f7 = wrap2callable(lambda x: 1+2*x)
    >>> f7(0.5)
    2.0
    >>> class MyClass:
            'Representation of a function f(x; a, b) =a + b*x'
            def __init__(self, a=1, b=1):
                self.a = a;  self.b = b
            def __call__(self, x):
                return self.a + self.b*x
    >>> myclass = MyClass(a=1, b=2)
    >>> f8 = wrap2callable(myclass)
    >>> f8(0.5)
    2.0
    >>> # 3D functions:
    >>> f9 = wrap2callable('1+2*x+3*y+4*z', \
                           independent_variables=('x','y','z'))
    >>> f9(0.5,1/3.,0.25)
    4.0
    >>> # discrete 3D data:
    >>> y = linspace(0, 1, 3); z = linspace(-1, 0.5, 16)
    >>> xv = reshape(x, (len(x),1,1))
    >>> yv = reshape(y, (1,len(y),1))
    >>> zv = reshape(z, (1,1,len(z)))
    >>> def myfunc3(x,y,z):  return 1+2*x+3*y+4*z

    >>> values = myfunc3(xv, yv, zv)
    >>> f10 = wrap2callable((x, y, z, values))
    >>> f10(0.5, 1/3., 0.25)
    4.0

    One can also check what the object is wrapped as and do more
    specific operations, e.g.,
    
    >>> f9.__class__.__name__
    'StringFunction'
    >>> str(f9)     # look at function formula
    '1+2*x+3*y+4*z'
    >>> f8.__class__.__name__
    'MyClass'
    >>> f8.a, f8.b  # access MyClass-specific data
    (1, 2)

    Troubleshooting regarding string functions:
    If you use a string formula with a NumPy array, you typically get
    error messages like::
        
       TypeError: only rank-0 arrays can be converted to Python scalars.
    
    You must then make the right import (numpy is recommended)::

       from Numeric/numarray/numpy/scitools.numpytools import *
       
    in the calling code and supply the keyword argument::
        
       globals=globals()
       
    to wrap2callable. See also the documentation of class StringFunction
    for more information.
    """
    if isinstance(f, str):
        return StringFunction(f, **kwargs)
        # this is a considerable optimization (up to a factor of 3),
        # but then the additional info in the StringFunction instance
        # is lost in the calling code:
        # return StringFunction(f, **kwargs).__call__
    elif isinstance(f, (float, int, complex)):
        return WrapNo2Callable(f)
    elif isinstance(f, (list,tuple)):
        return WrapDiscreteData2Callable(f)
    elif operator.isCallable(f):
        return f
    else:
        raise TypeError, 'f of type %s is not callable' % type(f)


# problem: setitem in ArrayGen does not support multiple indices
# relying on inherited __setitem__ works fine

def NumPy_array_iterator(a, **kwargs):
    """
    Iterate over all elements in a NumPy array a.
    Return values: generator function and the code of this function.
    The numpy.ndenumerate iterator performs the same iteration over
    an array, but NumPy_array_iterator has some additional features
    (especially handy for coding finite difference stencils, see next
    paragraph).

    The keyword arguments specify offsets in the start and stop value
    of the index in each dimension. Legal values are
    offset0_start, offset0_stop, offset1_start, offset1_stop, etc.
    Also offset_start and offset_stop are legal keyword arguments,
    these imply the same offset value for all dimensions.

    Another keyword argument is no_value, which can be True or False.
    If the value is True, the iterator returns the indices as a tuple,
    otherwise (default) the iterator returns a two-tuple consisting of
    the value of the array and the corresponding indices (as a tuple).
    
    Examples::
    
    >>> q = linspace(1, 2*3*4, 2*3*4);  q.shape = (2,3,4)
    >>> it, code = NumPy_array_iterator(q)
    >>> print code  # generator function with 3 nested loops:
    def nested_loops(a):
        for i0 in xrange(0, a.shape[0]-0):
            for i1 in xrange(0, a.shape[1]-0):
                for i2 in xrange(0, a.shape[2]-0):
                    yield a[i0, i1, i2], (i0, i1, i2)
    >>> type(it)
    <type 'function'>
    >>> for value, index in it(q):
    ...     print 'a%s = %g' % (index, value)
    ...
    a(0, 0, 0) = 1
    a(0, 0, 1) = 2
    a(0, 0, 2) = 3
    a(0, 0, 3) = 4
    a(0, 1, 0) = 5
    a(0, 1, 1) = 6
    a(0, 1, 2) = 7
    a(0, 1, 3) = 8
    a(0, 2, 0) = 9
    a(0, 2, 1) = 10
    a(0, 2, 2) = 11
    a(0, 2, 3) = 12
    a(1, 0, 0) = 13
    a(1, 0, 1) = 14
    a(1, 0, 2) = 15
    a(1, 0, 3) = 16
    a(1, 1, 0) = 17
    a(1, 1, 1) = 18
    a(1, 1, 2) = 19
    a(1, 1, 3) = 20
    a(1, 2, 0) = 21
    a(1, 2, 1) = 22
    a(1, 2, 2) = 23
    a(1, 2, 3) = 24

    Here is the version where only the indices and no the values
    are returned by the iterator::

    >>> q = linspace(1, 1*3, 3);  q.shape = (1,3)
    >>> it, code = NumPy_array_iterator(q, no_value=True)
    >>> print code
    def nested_loops(a):
        for i0 in xrange(0, a.shape[0]-0):
            for i1 in xrange(0, a.shape[1]-0):
                yield i0, i1
    >>> for i,j in it(q):
    ...   print i,j
    0 0
    0 1
    0 2
    

    Now let us try some offsets::

    >>> it, code = NumPy_array_iterator(q, offset1_stop=1, offset_start=1)
    >>> print code
    def nested_loops(a):
        for i0 in xrange(1, a.shape[0]-0):
            for i1 in xrange(1, a.shape[1]-1):
                for i2 in xrange(1, a.shape[2]-0):
                    yield a[i0, i1, i2], (i0, i1, i2)
    >>> # note: the offsets appear in the xrange arguments
    >>> for value, index in it(q):
    ...     print 'a%s = %g' % (index, value)
    ...
    a(1, 1, 1) = 18
    a(1, 1, 2) = 19
    a(1, 1, 3) = 20
    """
    # build the code of the generator function in a text string
    # (since the number of nested loops needed to iterate over all
    # elements are parameterized through len(a.shape))
    dims = range(len(a.shape))
    offset_code1 = ['offset%d_start=0' % d for d in dims]
    offset_code2 = ['offset%d_stop=0'  % d for d in dims]
    for d in range(len(a.shape)):
        key1 = 'offset%d_start' % d
        key2 = 'offset%d_stop' % d
        if key1 in kwargs:
            offset_code1.append(key1 + '=' + str(kwargs[key1]))
        if key2 in kwargs:
            offset_code2.append(key2 + '=' + str(kwargs[key2]))
        
    for key in kwargs:
        if key == 'offset_start':
            offset_code1.extend(['offset%d_start=%d' % (d, kwargs[key]) \
                            for d in range(len(a.shape))])
        if key == 'offset_stop':
            offset_code2.extend(['offset%d_stop=%d' % (d, kwargs[key]) \
                            for d in range(len(a.shape))])

    no_value = kwargs.get('no_value', False)

    for line in offset_code1:
        exec line
    for line in offset_code2:
        exec line
    code = 'def nested_loops(a):\n'
    indentation = ' '*4
    indent = '' + indentation
    for dim in range(len(a.shape)):
        code += indent + \
        'for i%d in xrange(%d, a.shape[%d]-%d):\n' \
                % (dim, eval('offset%d_start' % dim),
                   dim, eval('offset%d_stop' % dim))
        indent += indentation
    index = ', '.join(['i%d' % d for d in range(len(a.shape))])
    if no_value:
        code += indent + 'yield ' + index
    else:
        code += indent + 'yield ' + 'a[%s]' % index + ', (' + index + ')'
    exec code
    return nested_loops, code

def compute_histogram(samples, nbins=50, piecewise_constant=True):
    """
    Given a NumPy array samples with random samples, this function
    returns the (x,y) arrays in a plot-ready version of the histogram.
    If piecewise_constant is True, the (x,y) arrays gives a piecewise
    constant curve when plotted, otherwise the (x,y) arrays gives a
    piecewise linear curve where the x coordinates coincide with the
    center points in each bin.
    """
    # old primitive code based on ScientificPython:
    #from Scientific.Statistics.Histogram import Histogram
    #h = Histogram(samples, nbins)
    #h.normalizeArea() # let h be a density (unit area)
    #print h.array[:,0], '\n', h.array[:,1]
    #return h.array[:,0], h.array[:,1]
    # new code based on numpy:
    import sys
    if 'numpy' in sys.modules:
        y0, xleft = histogram(samples, bins=nbins, normed=True)
        h = xleft[1] - xleft[0]  # bin width
        if piecewise_constant:
            x = zeros(2*len(xleft) + 2, type(xleft[0]))
            y = x.copy()
            for i in range(len(xleft)):
                x[2*i+1] = xleft[i]
                x[2*i+2] = xleft[i] + h
                y[2*i+1] = y0[i]
                y[2*i+2] = y0[i]
            y[0] = 0
            x[0] = xleft[0]
            y[-1] = 0
            y[-2] = y0[-1]
            x[-1] = xleft[-1] + h
            x[-2] = x[-1]
        else:
            x = zeros(len(xleft), type(xleft[0]))
            y = y0.copy()
            for i in range(len(xleft)):
                x[i] = xleft[i] + h/2.0
    return x, y

        

def factorial(n, method='reduce'):
    """
    Compute the factorial n! using long integers.
    Different implementations are available
    (see source code for the methods).

    Here is an efficiency comparison of the methods (computing 80!):
    reduce                    |     1.00
    lambda list comprehension |     1.70
    lambda functional         |     3.08
    plain recursive           |     5.83
    lambda recursive          |    21.73
    scipy                     |   131.18
    """
    if not isinstance(n, (int, long, float)):
        raise TypeError, 'factorial(n): n must be integer not %s' % type(n)
    n = long(n)

    if n == 0 or n == 1:
        return 1

    if method == 'plain iterative':
        f = 1
        for i in range(1, n+1):
            f *= i
        return f
    elif method == 'plain recursive':
        if n == 1:
            return 1
        else:
            return n*factorial(n-1, method)
    elif method == 'lambda recursive':
        fc = lambda n: n and fc(n-1)*long(n) or 1
        return fc(n)
    elif method == 'lambda functional':
        fc = lambda n: n<=0 or \
             reduce(lambda a,b: long(a)*long(b), xrange(1,n+1))
        return fc(n)
    elif method == 'lambda list comprehension':
        fc = lambda n: [j for j in [1] for i in range(2,n+1) \
                        for j in [j*i]] [-1]
        return fc(n)
    elif method == 'reduce':
        return reduce(operator.mul, xrange(2, n+1))
    elif method == 'scipy':
        try:
            import scipy.misc.common as sc
            return sc.factorial(n)
        except ImportError:
            print 'numpyutils.factorial: scipy is not available'
            print 'default method="reduce" is used instead'
            return reduce(operator.mul, xrange(2, n+1))
            # or return factorial(n)
    else:
        raise ValueError, 'factorial: method="%s" is not supported' % method



    
    

#---- build doc string from numpyload/util doc strings ----

import numpyload as _load
_load.__doc__ += """

Example on what gets imported
-----------------------------

(basic_NumPy holds the name of the Numeric
Python module after import of numpytools (or numpyload):

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

import numpyutils as _utils
# insert numpyutils and numpyload documentation into the
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
        import numpytools as N
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
    import numpytools as N

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
                raise AssertionError, \
                      "Meshgrid failed with arraytype mix of  Numeric and %s"\
                      %N.basic_NumPy
            import numarray
            x = numarray.arange(10)
            X, Y, Z = N.meshgrid(x, y, z, sparse=False)

            if not  N.rank(X) == 3:
                raise AssertionError, \
                      "Meshgrid failed with arraytype mix of numarray and %s"\
                      %N.basic_NumPy

            import numpy
            x = numpy.arange(10)
            X, Y, Z = N.meshgrid(x, y, z, sparse=False)
            #assert N.rank(X) == 3
            if not  N.rank(X) == 3:
                raise AssertionError, \
                      "Meshgrid failed with arraytype mix of numpy and %s"\
                      %N.basic_NumPy
            
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
