#!/usr/bin/env python
"""
Class for a scalar (or vector) field over a BoxGrid or UniformBoxGrid grid.
"""

from scitools.BoxGrid import BoxGrid, UniformBoxGrid, X, Y, Z
from numpy import zeros, array


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
        @param kwargs: optional keyword arguments, stored as metadata in
        the field (see class Field)
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

        if 'values' in kwargs and values is not None: 
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

    def gridline(self, start_coor, direction=0, end_coor=None):
        """
        Return a coordinate array and corresponding field values
        along a line starting with start_coor, in the given
        direction, and ending in end_coor (default: grid boundary).

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
        slice_index, snapped = \
             self.grid.gridline_slice(start_coor, direction, end_coor)
        fixed_coor = [self.grid[s][i] for s,i in enumerate(slice_index) \
                      if not isinstance(i, slice)]
        return self.grid.coor[direction][slice_index[direction].start:\
                                         slice_index[direction].stop], \
               self.values[slice_index], fixed_coor, snapped
    
    def gridplane(self, value, constant_coor=0):
        """
        Return two one-dimensional coordinate arrays and
        corresponding field values over a plane where one coordinate,
        constant_coor, is fixed at a value.
        The plane is snapped onto a grid plane such that the points
        in the plane coincide with the grid points.
        """
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
