"""
Finite element field.
"""
from scitools.basics import arr, arrmax, size, put
from scitools.errorcheck import *

__all__ = ['Field',]

class Field:
    def __init__(self, grid, basis_function_types=None,
                 loc2dof=None, components=1):
        """
        grid is a finite element grid.

        basis_function_types is a list of class names in the Element
        hierarchy, used to define basis functions over the elements.
        basis_function_types=None implies isoparametric elements
        (the basis_function_types is then set to a the grid's
        element_types list).

        loc2dof(i,e) is the mapping from local degree of freedom i in
        element e to the corresponding global degree of freedom. If None,
        we use the grid's loc2dof array.

        components denotes the number of scalar components in a
        vector field. If components is 1, Field represents a scalar
        field, otherwise a vector or tensor field.
        """
        self.grid = grid

        if basis_function_types is None:
            # assume isoparametric elements and apply the
            # geometry element for definition of basis functions
            self.basis_function_types = self.grid.elm_tp
        elif isinstance(basis_function_types, Element):
            self.basis_function_types = [basis_function_types]*self.grid.nel
        elif isinstance(basis_function_types, (list,tuple)):
            right_length(basis_function_types, len(self.grid.elm_tp))
            self.basis_function_types = basis_function_types

        if loc2dof is not None:
            self.loc2dof = loc2dof
        else:
            self.loc2dof = grid.loc2glob

        self.global_dofs = arrmax(self.loc2dof)
        self.components = components
        if self.components == 1:
            self.coefficients = arr(self.global_dofs)
        else:
            self.coefficients = arr((self.global_dofs, self.components))
        #self.elm_coefficients = should be (e,i) indexed, where e is elm and
        #i is local dof
        #self.coefficients = should be all dofs for _this_ field, or do we
        #need it? well, normally for storage of data, this is probably
        #smart - all the dofs according to loc2dof in one array

    def prescribe_coefficients(self, indices, values, component=0):
        self.prescribed_indices = indices
        self.prescribed_values = values
        if len(self.coefficients.shape) == 1:
            put(self.coefficients, indices, values)
        else: # vector field
            put(self.coefficients[:,component], indices, values)

    def __len__(self):
        """Return total no of degrees of freedom (coefficients)."""
        return size(self.coefficients)
    
    def get_nodal_values(self):
        pass

    # all interpolation in separate Interpolation module!
    def interpolate_at_loc_pt(self, loc_pt):
        """
        Interpolate the field at the local point loc_pt in all
        elements and return all these values.
        """
        #self.elm_coefficients(i,e)*N(i)
        #self.elm_coefficients(i,e)*someobj.dN(i,j,e)
        pass
    
    def interpolate_gradient_at_loc_pt(self, loc_pt):
        """
        Interpolate the gradient of the field at the local
        point loc_pt in all elements and return all these values
        as an array of (k,e) (e is element, k is direction)
        for scalar fields and (i,k,e) for vector fields (i is component).
        """
        #self.elm_coefficients(i,e)*N(i)
        #self.elm_coefficients(i,e)*someobj.dN(i,j,e)
        pass

    def interpolate_at_global_pts(self, global_pts):
        # very slow; should use Diffpack techniques to locate the
        # points, interpolate all these (since we may provide several
        # points, one can utilize that these are local, along a line,
        # etc. The functionality is best implemented in the grid class,
        # or better: as a separate module working with grid and field
        pass


def _test1D():
    from Grid import _test1D as grid_1D
    g, bi = grid_1D()
    f = Field(g)
    f.coefficients = 2*g.coor
    print f.coefficients
    f.prescribe_coefficients([bi['left'][0], bi['right'][0]], [-1.0, 10.0])
    print f.coefficients
    return f

def _tests():
    _test1D()


if __name__ == '__main__':
    _tests()
    
