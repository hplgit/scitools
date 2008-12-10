from explicitsolver import ODESolver

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

