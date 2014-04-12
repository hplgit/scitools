#!/usr/bin/env python
"""Make a string with a mathematical expression behave as a Python function."""
from __future__ import division

# Default import of mathematical functions (in case the user
# supplies expressions with math functions and does not provide
# a globals keyword to the constructor with appropriate modules
# defining these math functions):
# from math import *
math_functions = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos',
                  'cosh', 'exp', 'fabs', 'floor', 'log', 'log10',
                  'pi', 'pow', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
s = 'from math import ' + ', '.join(math_functions)
exec(s)
# Problem: vectorized expressions require NumPy versions
# of the math functions. We try to detect errors arising from
# such lacking imports.

# The first edition of the "Python for Computational Science" book
# introduced the classes StringFunction1x, StringFunction1, and
# StringFunction. These are now (for the second edition) named
# StringFunction_v3, StringFunction_v4, and StringFunction_v5,
# respectively.


# The following implementation of StringFunction is an
# improved version compared to the one explained in the
# first edition of the book "Python for Computational Science".
# The new version is created by Mario Pernici <Mario.Pernici@mi.infn.it>
# and Hans Petter Langtangen <hpl@simula.no>. The basic idea is to
# build a lambda function out of the string expression and define
# self.__call__ to be this lambda function.

import re

class StringFunction:
    """
    Representation of a string formula as a function of one or
    more variables, optionally with parameters.

    Example on usage:

    >>> from scitools.StringFunction import StringFunction
    >>> f = StringFunction('1+sin(2*x)')
    >>> f(1.2)
    1.6754631805511511

    >>> f = StringFunction('1+sin(2*t)', independent_variable='t')
    >>> f(1.2)
    1.6754631805511511

    >>> f = StringFunction('1+A*sin(w*t)', independent_variable='t', \
                           A=0.1, w=3.14159)
    >>> f(1.2)
    0.94122173238695939
    >>> f.set_parameters(A=1, w=1)
    >>> f(1.2)
    1.9320390859672263

    >>> f(1.2, A=2, w=1)   # can also set parameters in the call
    2.8640781719344526

    >>> # function of two variables:
    >>> f = StringFunction('1+sin(2*x)*cos(y)', \
                           independent_variables=('x','y'))
    >>> f(1.2,-1.1)
    1.3063874788637866

    >>> f = StringFunction('1+V*sin(w*x)*exp(-b*t)', \
                           independent_variables=('x','t'))
    >>> f.set_parameters(V=0.1, w=1, b=0.1)
    >>> f(1.0,0.1)
    1.0833098208613807
    >>> str(f)  # print formula with parameters substituted by values
    '1+0.1*sin(1*x)*exp(-0.1*t)'
    >>> repr(f)
    "StringFunction('1+V*sin(w*x)*exp(-b*t)', independent_variables=('x', 't'), b=0.10000000000000001, w=1, V=0.10000000000000001)"

    >>> # vector field of x and y:
    >>> f = StringFunction('[a+b*x,y]', \
                           independent_variables=('x','y'))
    >>> f.set_parameters(a=1, b=2)
    >>> f(2,1)  # [1+2*2, 1]
    [5, 1]

    StringFunction expressions may contain fractions like 1/2 and these
    always result in float division (not integer division). Here is
    an example:

    >>> from scitools.StringFunction import StringFunction
    >>> f = StringFunction('1/4 + 1/2*x')
    >>> f(2)
    1.25


    The string parameter can, instead of a valid Python expression,
    be a function in a file (module). The string is then the
    complete path to the function, typically of the form
    somepackage.somemodule.function_name. This functionality is useful
    when simple string formulas cannot describe the function, e.g., when
    there are multiple if-branches inside the function expression.

    As an example, there is a function called _test_function::

        def _test_function(x, c=0, a=1, b=2):
            if x > c:
                return a*(x-c) + b
            else:
                return -a*(x-c) + b

    in the module scitools.misc (i.e., the misc.py file in the scitools
    package). We can then specify the complete path of this function
    as "string expression":

    >>> f = StringFunction('scitools.misc._test_function', independent_variable='x', a=10)
    >>> f(4)  # 10*(4-0) + 2 = 42
    42

    (Note that in Python 2.5 the _test_function can be coded as a
    simple string expression a*(x-c)+b if x > c else -a*(x-c)+b.)

    Giving the name of a function in a file (module) is convenient in
    user interfaces because the user can then write the name of
    the function as a standard Python module.function path. StringFunction
    turns this name, as a string, into a working module.function path.

    Troubleshooting:

    1)
    The StringFunction class can work with sin, cos, exp, and other
    mathematical functions if the argument is a scalar (float or int) type.
    If the argument is a vector, the NumPy versions of sin, cos,
    exp, etc., are needed. A common error message in the latter case is::

       TypeError: only rank-0 arrays can be converted to Python scalars.

    Make something like::

       from numpy import *
       # or
       from scitools.std import *
       # or
       from numpy import sin, cos

    in the calling code and supply globals=globals() as argument to
    the constructor::

       f = StringFunction('cos(x)*sin(y)', independent_variables=('x', 'y'),
                          globals=globals())
       # f(p,q) will now work for NumPy arrays p and q.

    You can also omit the globals argument when constructing the
    StringFunction and later call
    f.vectorize(globals())
    to allow array arguments.

    2) StringFunction builds a lambda function and evaluates this.
    You can see the lambda function as a string by accessing the
    _lambda attribute.
    """
    def __init__(self, expression, **kwargs):
        self._f = str(expression)  # ensure a string

        # check if expression is a function in a module:
        self._function_in_module = None

        # a module function specification is on the form
        # [A-Za-z_][A-Za-z0-9_.]x where x+1 is the len(expression)
        # but there MUST be a dot in there
        pattern = r'[A-Za-z_][A-Za-z0-9_.]{%d}' % (len(expression)-1)
        if "." in expression:
            if re.search(pattern, expression):
                parts = expression.split('.')
                module = '.'.join(parts[:-1])
                function = parts[-1]
                self._function_in_module = (module, function)

        # self._var holds the independent variables in a tuple:
        if 'independent_variable' in kwargs:  # allow "variable" and "variables"
            # note that tuple(string) gives a tuple of the characters
            # so we need to be careful (if the indep. var has more than
            # one character)
            name = kwargs['independent_variable'] # 'x', 't', 'dudt' etc.
            if not isinstance(name, str):
                raise ValueError(
                    'name "%s" of independent variable is illegal' % name)
            self._var = (name,)
        else:
            names = kwargs.get('independent_variables', ('x',))
            if isinstance(names, str):
                names = (names,)
            elif not isinstance(names, (list,tuple)):
                raise ValueError(
                    'independent variables=%s is invalid' % names)
            self._var = tuple(names)

        # user's globals() array (with relevant imported modules/functions):
        if 'globals' in kwargs:
            if kwargs['globals'] is None:
                self._globals = globals()
            else:
                self._globals = kwargs['globals']
        else:
            self._globals = globals()

        self._prms = kwargs.copy()
	try:    del self._prms['independent_variable']
        except: pass
        try:    del self._prms['independent_variables']
        except: pass
        try:    del self._prms['globals']
        except: pass
        try:
            # may fail if not all parameters are defined yet
            self._build_lambda()
        except NameError as e:
            #print e
            pass # ok at this stage: parameters might be missing

    def _build_lambda(self):
        """
        Translate the expression to a lambda function taking the
        independent variables as positional arguments and the
        parameters as keyword arguments.
        The idea is due to Mario Pernici <Mario.Pernici@mi.infn.it>.
        """
        args = ', '.join(self._var)
        s = 'lambda ' + args

        # add parameters as keyword arguments:
        if self._prms:
            kwargs = ', '.join(['%s=%s' % (k, self._prms[k]) \
                                for k in self._prms])
            s += ', ' + kwargs
        else:
            kwargs = ''

        if self._function_in_module is None:
            # insert string expression as body in the lambda function:
            s += ': ' + self._f
        else:
            exec('import ' + self._function_in_module[0])
            # let lambda call a function in a file (module):
            s += ', module=%s: module.%s(%s, %s)' % \
                 (self._function_in_module[0],
                  self._function_in_module[1],
                  args, kwargs)
            # note: we could use self._f directly here (giving the
            # full module path), but then we need to do import first,
            # all this is done in the __init__ and then it is simpler
            # to just let self_function_in_module point to the imported
            # function

        self._lambda = s # store lambda function code; just for convenience

        try:
            if self._function_in_module is None:
                try:
                    self.__call__ = eval(s, self._globals)
                except Exception as e:
                    print """
Making StringFunction with formula %s failed!
Tried to build a lambda function:\n %s""" % (self._f, s)
                    raise e

                ## the following makes all instances have the same function :-(
                ##StringFunction.__call__ = eval(s, self._globals)
            else:
                # didn't work with self._globals...and we don't need it...????
                self.__call__ = eval(s, globals(), locals())
                #self.__call__ = eval(s)
                #print 'call is', self.__call__

        except NameError as e:
            prm = str(e).split()[1]
            raise NameError('name "%s" is not defined - if it is '\
                  'a parameter,\nset it in the constructor or the '\
                  'set_parameters method, or provide\nglobals=globals() '\
                  'in the constructor if "%s" is a global name in the '\
                  'calling code.' % (prm, prm))


    def set_parameters(self, **kwargs):
        """Set keyword parameters in the function."""
        self._prms.update(kwargs)
        self._build_lambda()

    def vectorize(self, globals_dict):
        """
        Allow the StringFunction object to take NumPy array
        arguments. The calling code must have done a
        from numpy import * or similar and send the globals()
        dictionary as the argument globals_dict.
        Alternatively, the globals() dictionary can be supplied
        as a globals keyword argument to the constructor.
        """
        self._globals = globals_dict
        self._build_lambda()

    def troubleshoot(self, *args, **kwargs):
        """
        Perform function evaluation call with lots of testing to
        try to help the user with problems.
        """
        try:
            v = self(*args, **kwargs)
        except TypeError as e:
            if str(e).find('only rank-0 arrays can be converted to Python scalars') != -1:

                print '\nThe call resulted in the exception TypeError:'
                print e

                # *args contains NumPy arrays and the operations in
                # the string formula are not compatible

                # do we have intrinsic math functions of wrong type?
                math_funcs = False; not_NumPy = False
                for f in math_functions:
                    if self._f.find(f) != -1:
                        math_funcs = True
                        if str(type(f))[7:-2] != 'ufunc':
                            not_NumPy = True
                        break
                if math_funcs and not_NumPy:
                    print '\nThis message is caused by using scalar math\n'\
                          'functions (like %s) with array arguments.\n'\
                          'Make some\nfrom numarray import *\n'\
                          'or similar in the calling code and '\
                          'supply the globals=globals() constructor\n'\
                          'argument when creating the StringFunction instance.'\
                          % f
                else:
                    print 'Internal error - this should not happen...'
            else:
                print e
        except NameError as e:
            print e
        else:
            print 'This call worked perfectly!'

    def __str__(self):
        """
        Return the string function formula as a string, with
        parameters substituted by their values.

        The return value can be used when creating Fortran or C/C++
        functions out of the string formula:
        f = StringFunction('a + p*x', a=1, p=0)
        somefile.write('double somefunc(double x) { return %s; }' % str(f))
        """
        s = self._f  # formula with parameter names and indep. variables

        # Substitute parameter names by their numerical values.
        # Start with the most complicated parameter names
        # Improvement by Eigil Skjaelveland <eigilhs@student.matnat.uio.no>.
        prm_names = list(self._prms.keys())
        prm_names.sort(key=len, reverse=1)
        for name in prm_names:
            s = re.sub(r'([^a-z_])' + name + '([^a-z_])',
                       r'\1{0}\2', s).format(str(self._prms[name]))
        return s

    def __repr__(self):
        """Return the code required to reconstruct this instance."""
        kwargs = ', '.join(['%s=%s' % (key, repr(value)) \
                            for key, value in self._prms.items()])
        return """StringFunction(%s, independent_variables=%s, %s)""" % \
               (repr(self._f), repr(self._var), kwargs)

    # The next code generation functions work only for scalar
    # function values, not vector values (can extend to vectors by
    # checking if self._f has a list form, and then include the
    # return value as an array argument in the functions).

    def _no_of_vector_components(self):
        """
        Return the number of vector components in the string
        expression.
        """
        ni = len(self._var)
        if ni == 1:
            return 1
        # function of more than one variable may be a vector field:
        args = tuple([0]*ni)  # try (0,0,...) as indep. variables
        try:
            v = self(args)
            return ni
        except:
            # try another argument (in case (0,0,...) caused wrong calculations:
            args = tuple([1.105]*ni)
            v = self(args)
            return ni


    def Cpp_code(self, function_name='somefunc'):
        """
        Dump the string expression to C++.
        In C++ we use a plain function if there are no parameters,
        otherwise we use a function object with operator() for
        the function evaluation.
        """
        varlist = ', '.join(['double %s' % var for var in self._var])
        expr = self._f
        # ** does not work in C, instead of doing sophisticated
        # parsing and edit, provide an error message
        self._pow_check()
        if self._prms:
            decl = ' '.join(['double %s;' % name for name in self._prms])
            prms = ', '.join(['double %s_=%s' % (name, self._prms[name]) \
                    for name in self._prms])
            setp = ' '.join(['%s = %s_;' % (name, name) \
                             for name in self._prms])
            # function object:
            s = """
class %(function_name)s
{
  // parameters:
  %(decl)s
 public:
  %(function_name)s (%(prms)s)
    { %(setp)s }
  double operator() const (%(varlist)s)
    { return %(expr)s; }
};
""" % vars()
        else:
            s = """
double %(function_name)s (%(varlist)s)
{ return %(expr)s; }
"""
        return s

    def F77_code(self, function_name='somefunc'):
        """
        Dump the string expressions as a Fortran 77 function or subroutine.

        Note: if pow(x,a) is used in the expression, this is
        translated to x**a by a simple regex, which may fail if
        there are function calls inside pow(.,.).
        """
        expr = self._f
        real = 'real*8'
        varlist = ', '.join(self._var)
        varlist_decl = '\n'.join(['      %s %s' % (real, name) \
                                  for name in self._var])
        decl = '\n'.join(['      %s %s' % (real,name) for name in self._prms])
        import re
        if re.search(r'pow\s*\(', expr):
            # try to replace pow(x,a) by x**a
            expr = re.sub(r'pow\(([^,]+),([^)]+)\)', '((\g<1>)**(\g<2>))',
                          expr)
        # set parameter values:
        setp = '\n'.join(['      %s = %s' % (name, self._prms[name]) \
                          for name in self._prms])
        s = """
      %(real)s function %(function_name)s(%(varlist)s)
C     independent variables:
%(varlist_decl)s
""" % vars()
        if self._prms:
            s += """
C     parameters:
%(decl)s
%(setp)s
""" % vars()
        s += """
      %(function_name)s = %(expr)s

      return
      end
""" % vars()
        return s

    def F77_pow(self):
        """
        Generate an F77 function pow(x,a) (x**a). In some
        string expressions that are to be translated to C/C++,
        pow(x,a) must be used instead of x**a, but pow is not
        defined in F77. This code dumpes the necessary F77 version
        of pow such that string functions can be seamlessly translated
        to C, C++, and F77.

        Note: this function is difficult to use since it expects
        exactly a single-precision power. We now rely on regular
        expressions to replace pow(x,a) by x**a in F77_code instead.
        """
        s = """

      real*8 function pow(x, a)
      real*8 x
C     the power a is usually a number (single precision),
C     note: it cannot be int
      real*4 a
      pow = x**a
      return
      end
"""
        return s

    def C_code(self, function_name='somefunc', inline=False):
        """
        Dump the string expressions as a C function.
        If inline is true, the C++ inline keyword is inserted
        to make the function inline.
        """
        if inline:
            s = 'inline '
        else:
            s = ''
        expr = self._f
        # ** does not work in C, instead of doing sophisticated
        # parsing and edit, provide an error message
        self._pow_check()

        varlist = ', '.join(['double %s' % var for var in self._var])
        s += 'double %s (%s)\n{\n' % (function_name, varlist)
        if self._prms:
            # declare variables for parameters:
            decl = ' '.join(['double %s;' % name for name in self._prms])
            # set parameter values:
            prms = ' '.join(['%s = %s;' % (name, self._prms[name]) \
                            for name in self._prms])
            s += '  %s\n  %s\n' % (decl, prms)
        # evaluate math expression:
        s += '  return ' + expr + ';\n}\n'
        return s

    def _pow_check(self):
        """
        Raise a SyntaxError exception if the ** power operator is used
        in the string formula.
        """
        if self._f.find('**') != -1:
            raise SyntaxError(
                  'use pow(a,b) instead of a**b in the expression'\
                  '\n%s\n(since you demand translation to C/C++)' % self._f)

def _doctest():
    import doctest, StringFunction
    return doctest.testmod(StringFunction)

def _demo():
    f = StringFunction('a+b*sin(x)', a=1, b=4)
    print f(2)
    f.set_parameters(a=-1, b=pi)
    print f(1)
    print 'internals:', str(f), repr(f), f._lambda, f._prms
    f = StringFunction('amp*sin(a*t)*exp(-6.211*x)',
                       independent_variables=('x','t'))
    f.set_parameters(amp=0.1, a=1)
    print f(0,pi/2.0,a=2)
    print 'internals:', str(f), repr(f), f._lambda, f._prms
    print f.C_code()
    print f.Cpp_code()
    print f.F77_code()


# simplified "pedagogical" versions from the
# "Python for Computational Science" book:

class StringFunction_v1:
    def __init__(self, expression):
        self._f = expression

    def __call__(self, x):
        return eval(self._f)  # evaluate function expression

# compile eval expression:
class StringFunction_v2:
    def __init__(self, expression):
        self._f_compiled = compile(expression, '<string>', 'eval')

    def __call__(self, x):
        return eval(self._f_compiled)

# allow parameters and an arbitrary name of the independent variable:
class StringFunction_v3:
    def __init__(self, expression,
                 independent_variable='x',
                 set_parameters=''):
        self._f_compiled = compile(expression, '<string>', 'eval')
        self._var = independent_variable  # 'x', 't' etc.
        self._code = set_parameters
        self.__name__ = expression  # name of func is expression

    def set_parameters(self, code):
        self._code = code

    def __call__(self, x):
        # assign value to independent variable:
        exec('%s = %g' % (self._var, x))
        # execute some user code (defining parameters etc.):
        if self._code:  exec(self._code)
        return eval(self._f_compiled)

# let parameters be keyword arguments:
class StringFunction_v4:
    def __init__(self, expression, **kwargs):
        self._f = expression
        self._var = kwargs.get('independent_variable', 'x') # 'x', 't' etc.
        self._globals = kwargs.get('globals', globals())
        self.__name__ = self._f  # class name = function expression
        self._f_compiled = compile(self._f, '<string>', 'eval')
        self._prms = kwargs.copy()
	try:
            del self._prms['independent_variable']
            del self._prms['globals']
        except: pass

    def set_parameters(self, **kwargs):
        self._prms.update(kwargs)

    def __call__(self, x):
        # include indep. variable in dictionary of function parameters:
        self._prms[self._var] = x
        # evaluate function expression:
        return eval(self._f_compiled, self._globals, self._prms)

    def test(self, x=1.4325):
        # test that all parameters are defined
        try:
            self(x)  # sample call
            return True
        except NameError as e:
            prm = str(e).split()[2]
            raise NameError('Parameter "%s" is not defined,\nneither in '\
                  'the constructor nor set_parameters.\n'\
                  'Update the constructor call or call set_parameters'\
                  '(%s=...)' % (prm, prm))
        else:
            return True  # accept other errors

    def __str__(self):
        s = self._f
        # Substitute parameter names by their numerical values.
        # Start with the most complicated parameter names.
        # Improvements by Eigil Skjaelveland.

        # first remove indep. variables possibly inserted in self._prms
        # by the self.__call__ method:
        try:
            del self._prms[self._var]
        except:
            pass
        prm_names = list(self._prms.keys())
        prm_names.sort(key=len, reverse=1)
        for name in prm_names:
            s = re.sub(r'([^a-z_])' + name + '([^a-z_])',
                       r'\1{0}\2', s).format(str(self._prms[name]))
        return s

    def __repr__(self):
        # first remove indep. variables possibly inserted in self._prms
        # by the self.__call__ method:
        try:
            del self._prms[self._var]
        except:
            pass
        kwargs = ', '.join(['%s=%s' % (key, repr(value)) \
                            for key, value in self._prms.items()])
        return """StringFunction1(%s, independent_variable=%s, %s)""" % \
               (repr(self._f), repr(self._var), kwargs)

class StringFunction_v5(StringFunction_v4):
    """
    Extension of class StringFunction_v4 to an arbitrary
    number of independent variables.
    """
    def __init__(self, expression, **kwargs):
        StringFunction_v4.__init__(self, expression, **kwargs)
        self._var = tuple(kwargs.get('independent_variables', 'x'))
        try:    del self._prms['independent_variables']
        except: pass

    def __call__(self, *args):
        # add independent variables to self._prms:
        for name, value in zip(self._var, args):
            self._prms[name] = value
        return eval(self._f_compiled, self._globals, self._prms)

    def __str__(self):
        # remove the independent variables from self._prms such that
        # this dict contains parameters (to be subsituted by values) only:
        try:
            for v in self._var:
                del self._prms[v]
        except:
            pass
        return StringFunction1.__str__(self)


    def __repr__(self):
        # first remove indep. variables possibly inserted in self._prms
        # by the self.__call__ method:
        try:
            for v in self._var:
                del self._prms[v]
        except:
            pass
        kwargs = ', '.join(['%s=%s' % (key, repr(value)) \
                            for key, value in self._prms.items()])
        return """StringFunction(%s, independent_variables=%s, %s)""" % \
               (repr(self._f), repr(self._var), kwargs)



def _efficiency():
    print '\nPerform some efficiency tests (this might take some time...):'
    formula = 'sin(x) + x**3 + 2*x'
    formula_wprm = formula + ' + A*B'
    def s0(x):
        return sin(x) + x**3 + 2*x
    s1 = StringFunction_v1(formula)
    s2 = StringFunction_v2(formula)  # compiled
    s3 = StringFunction_v3(formula_wprm, set_parameters='A=0; B=0')
    s4 = StringFunction_v4(formula)
    s5 = StringFunction_v5(formula, independent_variables=('x',),
                           A=0, B=0)
    s6 = StringFunction(formula, independent_variables=('x',),
                        A=0, B=0)
    s7 = s6.__call__
    x = 0.9
    # verification first:
    values = [s(x) for s in (s0, s1, s2, s3, s4, s5, s6, s7)]
    print 'values of %s for x=%s: %s' % (formula, x, values)

    n = 400000
    from scitools.misc import timer
    from scitools.EfficiencyTable import EfficiencyTable as ET
    e = ET('Efficiency check of StringFunction implementations; '
           'formula=%s, n=%d' % (formula, n))
    import inspect
    for s in s0, s1, s2, s3, s4, s5, s6, s7:
        if inspect.isfunction(s) or inspect.ismethod(s):
            name = s.__name__
        else:
            name = s.__class__.__name__
        t = timer(s, args=(x,), repetitions=100000,
                  comment=name)
        e.add(name, t)
    print e
    print 'End of efficiency tests\n'

if __name__ == '__main__':
    _doctest()
    _demo()
    _efficiency()
