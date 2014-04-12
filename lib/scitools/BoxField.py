#!/usr/bin/env python
"""
Class for a scalar (or vector) field over a BoxGrid or UniformBoxGrid grid.
"""

from scitools.BoxGrid import BoxGrid, UniformBoxGrid, X, Y, Z
from numpy import zeros, array, transpose

import dolfin

__all__ = ['BoxField', 'BoxGrid', 'UniformBoxGrid', 'X', 'Y', 'Z',
           'dolfin_function2BoxField', 'update_from_dolfin_array']


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

    =============      =============================================
      Attributes                       Description
    =============      =============================================
    grid               reference to the underlying grid instance
    values             array holding field values at the grid points
    =============      =============================================

    """
    def __init__(self, grid, name, vector=0, **kwargs):
        """
        Initialize scalar or vector field over a BoxGrid/UniformBoxGrid.

        =============      ===============================================
          Arguments                          Description
        =============      ===============================================
        *grid*             grid instance
        *name*             name of the field
        *vector*           scalar field if 0, otherwise the no of vector
                           components (spatial dimensions of vector field)
        *values*           (*kwargs*) optional array with field values
        =============      ===============================================

        Here is an example::

        >>> g = UniformBoxGrid(min=[0,0], max=[1.,1.], division=[3, 4])

        >>> print g
        domain=[0,1]x[0,1]  indices=[0:3]x[0:4]

        >>> u = BoxField(g, 'u')
        >>> u.values = u.grid.vectorized_eval(lambda x,y: x + y)

        >>> i = 1; j = 2
        >>> print 'u(%g, %g)=%g' % (g.coor[X][i], g.coor[Y][j], u.values[i,j])
        u(0.333333, 0.5)=0.833333

        >>> # visualize:
        >>> from scitools.std import surf
        >>> surf(u.grid.coorv[X], u.grid.coorv[Y], u.values)

        ``u.grid.coorv`` is a list of coordinate arrays that are
        suitable for Matlab-style visualization of 2D scalar fields.
        Also note how one can access the coordinates and u value at
        a point (i,j) in the grid.
        """
        Field.__init__(self, grid, name, **kwargs)

        if vector > 0:
            # for a vector field we add a "dimension" in values for
            # the various vector components (first index):
            self.required_shape = [vector]
            self.required_shape += list(self.grid.shape)
        else:
            self.required_shape = self.grid.shape

        if 'values' in kwargs:
            values = kwargs['values']
            self.set_values(values)
        else:
            # create array of scalar field grid point values:
            self.values = zeros(self.required_shape)

        # doesn't  work: self.__getitem__ = self.values.__getitem__
        #self.__setitem__ = self.values.__setitem__

    def copy_values(self, values):
        """Take a copy of the values array and reshape it if necessary."""
        self.set_values(values.copy())

    def set_values(self, values):
        """Attach the values array to this BoxField object."""
        if values.shape == self.required_shape:
            self.values = values  # field data are provided
        else:
            try:
                values.shape = self.required_shape
                self.values = values
            except ValueError:
                raise ValueError(
                    'values array are incompatible with grid size; '\
                    'shape is %s while required shape is %s' % \
                    (values.shape, self.required_shape))

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
        raise ValueError('array a cannot be multi-dimensional (not %s), ' \
                         'break it up into one-dimensional components' \
                         % a.shape)

def dolfin_mesh2UniformBoxGrid(dolfin_mesh, division=None):
    """
    Turn a regular, structured DOLFIN finite element mesh into
    a UniformBoxGrid object. (Application: plotting with scitools.)
    Standard DOLFIN numbering numbers the nodes along the x[0] axis,
    then x[1] axis, and so on.
    """
    if hasattr(dolfin_mesh, 'structured_data'):
        coor = dolfin_mesh.structured_data
        min_coor = [c[0]  for c in coor]
        max_coor = [c[-1] for c in coor]
        division = [len(c)-1 for c in coor]
    else:
        if division is None:
            raise ValueError('division must be given when dolfin_mesh does not have a strutured_data attribute')
        else:
            coor = dolfin_mesh.coordinates() # numpy array
            min_coor = coor[0]
            max_coor = coor[-1]

    return UniformBoxGrid(min=min_coor, max=max_coor,
                          division=division)

def dolfin_mesh2BoxGrid(dolfin_mesh, division=None):
    """
    Turn a structured DOLFIN finite element mesh into
    a BoxGrid object. (Mostly for ease of plotting with scitools.)
    Standard DOLFIN numbering numbers the nodes along the x[0] axis,
    then x[1] axis, and so on.
    """
    if hasattr(dolfin_mesh, 'structured_data'):
        coor = dolfin_mesh.structured_data
        return BoxGrid(coor)
    else:
        if division is None:
            raise ValueError('division must be given when dolfin_mesh does not have a strutured_data attribute')
        else:
            c = dolfin_mesh.coordinates() # numpy array
            shape = [n+1 for n in division]  # shape for points in each dir.

            c2 = [c[:,i] for i in range(c.shape[1])]  # split x,y,z components
            for i in range(c.shape[1]):
                c2[i] = _rank12rankd_mesh(c2[i], shape)
            # extract coordinates in the different directions
            coor = []
            if len(c2) == 1:
                coor = [c2[0][:]]
            elif len(c2) == 2:
                coor = [c2[0][:,0], c2[1][0,:]]
            elif len(c2) == 3:
                coor = [c2[0][:,0,0], c2[1][0,:,0], c2[2][0,0,:]]
            return BoxGrid(coor)


def dolfin_function2BoxField(dolfin_function, dolfin_mesh,
                             division=None, uniform_mesh=True):
    """
    Turn a DOLFIN P1 finite element field over a structured mesh into
    a BoxField object. (Mostly for ease of plotting with scitools.)
    Standard DOLFIN numbering numbers the nodes along the x[0] axis,
    then x[1] axis, and so on.

    If the DOLFIN function employs elements of degree > 1, one should
    project or interpolate the field onto a field with elements of
    degree=1.
    """
    if dolfin_function.ufl_element().degree() != 1:
        raise TypeError("""\
The dolfin_function2BoxField function works with degree=1 elements
only. The DOLFIN function (dolfin_function) has finite elements of type
%s
i.e., the degree=%d != 1. Project or interpolate this function
onto a space of P1 elements, i.e.,

V2 = FunctionSpace(mesh, 'CG', 1)
u2 = project(u, V2)
# or
u2 = interpolate(u, V2)

""" % (str(dolfin_function.ufl_element()), dolfin_function.ufl_element().degree()))

    if dolfin.__version__[:3] == "1.0":
        nodal_values = dolfin_function.vector().array().copy()
    else:
        map = dolfin_function.function_space().dofmap().vertex_to_dof_map(dolfin_mesh)
        nodal_values = dolfin_function.vector().array().copy()
        nodal_values[map] = dolfin_function.vector().array().copy()

    if uniform_mesh:
        grid = dolfin_mesh2UniformBoxGrid(dolfin_mesh, division)
    else:
        grid = dolfin_mesh2BoxGrid(dolfin_mesh, division)

    if nodal_values.size > grid.npoints:
        # vector field, treat each component separately
        ncomponents = int(nodal_values.size/grid.npoints)
        try:
            nodal_values.shape = (ncomponents, grid.npoints)
        except ValueError as e:
            raise ValueError('Vector field (nodal_values) has length %d, there are %d grid points, and this does not match with %d components' % (nodal_values.size, grid.npoints, ncomponents))
        vector_field = [_rank12rankd_mesh(nodal_values[i,:].copy(),
                                          grid.shape) \
                        for i in range(ncomponents)]
        nodal_values = array(vector_field)
        bf = BoxField(grid, name=dolfin_function.name(),
                      vector=ncomponents, values=nodal_values)
    else:
        try:
            nodal_values = _rank12rankd_mesh(nodal_values, grid.shape)
        except ValueError as e:
            raise ValueError('DOLFIN function has vector of size %s while the provided mesh has %d points and shape %s' % (nodal_values.size, grid.npoints, grid.shape))
        bf = BoxField(grid, name=dolfin_function.name(),
                      vector=0, values=nodal_values)
    return bf

def update_from_dolfin_array(dolfin_array, box_field):
    """
    Update the values in a BoxField object box_field with a new
    DOLFIN array (dolfin_array). The array must be reshaped and
    transposed in the right way
    (therefore box_field.copy_values(dolfin_array) will not work).
    """
    nodal_values = dolfin_array.copy()
    if len(nodal_values.shape) > 1:
        raise NotImplementedError # no support for vector valued functions yet
                                  # the problem is in _rank12rankd_mesh
    try:
        nodal_values = _rank12rankd_mesh(nodal_values, box_field.grid.shape)
    except ValueError as e:
        raise ValueError('DOLFIN function has vector of size %s while the provided mesh demands %s' % (nodal_values.size, grid.shape))
    box_field.set_values(nodal_values)
    return box_field

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
