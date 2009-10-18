#!/usr/bin/env python
"""
Class for a scalar (or vector) field over a BoxGrid or UniformBoxGrid grid.
"""

from scitools.BoxGrid import BoxGrid, UniformBoxGrid, X, Y, Z
from numpy import zeros, array, transpose

__all__ = ['BoxField', 'BoxGrid', 'UniformBoxGrid', 'X', 'Y', 'Z',
           'dolfin_function2BoxField']


class Field(object):
    """
    General base class for all grids. Holds a connection to a
    grid, a name of the field, and optionally a list of the
    independent variables and a string with a description of the
    field.
    """
    def __init__(self, grid, name,
                 independent_variables=None,
                 description=None,
                 **kwargs):
        self.grid = grid

        self.name = name
        self.independent_variables = independent_variables
        if self.independent_variables is None:
            # copy grid.dirnames as independent variables:
            self.independent_variables = self.grid.dirnames
            
        # metainformation:
        self.meta = {'description': description,}
        self.meta.update(kwargs)  # user can add more meta information


class BoxField(Field):
    """
    Field over a BoxGrid or UniformBoxGrid grid.

    @ivar grid : reference to the underlying grid instance.
    @ivar values: array holding field values at the grid points.
    """
    def __init__(self, grid, name, vector=0, **kwargs):
        """
        Initialize scalar or vector field over a BoxGrid/UniformBoxGrid.

        @param grid: grid instance.
        @param name: name of the field.
        @param vector: scalar field if 0, otherwise the no of vector
        components (spatial dimensions of vector field).
        @param kwargs:
          values: optional array with field values
          other arguments just stored as metadata in the field (see class Field)

        The BoxGrid object has the following two key attributes:

        @ivar grid    : a UniformBoxGrid or BoxGrid instance
        @ivar values  : an array of values, indexed as [i,j], [i,j,k] etc.

        Here is an example::
        >>> g = UniformBoxGrid(min=[0,0], max=[1.,1.], division=[3, 4])
        >>> print g
        domain=[0,1]x[0,1]  indices=[0:3]x[0:4]
        >>> u = BoxField(g, 'u')
        >>> u.values = u.grid.vectorized_eval(lambda x,y: x + y)
        >>> i = 1; j = 2
        >>> print 'u(%g, %g)=%g' % (g.coor[X][i], g.coor[Y][j], u.values[i,j])
        u(0.333333, 0.5)=0.833333
        >>>
        >>> # visualize:
        >>> from scitools.std import surf
        >>> surf(u.grid.coorv[X], u.grid.coorv[Y], u.values)

        Note that u.grid.coorv is a list of coordinate arrays that are
        suitable for Matlab-style visualization of 2D scalar fields.
        Also note how one can access the coordinates and u value at
        a point (i,j) in the grid.
        """
        Field.__init__(self, grid, name, **kwargs)
        
        if vector > 0:
            # for a vector field we add a "dimension" in values for
            # the various vector components:
            required_shape = list(self.grid.shape)
            required_shape.append(vector)
            # required_shape has length self.grid.nsd+1 for vector fields
        else:
            required_shape = self.grid.shape

        if 'values' in kwargs:
            values = kwargs['values']
            if values is not None: 
                if values.shape == required_shape:
                    self.values = values  # field data are provided
                else:
                    raise ValueError(
                          'values array are incompatible with grid size; '\
                          'shape is %s while required shape is %s' % \
                          (values.shape, required_shape))
        else:
            # create array of scalar field grid point values:
            self.values = zeros(required_shape)

        # doesn't  work: self.__getitem__ = self.values.__getitem__
        #self.__setitem__ = self.values.__setitem__

    def update(self):
        """Update the self.values array (if grid has been changed)."""
        if self.grid.shape != self.values.shape:
            self.values = zeros(self.grid.shape)

    # these are slower than u_ = u.values; u_[i] since an additional
    # function call is required compared to NumPy array indexing:
    def __getitem__(self, i):  return self.values[i]
    def __setitem__(self, i, v):  self.values[i] = v

    def __str__(self):
        if len(self.values.shape) > self.grid.nsd:
            s = 'Vector field with %d components' % self.values.shape[-1]
        else:
            s = 'Scalar field'
        s += ', over ' + str(self.grid)
        return s

    def gridline(self, start_coor, direction=0, end_coor=None,
                 snap=True):
        """
        Return a coordinate array and corresponding field values
        along a line starting with start_coor, in the given
        direction, and ending in end_coor (default: grid boundary).
        Two more boolean values are also returned: fixed_coor
        (the value of the fixed coordinates, which may be different
        from those in start_coor if snap=True) and snapped (True if
        the line really had to be snapped onto the grid, i.e.,
        fixed_coor differs from coordinates in start_coor.

        If snap is True, the line is snapped onto the grid, otherwise
        values along the line must be interpolated (not yet implemented).

        >>> g2 = UniformBoxGrid.init_fromstring('[-1,1]x[-1,2] [0:3]x[0:4]')
        >>> print g2
        UniformBoxGrid(min=[-1. -1.], max=[ 1.  2.],
        division=[3, 4], dirnames=('x', 'y'))
        >>> print g2.coor
        [array([-1.        , -0.33333333,  0.33333333,  1.        ]),
        array([-1.  , -0.25,  0.5 ,  1.25,  2.  ])]

        >>> u = BoxField(g2, 'u')
        >>> u.values = u.grid.vectorized_eval(lambda x,y: x + y)
        >>> xc, uc, fixed_coor, snapped = u.gridline((-1,0.5), 0)
        >>> print xc
        [-1.         -0.33333333  0.33333333  1.        ]
        >>> print uc
        [-0.5         0.16666667  0.83333333  1.5       ]
        >>> print fixed_coor, snapped
        [0.5] False
        >>> #plot(xc, uc, title='u(x, y=%g)' % fixed_coor)
        """
        if not snap:
            raise NotImplementedError('Use snap=True, no interpolation impl.')

        slice_index, snapped = \
             self.grid.gridline_slice(start_coor, direction, end_coor)
        fixed_coor = [self.grid[s][i] for s,i in enumerate(slice_index) \
                      if not isinstance(i, slice)]
        if len(fixed_coor) == 1:
            fixed_coor = fixed_coor[0]  # avoid returning list of length 1
        return self.grid.coor[direction][slice_index[direction].start:\
                                         slice_index[direction].stop], \
               self.values[slice_index], fixed_coor, snapped
    
    def gridplane(self, value, constant_coor=0, snap=True):
        """
        Return two one-dimensional coordinate arrays and
        corresponding field values over a plane where one coordinate,
        constant_coor, is fixed at a value.

        If snap is True, the plane is snapped onto a grid plane such
        that the points in the plane coincide with the grid points.
        Otherwise, the returned values must be interpolated (not yet impl.).
        """
        if not snap:
            raise NotImplementedError('Use snap=True, no interpolation impl.')

        slice_index, snapped = self.grid.gridplane_slice(value, constant_coor)
        if constant_coor == 0:
            x = self.grid.coor[1]
            y = self.grid.coor[2]
        elif constant_coor == 1:
            x = self.grid.coor[0]
            y = self.grid.coor[2]
        elif constant_coor == 2:
            x = self.grid.coor[0]
            y = self.grid.coor[1]
        fixed_coor = self.grid.coor[constant_coor][slice_index[constant_coor]]
        return x, y, self.values[slice_index], fixed_coor, snapped

def _rank12rankd_mesh(a, shape):
    """
    Given rank 1 array a with values in a mesh with the no of points
    described by shape, transform the array to the right "mesh array"
    with the same shape.
    """
    shape = list(shape)
    shape.reverse()
    if len(a.shape) == 1:
        return a.reshape(shape).transpose()
    else:
        # reshape first dimension, keep the others
        total_shape = shape + list(a.shape[1:])
        print 'total shape:', total_shape
        a = a.reshape(total_shape)
        return transpose(a, axes=None)
    #return transpose(a, axes=range(len(shape)))

def dolfin_mesh2UniformBoxGrid(dolfin_mesh, division):
    """
    Turn a regular, structured DOLFIN finite element mesh into
    a UniformBoxGrid object. (Mostly for ease of plotting with scitools.)
    Standard DOLFIN numbering numbers the nodes along the x[0] axis,
    then x[1] axis, and so on.
    """
    c = dolfin_mesh.coordinates() # numpy array
    return UniformBoxGrid(min=c[0], max=c[-1],
                          division=division)
    
def dolfin_mesh2BoxGrid(dolfin_mesh, division):
    """
    Turn a structured DOLFIN finite element mesh into
    a BoxGrid object. (Mostly for ease of plotting with scitools.)
    Standard DOLFIN numbering numbers the nodes along the x[0] axis,
    then x[1] axis, and so on.
    """
    c = dolfin_mesh.coordinates() # numpy array
    shape = [n+1 for n in division]  # shape for points in each dir.
    raise NotImplementedError # must redo how to reshape vector fields
    c = _rank12rankd_mesh(c, shape)  # Ooops, might not work!!! works for scalars...
    print 'reshaped coor:\n', c
    print c[1,2]
    if len(c.shape) == 1:
        coor = [c]
    elif len(c.shape) == 2:
        coor = [c[:,0], c[0,:]]
    elif len(c.shape) == 3:
        coor = [c[:,0,0], c[0,:,0], c[0,0,:]]
        
    return BoxGrid(coor)


def dolfin_function2BoxField(dolfin_function, dolfin_mesh,
                             division, uniform_mesh=True):
    """
    Turn a DOLFIN finite element field over a structured mesh into
    a BoxField object. (Mostly for ease of plotting with scitools.)
    Standard DOLFIN numbering numbers the nodes along the x[0] axis,
    then x[1] axis, and so on.
    """
    nodal_values = dolfin_function.vector().array().copy()
    if len(nodal_values.shape) > 1:
        raise NotImplementedError # no support for vector valued functions yet
                                  # the problem is in _rank12rankd_mesh
    if uniform_mesh:
        grid = dolfin_mesh2UniformBoxGrid(dolfin_mesh, division)
    else:
        grid = dolfin_mesh2BoxGrid(dolfin_mesh, division)
    try:
        nodal_values = _rank12rankd_mesh(nodal_values, grid.shape)
    except ValueError, e:
        raise ValueError('DOLFIN function has vector of size %s while the provided mesh demands %s' % (nodal_values.size, grid.shape))
    
    return BoxField(grid, name=dolfin_function.name(), values=nodal_values)
    
def _test(g):
    print 'grid: %s' % g

    # function: 1 + x + y + z
    def f(*args):
        sum = 1.0
        for x in args:
            sum = sum + x
        return sum

    u = BoxField(g, 'u')
    v = BoxField(g, 'v', vector=g.nsd)

    u.values = u.grid.vectorized_eval(f)  # fill field values

    if   g.nsd == 1:
        v[:,X] = u.values + 1  # 1st component
    elif g.nsd == 2:
        v[:,:,X] = u.values + 1  # 1st component
        v[:,:,Y] = u.values + 2  # 2nd component
    elif g.nsd == 3:
        v[:,:,:,X] = u.values + 1  # 1st component
        v[:,:,:,Y] = u.values + 2  # 2nd component
        v[:,:,:,Z] = u.values + 3  # 3rd component

    # write out field values at the mid point of the grid
    # (convert g.shape to NumPy array and divide by 2 to find
    # approximately the mid point)
    midptindex = tuple(array(g.shape,int)/2)
    ptcoor = g[midptindex]
    # tuples with just one item does not work as indices
    print 'mid point %s has indices %s' % (ptcoor, midptindex)
    print 'f%s=%g' % (ptcoor, f(*ptcoor))
    print 'u at %s: %g' % (midptindex, u[midptindex])
    v_index = list(midptindex); v_index.append(slice(g.nsd))
    print 'v at %s: %s' % (midptindex, v[v_index])

    # test extraction of lines:
    if u.grid.nsd >= 2:
        direction = u.grid.nsd-1
        coor, u_coor, fixed_coor, snapped = \
              u.gridline(u.grid.min_coor, direction)
        if snapped: print 'Error: snapped line'
        print 'line in x[%d]-direction, starting at %s' % \
              (direction, u.grid.min_coor)
        print coor
        print u_coor

        direction = 0
        point = u.grid.min_coor.copy()
        point[direction+1] = u.grid.max_coor[direction+1]
        coor, u_coor, fixed_coor, snapped = \
              u.gridline(u.grid.min_coor, direction)
        if snapped: print 'Error: snapped line'
        print 'line in x[%d]-direction, starting at %s' % \
              (direction, point)
        print coor
        print u_coor

    if u.grid.nsd == 3:
        y_center = (u.grid.max_coor[1] + u.grid.min_coor[1])/2.0
        xc, yc, uc, fixed_coor, snapped = \
            u.gridplane(value=y_center, constant_coor=1)
        print 'Plane y=%g:' % fixed_coor,
        if snapped: print ' (snapped from y=%g)' % y_center
        else: print
        print xc
        print yc
        print uc

def _test2():
    g1 = UniformBoxGrid(min=0, max=1, division=4)
    _test(g1)
    spec = '[0,1]x[-1,2] with indices [0:4]x[0:3]'
    g2 = UniformBoxGrid.init_fromstring(spec)
    _test(g2)
    g3 = UniformBoxGrid(min=(0,0,-1), max=(1,1,1), division=(4,3,2))
    _test(g3)
    
if __name__ == '__main__':
    _test2()
