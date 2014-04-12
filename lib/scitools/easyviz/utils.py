from scitools.numpyutils import zeros, ones, exp, reshape, ravel, \
     ndgrid, seq, linspace, arctan2, sqrt, shape, log, sin, cos

def available_backends():
    """Return a list of the available backends."""
    import os
    from scitools.misc import check_if_module_exists
    files = os.listdir(os.path.dirname(__file__))
    files.remove('template_.py')
    if '__init__.py' in files:
        files.remove('__init__.py')
    backends = [f for f in files if f.endswith('_.py')]
    available = []
    print '\nChecking if you have all the Easyviz backends...'
    for b in backends:
        module = 'scitools.easyviz.' + b[:-3]
        try:
            check_if_module_exists(module, abort=False, raise_exception=True, msg='')
            available.append(module[17:])
        except:
            pass
            #print "You can't use the %s backend" % module
    return available
            
    
def peaks(*args):
    # z = peaks()
    # z = peaks(n)
    # z = peaks(x,y)
    n = 49
    nargs = len(args)
    if nargs in (0,1):
        if nargs == 1:
            n = int(args[0])
        x, y = ndgrid(linspace(-3,3,n),linspace(-3,3,n))
    elif nargs == 2:
        x, y = args
    else:
        raise SyntaxError("Invalid number of arguments.")
    return 3*(1-x)**2*exp(-x**2-(y+1)**2) \
           - 10*(x/5-x**3-y**5)*exp(-x**2-y**2) - 1/3*exp(-(x+1)**2-y**2)

def flow(*args):
    # xx,yy,zz,vv = flow()
    # xx,yy,zz,vv = flow(n)
    # xx,yy,zz,vv = flow(xx,yy,zz)
    if len(args) == 0:
        xx, yy, zz = ndgrid(linspace(0.1, 10, 50),
                            linspace(-3, 3, 25),
                            linspace(-3, 3, 25),
                            sparse=False)
    elif len(args) == 1:
        n = int(args[0])
        xx, yy, zz = ndgrid(linspace(0.1, 10, 2*n),
                            linspace(-3, 3, n),
                            linspace(-3, 3, n),
                            sparse=False)
    elif len(args) == 3:
        xx, yy, zz = args
    else:
        raise SyntaxError("Invalid number of arguments.")
    
    # convert to spherical coordinates:
    theta = arctan2(zz, yy)
    phi = arctan2(xx, sqrt(yy**2 + zz**2))
    r = sqrt(xx**2 + yy**2 + zz**2)

    rv = 2/r*(3/(2-cos(phi))**2 - 1)
    phiv = -2*sin(phi)/(2-cos(phi))/r
    thetav = zeros(shape(r))

    # convert back to cartesian coordinates:
    xv = rv*cos(phiv)*cos(thetav)
    yv = rv*cos(phiv)*sin(thetav)
    zv = rv*sin(phiv)

    vv = log(sqrt(xv**2 + yv**2 + zv**2))

    return xx, yy, zz, vv
