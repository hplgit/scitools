#!/usr/bin/env python

# Note: doc strings in this module are written with minimal "invisible"
# Epytext tagging for nice formatting with Epydoc.

"""
Python interface to ODE solvers
===============================

Basic Usage
-----------

The design goal of this interface was to make the user code for
solving ODEs as simple as possible. More specifically, if we want to
solve y'(t) = -y, y(0)=1, by method (class) X, a minimal program will
work::

    def f(y,t):
        return -y

    solver = X()
    solver.set(y0=1, f=f, dt=0.1)
    #solver.set(t0=1, y0=y[1,:], f=f, dt=0.1) ?
    # HP world:
    y, t = solver.integrate(y0=y[1,:], t0=1, T=2.0)  ?

    # Ola world:
    solver.set(returner bare y plain, lagre minst mulig, store data)
    for i in xrange(1000000):
        print y.shape(1) # 1000000 e.g.
        y[i] = solver.integrate(y0=y[i], t0=1, T=2.0)  ?
        
    # can configure return values with solver.set(...)
    # solver.set(return_values={'y': 'all', 't': 'all', 'info': ...syntax...})
    #y, t = solver.integrate(T=2.0)   # solve for t in [0,T]
    y, info = solver.integrate(T=2.0)   # solve for t in [0,T]
    plot(solver.t, solver.y)
    print solver.info('error estimates')
    plot(t, y)

    # above: we store y for all t, but in big problems we may only want
    # store the final y
    # solver.set(skip_intermediate_values=True) ... :-(

The returned objects y and t are (by default) Numerical Python
arrays: y has shape (m, n) and t has shape m, where m is the number
of time steps at which the solution was computed, and n is the
number of equations in the ODE system. To plot the solution at
time j*dt, we send the one-dimensional arrays t and y[j,:]
to some plotting tool.

The returned arrays y and t from solver.integrate can at any time
also be fetched directly from the solver object as the solver.y
and solver.t attributes.

A system of ODEs is solved using the same natural syntax as for
a scalar ODE::

    def f(y,t):
        return [-y[0],-2*y[1]]

    solver = X()
    solver.set(f=f, dt=0.1)
    y, t = solver.integrate(y0=[1,0], T=2.0)

(It is remarked that the f function and the initial condition are here
prescribed as lists, but internally in the ODE solver interface these
lists are automatically converted to Numerical Python arrays.)

An important feature is that we only change the name X in the above
statements to change the type of solver. That is, all solvers are
adapted to the same user interface. Some solvers may, however, demand
the user to set more parameters in the solution algorithm (see
example below), but if the interface provides suitable default values,
the compact statements above may work even with very sophisticated
solvers.


Additional Parameters in the ODE System
---------------------------------------

Consider the ODE y'(t)= -a*y + b, where a and b are parameters.
These can be fed to the f(y,t) function that defines the right-hand
side through a parameter called f_args::

    def f(y,t, a,b):
        return -a*y + b

    solver = X()
    solver.set(initial_condition=1, f=f, dt=0.1, f_args=(1,0))
    y, t = solver.integrate(T=2.0)

f_args holds the tuple of additional arguments to f, i.e., we view
f as f(y,t, *f_args).
Keyword arguments also work::

    def f(y,t, a=1,b=1):
        return -a*y + b
    
    solver.set(initial_condition=1, f=f, dt=0.1,
               f_kwargs={'a': 2.5, 'b': 0})

In general, the signature of f is f(y, t, *f_args, **f_kwargs).

The right-hand side can be defined as a class in more complicated problems,
for instance when ODE parameters depend on other simulations. A class
version of f in the previous example reads::

    class F:
        def __init__(self, a, b):
            self.a, self.b = a, b

        def __call__(self, y, t):
            return -self.a*y + self.b

    f = F(2.5, 0)
    solver.set(initial_condition=1, f=f, dt=0.1)


# f implemented in Fortran or C (f2py)

Handling of Solver Parameters
-----------------------------

Many ODE solvers require large amounts of input data to steer the
behavior of the solution algorithm. The collection of parameters
is documented in the solver's doc string, and suitable default
values are normally supplied by this interface (if not, the value
of a parameter is None). The set method is used to set the values
of the parameters, e.g.::

    solver.set(initial_condition=1, f=f, dt=0.1,
               f_kwargs={'a': 2.5, 'b': 0},
               adaptivity_method=2,
               k1=0, k2=0, k3=4,
               initial_Q_value=0,)

All keyword arguments that can be used with set are also available
as attributes (actually properties in Python terminology).
The call above could alternatively been obtained by::

    solver.initial_condition = 1
    solver.f = f

etc.

Some solvers calculate lots of additional numerical quantities besides
the solution at discrete time levels (y above). For example, adaptive
algorithms may provide a list of time steps used, error estimates, etc.
Such output data from the solver are available as a dictionary::

    solver.out

The keys in this dictionary are also available as attributes (actually
properties in Python terminology). Any input or output parameter
associated with the algorithm can be read with the get method or as
attributes::

    print solver.get('initial_condition')
    print solver.initial_condition
    print solver.get('adaptive_time_steps')
    print solver.adaptive_time_steps


Handling of f and its Jacobian
------------------------------

The (vector) function f(y,t) defining the ODE system can for some
solvers be implemented as a Python function (or class with a __call__
method), as we did above, while for other solvers the function is
supposed to be implemented in a compiled language (Fortran, C or C++).
In the latter case, one assigns a string as f value rather than a
function. This string holds the filename of a file containing the source
code.

The Jacobian (gradient of f with respect to y; needed in implicit
methods) is treated in the same way as f, i.e., it can be
implemented in Python, Fortran, C, or C++, depending on what
the ODE solver supports.

When f and the Jacobian are implemented in Python, one can return
a scalar value in case of a scalar ODE, otherwise one can return a
list, tuple, or a Numerical Python array. The solver object has
a method get_safe which automatically wraps the f or Jacobian function
in a new function returning a Numerical Python array, if necessary.
For example::

>>> solver = ForwardEuler()
>>> 
>>> def myrhs(y,t, a,b):
...     return [-a*y[0],-b*y[1]]
... 
>>> solver.set(f=myrhs, f_args=(1,1), initial_condition=[0,0])
>>> f = solver.get('f')
>>> f
<function myrhs at 0xb709bc6c>
>>> f1 = f([0,1], 0.1, 1, 1)
>>> f1, type(f1)               # f1 is a list
([0, -1], <type 'list'>)
>>> f = solver.get_safe('f')   # convert f's list to NumPy array
>>> f                          # f is now a wrapper of myrhs
<function f_wrapper at 0xb709bd4c>
>>> import inspect
>>> print inspect.getsource(f) # let's look at the wrapper
                def f_wrapper(y, t, *f_args, **f_kwargs):
                    return N.array(f(y, t, *f_args, **f_kwargs))
>>> f1 = f([0,1], 0.1, 1, 1)
>>> f1, type(f1)               # f1 is now a NumPy array
(array([ 0, -1]), <type 'array'>)
>>> i = solver.get('initial_condition')
>>> i, type(i)                 # i is a list
([0, 0], <type 'list'>)
>>> i = solver.get_safe('initial_condition')  # convert to array
>>> i, type(i)                 # is not converted to NumPy array
(array([0, 0]), <type 'array'>)
 

"""

            

def _str2obj(s, globals=globals(), locals=locals()):
    """Turn string s into the corresponding object."""
    try:
        s = eval(s, globals, locals)
        return s
    except:
        return s

import sys

class CommandLineUI(object):
    """
    Utility for interpreting command line options as parameter
    specifications for ODE solver classes in the ODESolver hierarchy.
    """
    def __init__(self, argv=sys.argv[1:]):
        self.argv = argv[:]  # hold a copy in case others destroy sys.argv

    def commandline2solver(self, solver, globals, locals):
        """
        Read command line options. If a pair --name value is encountered
        and name is a valid parameter name in the solver object,
        this parameter is set.

        It is necessary for the calling code to provide its globals()
        and locals() dictionary such that strings read from the command
        line can be eval'ed correctly to yield user-defined objects.

        Example::

        >>> sysargv = '--initial_condition [-1,1] --dt 0.5 --f_args (1,7)  --f myrhs'
        >>> ui = CommandLineUI(sysargv.split())
        >>> ui.commandline2solver(solver, globals(), locals())
        >>> pprint.pprint(solver.get())
        {'dt': 0.5,
         'f': <function myrhs at 0xb6d52e64>,
         'f_args': (1, 7),
         'f_kwargs': {},
         'initial_condition': [-1, 1],
         'initial_time': 0.0,
         'solution_storage': 'array'}
        
        """
        valid_names = solver._prm.keys()
        values = {}
        i = 0
        while i <= len(self.argv)-2:
            name = self.argv[i]
            name = name.replace('-', '') # remove hyphens
            if name in valid_names:
                i += 1
                values[name] = _str2obj(self.argv[i], globals, locals)
            i += 1
        #print 'values to be set from the command line:', values
        solver.set(**values)
        # save globals and locals for, e.g., the get method
        self.globals, self.locals = globals, locals

    def get(self, name, default=None, locals=None, globals=None):
        """Extract value of option --name."""
        if globals is None and hasattr(self, 'globals'):
            globals = self.globals
        if locals is None and hasattr(self, 'locals'):
            locals = self.locals
        i = 0
        while i <= len(self.argv)-2:
            n = self.argv[i]
            n = n.replace('-', '') # remove hyphens
            if n == name:
                value = _str2obj(self.argv[i+1], globals, locals)
                break
            i += 1
        try:
            return value
        except NameError:
            if default is None:
                raise ValueError, '%s is not given as a command-line '\
                      'option and no default value is available' % name
            else:
                return default
            
    def help(self, solver):
        """Explain what valid command line options are."""
        s = ''
        for name in solver._prm:
            if name in solver._prm_help:
                help = solver._prm_help[name]
            else:
                help = ''
            s += '--%s: default=%s\n' % (name, solver._prm[name])
            if help:
                s += '[%s]\n\n' % help
        return s
                
            
"""
Issues:

1. Jacobian and f may have different signatures in different packages. How
can we make a unified interface when we go directly from F/C to F/C?
Could have a wrapper in between.

2. Jacobian is now a function returning some matrix (Python) or a file.
What about different storage schemes for the matrix? The user would avoid
to write different Jacobian functions for different choices of solvers.
Could then make use of the matrix hierarchy to simplify input into matrix,
but we still have a problem with dense vs banded vs CRS (different solvers
will treat different banded and CRS differently, especially banded).

ODEPACK standard:
           SUBROUTINE F (NEQ, T, Y, YDOT, RPAR, IPAR)
           DOUBLE PRECISION T, Y, YDOT, RPAR(*)
           INTEGER IPAR(*)
           DIMENSION Y(NEQ), YDOT(NEQ)

C RPAR,IPAR = user-defined real and integer arrays passed to F and JAC.
C vode accepts RPAR,IPAR, while some other routines do not have these
C arrays or just one (RPAR) of them. Some routines allow the user to
C supply a preprocessing Jacobian routine, and/or a routine to solve
C linear systems with the Jacobian as coefficient matrix.

Jacobian:

C If the problem is nonstiff,
C use a method flag MF = 10.  If it is stiff, there are four standard
C choices for MF (21, 22, 24, 25), and DVODE requires the Jacobian
C matrix in some form.  In these cases (MF .gt. 0), DVODE will use a
C saved copy of the Jacobian matrix.  If this is undesirable because of
C storage limitations, set MF to the corresponding negative value
C (-21, -22, -24, -25).  (See full description of MF below.)
C The Jacobian matrix is regarded either as full (MF = 21 or 22),
C or banded (MF = 24 or 25).  In the banded case, DVODE requires two
C half-bandwidth parameters ML and MU.  These are, respectively, the
C widths of the lower and upper parts of the band, excluding the main
C diagonal.  Thus the band consists of the locations (i,j) with
C i-ML .le. j .le. i+MU, and the full bandwidth is ML+MU+1.

C C. If the problem is stiff, you are encouraged to supply the Jacobian
C directly (MF = 21 or 24), but if this is not feasible, DVODE will
C compute it internally by difference quotients (MF = 22 or 25).
C If you are supplying the Jacobian, provide a subroutine of the form..
C
C           SUBROUTINE JAC (NEQ, T, Y, ML, MU, PD, NROWPD, RPAR, IPAR)
C           DOUBLE PRECISION T, Y, PD, RPAR
C           DIMENSION Y(NEQ), PD(NROWPD,NEQ)
C
C which supplies df/dy by loading PD as follows..
C     For a full Jacobian (MF = 21), load PD(i,j) with df(i)/dy(j),
C the partial derivative of f(i) with respect to y(j).  (Ignore the
C ML and MU arguments in this case.)
C     For a banded Jacobian (MF = 24), load PD(i-j+MU+1,j) with
C df(i)/dy(j), i.e. load the diagonal lines of df/dy into the rows of
C PD from the top down.
C     In either case, only nonzero elements need be loaded.



"""


    
