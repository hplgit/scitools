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

    # auto update of doc string with info about valid parameter names:
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

    # auto update of doc string with info about valid parameter names:
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
