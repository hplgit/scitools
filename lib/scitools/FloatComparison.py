import numpy, math, operator

class FloatComparison:
    """
    Class FloatComparison is used to test
    a == b, a < b, a <= b, a > b, a >= b and a != b
    when a and b are floating-point numbers, complex numbers,
    or NumPy arrays.

    Because of possible round-off errors in the numbers, the tests are
    performed approximately with a prescribed tolerance.

    For example, a==b is true if abs(a-b) < atol + rtol*abs(b).
    The atol parameter comes into play when |a| and |b| are large.
    (It would be mathematically more appealing to have
    rtol*max(abs(a), abs(b)), but float_eq is used with a is
    close to b so the max function is not necessary.)

    If the desired test is |a-b| < eps, set atol=eps and rtol=0.
    If a relative test is wanted, |(a-b)/b| < eps, set atol=0
    and rtol=eps.

    The test a < b is performed as a < b + atol (a can be
    larger than b, but not more than atol).
    A corresponding relative test reads a/abs(b) < 1 + rtol.
    These are combined into a common test a < b + atol + rtol*abs(b).
    Similarly, a > b if a > b - atol (i.e., a can be less than b,
    but not less than b-atol). The relative test is then
    a/abs(b) > 1 - rtol. These are combined to
    a > b - a tol - rtol*abs(b). The >= and <= operators
    are the same as > and < when tolerances are used.

    Class FloatComparison can be used directly, or the convenience
    names float_eq, float_ne, float_lt, float_le, float_gt and float_ge
    for the various operators can be used instead. For example,
    float_eq is a FloatComparison object for the equality operator.

    Here is an interactive example::

    >>> from FloatComparison import FloatComparison, float_eq, \
             float_ne, float_lt, float_le, float_gt, float_ge
    >>> float_eq.get_absolute_tolerance()   # default
    1e-14
    >>> float_eq.get_relative_tolerance()   # default
    1e-14
    >>> float_eq.set_absolute_tolerance(1E-2)
    >>> float_eq.set_relative_tolerance(1E-2)
    >>> print float_eq
    a == b, computed as abs(a-b) < 0.01 + 0.01*abs(b)
    >>>
    >>> float_eq(2.1, 2.100001)
    True
    >>> # tolerances can be given as part of the test:
    >>> float_ne(2.1, 2.100001, atol=1E-14, rtol=1E-14)
    True

    >>> float_gt(2.0999999, 2.1000001)      # not greater with strict tol
    False
    >>> print float_gt
    a > b, computed as a > b - 1e-14 - 1e-14*abs(b)
    >>> float_gt.set_absolute_tolerance(1E-4)
    >>> print float_gt
    a > b, computed as a > b - 0.0001 - 1e-14*abs(b)
    >>> float_gt(2.0999999, 2.1000001)      # greater with less strict tol
    True

    >>> import numpy
    >>> a = numpy.array([2.1,      2.1000001])
    >>> b = numpy.array([2.100001, 2.0999999])
    >>> float_eq(a, b)
    True
    >>> float_lt(a, b)  # not less with strict tol
    False
    >>> float_lt(a, b, atol=1E-2, rtol=1E-2)
    True

    >>> # use class FloatComparison directly:
    >>> compare = FloatComparison('==', atol=1E-3, rtol=1E-3)
    >>> compare(2.1, 2.100001)     # __call__ directs to compare.eq
    True
    >>> compare.gt(2.1, 2.100001)  # same tolerance
    True
    >>> compare.ge(a, b)
    False

    The __call__ method calls eq, ne, lt, le, gt, or ge, depending on
    the first argument to the constructor.
    """
    # rtol and atol are static attributes so that changing
    # tolerances in e.g. the float_eq object also changes
    # the tolerances in all other comparison objects (float_lt, etc.).
    rtol = 1E-14
    atol = 1E-14

    def __init__(self, operation='==', rtol=1E-14, atol=1E-14):
        """
        operation is '==', '<', '<=', '>', '>=' or '!='.
        The value determines what operation that __call__ performs.

        rtol: relative tolerance, atol: absolute tolerance.
        a==b is true if abs(a-b) < atol + rtol*abs(b).
        atol comes into play when abs(b) is large.
        """
        comparisons = {'==': self.eq,
                       '!=': self.ne,
                       '<' : self.lt,
                       '<=': self.le,
                       '>' : self.gt,
                       '>=': self.ge}
        if operation in comparisons:
            self.operation = comparisons[operation]
        else:
            raise ValueError('Wrong operation "%s"' % operation)
        self.comparison_op = operation  # nice to store for printouts/tests

        FloatComparison.rtol, FloatComparison.atol = rtol, atol

    def __call__(self, a, b, rtol=None, atol=None):
        """
        Compares a with b: a == b, a!= b, a < b, etc., depending
        on how this FloatComparison was initialized.
        a and b can be numbers or arrays. The comparison is actually
        performed in the methods eq, ne, lt, le, etc.
        """
        return self.operation(a, b, rtol, atol)

    def eq(self, a, b, rtol=None, atol=None):
        """Tests a == b with tolerance."""
        if rtol is None: rtol = FloatComparison.rtol
        if atol is None: atol = FloatComparison.atol
        if isinstance(a, (float, int)):
            return math.fabs(a-b) < atol + rtol*math.fabs(b)
        elif isinstance(a, complex):
            return self.eq(a.real, b.real, rtol, atol) and \
                   self.eq(a.imag, b.imag, rtol, atol)
        else: # assume NumPy array, tuple or list
            try:
                return numpy.allclose(numpy.asarray(a),
                                      numpy.asarray(b),
                                      rtol, atol)
                #r = numpy.abs(a-b) < atol + rtol*numpy.abs(b)
                #return r.all()
            except Exception as e:
                raise TypeError('Illegal types: a is %s and b is %s' % \
                                (type(a), type(b)))

    def ne(self, a, b, rtol=None, atol=None):
        """Tests a != b with tolerance."""
        return not self.eq(a, b, rtol, atol)

    def set_absolute_tolerance(self, atol):
        FloatComparison.atol = atol

    def set_relative_tolerance(self, rtol):
        FloatComparison.rtol = rtol

    def get_absolute_tolerance(self):
        return FloatComparison.atol

    def get_relative_tolerance(self):
        return FloatComparison.rtol

    def lt(self, a, b, rtol=None, atol=None):
        """Tests a < b with tolerance."""
        if rtol is None: rtol = FloatComparison.rtol
        if atol is None: atol = FloatComparison.atol
        if isinstance(a, (float, int)):
            return operator.lt(a, b + atol + rtol*math.fabs(b))
        elif isinstance(a, complex):
            return self.lt(a.real, b.real, op, rtol, atol) and \
                   self.lt(a.imag, b.imag, op, rtol, atol)
        else: # assume NumPy array
            try:
                r = a < b + atol + rtol*abs(b)
                return r.all()  # all must be true
            except:
                raise TypeError('Illegal types: a is %s and b is %s' % \
                                (type(a), type(b)))

    def le(self, a, b, rtol=None, atol=None):
        """Tests a <= b with tolerance."""
        return self.lt(a, b, rtol, atol)

    def gt(self, a, b, rtol=None, atol=None):
        """Tests a > b with tolerance."""
        if rtol is None: rtol = FloatComparison.rtol
        if atol is None: atol = FloatComparison.atol
        if isinstance(a, (float, int)):
            return operator.gt(a, b - atol - rtol*math.fabs(b))
        elif isinstance(a, complex):
            return self.gt(a.real, b.real, op, rtol, atol) and \
                   self.gt(a.imag, b.imag, op, rtol, atol)
        else: # assume NumPy array
            try:
                r = a > b - atol - rtol*abs(b)
                return r.all()  # all must be true
            except:
                raise TypeError('Illegal types: a is %s and b is %s' % \
                                (type(a), type(b)))

    def ge(self, a, b, rtol=None, atol=None):
        """Tests a >= b with tolerance."""
        return self.gt(a, b, rtol, atol)

    def __str__(self):
        """Return pretty print of operator, incl. tolerances."""
        if self.comparison_op == '==':
            s = 'a == b, computed as abs(a-b) < %g + %g*abs(b)' % \
                (FloatComparison.atol, FloatComparison.rtol)
        elif self.comparison_op == '!=':
            s = 'a != b, computed as abs(a-b) > %g + %g*abs(b)' % \
                (FloatComparison.atol, FloatComparison.rtol)
        elif '>' in self.comparison_op:
            s = 'a %s b, computed as a > b - %g - %g*abs(b)' % \
                (self.comparison_op, FloatComparison.atol, FloatComparison.rtol)
        elif '<' in self.comparison_op:
            s = 'a %s b, computed as a < b + %g + %g*abs(b)' % \
                (self.comparison_op, FloatComparison.atol, FloatComparison.rtol)
        return s

# define convenience functions for quicker use of class FloatComparison:
float_eq = FloatComparison('==')
float_eq.__doc__ = '    Test if a == b within some tolerance.\n' + \
                   FloatComparison.__doc__
float_ne = FloatComparison('!=')
float_ne.__doc__ = '    Test if a != b within some tolerance.\n' + \
                   FloatComparison.__doc__
float_lt = FloatComparison('<')
float_lt.__doc__ = '    Test if a < b within some tolerance.\n' + \
                   FloatComparison.__doc__
float_le = FloatComparison('<=')
float_le.__doc__ = '    Test if a <= b within some tolerance.\n' + \
                   FloatComparison.__doc__
float_gt = FloatComparison('>')
float_gt.__doc__ = '    Test if a > b within some tolerance.\n' + \
                   FloatComparison.__doc__
float_ge = FloatComparison('>=')
float_ge.__doc__ = '    Test if a >= b within some tolerance.\n' + \
                   FloatComparison.__doc__

def _test():
    """Verify FloatComparison functions."""
    a = 2.3
    b1 = 2.30000001
    b2 = 2.29999998

    a_a  = numpy.array([a,  a+1])
    a_b1 = numpy.array([b1, b1+1])
    a_b2 = numpy.array([b2, b2+1])

    funcs = [float_eq, float_ne, float_lt, float_le, float_gt, float_ge]
    for f in funcs:
        f.set_absolute_tolerance(1E-4)
        f.set_relative_tolerance(1E-4)

    print 'atol=%g, rtol=%g' % (float_eq.atol, float_eq.rtol)

    def printout(f):
        r1 = f(a, b1)
        print str(f) + ', a=%.16f, b=%.16f: ' % (a, b1) + str(r1)
        r2 = f(a, b2)
        print str(f) + ', a=%.16f, b=%.16f: ' % (a, b2) + str(r2)
        r3 = f(a_a, a_b1)
        print str(f) + ', a=%s, b=%s: ' % (a_a, a_b1) + str(r3)
        r4 = f(a_a, a_b2)
        print str(f) + ', a=%s, b=%s: ' % (a_a, a_b2) + str(r4)
        return r1, r2, r3, r4

    ok = True
    for f in funcs:
        res = printout(f)
        if f != float_ne:
            if False in res:
                ok = False
        else:
            if True in res:
                ok = False
    msg = 'works' if ok else 'does not work'
    print '\nThe module', msg


if __name__ == '__main__':
    _test()
