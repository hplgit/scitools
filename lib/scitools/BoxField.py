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
    

def _test(g):
    print 'g=%s' % str(g)

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

def _test2():
    g1 = UniformBoxGrid(x=(0,1), nx=4)
    _test(g1)
    spec = '[0,1]x[-1,2] with indices [0:3]x[0:2]'
    g2 = UniformBoxGrid.init_fromstring(spec)
    _test(g2)
    g3 = UniformBoxGrid(x=(0,1), nx=4, y=(0,1), ny=1, z=(-1,1), nz=2)
    _test(g3)
    
if __name__ == '__main__':
    _test2()
