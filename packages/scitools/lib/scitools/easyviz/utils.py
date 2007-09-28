from scitools.numpyutils import zeros, ones, exp, reshape, ravel, \
     ndgrid, seq, linspace, arctan2, sqrt, shape, log, sin, cos
from scitools.numpytools import NumPyArray, NumPy_type, NumPy_dtype

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
    z = 3*(1-x)**2*exp(-x**2 - (y+1)**2) \
        - 10*(x/5 - x**3 - y**5)*exp(-x**2-y**2) \
        - 1/3*exp(-(x+1)**2 - y**2)
    return z

def cart2sph(xx, yy, zz):
    # theta, phi, r = cart2sph(xx, yy, zz)
    theta = arctan2(yy, xx)
    phi = arctan2(zz, sqrt(xx**2 + yy**2))
    r = sqrt(xx**2 + yy**2 + zz**2)
    return theta, phi, r

def sph2cart(theta, phi, r):
    # xx, yy, zz = sph2cart(theta, phi, r)
    xx = r * cos(phi) * cos(theta)
    yy = r * cos(phi) * sin(theta)
    zz = r * sin(phi)
    return xx, yy, zz

def flow(*args):
    # xx,yy,zz,vv = flow()
    # xx,yy,zz,vv = flow(n)
    # xx,yy,zz,vv = flow(xx,yy,zz)
    if len(args) == 0:
        xx, yy, zz = ndgrid(seq(.1,10,.2),
                            seq(-3,3,.25),
                            seq(-3,3,.25),
                            sparse=False)
    elif len(args) == 1:
        n = int(args[0])
        xx, yy, zz = ndgrid(linspace(.1,10,2*n),
                            linspace(-3,3,n),
                            linspace(-3,3,n),
                            sparse=False)
    elif len(args) == 3:
        xx, yy, zz = args
    else:
        raise SyntaxError("Invalid number of arguments.")
    
    # Convert to spherical coordinates (with xx as the axis).
    A = 2; nu = 1

    th,phi,r = cart2sph(yy,zz,xx)
    vr = 2*nu/r*((A**2-1)/(A-cos(phi))**2 - 1)
    vphi = -2*nu*sin(phi)/(A-cos(phi))/r
    vth = zeros(shape(r))

    vx,vy,vz = sph2cart(vth,vphi,vr)
    vv = log(sqrt(vx**2 + vy**2 + vz**2))

    return xx, yy, zz, vv
