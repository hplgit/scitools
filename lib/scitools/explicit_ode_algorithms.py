def ForwardEuler_algorithm\
        (t0, y0, f, T, dt,
         store=lambda y,t: None, f_args=(), f_kwargs={}):
    """The simple, explicit, first-order Forward Euler method for ODEs."""
    t = t0
    y = y0
    store(y, t)
        
    while t+dt <= T:
        y = y + dt*f(y, t, *f_args, **f_kwargs)
        t += dt
        store(y, t)
    return y

def RK4_algorithm\
        (t0, y0, f, T, dt, store, f_args=(), f_kwargs={}):
    """The explicit 4th-order Runge-Kutta method for ODEs."""
    t = t0
    y = y0
    store(y, t)
        
    while t+dt <= T:
        k1 = dt*f(t, y)
        k2 = dt*f(t+dt/2, y + k1/2, *f_args, **f_kwargs)
        k3 = dt*f(t+dt/2, y + k2/2, *f_args, **f_kwargs)
        k4 = dt*f(t+dt,   y + k3,   *f_args, **f_kwargs) 
        t += dt
        y = y + (k1 + 2*k2 + 2*k3 + k4)/6.
        store(y, t)
    return y
    
