#!/usr/bin/env python
"""
Class for uniform and non-uniform grid on an interval, rectangle, or box.
"""

from scitools.errorcheck import right_type, wrong_type
from scitools.numpyutils import ndgrid, seq, ndarray, wrap2callable

# constants for indexing the space directions:
X = X1 = 0
Y = X2 = 1
Z = X3 = 2


class UniformBoxGrid(object):
    """
    Simple uniform grid on an interval, rectangle or box.

    Accessible attributes (after initialization):
    
    @ivar nsd          : no of space dimensions
    @ivar xmin, xmax   : extent of grid in x dir.
    @ivar ymin, ymax   : extent of grid in y dir.
    @ivar zmin, zmax   : extent of grid in z dir.
    @ivar nx, ny, nz   : no of cells in each dir.
    @ivar dx, dy, dz   : grid spacings
    @ivar dirnames     : names of the space dir. ('x', 'y', etc.)
    
    @ivar shape        : (nx+1, ny+1, ...); dimension of array over grid
    @ivar coor         : list of coordinates; coor[i]  holds coordinates
                         in direction i (X,Y,Z); the k-th coordinate in
                         direction 0 can be accessed as
                         self.coor[0][k]
                         self.coor[X][k]
                         self.coor[self.dirnames['x']][k]
                         Note that X, Y, Z are predefined constants 0, 1, 2
                   
    @ivar xcoor        : nickname for self.coor[0] (self.coor[X])
    @ivar ycoor, zcoor : nicknames for self.coor[1] and self.coor[2]

    @ivar coorv        : expanded version of coor for vectorized expressions
                         (in 2D, self.coorv[0] = self.coor[0][:,newaxis,newaxis])
    @ivar xcoorv, ycoorv, zcoorv: nickname for self.coorv[i], i=0,1,2
    """
    def __init__(self,
                 x=None, nx=None,
                 y=None, ny=None,
                 z=None, nz=None):
        """
        Initialize a BoxGrid by giving domain range and number of
        cells in each space direction.

        >>> g = UniformBoxGrid(x=(0,1), nx=10)
        >>> g = UniformBoxGrid(x=(0,1), nx=10, y=(-1,1), ny=4)
        >>> g = UniformBoxGrid(x=(0,2), nx=10, y=(0,1), ny=4, z=(-1,1), nz=14)
        """
        self.nsd = 0
        self.dirnames = []
        self.coor = []
        self.shape = []

        
        if x is not None and nx is not None:
            right_type(x, (list,tuple))
            right_type(x[0], (float,int))
            right_type(x[1], (float,int))
            right_type(nx, int)

            self.nsd += 1
            self.nx = nx; self.xmin = x[0]; self.xmax = x[1]
            self.dx = (self.xmax-self.xmin)/float(nx)
            self.coor.append(seq(self.xmin, self.xmax, self.dx))
            self.xcoor = self.coor[-1]
            self.dirnames.append('x')
            self.shape.append(nx+1)

        if y is not None and ny is not None:
            right_type(y, (list,tuple))
            right_type(y[0], (float,int))
            right_type(y[1], (float,int))
            right_type(ny, int)

            self.nsd += 1
            self.ny = ny; self.ymin = y[0]; self.ymax = y[1]
            self.dy = (self.ymax-self.ymin)/float(ny)
            self.coor.append(seq(self.ymin, self.ymax, self.dy))
            self.ycoor = self.coor[-1]
            self.dirnames.append('y')
            self.shape.append(ny+1)

        if z is not None and nz is not None:
            right_type(z, (list,tuple))
            right_type(z[0], (float,int))
            right_type(z[1], (float,int))
            right_type(nz, int)

            self.nsd += 1
            self.nz = nz; self.zmin = z[0]; self.zmax = z[1]
            self.dz = (self.zmax-self.zmin)/float(nz)
            self.coor.append(seq(self.zmin, self.zmax, self.dz))
            self.zcoor = self.coor[-1]
            self.dirnames.append('z')
            self.shape.append(nz+1)

        self._more_init()

    def _more_init(self):
        if self.nsd == 0:
            # no coordinates initialized...
            raise TypeError('too few arguments to UniformBoxGrid constructor')

        # convert lists to tuples (for constness):
        self.shape = tuple(self.shape)
        # self.dirnames needs list functionality
        
        self.coorv = ndgrid(*self.coor)
        if not isinstance(self.coorv, (list,tuple)):
            # 1D grid, wrap self.coorv as list:
            self.coorv = [self.coorv]
        # xcoorv, ycoorv, etc:
        for i in range(self.nsd):
            self.__dict__[self.dirnames[i]+'coorv'] = self.coor[i]

        if self.nsd == 3:
            # make boundary coordinates for vectorization:
            xdummy, \
            self.ycoorv_xfixed_boundary, \
            self.zcoorv_xfixed_boundary = ndgrid(0, self.ycoor, self.zcoor)
            
            self.xcoorv_yfixed_boundary, \
            ydummy, \
            self.zcoorv_yfixed_boundary = ndgrid(self.xcoor, 0, self.zcoor)
            
            self.xcoorv_yfixed_boundary, \
            self.zcoorv_yfixed_boundary, \
            zdummy = ndgrid(self.xcoor, self.ycoor, 0)
            
    # could have _ in all variable names and define read-only
    # access via properties

    def string2griddata(s):
        """
        Turn a text specification of a grid into a dictionary
        with the grid data.
        For example,

        >>> s = "domain=[0,10] indices=[0:11]"
        >>> data = BoxGrid.string2griddata(s)
        >>> data
        {'nx': 11, 'x': (0.0, 10.0)}

        >>> s = "domain=[0.2,0.5]x[0,2E+00] indices=[0:20]x[0:100]"
        >>> data = BoxGrid.string2griddata(s)
        >>> data
        {'nx': 20, 'x': (0.20000000000000001, 0.5), 'y': (0.0, 2.0), 'ny': 100}

        >>> s = "[0,1]x[0,2]x[-1,1.5] [0:25]x[0:10]x[0:15]"
        >>> data = BoxGrid.string2griddata(s)
        >>> data
        {'nx': 25, 'ny': 10, 'nz': 15, 'y': (0.0, 2.0), 'x': (0.0, 1.0), 'z': (-1.0, 1.5)}

        The data dictionary can be used as keyword arguments to the
        class UniformBoxGrid constructor.
        """
        
        domain  = r'\[([^,]*),([^\]]*)\]'
        indices = r'\[([^:,]*):([^\]]*)\]'
        import re
        d = re.findall(domain, s)
        i = re.findall(indices, s)
        nsd = len(d)
        if nsd != len(i):
            raise ValueError('could not parse "%s"' % s)
        kwargs = {}
        dirnames = ('x', 'y', 'z')
        for dir in range(nsd):
            if not isinstance(d[dir], (list,tuple)) or len(d[dir]) != 2 or \
               not isinstance(i[dir], (list,tuple)) or len(i[dir]) != 2:
                raise ValueError('syntax error in "%s"' % s)

            kwargs[dirnames[dir]] = (float(d[dir][0]), float(d[dir][1]))
            kwargs['n'+dirnames[dir]] = int(i[dir][1]) - int(i[dir][0]) # no of cells!
        return kwargs
    string2griddata = staticmethod(string2griddata)

    def __getitem__(self, i):
        """
        Return access to coordinate array in direction no i, or direction
        name i, or return the coordinate of a point if i is an nsd-tuple.
        
        >>> g = UniformBoxGrid(x=(0,1), y=(-1,1), nx=2, ny=4)  # xy grid
        >>> g[0][0] == g.xmin     # min coor in direction 0
        True
        >>> g['x'][0] == g.xmin   # min coor in direction 'x'
        True
        >>> g[0,4]
        (0.0, 1.0)
        >>> g = UniformBoxGrid(y=(0,1), z=(-1,1), ny=2, nz=4)  # yz grid
        >>> g[1][0] == g.zmin     # min coor in direction 1 (now z!)
        True
        >>> g['z'][0] == g.zmin   # min coor in direction 'z'
        True
        """
        if isinstance(i, str):
            return self.coor[self.name2dirindex(i)]
        elif isinstance(i, int):
            if self.nsd > 1:
                return self.coor[i]     # coordinate array
            else:
                return self.coor[0][i]  # coordinate itself in 1D
        elif isinstance(i, (list,tuple)):
            return tuple([self.coor[k][i[k]] for k in range(len(i))])
        else:
            wrong_type(i, 'i', 'Must be str, int, tuple')
            

    def __setitem__(self, i, value):
        raise AttributeError('subscript assignment is not valid for '\
                             '%s instances' % self.__class__.__name__)

    def ncells(self, i):
        """Return no of cells in direction i."""
        # i has the meaning as in __getitem__. May be removed if not much used
        return len(self.coor[i])-1

    def name2dirindex(self, name):
        """
        Return direction index corresponding to direction name.
        In an xyz-grid, 'x' is 0, 'y' is 1, and 'z' is 2.
        In an yz-grid, 'x' is not defined, 'y' is 0, and 'z' is 1.
        """
        try:
            return self.dirnames.index(name)
        except ValueError:
            print name, 'is not defined'
            return None

    def dirindex2name(self, i):
        """Inverse of name2dirindex."""
        try:
            return self.dirnames[i]
        except IndexError:
            print i, 'is not a valid index'
            return None
    
    def ok(self):
        return True  # constructor init only => always ok

    def __len__(self):
        """Total number of grid points."""
        n = 1
        for dir in self.coor:
            n *= len(dir)
        return n

    def __repr__(self):
        s = self.__class__.__name__ + '('
        args = []
        for i in range(len(self.coor)):
            p = self.dirnames[i]
            args.append('%s=(%g,%g), n%s=%d' % \
                        (p, self.coor[i][0], self.coor[i][-1],
                         p, len(self.coor[i])-1))
        s += ', '.join(args) + ')'
        return s

    def __str__(self):
        return self.__repr__()
                      
    def interpolator(self, point_values):
        """
        Given a self.nsd dimension array point_values with
        values at each grid point, this method returns a function
        for interpolating the scalar field defined by point_values
        at an arbitrary point.

        2D Example:
        given a filled array point_values[i][j], compute
        interpolator = grid.interpolator(point_values)
        v = interpolator(0.1243, 9.231)  # interpolate point_values
        
        >>> g=UniformBoxGrid(x=(0,2), nx=2, y=(-1,1), ny=2)
        >>> g
        UniformBoxGrid(x=(0,2), nx=2, y=(-1,1), ny=2)
        >>> def f(x,y): return 2+2*x-y

        >>> f=g.vectorized_eval(f)
        >>> f
        array([[ 3.,  2.,  1.],
               [ 5.,  4.,  3.],
               [ 7.,  6.,  5.]])
        >>> i=g.interpolator(f)
        >>> i(0.1,0.234)        # interpolate (not a grid point)
        1.9660000000000002
        >>> f(0.1,0.234)        # exact answer
        1.9660000000000002
        """
        args = self.coor
        args.append(point_values)
        # make use of wrap2callable, which applies ScientificPython
        return wrap2callable(args)

    def vectorized_eval(self, f):
        """
        Evaluate a function f (of the space directions) over a grid.
        f is supposed to be vectorized.

        >>> g = BoxGrid(x=(0,1), y=(0,1), nx=3, ny=3)
        >>> # f(x,y) = sin(x)*exp(x-y):
        >>> a = g.vectorized_eval(lambda x,y: sin(x)*exp(y-x))
        >>> print a
        [[ 0.          0.          0.          0.        ]
         [ 0.23444524  0.3271947   0.45663698  0.63728825]
         [ 0.31748164  0.44308133  0.6183698   0.86300458]
         [ 0.30955988  0.43202561  0.60294031  0.84147098]]

        >>> # f(x,y) = 2: (requires special consideration)
        >>> a = g.vectorized_eval(lambda x,y: arr(g.shape)+2)
        >>> print a
        [[ 2.  2.  2.  2.]
         [ 2.  2.  2.  2.]
         [ 2.  2.  2.  2.]
         [ 2.  2.  2.  2.]]
        """
        a = f(*self.coorv)

        # check if f is really vectorized:
        try:
            msg = 'calling %s, which is supposed to be vectorized' % f.__name__
        except AttributeError:  # if __name__ is missing
            msg = 'calling a function, which is supposed to be vectorized'
        try:
            self.compatible(a)
        except (IndexError,TypeError), e:
            print 'e=',e, type(e), e.__class__.__name__
            raise e.__class__('BoxGrid.vectorized_eval(f):\n%s, BUT:\n%s' % \
                              (msg, e))
        return a
        
    def init_fromstring(s):
        data = UniformBoxGrid.string2griddata(s)
        print 'interpreted string, data=\n', data
        return UniformBoxGrid(**data)
    init_fromstring = staticmethod(init_fromstring)

    def compatible(self, data_array, name_of_data_array=''):
        """
        Check that data_array is a NumPy array with dimensions
        compatible with the grid.
        """
        if not isinstance(data_array, ndarray):
            raise TypeError('data %s is %s, not NumPy array' % \
                            (name_of_data_array, type(data_array)))
        else:
            if data_array.shape != self.shape:
                raise IndexError("data %s of shape %s is not "\
                                 "compatible with the grid's shape %s" % \
                                 (name_of_data_array, data_array.shape,
                                  self.shape))
        return True # if we haven't raised any exceptions

    def iter(self, domain_part='all', vectorized_version=True):
        """
        Return iterator over grid points.
        domain_part = 'all':  all grid points
        domain_part = 'interior':  interior grid points
        domain_part = 'all_boundary':  all boundary points
        domain_part = 'interior_boundary':  interior boundary points
        domain_part = 'corners':  all corner points
        domain_part = 'all_edges':  all points along edges in 3D grids
        domain_part = 'interior_edges':  interior points along edges

        vectorized_version is true if the iterator returns slice
        objects for the index slice in each direction.
        vectorized_version is false if the iterator visits each point
        at a time (scalar version).
        """
        self.iterator_domain = domain_part
        self.vectorized_iter = vectorized_version
        return self

    def __iter__(self):
        # Idea: set up slices for the various self.iterator_domain
        # values. In scalar mode, make a loop over the slices and
        # yield the scalar value. In vectorized mode, return the
        # appropriate slices.
        
        self._slices = []  # elements meant to be slice objects
                    
        if self.iterator_domain == 'all':
            self._slices.append([])
            for i in range(self.nsd):
                self._slices[-1].append((i, slice(0, len(self.coor[i]), 1)))

        elif self.iterator_domain == 'interior':
            self._slices.append([])
            for i in range(self.nsd):
                self._slices[-1].append((i, slice(1, len(self.coor[i])-1, 1)))

        elif self.iterator_domain == 'all_boundary':
            for i in range(self.nsd):
                self._slices.append([])
                # boundary i fixed at 0:
                for j in range(self.nsd):
                    if j != i:
                        self._slices[-1].\
                           append((j, slice(0, len(self.coor[j]), 1)))
                    else:
                        self._slices[-1].append((i, slice(0, 1, 1)))
                # boundary i fixed at its max value:
                for j in range(self.nsd):
                    if j != i:
                        self._slices[-1].\
                           append((j, slice(0, len(self.coor[j]), 1)))
                    else:
                        n = len(self.coor[i])
                        self._slices[-1].append((i, slice(n-1, n, 1)))
                        
        elif self.iterator_domain == 'interior_boundary':
            for i in range(self.nsd):
                self._slices.append([])
                # boundary i fixed at 0:
                for j in range(self.nsd):
                    if j != i:
                        self._slices[-1].\
                           append((j, slice(1, len(self.coor[j])-1, 1)))
                    else:
                        self._slices[-1].append((i, slice(0, 1, 1)))
                # boundary i fixed at its max value:
                for j in range(self.nsd):
                    if j != i:
                        self._slices[-1].\
                           append((j, slice(1, len(self.coor[j])-1, 1)))
                    else:
                        n = len(self.coor[i])
                        self._slices[-1].append((i, slice(n-1, n, 1)))

        elif self.iterator_domain == 'corners':
            if self.nsd == 1:
                for i0 in (0, len(self.coor[0])-1):
                    self._slices.append([])
                    self._slices[-1].append((0, slice(i0, i0+1, 1)))
            elif self.nsd == 2:
                for i0 in (0, len(self.coor[0])-1):
                    for i1 in (0, len(self.coor[1])-1):
                        self._slices.append([])
                        self._slices[-1].append((0, slice(i0, i0+1, 1)))
                        self._slices[-1].append((0, slice(i1, i1+1, 1)))
            elif self.nsd == 3:
                for i0 in (0, len(self.coor[0])-1):
                    for i1 in (0, len(self.coor[1])-1):
                        for i2 in (0, len(self.coor[2])-1):
                            self._slices.append([])
                            self._slices[-1].append((0, slice(i0, i0+1, 1)))
                            self._slices[-1].append((0, slice(i1, i1+1, 1)))
                            self._slices[-1].append((0, slice(i2, i2+1, 1)))

        elif self.iterator_domain == 'all_edges':
            print 'iterator over "all_edges" is not implemented'
        elif self.iterator_domain == 'interior_edges':
            print 'iterator over "interior_edges" is not implemented'
        else:
            raise ValueError('iterator over "%s" is not impl.' % \
                             self.iterator_domain)
        
#    "def __next__(self):"
        """
        If vectorized mode:
        Return list of slice instances, where the i-th element in the
        list represents the slice for the index in the i-th space
        direction (0,...,nsd-1).

        If scalar mode:
        Return list of indices (in multi-D) or the index (in 1D).
        """
        if self.vectorized_iter:
            for s in self._slices:
                yield [slice_in_dir for dir, slice_in_dir in s]
        else:
            # scalar version
            for s in self._slices:
                slices = [slice_in_dir for dir, slice_in_dir in s]
                if len(slices) == 1:
                    for i in xrange(slices[0].start, slices[0].stop):
                        yield i
                elif len(slices) == 2:
                    for i in xrange(slices[0].start, slices[0].stop):
                        for j in xrange(slices[1].start, slices[1].stop):
                            yield [i, j]
                elif len(slices) == 3:
                    for i in xrange(slices[0].start, slices[0].stop):
                        for j in xrange(slices[1].start, slices[1].stop):
                            for k in xrange(slices[2].start, slices[2].stop):
                                yield [i, j, k]
                             
                
class BoxGrid(UniformBoxGrid):
    """
    Extension of class UniformBoxGrid to non-uniform box grids.
    The coordinate vectors (in each space direction) can have
    arbitrarily spaced coordinate values.
    """
    def __init__(self, x=None, y=None, z=None):
        self.nsd = 0
        self.dirnames = []
        self.coor = []
        self.shape = []

        if x is not None:
            right_type(x, (list,tuple,ndarray))

            self.nsd += 1
            self.nx = len(x)-1; self.xmin = x[0]; self.xmax = x[-1]
            self.dx = None  # varies
            self.coor.append(x.copy())
            self.xcoor = self.coor[-1]
            self.dirnames.append('x')
            self.shape.append(nx+1)

        if y is not None:
            right_type(y, (list,tuple,ndarray))

            self.nsd += 1
            self.ny = len(y)-1; self.ymin = y[0]; self.ymax = y[-1]
            self.dy = None  # varies
            self.coor.append(y.copy())
            self.ycoor = self.coor[-1]
            self.dirnames.append('y')
            self.shape.append(ny+1)

        if z is not None:
            right_type(z, (list,tuple,ndarray))

            self.nsd += 1
            self.nz = len(z)-1; self.zmin = z[0]; self.zmax = z[-1]
            self.dz = None  # varies
            self.coor.append(z.copy())
            self.zcoor = self.coor[-1]
            self.dirnames.append('z')
            self.shape.append(nz+1)

        self._more_init()
        
def _test(g):
    print 'g=%s' % str(g)
    # dump all the contents of a grid object:
    import scitools.misc;  scitools.misc.dump(g, hide_nonpublic=False)
    from numpy import zeros
    def fv(*args):
        # vectorized evaluation function
        return zeros(g.shape)+2
    def fs(*args):
        # scalar version
        return 2
    fv_arr = g.vectorized_eval(fv)
    fs_arr = zeros(g.shape)
    coor = [0.0]*g.nsd
    itparts = ['all', 'interior', 'all_boundary', 'interior_boundary',
               'corners']
    if g.nsd == 3:
        itparts += ['all_edges', 'interior_edges']
    for domain_part in itparts:
        print '\niterator over "%s"' % domain_part
        for i in g.iter(domain_part, vectorized_version=False):
            if isinstance(i, int):  i = [i]  # wrap index as list (if 1D)
            for k in range(g.nsd):
                coor[k] = g.coor[k][i[k]]
            print i, coor
            if domain_part == 'all':  # fs_arr shape corresponds to all points
                fs_arr[i] = fs(*coor)
        print 'vectorized iterator over "%s":' % domain_part
        for slices in g.iter(domain_part, vectorized_version=True):
            if domain_part == 'all':
                fs_arr[slices] = fv(*g.coor)
            # else: more complicated
            print slices
    # boundary slices...

def _test2():
    g1 = UniformBoxGrid(x=(0,1), nx=4)
    _test(g1)
    spec = '[0,1]x[-1,2] with indices [0:3]x[0:2]'
    g2 = UniformBoxGrid.init_fromstring(spec)
    _test(g2)
    g3 = UniformBoxGrid(x=(0,1), nx=4, y=(0,1), ny=1, z=(-1,1), nz=2)
    _test(g3)
    print 'g3=\n%s' % str(g3)
    print 'g3[Z]=', g3[Z]
    print 'g3[Z][1] =', g3[Z][1]
    print 'dx, dy, dz spacings:', g3.dx, g3.dy, g3.dz
    g4 = UniformBoxGrid(y=(0,1), ny=4, z=(-1,1), nz=2)
    _test(g4)
    print 'g4["y"][-1]:', g4["y"][-1]
    
def _test4():
    from numpy import sin, zeros, exp
    # check vectorization evaluation:
    g = UniformBoxGrid(x=(0,1), y=(0,1), nx=3, ny=3)
    try:
        g.vectorized_eval(lambda x,y: 2)
    except TypeError, msg:
        # fine, expect to arrive here
        print msg
    try:
        g.vectorized_eval(lambda x,y: zeros((2,2))+2)
    except IndexError, msg:
        # fine, expect to arrive here
        print msg

    a = g.vectorized_eval(lambda x,y: sin(x)*exp(y-x))
    print a
    a = g.vectorized_eval(lambda x,y: zeros(g.shape)+2)
    print a

        
if __name__ == '__main__':
    _test2()
    #_test4()
