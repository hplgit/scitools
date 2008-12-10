import numpy as N
import operator, os
from codegenerator import *

#---------------------------------------------------------------------
# ----- helper functions for detecting right object type ------------

# test that a variable v is a function or None:
func_type = lambda v: v is None or callable(v)

# test that a variable v is a function, None, or source code of a
# function in a file:
func_or_file_type = lambda v: v is None or callable(v) or \
                     (isinstance(v, basestring) and os.path.isdir(v))

# test that a variable v is array/list-like, a number, or None:
array_or_number_type = lambda v: v is None or \
      isinstance(v, (list, tuple, N.ndarray, float, complex, int))


# test that a variable v is a function or the string 'built-in'
# (used for linear or nonlinear solvers that can be part of the
# ODE routine or supplied as a user-defined algorithm):
user_alg_type = lambda v: callable(v) or v == 'built-in'
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

def doc_format(*classes_or_list_of_prm_dicts):
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
    
      __doc__ += doc_format(ImplicitSolver,
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
                raise TypeError, 'not right arguments to doc_format'
            
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




def constant_step_size_prm(_solver_prm, _solver_prm_help, _solver_prm_type):
    """
    In-place update of dictionaries with typical parameters for a
    constant step-size solver.
    """
    _solver_prm.update({'dt': 1.0,})
    _solver_prm_type.update({'dt': float,})
    _solver_prm_help.update({'dt' : 'constant/initial time step size',})
    

# ============================================================================

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
    func_type = lambda v: v is None or callable(v)
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
    array_or_number_type = lambda v: v is None or \
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
        'f': func_or_file_type,
        'f_args': (list,tuple),
        'f_kwargs': (dict,),
        'initial_condition': array_or_number_type,
        'initial_time': float,
        'solution_storage': str,
        }
    _solver_out = {}
    _solver_out_help = {}

    __doc__ += doc_format()

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
