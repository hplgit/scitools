from implicit_2 import ImplicitSolver, doc_format, array_or_number_type

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

    __doc__ += doc_format(ImplicitSolver,
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

    _solver_prm_type = {'atol': array_or_number_type,
                        'rtol': array_or_number_type,
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

    __doc__ += doc_format(SciPyIntegrator,
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

