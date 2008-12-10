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
import numpy as N
import operator, os

#---------------------------------------------------------------------
# ----- helper functions for detecting right object type ------------

# test that a variable v is a function or None:
_func_type = lambda v: v is None or callable(v)

# test that a variable v is a function, None, or source code of a
# function in a file:
_func_or_file_type = lambda v: v is None or callable(v) or \
                     (isinstance(v, basestring) and os.path.isdir(v))

# test that a variable v is array/list-like, a number, or None:
_array_or_number_type = lambda v: v is None or \
      isinstance(v, (list, tuple, N.ndarray, float, complex, int))


# test that a variable v is a function or the string 'built-in'
# (used for linear or nonlinear solvers that can be part of the
# ODE routine or supplied as a user-defined algorithm):
_user_alg_type = lambda v: callable(v) or v == 'built-in'
#---------------------------------------------------------------------

def indent(text, indent_size=4):
    """
    Indent each line in the string text by indent_size spaces.
    """
    # indent each line properly:
    ind = ' '*indent_size
    lines = text.splitlines()
    for i in range(len(lines)):
        lines[i] = ind + lines[i]
    text = '\n'.join(lines)
    return text

def _doc_format(*classes_or_list_of_prm_dicts):
    """
    Combine all dictionaries _solver_prm, solver_prm_help, etc. in
    the arguments, and print the information in a nice
    way suitable for a doc string. That is, this function is used to
    update a doc string of a solver with all available parameters
    registered in _solver_prm etc. of a class and its base class.

    The classes_or_list_of_prm_dicts argument may hold either class
    objects (typical the base class of a solver) or a list of dictionaries
    (typical the local _solver_prm etc.).

    Example on call::
    
      __doc__ += _doc_format(ImplicitSolver,
                             [_solver_prm, _solver_prm_help, _solver_prm_type,
                              _solver_out, _solver_out_help])
    """
    all_prm = {}
    all_prm_help = {}
    all_prm_type = {}
    all_out = {}
    all_out_help = {}
    for c in classes_or_list_of_prm_dicts:
        if isinstance(c, type):
            all_prm.update(getattr(c, '_solver_prm'))
            all_prm_help.update(getattr(c, '_solver_prm_help'))
            all_prm_type.update(getattr(c, '_solver_prm_type'))
            all_out.update(getattr(c, '_solver_out'))
            all_out_help.update(getattr(c, '_solver_out_help'))
        elif isinstance(c, (list,type)):
            # list of dictionaries _solver_prm etc.
            try:
                _solver_prm, _solver_prm_help, _solver_prm_type, \
                             _solver_out, _solver_out_help = c
            except ValueError:
                raise TypeError, 'not right arguments to _doc_format'
            
            all_prm.update(_solver_prm)
            all_prm_help.update(_solver_prm_help)
            all_prm_type.update(_solver_prm_type)
            all_out.update(_solver_out)
            all_out_help.update(_solver_out_help)
            
    if len(all_prm) > 0:
        #s = '\n\nLegal Parameter Names for the "set" Method (or Attributes)\n'
        #s +=    '----------------------------------------------------------\n'
        s = '\n\nLegal parameter names for the "set" method (or attributes):\n'
    else:
        s = ''
    names = all_prm.keys()
    names.sort()
    for name in names:
        help = all_prm_help[name]
        # left strip all help lines and indent with list (required by Epydoc):
        help = '\n'.join(['    '+line.lstrip() for line in help.split('\n')])
        s += '\n  - %s: (default %s)\n%s\n' % \
             (name, all_prm[name], help)
    if len(all_out) > 0:
        #s += '\nOutput Parameters from Solver\n'
        #s +=   '-----------------------------\n'
        s += '\nOutput parameters from solver:\n'
    names = all_out.keys()
    names.sort()
    for name in names:
        help = all_out_help[name]
        # left strip all help lines and indent with list (required by Epydoc):
        help = '\n'.join(['    '+line.lstrip() for line in help.split('\n')])
        s += '\n  - %s: %s\n' % (name, help)

    # indent each line to be aligned with the rest of the doc string:
    return indent(s, 4)


def generate_template_solver(implicit=False):
    """
    Generate template code for a solver class.
    If the solver is based on an explicit method, set implicit=False,
    and the class will be derived from class ODESolver.
    Implicit methods have implicit=True and the class is derived
    from class ImplicitSolver.
    """
    if implicit:
            
            code = '''
class NewImplicitSolver(ImplicitSolver):
    """doc string."""

    _solver_prm = {}
    _solver_prm_help = {}
    _solver_prm_type = {}
    # add dt etc. if this is a solver with constant step size
    _constant_step_size_prm(_solver_prm, _solver_prm_help, _solver_prm_type)
    # otherwise, set _solver_prm extensions here
    _solver_out = {}
    _solver_out_help = {}

    # auto update of doc string with info about legal parameter names:
    __doc__ += _doc_format(ImplicitSolver,
                           [_solver_prm, _solver_prm_help, _solver_prm_type,
                            _solver_out, _solver_out_help])

    
    def __init__(self, **kwargs):
        solver_language = kwargs.get('solver_language', 'Python')
        ImplicitSolver.__init__(self, solver_language=solver_language)
        self._prm.update(NewImplicitSolver._solver_prm)
        self._prm_help.update(NewImplicitSolver._solver_prm_help)
        self._prm_type.update(NewImplicitSolver._solver_prm_type)
        self._out.update(NewImplicitSolver._solver_out)
        self._out_help.update(NewImplicitSolver._solver_out_help)

        self.set(**kwargs)
        self.make_attributes()

    def _update(self, **kwargs_in_last_set_call):
        # _update is called after any set(param=value,...) call to
        # make sure that internal data structures are properly resized

        size = self.size  # used to check if size of ODE system changes
        ImplicitSolver._update(self, **kwargs_in_last_set_call)

        # do additional checks or resizing of internal data
        
        return size != self.size
    
    def integrate(self, T):
        """Integrate the ODE system from initial time to time T."""
        # extract data and call self.algorithm:
        f, J, dt, y0, t0, f_args, f_kwargs, J_args, J_kwargs = \\
           self.get_safe('f', 'Jacobian', 'dt', 'initial_condition',
                         'initial_time',
                         'f_args', 'f_kwargs', 'J_args', 'J_kwargs',
                         ignore_None=['Jacobian'])
        if T-t0 < dt:  dt = T-t0
        return self.algorithm(t0, y0, f, J, T, dt,
                              f_args, f_kwargs, J_args, J_kwargs)
    
    def algorithm(self, t0, y0, f, J, T, dt,
                  f_args=(), f_kwargs={}, J_args=(), J_kwargs={}):
        t = t0
        y = y0
        self._store(y, t)
        
        while t+dt <= T:
            t += dt
            # here goes the algoritm
            # f(y, t, *f_args, **f_kwargs)
            # J(y, t, *J_args, **J_kwargs)
            
            self._store(y, t)

        return self._stored_data()
'''

    else:  # explicit codes

            code = '''
class NewExplicitSolver(ODESolver):
    """doc string."""

    _solver_prm = {}
    _solver_prm_help = {}
    _solver_prm_type = {}
    # add dt etc. if this is a solver with constant step size
    _constant_step_size_prm(_solver_prm, _solver_prm_help, _solver_prm_type)
    # otherwise, set _solver_prm extensions here
    _solver_out = {}
    _solver_out_help = {}

    # auto update of doc string with info about legal parameter names:
    __doc__ += _doc_format(ODESolver,
                           [_solver_prm, _solver_prm_help, _solver_prm_type,
                            _solver_out, _solver_out_help])

    
    def __init__(self, **kwargs):
        solver_language = kwargs.get('solver_language', 'Python')
        ODESolver.__init__(self, solver_language=solver_language)
        self._prm.update(NewExplicitSolver._solver_prm)
        self._prm_help.update(NewExplicitSolver._solver_prm_help)
        self._prm_type.update(NewExplicitSolver._solver_prm_type)
        self._out.update(NewExplicitSolver._solver_out)
        self._out_help.update(NewExplicitSolver._solver_out_help)

        self.set(**kwargs)
        self.make_attributes()

    def _update(self, **kwargs_in_last_set_call):
        # _update is called after any set(param=value,...) call to
        # make sure that internal data structures are properly resized

        size = self.size  # check if size of ODE system changes
        ODESolver._update(self, **kwargs_in_last_set_call)

        # do additional checks or resizing of internal data
        
        return size != self.size
    
    def integrate(self, T):
        """Integrate the ODE system from initial time to time T."""
        # extract data and call self.algorithm:
        f, dt, y0, t0, f_args, f_kwargs = \\
           self.get_safe('f', 'dt', 'initial_condition',
                         'initial_time', 'f_args', 'f_kwargs')
        if T-t0 < dt:  dt = T-t0
        return self.algorithm(t0, y0, f, T, dt, f_args, f_kwargs)
    
    def algorithm(self, t0, y0, f, T, dt, f_args=(), f_kwargs={}):
        t = t0
        y = y0
        self._store(y, t)
        
        while t+dt <= T:
            t += dt
            # here goes the algoritm
            # f(y, t, *f_args, **f_kwargs)
            
            self._store(y, t)

        return self._stored_data()
'''
    return code


# ===========================================================================

class ODESolver(object):
    """
    Base class of ODE solvers
    =========================

    Each subclass reflects a solver, implemented in Python or
    in a compiled language like Fortran, C, or C++.
    

    Public Attributes
    -----------------
    
     - size : number of unknowns in the ODE system
     - y : list of solution vectors at all time steps
     - t : list of time values at all time steps (y[i] corresponds to t[i])

    
    Public Methods
    --------------

     - set(name1=value1, name2=value2, ...) : set parameter names and values
     - get('name1') : get value of parameter name1
     - get_safe('name1', ...): as get, but exceptions raised for None values
     - get_size()  : get number of equations/unknowns
     - make_attributes() : turn parameter names into data attributes
     - usage(return_string=False) : list all registered parameter names


    Methods Accessible in Subclasses
    --------------------------------

     - _check_compatibility(): Check that f (and Jacobian) has size
       compatible with initial_condition, and check if f (or Jacobian)
       returns list (not NumPy arrays) such that a list to array
       transformation must be performed.
       

    Design
    ------

    Each class in the ODESolver hierarchy has four dictionaries
    declared at the class level (static variables):

     - _solver_prm : Holds all input data to a solver method as (name,value)
       pairs. The value should reflect a suitable default value, or None.
    
     - _solver_prm_help : Documentation of each parameter name in _solver_prm
       (preferably taken from the official documentation of the underlying
       solver routine).

     - _solver_prm_type : Items in _solver_prm can optionally be checked
       for the right type with a convention described below (Type Checking).

     - _solver_out : Holds result parameters from the solution method.

     - _solver_out_help : Describes each if the parameter names in _solver_out
       (preferably taken from the official documentation of the underlying
       solver routine).
    
    These four dictionaries are defined in each solver class. The constructor
    combines the class' _solver* dictionaries with those of the base classes.
    The result is self._prm, self._prm_help, self._prm_type, and self._out.
    The information on legal parameter names, help, and type is automatically
    added to the doc strings to keep the documentation as up to date as
    possible.

    The set(prm1=value1, prm2=value2, ...) method is used to assign
    values to all legal parameters (i.e., those defined in self._prm).

    The get('prm1') method is used to extract the value of a parameter
    with name 'prm1'. Alternatively, many parameters can be extracted
    by multiple arguments: get('prm1', 'prm2', ...).


    Type Checking
    -------------

    Some (or all) names in _solver_prm can be associated with type checking.
    Here are examples::

     _solver_prm_type = {
       'param1': None,         # no type checking (default anyway)
       'param2': (float,int),  # must be float or int (actually any number)
       'param3': _mycheck,     # _mycheck(v) returns true if v is of right type
       'param4': True,         # new value must have same type as old value
       'param5': MyClass,      # must be instance of class MyClass
       }

    The generic set method in ODESolver also implements all type checking
    of new values.

    Examples on Error Handling
    --------------------------

    Here is a session with various exceptions::

    >>> solver = ForwardEuler()
    >>>
    >>> def myrhs(y,t, a,b):
    ...     return [-a*y[0],-b*y[1]]
    ...
    >>> # try setting f and initial_condition, but not f_args:
    >>> solver.set(f=myrhs, initial_condition=[0,0])
    Traceback (most recent call last):
    ValueError: f_args and/or f_kwargs must be set
    myrhs() takes exactly 4 arguments (2 given)
    >>>
    >>> # try setting the name as string
    >>> solver.set(f="myrhs", f_args=(1,1), initial_condition=[0,0])
    Traceback (most recent call last):
    f='myrhs': this function is called to approve the value myrhs:
    _func_type = lambda v: v is None or callable(v)
    ...and the function returned False
    >>>
    >>> # try setting wrong size of initial_condition
    >>> solver.set(f=myrhs, f_args=(1,1), initial_condition=0)
    File "<input>", line 2, in myrhs
    IndexError: index out of bounds
    >>>
    >>> # try setting wrong type of initial_condition:
    >>> solver.set(initial_condition={})
    Traceback (most recent call last):
    initial_condition={}: this function is called to approve the value {}:
    _array_or_number_type = lambda v: v is None or \
      isinstance(v, (list, tuple, N.ndarray, float, complex, int))
    ...and the function returned False
    >>>
    >>>
    >>> solver.get('dt', 'f_args')  # returns list of values
    [1.0, (1, 1)]
    >>> solver.get('dt')  # returns scalar value
    1.0
    >>> p = solver.get()  # get all parameters
    >>> import pprint
    >>> pprint.pprint(p)
    {'dt': 1.0,
    'f': <function myrhs at 0xb6d0cd4c>,
    'f_args': (1, 1),
    'f_kwargs': {},
    'initial_condition': 0,
    'initial_time': 0.0,
    'solution_storage': 'array'}
    >>>
    >>> # exemplify attributes:
    >>> solver.dt = 0.01
    >>> solver.dt
    0.01
    >>> solver.f_args
    (1, 1)


    How to Implement a New Solver
    -----------------------------

    The following function in this module writes out the template of
    a new solver class (subclass in the ODESolver hierarchy)::

        generate_template_solver(implicit=False)

    If implicit is False, the ODE solver applies an explicit scheme, and
    there is no need for a Jacobian and related data. The class
    is then usually a subclass of ODESolver. If implicit is True,
    the solver may need a user-provided Jacobian, and the class is
    derived from class ImplicitSolver.
    
    
    """

    _solver_prm = {
        'f': None,
        'f_args': (),
        'f_kwargs': {},
        'initial_condition': None,
        'initial_time': 0.0,
        'solution_storage': 'array',
        }

    _solver_prm_help = {
        'f': 'right-hand side of ODE system: dy/dt = f(y,t)',
        'f_args': 'optional positional arguments to f: '\
        'f(y, t, *f_args)',
        'f_kwargs': 'optional keyword arguments to f: '\
        'f(y, t, *f_args, **f_kwargs)',
        'initial_condition': 'y(0)',
        'initial_time': 'time for initial condition y(0)',
        'solution_storage': """\
'list': self.y, self.t are lists holding the solution and the
corresponding time levels.
'array': self.y, self.t are Numerical Python arrays holding the
solution and the corresponding time levels. (The y and t values
are stored in lists and finally converted to arrays.)
'file': the y and t values are stored in a file-based database.""",
        }

    _solver_prm_type = {
        'f': _func_or_file_type,
        'f_args': (list,tuple),
        'f_kwargs': (dict,),
        'initial_condition': _array_or_number_type,
        'initial_time': float,
        'solution_storage': str,
        }
    _solver_out = {}
    _solver_out_help = {}

    __doc__ += _doc_format()

    __doc__ += """

    Code examples
    -------------

    Typical look of a solver class for an explicit method::

    """ + indent(generate_template_solver(implicit=False),8) + """

    .
    """
        
    def __init__(self, solver_language='Python'):
        """
        @param solver_language: computer language used in the implementation
        of the solver ('F77', 'F90', 'C', 'C++', 'Python')
        """
        self._solver_language = solver_language
        self._prm = {}  # solver-specified parameter names and values
        self._prm.update(ODESolver._solver_prm)
        self._prm_help = {}
        self._prm_help.update(ODESolver._solver_prm_help)
        self._prm_type = {}
        self._prm_type.update(ODESolver._solver_prm_type)
        self._out = {}
        self._out.update(ODESolver._solver_out)
        self._out_help = {}
        self._out_help.update(ODESolver._solver_out_help)
        
        self._meta_data = {}  # user-specified parameter names and values
        # do this in subclass: self.set(**kwargs)

        self._size = 0

    def usage(self, return_string=False):
        """
        Create a message containing a list of the names of all parameters
        that can be set. If return_string is true, the message is returned
        as a string, otherwise it is printed to standard output.
        
        """
        names = self._prm.keys()
        names.sort()
        s = 'ODE solver %s has the following registered parameters:\n' \
            % self.__class__.__name__
        for name in names:
            s += '%-20s: value=%s' % (name, self._prm[name])
            if name in self._prm_type:
                s += ' (%s)' % self._prm_type[name]
            if name in self._prm_help:
                s += '   %s' % self._prm_help[name],
            s += '\n'

        # add solver output parameters:
        names = self._out.keys()
        if len(names) > 0:
            names.sort()
            s += 'Output (result) parameters that can be extracted after '\
                 'a solve:\n'
            for name in names:
                s += '%-20s: value=%s' % (name, self._out[name])
                if name in self._out_help:
                    s += '   %s' % self._out_help[name],
                s += '\n'

        if return_string:
            return s
        else:
            print s

    def make_attributes(self):
        """
        Allow parameters to be set as attributes. For example::
          solver.tol = 1.0E-8
        is the same as::
          solver.set(tol=1.0E-8)
        """
        for name in self._prm:
            cmd = '%s.%s = property(fset=lambda self, v: self.set(%s=v), '\
                  'fget=lambda self: self.get("%s"))' % \
                  (self.__class__.__name__, name, name, name)
            exec cmd

    size = property(fget=lambda self: self._size)
    
    def set(self, **kwargs):
        """Set legal solver parameters (as keyword arguments)."""
        # use techniques from help.easyviz.PrmDictBase (but make things simpler here)

        for prm in kwargs:
            if prm in self._prm:
                self._set_value(prm, kwargs[prm])
                # exception is raised if assignment was not successful
            else:
                raise NameError, \
                '"%s" is not a registered parameter!\nSee the documentation '\
                'of the %s class for a list of\nthe solver\'s registered '\
                'parameter names\n(or use the solver\'s usage() method to '\
                'print out the list)' % (prm, self.__class__.__name__)
        self._update(**kwargs)

    def _set_value(self, name, value):
        """
        Assign value to name in self._prm.
        Check type(value) if self._prm_type[name] is specified.
        """
        can_set = False
        type_check = self._prm_type  # short hand
        if name in type_check:
            if isinstance(type_check[name], int):
                # (bool is subclass of int so bool goes here too)
                if type[name]:
                    # type check against previous value or None:
                    if isinstance(value, (type(self._prm[name]), None)):
                        can_set = True
                    elif operator.isNumberType(value) and \
                         operator.isNumberType(self._prm[name]):
                        # allow mixing int, float, complex:
                        can_set = True
                    else:
                        raise TypeError, \
                          '\n\n%s=%s: %s demands type %s, not %s' % \
                          (name, value, name, type(self._prm[name]),
                           type(value))

            elif isinstance(type_check[name], (tuple,list,type)):
                # type_check[name] holds either the type or a typle/list of
                # types; test against them
                if isinstance(value, type_check[name]):
                    can_set = True
                else:
                    raise TypeError, \
                          '\n\n%s=%s: %s demands type %, not %s' % \
                          (name, value, name, type_check[name], type(value))

            elif callable(type_check[name]):
                can_set = type_check[name](value)

                if not can_set:
                    import inspect
                    source = inspect.getsource(type_check[name])
                    # see if we can find the function in globals():
                    # (gives more descriptive error message)
                    #for n in globals():
                    #    if globals()[n] == type_check[name]:
                    #        func_var = n
                    #        break
                    #raise TypeError, \
                    #      '\n\n%s=%s: %s calls %s to check the type, value '\
                    #      'of type %s is not accepted' % \
                    #      (name, value, name, func_var, type(value))
                    raise TypeError, \
                          '\n\n%s=%s: this function is called to approve '\
                          'the value %s:\n%s\n...and the function returned '\
                          'False' % (name, repr(value), repr(value), source)

            else:
                raise TypeError, '%s._prm_type["%s"] has an '\
                      'illegal value %s' % (self.__class__.__name__,
                                            name, type_check[prm])
        else:
            can_set = True

        if can_set:
            self._prm[name] = value
            return True
        return False  # could not set

    
    def get(self, *prm_names):
        """
        Return values of one or more solver input or output parameters.
        Non-existing parameter names lead to a NameError exception.
        @param prm_names: name(s) of parameter(s).
        @type prm_names: strings.

        If no arguments are given, all parameters to be set and reported
        will be returned as one dictionary.
        @return: 1) list of values, with sequence of parameters corresponding
        to sequence of arguments in the call, or 2) dictionary with
        all parameter names and values, if no arguments are provided

        Example::

        >>> solver = ForwardEuler()
        >>>
        >>> def myrhs(y,t, a,b):
        ...     return [-a*y[0],-b*y[1]]
        ...
        >>> solver.set(f=myrhs, initial_condition=[0,0], f_args=(1,1))
        >>> solver.get('dt', 'f_args')  # returns list of values
        [1.0, (1, 1)]
        >>> solver.get('dt')  # returns scalar value
        1.0
        >>> p = solver.get()  # get all parameters
        >>> import pprint
        >>> pprint.pprint(p)
        {'dt': 1.0,
         'f': <function myrhs at 0xb6d56ae4>,
         'f_args': (1, 1),
         'f_kwargs': {},
         'initial_condition': 0,
         'initial_time': [0.0, 0.0]
         'solution_storage': 'array'}
        
        """
        values = []
        all = False  # True: return everything in self._prm and self._out
        if len(prm_names) == 0:
            prm_names = self._prm.keys() + self._out.keys()
            all = True

        for name in prm_names:
            if name in self._prm:
                values.append(self._prm[name])
            elif name in self._out:
                values.append(self._out[name])
            else:
                
                raise NameError, '%s is a non-existing parameter name.\n'\
                      '%s' % (name, self.usage(return_string=True))

        if all:
            r = {}
            for name, value in zip(prm_names, values):
                r[name] = value
            return r
        else:
            # return scalar if just one name, otherwise a list:
            if len(values) == 1:
                return values[0]
            else:
                return values

    def get_safe(self, *prm_names, **kwargs):
        """
        As get, but None values indicate uninitialized/illegal values
        causing a ValueError exception to be raised unless the
        parameter name is listed for the "ignore_None" keyword
        argument (in kwargs).
        
        Some parameters like 'f', 'initial_condition', etc. are
        checked for validity and wrapped such that the result is a
        Numerical Python array. Here is a demo::

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
        values = self.get(*prm_names)
        ignore_None = kwargs.get('ignore_None', [])

        if len(prm_names) == 1:
            # values is a scalar
            if values is None and prm_names not in ignore_None:
                raise ValueError, \
                      'parameter %s is None; it must be initialized' % \
                      (prm_names[0])
            values = [values]  # wrap in list for code below
            
        else:
            # values is a list/tuple
            msg = [name \
                   for value, name in zip(values, prm_names) \
                   if value is None and name not in ignore_None]
            if msg:
                raise ValueError, \
                      'parameter(s) %s = None; must be initialized' % \
                      (str(prm_names)[1:-1])
            values = list(values)   # need list functionality

        prm_names = list(prm_names) # need list functionality

        # right-hand side and Jacobian functions may need to be wrapped
        # (self._f2array and self._J2array indicate this;
        #  set in self._check_compatibility)
        if 'f' in prm_names:
            if not hasattr(self, '_f2array'):
                raise ValueError, 'initial_condition must be set before '\
                      'a safe f can be extracted'
            if self._f2array:
                # f does not return an array, wrap in NumPy array:
                idx = prm_names.index('f')
                f = values[idx]
                def f_wrapper(y, t, *f_args, **f_kwargs):
                    return N.array(f(y, t, *f_args, **f_kwargs))
                values[idx] = f_wrapper
#                values[idx] = lambda y, t, f=values[idx]: N.array(f(y, t))
        if 'Jacobian' in prm_names:
            if not hasattr(self, '_J2array'):
                raise ValueError, 'initial_condition must be set before '\
                      'a safe Jacobian can be extracted'
            if self._J2array:
                # J does not return an array, wrap in NumPy array:
                idx = prm_names.index('Jacobian')
                J = values[idx]
                def J_wrapper(y, t, *J_args, **J_kwargs):
                    return N.array(J(y, t, *J_args, **J_kwargs))
                values[idx] = J_wrapper
#                values[idx] = lambda y, t, J=values[idx]: N.array(J(y, t))
        if 'initial_condition' in prm_names:
            # wrap as Numerical Python array:
            idx = prm_names.index('initial_condition')
            values[idx] = N.array(values[idx], copy=False)

        if len(values) == 1:
            return values[0]
        else:
            return values
        

    def set_meta_data(self, **kwargs):
        self._meta_data.update(**kwargs)  # accept anything


    def get_meta_data(self, name):
        try:
            return self._meta_data[name]
        except KeyError:
            return None

    def import_parameters(self, solver):
        """
        Import parameters from another solver object.
        (That is, items in solver._prm are copied to self._prm
        if the name (key) is already registered in self._prm.)
        """
        
        for name in solver._prm:
            if name in self._prm:
                self._prm[name] = solver._prm[name]
                
    def _update(self, **kwargs_in_last_set_call):
        """
        Check data consistency and make updates of data structures
        after a call to set(**kwargs_in_last_set_call).
        @return: False means that size of data structures is unaltered,
        while True means that the size of the ODE system has changed and
        so may internal data structures.
        """
        size = self.size  # check if size changes due to new parameter
        if 'initial_condition' in kwargs_in_last_set_call and \
             self._prm['f'] is not None:
            # initial_condition was set, f is initialized:
            self._check_compatibility()
        elif 'f' in kwargs_in_last_set_call and \
             self._prm['initial_condition'] is not None:
            # f was set, initial_condition is initialized:
            self._check_compatibility()
        elif 'initial_condition' in kwargs_in_last_set_call and \
           self.size > 0:
            # initial_condition has been reset,
            # check that new length is compatible:
            try:
                n = len(initial_condition)
            except TypeError:
                # len() does not work on scalar initial_condition
                n = 1
            if n != self.size:
                raise ValueError, \
                      'initial_condition=%s has length %d, not %d' % \
                      (str(initial_condition), n, self.size)

        return size != self.size


    def _store(self, y, t):
        """
        Store solution y and corresponding time t.
        Methods of storage: local list, file (set by the
        parameter name "solution_storage").
        """
        # file or arrays
        if self._prm['solution_storage'] == 'file':
            raise NotImplementedError, \
                  'solution_storage="file" is not yet implemented'
        else:
        #elif self._prm['solution_storage'] == 'list':
            if not hasattr(self, '_y'):
                self._y = []
            if not hasattr(self, '_t'):
                self._t = []
            if isinstance(y, N.ndarray):
                # storing references is potentially problematic since
                # algorithms may update y by in-place modifications;
                # take a copy to be safe:
                y = y.copy()
            self._y.append(y)
            self._t.append(t)

    y = property(fget=lambda self: self._y,
                 doc='solution of ODE (mxn array for m steps and n unknowns)')
    t = property(fget=lambda self: self._t,
                 doc='time points for discrete solution')

    def _callable_or_source(self, f):
        """
        Check if f is a callable object or the source code of a function
        to be compiled.
        """
        if callable(f):
            return f
        
        if not isinstance(f, basestring):
            raise ValueError, 'f=%s %s is not callable or a '\
                  'filename (of a C/C++/Fortran source' % (str(f), type(f))
        if not os.path.isfile(f):
            raise ValueError, \
                  'f function given as source code, but the path\n%s '\
                  'does not exist' % f

        # compile source into module, load function from module and return
        root, ext = os.path.splitext(f)
        if ext == '.f':
            # F77 function
            pass
        elif ext == '.f90':
            # F90 function
            pass
        elif ext == '.c':
            # C function
            pass
        elif ext in ('.cpp', '.C', '.cxx'):
            # C++ function
            pass
        return f
        
        
    def _check_compatibility(self):
        """
        Investigate f function.
        Check compatibility of length with initial_condition.
        """
        #try:
        #    if self._check_compatibility_called:
        #        return  # avoid multiple calls to this method
        #except AttributeError:        # self._check_compatibility_called not defined
        #    self_init_called = False  # initialize indicator
            
        method = '%s._check_compatibility' % self.__class__.__name__
        if 1: # try:
            initial_condition = self.get_safe('initial_condition')
            try:
                n = len(initial_condition)
            except TypeError:
                # len() does not work on scalar initial_condition
                n = 1
            self._size = n
        else: #except ValueError:
            # cannot do anything below without initial_condition,
            # need to wait until this parameter is supplied
            return 0
        
        f = self._prm['f']
        if f is None:
            raise ValueError, '%s:\ncall %s.set(f=...) to set right-hand '\
                  'side of ODE system' % (method, self.__class__.__name__)
        else:
            # is f a function or the source of a file to be compiled?
            f = self._callable_or_source(f)
            f_args, f_kwargs = self.get('f_args', 'f_kwargs')

            try:
                f0 = f(initial_condition, 0.0, *f_args, **f_kwargs)
            except TypeError, e:
                # f_args and f_kwargs might be missing
                raise ValueError, 'f_args and/or f_kwargs must be set\n%s' % e

            # check if f returns list/tuple, which we in algorithms need
            # to wrap to NumPy arrays (self._f2array is then set to True):
            if isinstance(f0, (list,tuple)):
                self._f2array = True
            elif isinstance(f0, N.ndarray):
                self._f2array = False
            elif operator.isNumberType(f0):
                self._f2array = False
            elif isinstance(f0, type):   # class with __call__
                self._f2array = True
                # (it's already checked that f is callable (type check))
            else:
                raise TypeError, 'f (right-hand side) returns %s, not '\
                      'list, tuple, array or number' % type(f0)
            f0 = N.array(f0, copy=False)
            if f0.size != n:
                raise ValueError, 'f returns vector of length %d while '\
                      'initial_condition has incompatible length %d' % \
                      (len(f0), n)

            
        #self._check_compatibility_called = True  # avoid repeated calls to _init
        
        return n

    def _stored_data(self):
        """Return the collection of y(t) and t values stored as solution."""
        if self._prm['solution_storage'] == 'list':
            return self.y, self.t
        elif self._prm['solution_storage'] in ('array', 'NumPy', 'numpy',
                                               'Numerical Python'):
            y = N.array(self.y, copy=False)
            if len(y.shape) == 1:
                # individual y values were scalars so y is now a
                # one-dim array; turn it into the standard two-dim array:
                y = y[:,N.newaxis]
            t = N.array(self.t, copy=False)
            self._y = y;  self._t = t
            return self.y, self.t
        elif self._prm['solution_storage'] == 'file':
            raise NotImplementedError, \
                  'solution_storage="file" is not yet implemented'


    def __repr__(self):
        """
        Write the string that can (partially) reconstruct the state
        of the object.

        For readability, parameters with a trivial value (None, {},
        (), []) are not printed. Callable objects (whose values are
        memory addresses and hence not of much use for reconstructing
        the state) are also skipped in the output.
        """
        p = self._prm  # short form
        ok_names = [name for name in p \
                    if p[name] is not None and p[name] != {} and \
                    p[name] != () and p[name] != [] and not callable(p[name])]
        ok_names.sort()
            
        s = self.__class__.__name__ + '('
        args = ', '.join(['%s=%s' % (name, repr(self._prm[name])) \
                          for name in ok_names])
        s += args + ')'
        return s


# --- end of class ODESolver ---


def _constant_step_size_prm(_solver_prm, _solver_prm_help, _solver_prm_type):
    """
    In-place update of dictionaries with typical parameters for a
    constant step-size solver.
    """
    _solver_prm.update({'dt': 1.0,})
    _solver_prm_type.update({'dt': float,})
    _solver_prm_help.update({'dt' : 'constant/initial time step size',})
    

class ImplicitSolver(ODESolver):
    """
    Base class for implicit solvers.
    The class extends ODESolver's parameters by data for Jacobian,
    linear and nonlinear solver methods.
    """
    
    _solver_prm = {
        'Jacobian': None,
        'J_args': (),
        'J_kwargs': {},
        'linear_solver': 'built-in',
        'nonlinear_solver': 'built-in',
        'nls_args': [],
        'g_args': []
        }
    _solver_prm_help = {
        'Jacobian': 'Jacobian of right-hand side (f)',
        'J_args': 'optional positional arguments to '\
        'Jacobian : Jacobian(y, t, *J_args)',
        'J_kwargs': 'optional keyword arguments to '\
        'Jacobian: Jacobian(y, t, *J_args, **J_kwargs)',
        
        'linear_solver': '''\
If not "built-in" in the solver, this parameter must be a user-specified
  function(J, b, *ls_args),
where J is the coefficient matrix of a linear system, b is the
right-hand side, and ls_args is a tuple of optional arguments.
The function must return the solution as a NumPy array.''',
                        
        'nonlinear_solver': '''\
If not "built-in", this parameter must be a user-specified
function that can solve systems of nonlinear equations: g=0.
The signature of the function is
  function(g, guess, *nls_args, *g_args),
where g is a vector-valued function describing the equations,
  g(x, *g_args)
with x as the vector of unknowns. The lists nls_args and g_args
hold optional user-given parameters to the nonlinear solver
function and the g function, respectively.''',

        'nls_args': '''\
arguments to the function specified as nonlinear_solver''',
        'g_args': '''\
arguments to the function g call by a nonlinear_solver to solve g=0''',
        }

    _solver_prm_type = {
        'Jacobian': _func_or_file_type,
        'J_args': (list,tuple),
        'J_kwargs': (dict,),
        'linear_solver': _user_alg_type,
        'nonlinear_solver': _user_alg_type,
        'nls_args': (list,tuple),
        'g_args': (list,tuple),
        }
                        
    _solver_out = {}
    _solver_out_help = {}
    
    def __init_(self, solver_language='Python'):
        ODESolver.__init__(self, solver_language=solver_language)
        self._prm.update(ImplicitSolver._solver_prm)
        self._prm_help.update(ImplicitSolver._solver_prm_help)
        self._prm_type.update(ImplicitSolver._solver_prm_type)
        self._out.update(ImplicitSolver._solver_out)
        self._out_help.update(ImplicitSolver._solver_out_help)

    def _check_compatibility(self):
        """
        Investigate f and J functions.
        Check compatibility of size with that of the initial_condition.
        """
        # check f and initial_condition:
        ODESolver._check_compatibility(self)

        # check Jacobian here:

        method = '%s._check_compatibility' % self.__class__.__name__
        J = self._prm['Jacobian']
        if J:
            # is J a function or the source of a file to be compiled?
            J = self._callable_or_source(J)
            J_args, J_kwargs = self.get('J_args', 'J_kwargs')

            try:
                J0 = J(initial_condition, 0.0, *J_args, **J_kwargs)
            except TypeError, e:
                # J_args and J_kwargs might be missing
                raise ValueError, 'J_args and/or J_kwargs must be set\n%s' % e
            
            # check if f returns list/tuple, which we in algorithms need
            # to wrap to NumPy arrays:
            if isinstance(J0, (list,tuple)):
                self._Jacobian2array = True
            elif isinstance(J0, N.ndarray):
                self._Jacobian2array = False
            elif operator.isNumberType(J0):
                self._f2array = False
            elif isinstance(J0, type):  # class with __call__
                self._J2array = True
                # (it's already checked that J is callable (type check))
            else:
                raise TypeError, 'Jacobian returns %s, not '\
                      'list, tuple, array or number' % type(J0)

            J0 = N.array(J0, copy=False)
            if len(J0.shape) != 2:
                raise ValueError, '%s:\nJacobian has wrong dimension '\
                      '(%s != 2)' % (method, len(J0.shape))
            n = self.size
            if J0.shape[0] != n and J0.shape[1] != n:
                raise ValueError, '%s:\nJacobian has wrong shape '\
                      '%s, not (%s, %s) as initial_condition indicates' \
                      % (method, J0.shape, n, n)

        return n

    def _update(self, **kwargs_in_last_set_call):
        """
        Check data consistency and make updates of data structures
        after calling set(**kwargs_in_last_set_call).
        @return: False means that size of data structures is unaltered,
        while True means that the size of the ODE system has changed.
        """
        size = self.size  # check if size of ODE system changes
        ODESolver._update(self, **kwargs_in_last_set_call)
            
        if 'initial_condition' in kwargs_in_last_set_call and \
             self._prm['Jacobian'] is not None:
            # initial_condition was set, J is initialized, check compatibility:
            self._check_compatibility()
        elif 'Jacobian' in kwargs_in_last_set_call and \
             self._prm['initial_condition'] is not None:
            # J was set, initial_condition is initialized, check compatibility:
            self._check_compatibility()

        return size != self.size


import pprint
import explicit_ode_algorithms
# load the functions implementing the algorithms:
_registered_explicit_algorithms = [funcname \
 for funcname in dir(explicit_algorithms) if funcname.endswith('_algorithm')]

class ExplicitSolver(ODESolver):
    """
    Simple explicit ODE solvers written in Python.
    The f(y,t) function is to be supplied as a Python function.
    """
    _solver_prm = {}
    _solver_prm_help = {}
    _solver_prm_type = {}
    _constant_step_size_prm(_solver_prm, _solver_prm_help, _solver_prm_type)
    _solver_out = {}   # _solver_info is a much better info!!!!!
    _solver_out_help = {}

    __doc__ += _doc_format(ODESolver,
                           [_solver_prm, _solver_prm_help, _solver_prm_type,
                            _solver_out, _solver_out_help])


    
    def __init__(self, **kwargs):
        self.algorithm = kwargs.get('algorithm', 'ForwardEuler') + \
                         '_algorithm'
        if self.algorithm not in _registered_explicit_algorithms:
            raise ValueError, 'algorithm %s is not available '\
                  '(must be one of %s)' % \
                  (self.algorithm, str(_registered_explicit_algorithms)[1:-1])
        if 'algorithm' in kwargs:
            del kwargs['algorithm']  # 'algorithm' is not a reg. parameter
        
        ODESolver.__init__(self, solver_language='Python')
        self._prm.update(ExplicitSolver._solver_prm)
        self._prm_help.update(ExplicitSolver._solver_prm_help)
        self._prm_type.update(ExplicitSolver._solver_prm_type)
        self._out.update(ExplicitSolver._solver_out)
        self._out_help.update(ExplicitSolver._solver_out_help)

    def integrate(self, y0=None, t0=None, T=None):
        assert(T is not None, 'T must be given!')
        f, dt, y0, t0, f_args, f_kwargs = \
           self.get_safe('f', 'dt', 'initial_condition',
                         'initial_time', 'f_args', 'f_kwargs')
        if T-t0 < dt:  dt = T-t0
        algorithm = eval('explicit_algorithms.' + self.algorithm)
        algorithm(t0, y0, f, T, dt, self._store, f_args, f_kwargs)
        return self._stored_data()


# make subclasses implementing all the methods in the explicit_algorithms
# module:
# (use the functions' doc strings in explicit_algorithms as doc strings
# in the classes, and also copy in the base class doc string (except for
# the now irrelevant heading line in ExplicitSolver.__doc__)

for _algorithm in _registered_explicit_algorithms:
    _algorithm = _algorithm.replace('_algorithm', '')
    code = '''
class %s(ExplicitSolver):
    """
    %s
    """
    _solver_prm_type = {'f': _func_type}  # must be Python callable
    def __init__(self, **kwargs):
        ExplicitSolver.__init__(self, algorithm='%s')
        self._prm_type.update(%s._solver_prm_type)
        self.set(**kwargs)
        self.make_attributes()
''' % (_algorithm,
        eval('explicit_algorithms.'+_algorithm+'_algorithm.__doc__') + \
        '\n'.join(ExplicitSolver.__doc__.split('\n')[2:]),
       _algorithm, _algorithm)
    #print code
    exec code


    

class SciPyIntegrator(ImplicitSolver):
    """
    Interface to SciPy ODE solvers (the scipy.integrate.ode class).
    """

    _solver_prm = {'time_points': []}
    _solver_prm_help = {'time_points':
                        'points of time when y needs to be computed',
                        }
    _solver_prm_type = {}
    _solver_out = {'success': True}
    _solver_out_help = {'success':
                "result of scipy.integrate.ode solver's successful() method",
                        }

    __doc__ += _doc_format(ImplicitSolver,
                           [_solver_prm, _solver_prm_help, _solver_prm_type,
                            _solver_out, _solver_out_help])
    
    def __init__(self, **kwargs):
        base = self.__class__.__bases__[0]  # assume single inheritance
        base.__init__(self, solver_language='F77')
        self.method = 'Not set'  # set in subclass
        self._prm.update(SciPyIntegrator._solver_prm)
        self._prm_help.update(SciPyIntegrator._solver_prm_help)
        self._prm_type.update(SciPyIntegrator._solver_prm_type)
        self._out.update(SciPyIntegrator._solver_out)
        self._out_help.update(SciPyIntegrator._solver_out_help)

        self.set(**kwargs)
        self.make_attributes()

    def _get_solver_specific_prm(self):
        """
        Extract (via self.get) the parameters that must be transferred
        to solver.set_integrator. Return as dictionary (leave out
        None values and employ available logic).
        """
        raise NotImplementedError
    
    def integrate(self, T):
        f, y0, t0, f_args, f_kwargs, J, J_args, J_kwargs, time_points = \
           self.get_safe('f', 'initial_condition',
                         'initial_time', 'f_args', 'f_kwargs',
                         'Jacobian', 'J_args', 'J_kwargs',
                         'time_points',
                         ignore_None=['Jacobian'])
        if T > time_points[-1]:
            time_points.append(T)
        if t0 < time_points[0]:
            time_points.insert(0, t0)
            
        if not hasattr(self, 'solver'):
            # initialize the class ode object the first time this
            # method is called:
            import scipy.integrate
            # wrap f and J to take t,y and not y,t (as here) as arguments:
            def f_wrapper(t, y, *f_prm):
                return f(y, t, *f_prm)
            if J is not None:
                def J_wrapper(t, y, *J_prm):
                    return J(y, t, *J_prm)
            else:
                J_wrapper = None
            self.solver = scipy.integrate.ode(f_wrapper, jac=J_wrapper)
            solver_parameters = self._get_solver_specific_prm()
            self.solver.set_integrator(self.solver.method,
                                       **solver_parameters)
            self.solver.set_f_params(*f_args)
            self.solver.set_J_params(*J_args)
            if f_kwargs or J_kwargs:
                raise ValueError, \
                      'f_kwargs or J_kwargs cannot be used with SciPy methods'
            
        return self.algorithm(t0, y0, T, time_points)
    
    def algorithm(self, t0, y0, T, time_points):
        t = time_points[0]
        y = y0
        self._store(y, t)
        
        for t in time_points[1:]:
            self.solver.integrate(t, step=0, relax=0)
            self._store(self.solver.y, self.solver.t)

        self._out['success'] = self.solver.successful()
        return self._stored_data()


class SciPyVode(SciPyIntegrator):
    """
    Interface to SciPy's vode integrator.
    """
    _solver_prm = {'atol': 1.0E-7,
                   'rtol': 1.0E-5,
                   'lband': None,
                   'rband': None,
                   'method': 'adams',
                   'nsteps': 1,
                   'first_step': 0.0,
                   'min_step': 0.0,
                   'max_step': 0.0,
                   'order': 12,
                   }
    _solver_prm_help = {
        'atol': '''Absolute error tolerance
given as scalar or array/list (for each component in the ODE system.
The estimated local error in Y(i) will be controlled so as
to be roughly less (in magnitude) than
        EWT(i) = rtol*abs(y[i]) + atol,
        EWT(i) = rtol*abs(y[i]) + atol[i].
Thus the local error test passes if, in each component,
either the absolute error is less than atol (or atol[i]),
or the relative error is less than rtol.
Use rtol = 0.0 for pure absolute error control, and
use atol = 0.0 (or atol[i] = 0.0) for pure relative error
control.  Caution.. Actual (global) errors may exceed these
local tolerances, so choose them conservatively.''',
        'rtol': 'Relative error tolerance, see doc of atol.',
        'lband': 'Left half-bandwidth of Jacobian',
        'rband': 'Right half-bandwidth of Jacobian',
        'method': 'Type of method: "adams" or "bdf"',
        'nsteps': '''Maximum number of (internally defined) steps
allowed during one call to the solver. The default value is 500
(also implied by nsteps=0).''',
        'first_step': '''The step size to be attempted on the first step.
The default value (implied by first_step=0) is determined by the solver.''',
        'min_step': '''The maximum absolute step size allowed.
The default value (implied by min_step=0) is infinite.''',
        'max_step': '''The minimum absolute step size allowed.
The default value is 0.''',
        'order': 'order of the method: <=12 for "adams", <=5 for "bdf"',
        }

    _solver_prm_type = {'atol': _array_or_number_type,
                        'rtol': _array_or_number_type,
                        'lband': int,
                        'rband': int,
                        'method': lambda v: v in ('adams', 'bdf'),
                        'nsteps': int,
                        'first_step': float,
                        'min_step': float,
                        'max_step': float,
                        'order': int,
                        }
    _solver_out = {}
    _solver_out_help = {}

    __doc__ += _doc_format(SciPyIntegrator,
                           [_solver_prm, _solver_prm_help, _solver_prm_type,
                            _solver_out, _solver_out_help])
    
    def __init__(self, **kwargs):
        base = self.__class__.__bases__[0]  # assume single inheritance
        base.__init__(self, solver_language='F77')
        self.solver_method = 'Not set'  # set in subclass
        self._prm.update(SciPyVode._solver_prm)
        self._prm_help.update(SciPyVode._solver_prm_help)
        self._prm_type.update(SciPyVode._solver_prm_type)
        self._out.update(SciPyVode._solver_out)
        self._out_help.update(SciPyVode._solver_out_help)

        self.set(**kwargs)
        self.make_attributes()

    def _get_solver_specific_prm(self):
        """
        Extract (via self.get) the parameters that must be transferred
        to solver.set_integrator. Return as dictionary (leave out
        None values and employ available logic).
        """
        d = {}  # dict to be returned
        prm_names = 'atol', 'rtol', 'lband', 'rband', 'method', 'nsteps', \
                    'first_step', 'first_min', 'first_max', 'order'
        for name in prm_names:
            value = self.get(name)
            if value is not None:
                d[name] = value
        if self._prm['Jacobian'] is None:
            d['with_jacobian'] = False
        else:
            d['with_jacobian'] = True

        # let method be lower case name:
        if re.search('adams', method, re.I):
            method = 'adams'
        elif re.search('bdf', method, re.I):
            method = 'bdf'
        else:
            raise ValueError, \
                  'method must be "adams" or "bdf", not %s' % method
        if method == 'adams':
            if order > 12:
                raise ValueError, \
                      'order=%d for Adams method must be <= 12' % order
        if method == 'bdf':
            if order > 12:
                raise ValueError, \
                      'order=%d for Adams method must be <= 12' % order
        return d
            

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
        and name is a legal parameter name in the solver object,
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
        legal_names = solver._prm.keys()
        values = {}
        i = 0
        while i <= len(self.argv)-2:
            name = self.argv[i]
            name = name.replace('-', '') # remove hyphens
            if name in legal_names:
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
        """Explain what legal command line options are."""
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


    
