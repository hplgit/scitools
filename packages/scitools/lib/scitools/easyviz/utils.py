from scitools.numpytools import zeros, ones, exp, reshape, ravel, Float, \
     meshgrid, seq, linspace, arctan2, sqrt, shape, log, sin, cos, \
     NumPyArray, NumPy_type

def peaks(*args):
    # z = peaks()
    # z = peaks(n)
    # z = peaks(x,y)
    n = 49
    nargs = len(args)
    if nargs in (0,1):
        if nargs == 1:
            n = int(args[0])
        x, y = meshgrid(linspace(-3,3,n),linspace(-3,3,n))
    elif nargs == 2:
        x, y = args
    else:
        raise SyntaxError("Invalid number of arguments.")
    z = 3*(1-x)**2*exp(-x**2 - (y+1)**2) \
        - 10*(x/5 - x**3 - y**5)*exp(-x**2-y**2) \
        - 1/3*exp(-(x+1)**2 - y**2)
    return z

# The gradient function is now available in numpy/scipy.
def gradient(f,*varargs): 
    """Written by Travis Oliphant?
    (http://aspn.activestate.com/ASPN/Mail/Message/scipy-user/2761129)
    """

    N = len(f.shape)  # number of dimensions
    n = len(varargs)
    if n==0:
        dx = [1.0]*N
    elif n==1:
        dx = [varargs[0]]*N
    elif n==N:
        dx = list(varargs)
    else:
        raise SyntaxError, "Invalid number of arguments"

    # use central differences on interior and first differences on endpoints

    outvals = []

    # create slice objects --- initially all are [:,:,...,:]
    slices = [None]*3
    for k in range(3):
        slices[k] = []
        for j in range(N):
            slices[k].append(slice(None))

    for axis in range(N):
        # select out appropriate parts for this dimension
        out = zeros(f.shape, f.typecode())
        slices[0][axis] = slice(1,-1)
        slices[1][axis] = slice(2,None)
        slices[2][axis] = slice(None,-2)
        # 1d equivalent -- out[1:-1] = (f[2:] - f[:-2])/2.0
        out[slices[0]] = (f[slices[1]] - f[slices[2]])/2.0   
        slices[0][axis] = 0
        slices[1][axis] = 1
        slices[2][axis] = 0
        # 1d equivalent -- out[0] = (f[1] - f[0])
        out[slices[0]] = (f[slices[1]] - f[slices[2]])
        slices[0][axis] = -1
        slices[1][axis] = -1
        slices[2][axis] = -2
        # 1d equivalent -- out[-1] = (f[-1] - f[-2])
        out[slices[0]] = (f[slices[1]] - f[slices[2]])
        
        # divide by step function
        outvals.append(out / dx[axis])
        
        # reset the slice object in this dimension to ":"
        slices[0][axis] = slice(None)
        slices[1][axis] = slice(None)
        slices[2][axis] = slice(None)

    if N == 1:
        return outvals[0]
    else:
        return outvals

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
        xx, yy, zz = meshgrid(seq(.1,10,.2), seq(-3,3,.25), seq(-3,3,.25),
                              sparse=False)
    elif len(args) == 1:
        n = int(args[0])
        xx, yy, zz = meshgrid(linspace(.1,10,2*n),
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
