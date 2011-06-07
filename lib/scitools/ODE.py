"""
Module for solving scalar ordinary differential equations (ODEs) or
systems of ODEs.

The module provides a unified interface to solving ODEs. Some classes
in this module implement algorithms in Python, while others are
wrappers of Python wrappers of compiled ODE solvers (from scipy, for instance).

The following methods are implemented:

Forward Euler (ForwardEuler)
4th-order Runge-Kutta (RungeKutta4)
Iterated Midpoint strategy (MidpointIter)
2nd-order Runge-Kutta (RungeKutta2)
Heun's method (Heun)
plain Leapfrog (Leapfrog)
filtered Leapfrog (LeapfrogFiltered)
3rd-order Adams-Bashforth (AdamsBashforth3)
VODE C code (VODE, calling scipy's vode wrapper)
Backward Euler (BackwardEuler)
Three-level backward scheme (Backward2Step)
Theta-rule (ThetaRule)
4-5-th order Runge-Kutta-Fehlberg (RungeKuttaFehlberg)

The usage is very simple. Here is an example on solving u'=-a*u:
>>> import scitools.ODE as ode
>>> name = ode.RungeKutta4  # example
>>> def f(u, t):
...     return -a*u   # right-hand side of ODE
...
>>> method = name(f)
>>> method.set_initial_condition(1)
>>> a = 1
>>> import numpy as np
>>> time_points = np.linspace(0, 3, 11)
>>> u, t = method.solve(time_points)
>>> import scitools.std as st
>>> st.plot(t, u)

Here is an example on solving a system, u'' + u = 0 expressed as
a 2x2 first-order ODE system:
>>> import scitools.ODE as ode
>>> name = ode.RungeKutta4  # example
>>> def f(u, t):
...     return [u[1], -u[0]]
...
>>> method = name(f)
>>> method.set_initial_condition([1, 0])
>>> import numpy as np
>>> time_points = np.linspace(0, 6*np.pi, 401)
>>> u, t = method.solve(time_points)
>>> import scitools.std as st
>>> st.plot(t, u[:,0], 'r-', t, u[:,1], 'b-', legend=('u[0]', 'u[1]'))
"""
# Remaining doc: setting parameters, using f_args, implicit methods

import pprint
import numpy as np
import sys, os

class Solver:
    """
    Superclass for numerical methods solving scalar and vector ODEs

      du/dt = f(u, t)

    Attributes stored in this class:
    t: array of time values
    u: array of solution values (at time points t)
    k: step number of the most recently computed solution
    f: callable object implementing f(u, t)
    """
    _legal_prms = dict(
        f = dict(
            help='right-hand side f(u,t) defining the ODE',
            type=callable),

        f_args = dict(
            help='extra parameters to f: f(u,t,*f_args,**f_kwargs)',
            type=(tuple,list), default=()),

        f_kwargs = dict(
            help='extra parameters to f: f(u,t,*f_args,**f_kwargs)',
            type=dict, default={}),

        complex_valued = dict(
            help='True if f is complex valued',
            default=False, type=bool),
        )
                   
    def __init__(self, f, **kwargs):
        self._legal_prms.update(Solver._legal_prms)
        # Each subclass must take its _legal_prms and update it
        # with the parent class' parameters. (See subclasses.)
        
        # Set default values
        for name in self._legal_prms:
            if 'default' in self._legal_prms[name]:
                setattr(self, name, self._legal_prms[name]['default'])

            elif name not in kwargs and name != 'f':
                #Liwei: I didn't understand this one, can you explain?
                #One does not need to set kwargs - that can be done
                #later through set(...)
                # Check whether it is optional input
                types = self._legal_prms[name]['type']
                if not isinstance(types, (list,tuple)) or \
                   None not in types:
                    raise AttributeError(\
                        '%s has to be set as a mandatory input' % name)
            
        self.set(**kwargs)

        self.users_f = f  # stored in case it is handy to have
        if not callable(f):
            raise TypeError('f is %s, not a function' % type(f))
        # For ODE systems, f will often return a list, but
        # arithmetic operations with f in numerical methods
        # require that f is an array. Let self.f be a function
        # that first calls f(u,t) and then ensures that the
        # result is an array (without imposing any type - if
        # U0 has integers it is detected and converted to floats
        # to ensure float results from f).
        self.f = lambda u, t: np.asarray(f(u, t, *self.f_args, **self.f_kwargs))
        self.initialize()
        
    def initialize(self):
        """Can be implemented in subclasses for special initialization."""
        return None

    def set(self, strict=False, **kwargs):
        """
        Set values of parameters. Check that the type of each value
        is among the specified legal types (float, int, callable, None,
        user-defined function for checking type).

        If strict is True, only registered parameter names are accepted,
        otherwise unregistered names are ignored.
        """
        for name in kwargs:
            value = kwargs[name]

            # Is the name of a parameter a registered, valid name?
            if name not in self._legal_prms:
                if strict:
                    raise ValueError('%s is not a legal parameter name in class %s\n(legal names: %s)' % (name, self.__class__.__name__, str(self._legal_prms.keys())[1:-1]))
                else:
                    print '%s is not a parameter in class %s' % (name, self.__class__.__name__)
                    continue

            # Test if value is of the right specified type
            if 'type' in self._legal_prms[name]:
                types = self._legal_prms[name]['type']
                # (Ex: types = (None, callable, float))
                if not isinstance(types, (list,tuple)):
                    types = [types]  # make list
                if value is None and None in types:
                    continue # None is ok
                checked_type = False
                for tp in types:
                    # Check if tp is callable or a user function for type
                    if tp is not None:
                        if tp == callable:
                            checked_type = True
                            if not callable(value):
                                raise TypeError('set: %s is %s, not a '\
                                                'callable function' %
                                                (name, type(value)))
                        else:
                            try:
                                # Assume tp is a type
                                if isinstance(value, tp):
                                    checked_type = True
                            except TypeError:
                                # tp is not a type (failure above)
                                if callable(tp):
                                    # User's function for checking type,
                                    # returns False if value is of wrong type
                                    if not tp(value):
                                        raise TypeError(
                                            'set: %s is wrong type %s, %s returned False' %
                                            (name, type(value), tp.__name__))
                                    else:
                                        checked_type = True

                if not checked_type:
                    raise TypeError('set: %s is %s, not %s' % \
                                    (name, type(value), types))
            # Test on right type was successful (if we come here)
            if 'range' in self._legal_prms[name]:
                if 'type' in self._legal_prms[name]:
                    if self._legal_prms[name]['type'] in (float, int, complex):
                        if len(self._legal_prms[name]['range']) == 2:
                            # Valid value is an interval
                            lo, hi = self._legal_prms[name]['range']
                            if not lo <= value <= hi:
                                raise ValueError(
                                    '%s=%s is illegal - range=[%s, %s]' %
                                    (name, value, lo, hi))
                    else:
                        # Valid value is among a range of values
                        if not value in self._legal_prms[name]['range']:
                            raise ValueError(
                                '%s=%s is illegal - range=%s' %
                                (name, value, str(self._legal_prms[name]['range'])))
                                
            # Test on right value was successful (if we come here)
            setattr(self, name, value)

        # For some subclasses with a lot of parameters, these
        # can be put in a dict p. The code can then look as
        # if name in self.p: set p keys
        # else: Solver.set(self, **kwargs)

    def get(self, parameter_name=None):
        """
        Return value of parameter.
        If parameter_name=None, return dict of all parameters.
        """
        if parameter_name is None:
            # Python v2.7 dict comprehension
            #return {name: getattr(self, name) for name in self._legal_prms}
            return dict([(name, getattr(self, name, None)) for name in self._legal_prms])
        else:
            if hasattr(self, parameter_name):
                return getattr(self, parameter_name)
            else:
                raise AttributeError('Parameter %s is not set' % parameter_name)
        
    def advance(self):
        """Advance solution one time step."""
        raise NotImplementedError

    def constant_time_step(self):
        """Check that self.t has a uniform mesh in time."""
        return np.allclose(self.t, np.linspace(self.t[0], self.t[-1],
                                               len(self.t)))
    def valid_data(self):
        return True
    
    def set_initial_condition(self, U0):
        # Test first if U0 is sequence (len(U0) possible),
        # and use that as indicator for system of ODEs.
        # The below code should work for U0 having
        # float,int,sympy.mpmath.mpi and other objects as elements.
        try:
            self.neq = len(U0)
            U0 = np.asarray(U0)          # (assume U0 is sequence)
        except TypeError:
            # U0 has no __len__ method, assume scalar
            self.neq = 1
            if isinstance(U0, int):
                U0 = float(U0)           # avoid integer division
        self.U0 = U0

    def solve(self, time_points, terminate=None):
        """
        Compute solution u for t values in the list/array
        time_points, as long as terminate(u,t,step_no) is False. 
        terminate(u,t,step_no) is a user-given function
        returning True or False. By default, a terminate
        function which always returns False is used.
        """
        if terminate is None:
            terminate = lambda u, t, step_no: False

        if isinstance(time_points, (float,int)):
            raise TypeError('solve: time_points is not a sequence')
        
        self.t = np.asarray(time_points)
        N = self.t.size - 1  # no of intervals

        f0 = np.array(self.f(self.U0, self.t[0]))
        if f0.dtype == np.int32 or f0.dtype == np.int64 or f0.dtype == np.int:
            # Do not allow integers in computations (i.e., ensure that
            # U0 is at least float even though the user has specified
            # it as int scalar or int array and self.f could propagate
            # int to an int (or int array) result).
            self.dtype = np.complex if self.complex_valued else np.float
        elif f0.dtype == np.complex:
            self.dtype = np.complex
        else:
            self.dtype = f0.dtype

        if self.neq == 1:  # scalar ODEs
            self.u = np.zeros(N+1, self.dtype)
        else:              # systems of ODEs
            self.u = np.zeros((N+1,self.neq), self.dtype)

        if not self.valid_data():
            raise ValueError('Invalid data in "%s":\n%s' % \
                             (self.__class__.__name__,
                              pprint.pformat(self.__dict__)))


        # Assume that self.t[0] corresponds to self.U0
        self.u[0] = self.U0

        # Time loop
        for n in range(N):
            self.n = n
            self.u[n+1] = self.advance()
            if terminate(self.u, self.t, self.n+1):
                break  # terminate loop over n
        return self.u, self.t
    

class ForwardEuler(Solver):
    """Forward Euler scheme: u[n+1] = u[n] + dt*f(u[n], t[n])."""
    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        unew = u[n] + dt*f(u[n], t[n])
        return unew


class Leapfrog(Solver):
    """
    Leapfrog scheme: u[n+1] = u[k-1] + dt2*f(u[n], t[n]),
    where dt2 = t[n+1] - t[k-1]. Forward Euler is used for the
    first step.
    """
    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        
        if n >= 1:
            dt2 = t[n+1] - t[n-1]
            unew = u[n-1] + dt2*f(u[n], t[n])
        else:
            dt = t[n+1] - t[n]
            unew = u[n] + dt*f(u[n], t[n])
        return unew


class LeapfrogFiltered(Solver):
    """
    Leapfrog scheme: u[n+1] = u[k-1] + dt2*f(u[n], t[n]),
    where dt2 = t[n+1] - t[k-1]. Forward Euler is used for the
    first step.
    Since Leapfrog gives oscillatory solutions, this class
    applies a common filtering technique:
    u[n] = u[n] + gamma*(u[n-1] - 2*u[n] + u[n+1])
    with gamma=0.6 as in the NCAR Climate Model.
    """
    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        gamma = 0.6  # NCAR Climate Model
        
        if n >= 1:
            dt2 = t[n+1] - t[n-1]
            unew = u[n-1] + dt2*f(u[n], t[n])
            u[n] = u[n] + gamma*(u[n-1] - 2*u[n] + unew)
        else:
            dt = t[n+1] - t[n]
            unew = u[n] + dt*f(u[n], t[n])
        return unew


class Heun(Solver):
    """
    Heun's method, also known as an RK2 or Trapezoidal method.
    Basically, it is a central difference method, with one
    iteration and the Forward Euler scheme as start value.
    In this sense, it is a predictor-corrector method.
    """
    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        u_star = u[n] + dt*f(u[n], t[n])  # Forward Euler step
        unew = u[n] + 0.5*dt*(f(u[n], t[n]) + f(u_star, t[n+1]))
        return unew

Trapezoidal = Heun

class RungeKutta2(Solver):
    """Standard RK2 method."""
    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        K1 = dt*f(u[n], t[n])
        K2 = dt*f(u[n] + 0.5*K1, t[n] + 0.5*dt)
	unew = u[n] + K2
        return unew

class RungeKutta4(Solver):
    """Standard RK4 method."""
    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        dt2 = dt/2.0
        K1 = dt*f(u[n], t[n])
        K2 = dt*f(u[n] + 0.5*K1, t[n] + dt2)
        K3 = dt*f(u[n] + 0.5*K2, t[n] + dt2)
        K4 = dt*f(u[n] + K3, t[n] + dt)
        unew = u[n] + (1/6.0)*(K1 + 2*K2 + 2*K3 + K4)
        return unew

class TDVRungeKutta3(Solver):
    """TDVRK3 method."""
    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        dt2 = dt/2.0
        K1 = f(u[n], t[n])
        K2 = f(u[n] + K1, t[n] + dt2)
        K3 = f(3/4.*u[n] + 0.25*K1 + 0.25*K2, t[n] + dt2)
        raise NotImplementedError('Wrong impl. Do it carefully')
        unew = 1./3*u[n] + (dt/6.0)*(K1 + 2*K2 + 2*K3 + K4)
        return unew

class AdamsBashforth3(Solver):
    """
    Third-order Adams-Bashforth method:
    u[n+1] = u[n] + dt/12.*(23*f(u[n], t[n]) - 16*f(u[n-1], t[k-1]) \
                                  + 5*f(u[n-2], t[k-2]))
    for constant time step dt.
    """
    _legal_prms = dict(
        start_method = dict(
            help='method for the first two steps',
            #default='TDVRungeKutta3',
            default='RungeKutta2',
            type=str),
         )
    def __init__(self, f, **kwargs):
        # Note that (in general) each class must register its
        # superclass' set of parameters (SuperClass._legal_prms)
        # in self._legal_prms, and then call the superclass
        # constructor.
        self._legal_prms.update(Solver._legal_prms)
        Solver.__init__(self, f, **kwargs)

        method = self.get('start_method')
        self.starter = eval(method)(f, **kwargs)

        # Create storage for f at previous time levels
        self.f_2 = None
        self.f_3 = None
        
    def valid_data(self):
        if not self.constant_time_step():
            print '%s must have constant time step' % self.__name__
            return False
        else:
            return True
        
    def advance(self):
        # old version
        u, f, n, t = self.u, self.f, self.n, self.t
        
        if n >= 2:
            dt = t[n+1] - t[n]  # must be constant
            unew = u[n] + dt/12.*(23*f(u[n], t[n]) - 16*f(u[n-1], t[n-1]) \
                                  + 5*f(u[n-2], t[n-2]))
        else:
            # RK2 as a starter
            dt = t[n+1] - t[n]
            K1 = dt*f(u[n], t[n])
            K2 = dt*f(u[n] + 0.5*K1, t[n] + 0.5*dt)
            unew = u[n] + K2
        return unew

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        
        if n >= 2:
            dt = t[n+1] - t[n]  # must be constant
            self.f_1 = f(u[n], t[n])
            unew = u[n] + dt/12.*(23*self.f_1 - 16*self.f_2 + 5*self.f_3)
            self.f_2, self.f_3, self.f_1 = self.f_1, self.f_2, self.f_3

        else:
            # Start method
            self.starter.set_initial_condition(u[n])
            time_points = [t[n], t[n+1]]
            u_starter, t_starter = self.starter.solve(time_points)
            unew = u_starter[-1]
            if n == 0:
                self.f_3 = f(u[0], t[0])
            elif n == 1:
                self.f_2 = f(u[1], t[1])
        return unew


class MidpointIter(Solver):
    """
    A midpoint/central difference method with max_iter fixed-point
    iterations to solve the nonlinear system.
    The Forward Euler scheme is recovered if max_iter=1 and f(u,t)
    is independent of t. For max_iter=2 we have the Heun/RK2 scheme.
    """
    _legal_prms = dict(
        max_iter = dict(
            help='max no of iterations in nonlinear solver',
            default=25, type=int),
        eps_iter = dict(
            help='max error measure in nonlinear solver',
            default=1E-4, type=float),
         )

    def __init__(self, f, **kwargs):
        self._legal_prms.update(Solver._legal_prms)
        Solver.__init__(self, f, **kwargs)
        
    def advance(self):
        if not hasattr(self, 'v'):
            if self.neq == 1:
                self.v = np.zeros(self.max_iter+1, self.u.dtype)
            else:
                self.v = np.zeros((self.max_iter+1, self.neq), self.u.dtype)

        u, f, n, t, v = \
           self.u, self.f, self.n, self.t, self.v
        dt = t[n+1] - t[n]

        # (it's usually dangerous to assign values to a v that was
        # set as v = self.v, but in lists this is ok, and moreover,
        # v is only an internal help array)

        v[0] = u[n]
        q = 0
        v_finished = False   # |v[q]-v[q-1]| < eps
        while not v_finished and q < self.max_iter:
            q += 1
            v[q] = u[n] + 0.5*dt*(f(v[q-1], t[n+1]) + f(u[n], t[n]))
            #print 'v[%d]=%g of %d/%d' % (q,v[q], len(v),N)
            if abs(v[q] - v[q-1]).max() < self.eps_iter:
                v_finished = True
            
        unew = v[q]
        return unew


def approximate_Jacobian(f, x, h, *f_args):
    """
    Compute approximate Jacobian of f(x) at x.
    Method: forward finite difference approximation with step
    size h. f_args are optional arguments to f.
    """
    x = np.asarray(x)
    f0 = func(*((x0,)+args))
    J = np.zeros((len(x), len(f0)))
    dx = np.zeros(len(x))
    for i in range(len(x)):
       dx[i] = h
       J[i] = (func(*((x+dx,) + args)) - f0)/h
       dx[i] = 0.0
    return J.transpose()

class VODE(Solver):
    """The classical vode.f integrator (this class just calls scipy's vode)."""

    _legal_prms = dict(
        jac = dict(
            help='Jacobian (df/du) of right-hand side function f',
            default=None,  # implies finite difference approx
            type=(None, callable)),

        jac_args = dict(
            help='extra parameters to jac: jac(u,t,*jac_args,**jac_kwargs)',
            type=(tuple,list), default=()),

        jac_kwargs = dict(
            help='extra parameters to jac: jac(u,t,*jac_args,**jac_kwargs)',
            type=dict, default={}),

        atol = dict(
            help='absolute tolerance for solution',
            type=float, default=1E-8),
        rtol = dict(
            help='relative tolerance for solution',
            type=float, default=1E-6),

        vode_method = dict(
            help='solver type: "adams" or "bdf"',
            type=str, default='adams'),

        nsteps = dict(
            help='max no of internal solver steps per time step',
            type=int, default=None),

        first_step = dict(
            help='first_step parameter to vode',
            type=float, default=None),

        min_step = dict(
            help='min_step parameter to vode',
            type=float, default=None),

        max_step = dict(
            help='max_step parameter to vode',
            type=float, default=None),

        order = dict(
            help='maximum order used by the integrator '\
            '(<= 12 for "adams", <= 5 for "bdf"',
            type=int, default=None),
        )
    def __init__(self, f, **kwargs):
        # Note that (in general) each class must register its
        # superclass' set of parameters (SuperClass._legal_prms)
        # in self._legal_prms, and then call the superclass
        # constructor.
        self._legal_prms.update(Solver._legal_prms)
        Solver.__init__(self, f, **kwargs)
    
    def initialize(self):
        # Note that vode requires f(t, y, *args),
        # not our f(u, t, *args, **kwargs)
        self.f4vode = lambda t, y: self.f(y, t)
        
        if self.jac is not None:
            # First wrap the user's Jacobian routine as we wrap f
            self.jac = lambda u, t: \
                np.asarray(jac(u, t, *self.jac_args, **self.jac_kwargs))
            self.jac4vode = lambda t, y: self.jac(y, t)
        else:
            self.jac4vode = None
            
        try:
            import scipy.integrate.ode as ode
        except ImportError:
            raise ImportError('The scipy package must be installed in order to use the VODE solver')

        self.integrator = ode(self.f4vode, jac=self.jac4vode)
        self.vode_params = dict(
            atol=self.atol,
            rtol=self.rtol,
            method=self.vode_method,
            with_jacobian=self.jac is not None,)
        for name in ('nsteps', 'first_step', 'min_step', 'max_step', 'order'):
            value = self.get(name)
            if value is not None:
                self.vode_params[name] = value

        self.integrator = self.integrator.set_integrator(
            'vode', **self.vode_params)

        # Never set parameters to f and jac (wrappers cannot handle
        # *args construction), let vode view f(t, y) and jac(t, y)
        # while we transfer additional arguments in our wrapper
        ##self.integrator = self.integrator.set_f_params(*self.f_args)
        ##self.integrator = self.integrator.set_jac_params(*self.jac_args)
        ##if self.jac_kwargs or self.f_kwargs:
        ##    raise ValueError('f_kwargs and jac_kwargs are not allowed in VODE')

    def set_initial_condition(self, U0):
        Solver.set_initial_condition(self, U0)

    def solve(self, time_points, terminate=None):
        self.integrator = self.integrator.set_initial_value(
            self.U0, time_points[0])
        return Solver.solve(self, time_points, terminate)

    def advance(self):
        u, f, n, t = self.u, self.f, self.n, self.t
        unew = self.integrator.integrate(t[n+1])
        if len(unew) == 1:
            return unew[0]
        else:
            return unew

class SymPy_odefun(Solver):
    """Wrapper for the sympy.mpmath.odefun method."""
    def initialize(self):
        try:
            import sympy
        except ImportError:
            raise ImportError('sympy is not installed - needed for sympy_odefun')
        self.sympy = sympy
        # Note that sympy.odefun requires f(x, y),
        # not our f(u, t, *args, **kwargs)
        self.f4odefun = lambda x, y: \
                        self.sympy.mpmath.matrix(self.users_f(y, x))

    def solve(self, time_points, terminate=None):

        self.sympy.mpmath.mp.dps = 15  # accuracy
        ufunc = self.sympy.mpmath.odefun(self.f4odefun,
                                         time_points[0],
                                         sympy.mpmath.matrix(self.U0))
        u = np.array([ufunc(t) for t in time_points])
        t = np.asarray(time_points)
        return u, t

        
class SolverImplicit(Solver):
    """Super class for implicit methods for ODEs."""
    _legal_prms = dict(
        jac = dict(
            help='Jacobian (df/du) of right-hand side function f',
            default=None,  # implies finite difference approx
            type=(None, callable)),
        
        h_in_fd_jac = dict(
            help='step size in finite difference '\
            'approximation of the Jacobian',
            default=1E-4, type=float),
        
        jac_args = dict(
            help='extra parameters to jac: jac(u,t,*jac_args,**jac_kwargs)',
            type=(tuple,list), default=()),

        jac_kwargs = dict(
            help='extra parameters to jac: jac(u,t,*jac_args,**jac_kwargs)',
            type=dict, default={}),

        nonlinear_solver = dict(
            help='Newton or Picard nonlinear solver',
            default='Picard', type=str, range=('Newton', 'Picard')),
        
        max_iter = dict(
            help='max no of iterations in nonlinear solver',
            default=25, type=int),

        eps_iter = dict(
            help='max error measure in nonlinear solver',
            default=1E-4, type=float),

        relaxation = dict(
            help='relaxation parameter (r): new_solution = r*solution + '\
            '(1-r)*old_solution', default=1.0, type=float),
         )

    def __init__(self, f, jac=None, **kwargs):
        # Note that (in general) each class must register its
        # superclass' set of parameters (SuperClass._legal_prms)
        # in self._legal_prms, and then call the superclass
        # constructor.
        self._legal_prms.update(Solver._legal_prms)
        Solver.__init__(self, f, **kwargs)

        if jac is None:
            self.jac = lambda u, t: \
                approximate_Jacobian(self.f, u, self.h_in_fd_jac, t)
        else:
            # Wrap user-supplied Jacobian in the way f is wrapped
            self.jac = lambda u, t: \
                np.asarray(jac(u, t, *self.jac_args, **self.jac_kwargs))  

    # General solve routine with Newton or Picard
    # Newton with FD or exact Jac

    def solve(self, time_points, terminate=None):
        """
        Compute solution u for t values in the list/array
        time_points, as long as terminate(u,t,step_no) is False. 
        terminate(u,t,step_no) is a user-given function
        returning True or False. By default, a terminate
        function which always returns False is used.
        """
        if terminate is None:
            terminate = lambda u, t, step_no: False

        if isinstance(time_points, (float,int)):
            raise TypeError('solve: time_points is not a sequence')

        self.t = np.asarray(time_points)
        N = self.t.size - 1  # no of intervals
        if self.neq == 1:  # scalar ODEs
            self.u = np.zeros(N+1)
        else:              # systems of ODEs
            self.u = np.zeros((N+1,self.neq))

        if not self.valid_data():
            raise ValueError('Invalid data in "%s":\n%s' % \
                             (self.__class__.__name__,
                              pprint.pformat(self.__dict__)))
        self.iter_info = []
        # Assume that self.t[0] corresponds to self.U0
        self.u[0] = self.U0

        # Time loop
        for n in range(N):
            self.n = n
            if self.nonlinear_solver == 'Picard':
                # Forward Euler step for initial guess for nonlinear solver
                self.u[n+1] = self.u[n] + \
                        (self.t[n+1]-self.t[n])*self.f(self.u[n], self.t[n])
                i = 1
                error = 1E+30
                while i <= self.max_iter and error > self.eps_iter:
                    unew = self.Picard_update(self.u[n+1])
                    error = np.abs(unew - self.u[n+1]).max()
                    # Relax
                    r = self.relaxation
                    self.u[n+1] = r*unew + (1-r)*self.u[n]
                    i += 1
            elif self.nonlinear_solver == 'Newton':
                i = 0
                while i <= self.max_iter and error > self.eps_iter:
                    F, J = self.Newton_eq_matrix(self.u[n+1])
                    if self.neq == 1:
                        du = F/J
                    else:
                        du = np.linalg.solve(J, F)
                    error = np.abs(du).max()
                    unew = self.u[n] - du
                    # Relax
                    r = self.relaxation
                    self.u[n+1] = r*unew + (1-r)*self.u[n]
                    i += 1
            self.iter_info.append((n+1, i-1, error))
            if terminate(self.u, self.t, self.n+1):
                break  # terminate loop over k
        return self.u, self.t
    

class Adaptive(Solver):
    _legal_prms = dict(
        rtol = dict(
            help='relative tolerance (float or array)',
            default=1E-10, type=(float, np.ndarray, list, tuple)),
        
        atol = dict(
            help='absolute tolerance (float or array)',
            default=1E-10, type=(float, np.ndarray, list, tuple)),
        
         )
    def __init__(self, f, **kwargs):
        # Note that (in general) each class must register its
        # set of parameters (ThisClass._legal_prms) and then
        # then call its superclass constructor.
        self._legal_prms.update(Solver._legal_prms)
        Solver.__init__(self, f, **kwargs)


class AdaptiveResidual(Adaptive):
    def __init__(self, f, solver, **kwargs):
        self.solver = solver(f, **kwargs)
        Adaptive.__init__(self, f, **kwargs)

    def residual(self, u_n, u_np1, t_n, t_np1):
        dt = t_np1 - t_n
        t_mean = 0.5*(t_n + t_np1)
        u_mean = 0.5*(u_n + u_np1)
        u_diff = u_np1 - u_n
        print 'res', u_diff, u_mean, dt, u_diff/dt, self.f(u_mean, t_mean)
        # Central 2nd order difference approx to the residual
        # Valid for scalar ODE only
        return abs(u_diff/dt - self.f(u_mean, t_mean))
    
    def solve(self, time_points, terminate=None):
        self.users_time_points = np.asarray(time_points).copy()
        self.solver.set_initial_condition(self.U0)
        t = self.users_time_points
        # Assume scalar equation...
        self.u = [self.U0]
        self.t = [t[0]]
        for k in range(1,len(t)):
            R = 1E+20
            # Try to jump until next user point in time
            ntpoints = 1
            # Halve the time step until residual is small enough
            while R > self.atol:
                ntpoints *= 2
                time_points = np.linspace(t[k-1], t[k], ntpoints)
                print 'k:', k, ntpoints, 'calling', self.solver.__class__.__name__, time_points
                self.solver.set_initial_condition(self.u[-1])
                unew, tnew = self.solver.solve(time_points, terminate)
                R = self.residual(unew[-2], unew[-1], tnew[-2], tnew[-1])
                print 'Residual:', R
                # reintegrate with dt/2
            self.u.extend(unew[1:])
            self.t.extend(tnew[1:])
        return self.u, self.t
        

class AdaptiveCombiner(Adaptive):
    def __init__(self, f, lower_order_solver, higher_order_solver, **kwargs):
        self.lower = lower_order_solver
        self.higher = higher_order_solver
        Adaptive.__init__(self, f, **kwargs)

    """
    def solve(self, ...):
        # step both solvers and subtract, update both for next step
        # use higher as main solver, set init cond in lower for each step?
        pass
    """

class AdaptiveDoubleStepSize(Adaptive):
    def __init__(self, f, solver, **kwargs):
        self.solver = solver
        Adaptive.__init__(self, f, **kwargs)

    """
    def solve(self, ...):
        # step with dt and dt/2, compare
        pass
    """



class RungeKuttaFehlberg(Adaptive):
    """
    Runge-Kutta-Fehlberg method of order 4-5.
    """
    _legal_prms = dict(
        h_min = dict(help='minimum step size',
                   default=None,
                   type=float),
        
        h_max = dict(help='maximum step size',
                   default=None,
                   type=float),
        h_0 = dict(help='initial step size',
                   default=None,
                   type=float),
         )
    
    def __init__(self, f, **kwargs):
        self._legal_prms.update(Adaptive._legal_prms)
        Adaptive.__init__(self, f, **kwargs)
        
    def advance(self):
        u, f, n, t, rtol, atol = \
           self.u, self.f, self.n, self.t, self.rtol, self.atol
        dt = t[n+1] - t[n]

        # default setting of step size
        if self.h_min is None:
            self.h_min = dt/1000.0
        if self.h_max is None:
            self.h_max = dt
        if self.h_0 is None:
            self.h_0 = dt

        h_min, h_max, h_0 = self.h_min, self.h_max, self.h_0

        # Algorithm
        urr = []; trr = []
        urr.append(u[n]);  trr.append(t[n])

        c = (1/4.,
             3/8.,
             3/32.,
             9/32.,
             12/13.,
             1932/2197.,
             -7200/2197.,
             7296/2197.,
             439/216.,
             -8.,
             3680/513.,
             -845/4104.,
             1/2.,
             -8/27.,
             2.,
             -3544/2565.,
             1859/4104.,
             -11/40.,
             1/360.,
             -128/4275.,
             -2197/75240.,
             1/50.,
             2/55.,
             25/216.,
             1408/2565.,
             2197/4104.,
             -1/5.)

        t_cur = t[n]
        while abs(t_cur-t[n]) <= abs(t[n+1]-t[n]):
            u_cur = urr[-1]
            k1 = h_0*f(u_cur, t_cur)
            k2 = h_0*f(u_cur + k1*c[0], t_cur + h_0*c[0])
            k3 = h_0*f(u_cur + k1*c[2] + k2*c[3], t_cur + h_0*c[1])
            k4 = h_0*f(u_cur + k1*c[5] + k2*c[6] + k3*c[7], t_cur + h_0*c[4])
            k5 = h_0*f(u_cur + k1*c[8] + k2*c[9] + k3*c[10] + k4*c[11],
                       t_cur + h_0)
            k6 = h_0*f(u_cur + k1*c[13] + k2*c[14] + k3*c[15] + k4*c[16] + \
                       k5*c[17], t_cur + h_0*c[12])
            #Liwei: I used np.abs here
            diff = np.abs(k1*c[18] + k3*c[19] + k4*c[20] + k5*c[21] + k6*c[22])
            u_new = u_cur + k1*c[23] + k3*c[24] + k4*c[25] + k5*c[26]

            #Liwei: made middle shorter (and clearer in my view)
            def middle(x, y=.1, z=4.):
                return sorted([x, y, z])[1]

            #Liwei: don't need to distinguish between scalar or system,
            #can always use np.abs on u_new etc.
            ewt = rtol*np.abs(u_new) + atol
            rms = diff/ewt
            rms_norm = np.sqrt((np.sum(rms*rms))/self.neq)

            if rms_norm <= 1 or h_0 == h_min:
                # Close enough or the step size can not be reduced
                urr.append(u_new); trr.append(t_cur + h_0)
                t_cur += h_0

            s = ((ewt*h_0)/(2*diff))**0.25
            s = min(map(middle, s)) if self.neq > 1 else s
            # Select minimum scalar in all dimensions for better accuracy
            h_0 *= s
            h_0 = middle(h_0, y=h_min, z=h_max)
            # Return when time close to t[n+1],
            # accuracy requirement might not be fulfilled
        return u_new        


class BackwardEuler(SolverImplicit):
    def __init__(self, f, jac=None):
        SolverImplicit.__init__(self, f, jac=jac)

    def Picard_update(self, ukp1):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        return u[n] + dt*f(ukp1, t[n+1])

    def Newton_system(self, ukp1):
        u, f, n, t = self.u, self.f, self.n, self.t
        dt = t[n+1] - t[n]
        F = ukp1 - (u[n] + dt*f(ukp1, t[n+1]))
        J = np.eye(self.neq) - dt*self.jac(ukp1, t[n+1])
        return F, J

class Backward2Step(SolverImplicit):
    def __init__(self, f, jac=None):
        SolverImplicit.__init__(self, f, jac=jac)

    def Picard_update(self, ukp1):
        u, f, n, t = self.u, self.f, self.n, self.t
        if n == 0:
            # Backward Euler as starter
            dt = t[n+1] - t[n]
            return u[n] + dt*f(ukp1, t[n+1])
        else:
            dt2 = t[n+1] - t[n-1]
            return 4./3*u[n] - 1./3*u[n-1] + (1./3)*dt2*f(ukp1, t[n+1])

class ThetaRule(SolverImplicit):
    _legal_prms = dict(
        theta = dict(
            help='parameter in [0,1]',
            default=0.5, type=float, range=[0, 1]))
    
    def __init__(self, f, **kwargs):
        self._legal_prms.update(SolverImplicit._legal_prms)
        SolverImplicit.__init__(self, f, **kwargs)

    def Picard_update(self, ukp1):
        u, f, n, t, theta = self.u, self.f, self.n, self.t, self.theta
        dt = t[n+1] - t[n]
        return u[n] + theta*dt*f(ukp1, t[n+1]) + (1-theta)*dt*f(u[n], t[n])
    


# Tests and verifications

def _f1(u, t):
    """Right-hand side for linear solution."""
    a = 5  # some arbitrary number
    return 0.2 + (u - _u_solution_f1(t))**a

def _u_solution_f1(t):
    """Exact u(t) corresponding to _f1 above."""
    return 0.2*t + 3

def _f2(u, t):
    """3*exp(-t) solution."""
    return -u

def _u_solution_f2(t):
    """Exact u(t) corresponding to _f2 above."""
    return 3*np.exp(-t)

def _f3(u, t):
    """u'' + u = 0 equation."""
    return [u[1], -u[0]]

def _u_solution_f3(t):
    """Exact u(t) corresponding to _f3 above."""
    return [np.sin(t), np.cos(t)]


tests = [(_f1, _u_solution_f1, 3),
         (_f2, _u_solution_f2, 3),
         (_f3, _u_solution_f1, [0, 1]),
         ]

method_classes = [ForwardEuler, RungeKutta4, MidpointIter,
                  RungeKutta2, Heun, Leapfrog, LeapfrogFiltered,
                  AdamsBashforth3, VODE,
                  BackwardEuler, Backward2Step,
                  ThetaRule,
                  RungeKuttaFehlberg]

def _verify(f, exact, U0, T, n, showplot=False, terminate_crit=False):
    import pprint, time
    import scitools.std as st
    t_points = np.linspace(0, T, n)
    for method_class in method_classes:
        print 'Testing', method_class.__name__,
        method = method_class(f)
        method.set_initial_condition(U0)
        if terminate_crit:
            u, t = method.solve(t_points,
                                terminate=lambda u, t, n: abs(u[n]) > U0)
        else:
            u, t = method.solve(t_points)

        u_exact = np.asarray(exact(t)).transpose()
        print 'max error:', (u_exact - u).max()
        pprint.pprint(method.get())
        if showplot:
            if len(u.shape) > 1:
                u = u[:,0]
            st.plot(t, u, legend=method_class.__name__)
            st.hold('on')
            time.sleep(0.2)

def _verify_adaptive1():
    import scitools.std as st
    Method = AdaptiveResidual
    f = lambda u, t, a, b: -a*u + b  # can test f_args functionality
    m = Method(f, solver=ForwardEuler, f_args=[1, 0], atol=0.005)
    m.set_initial_condition(1)
    time_points = np.linspace(0, 6, 5)
    u, t = m.solve(time_points)
    t = np.asarray(t)
    dt = t[1:] - t[:-1]
    st.figure()
    st.plot(t[1:], dt, 'bo',
            title='Time steps in %s' % Method.__name__)
    st.figure()
    u_ex = np.exp(-t)
    st.plot(t, u, 'r-', t, u_ex, 'b-', title='Adaptive solver')

def _verify_interval_arithmetics():
    """
    Test interesting feature of the ODE hierarchy: set U0 to an object
    of some type, that supports arithmetic operations, and the solution
    u will be of the same object type. Here we set U0 to an interval,
    using the interval arithmetic object mpi from sympy, and the whole
    solution is (automatically) computed by interval arithmetics.
    The output interval is far too big, though.
    """
    import sympy as sm
    Interval = sm.mpmath.mpi
    U0 = Interval('0.95', '1.05')
    method = ForwardEuler(lambda u,t: -u)
    method.set_initial_condition(U0)
    t = np.linspace(0, 3, 21)
    u, t = method.solve(t)
    print 'Computed end interval:', u[-1]
    print 'Lower U0 in exact solution:', float(U0.a)*np.exp(-t)[-1]
    print 'Upper U0 in exact solution:', float(U0.b)*np.exp(-t)[-1]

    # Just check the result by a manual computation:
    u_ = U0
    dt = t[1] - t[0]
    t_ = 0
    for n in range(len(t)-1):
        u_ = u_ + dt*(-u_)  # Forward Euler
    print 'Manually computed end interval:', u_

def _run_tests():
    """
    Run tests.
    Which test(s) depends the 1st command-line argument,
    if 'all', all tests are run, otherwise one specified
    test is run.
    """
    import scitools.std as st
    import time, sys
    if len(sys.argv) == 1:
        test = 'all'
    else:
        test = sys.argv[1]
    if test == 'linear' or test =='all':
        print '\n*** Exact numerical solution: ***'
        _verify(_f1, _u_solution_f1, U0=3, T=8, n=4)
    if test == 'exp' or test =='all':
        print '\n*** Exponential decay: ***'
        st.figure()
        _verify(_f2, _u_solution_f2, U0=3, T=8, n=25,
                showplot=True, terminate_crit=True)
    if test == 'vib' or test =='all':
        print '\n\n*** Oscillating system: ***'
        st.figure()
        _verify(_f3, _u_solution_f3,
                U0=[0,1], T=4*np.pi, n=20*4, showplot=True)
    if test == 'adaptive1' or test =='all':
        print '\n\n*** Adaptive method: ***'
        _verify_adaptive1()
    if test == 'interval' or test =='all':
        print '\n\n*** Interval arithmetics: ***'
        _verify_interval_arithmetics()
    
if __name__ == '__main__':
    _run_tests()
