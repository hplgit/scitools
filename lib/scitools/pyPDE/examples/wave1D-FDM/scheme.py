
def advance(up, u, um, t, x, f, c, U_0, U_L, L, dt, tstop,
            version='scalar'):
    """
    Advance the 1D wave equation one time step.
    """
    n = len(x)  # total no of points
    C2 = (c*dt/dx)**2
    dt2 = dt*dt
    if version == 'scalar':
        for i in iseq(start=1, stop=n-1):
            up[i] = - um[i] + 2*u[i] + \
                    C2*(u[i-1] - 2*u[i] + u[i+1]) + \
                    dt2*f(x[i], t_old)
    elif version == 'vectorized':
        up[1:n] = - um[1:n] + 2*u[1:n] + \
                  C2*(u[0:n-1] - 2*u[1:n] + u[2:n+1]) + \
                  dt2*f(x[1:n], t_old)
    else:
        raise ValueError, 'version=%s' % version

    return up, t

    
