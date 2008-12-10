"""
Definition of finite elements.
"""
import scitools_core as stc

class Element:
    """
    Base class for definition of finite elements.
    Each element subclass contains at least these data structures:

    nodes : list of coordinates of nodes in the reference element
    nodes_on_side : list of list of coordinates of nodes on each side
    basis_functions : list of basis function objects
    basis_functions_dx : list of derivatives of basis functions
    """
    
    def N(self, i):
        """Return basis function no.i as a function object."""
        return self.basis_functions[i]

    def dN(self, i, j):
        """
        Return the derivative i j direction of basis function no.i,
        as a function object.
        """
        return self.basis_functions_dx[i][j]

    def eval_N(self, loc_pt):
        """
        Evaluate all basis functions at the loc_pt in the
        reference element. Returns a NumPy array r:
        if loc_pt is a single point:
           r[i] = N[i] at loc_pt
        if loc_pt is an nsd*npoints array of points:
           r[i,j] = N[i] at point no. j

        Note: for a set of points, loc_pt _must_ be a two-dim array.
        """
        if isinstance(loc_pt, (int,float)):
            loc_pt = [loc_pt]  # *loc_pt syntax below requires sequence
            
        n = len(self)
        # shape of result r depends on whether loc_pt is a point or
        # an array of points (scalar or vector version of this function):
        try:
            l = len(loc_pt.shape)
            if l == 2:
                r = stc.arr((n, loc_pt.shape[1]))  # vectorized
            elif l == 1:
                r = stc.arr(n)  # scalar
        except:
            r = stc.arr(n)  # scalar
            
        for i in range(n):
            r[i] = self.basis_functions[i](*loc_pt)
        return r

    def eval_dN(self, loc_pt):
        """
        Evaluate the derivative in all directions of all basis functions,
        at the loc_pt in the reference element.
        Returns a NumPy array r.
        if loc_pt is a single point:
           r[i,j] = dN[i]/dx[j] at loc_pt
        if loc_pt is an nsd*npoints array of points:
           r[i,j,k] = dN[i]/dx[j] at point no. k
        """
        if isinstance(loc_pt, (int,float)):
            loc_pt = [loc_pt]  # *loc_pt syntax below requires sequence
            
        n, nsd = len(self), self.nsd()
        
        # shape of result r depends on whether loc_pt is a point or
        # an array of points (scalar or vector version of this function):
        try:
            l = len(loc_pt.shape)
            if l == 2:
                r = stc.arr((n, nsd, loc_pt.shape[1])) # vectorized
            elif l == 1:
                r = stc.arr((n, nsd))
        except:
            r = stc.arr((n, nsd))

        for i in xrange(n):
            for j in xrange(nsd):
                r[i,j] = self.basis_functions_dx[i][j](*loc_pt)
        return r

    def __eq__(self, other):
        # true if other is a class type of the same class as self:
        return self.__class__ is other

    def nsd(self):
        """Return the number of space dimensions of the element."""
        # default implementation:
        try:
            return len(self.nodes[0])
        except TypeError:  # self.nodes[0] is not a tuple/list/array (1D coor)
            return 1

    def __len__(self):
        """Return the number of basis functions."""
        return len(self.basis_functions)

    # could have iterators over basis functions and iterators over
    # gradients of basis functions


_elements = [
    'ElmInterval2n',
    'ElmTriangle3n',
    ]
__all__ = _elements

class ElmInterval2n(Element):
    nodes = (-1, 1)
    nodes_on_side = (-1, 1)

    basis_functions = [
        lambda x1: 0.5*(1-x1),
        lambda x1: 0.5*(1+x1)
        ]

    basis_functions_dx = [
        [lambda x1: -0.5],
        [lambda x1: 0.5]
        ]

    def __init__(self):
        pass

class ElmTriangle3n(Element):
    nodes = ((0,0), (1,0), (0,1))
    nodes_on_side = ((1,2), (2,3), (3,1))

    basis_functions = [
        lambda x1, x2: 1 - x1 -x2,
        lambda x1, x2: x1,
        lambda x1, x2: x2
        ]

    basis_functions_dx = [
        [lambda x1, x2: -1, lambda x1, x2: -1],
        [lambda x1, x2: 1,  lambda x1, x2: 0],
        [lambda x1, x2: 0,  lambda x1, x2: 1]
        ]

    def __init__(self):
        pass

# think about basis functions with user-defined, element-variable
# physical parameters (boundary layer thickness, e.g.)
# attach a simulator ref to basis func instance, override N and dN
# to look up in sim ref, also equip N and dN with an extra prm
# (how was this done in Dp? - initialized the prm for each element)
# doc/Book/src/fem/ExpBasisFunc/ElmB2nF1D.cpp
# Here in py: just attach a simulator object and the parameters,
# update the parameters from the simulator or look up the simulator
# when a basis_functions[i] is called (the simulator must then have
# a suitable parameter for the current element). Difficulty:
# basis functions are not constant for all elements, which is a fundamental
# issue in this fast py implementation, but in this case one can
# preprocess an array of N(i) for each element (must have callback to
# simulator that returns array of prm values, then this array is used to
# compute N(i,e)...yes, that's the solution).

# think about mixed type basis functions, type a rough example


def _test_element(class_):
    e = class_()
    loc_pt = stc.arr(e.nsd())  # (0,0,...)
    print 'loc_pt:', loc_pt
    nqpts = 5  # assume 5 quadature points
    loc_pts = stc.arr((e.nsd(), nqpts))
    print 'loc_pts:', loc_pts
    print 'eval_N scalar:\n', e.eval_N(loc_pt)
    print 'eval_N vector:\n', e.eval_N(loc_pts)
    print 'eval_dN scalar:\n', e.eval_dN(loc_pt)
    print 'eval_dN vector:\n', e.eval_dN(loc_pts)

def _tests():
    for e in _elements:
        # e is string, eval(e) gives us the class object
        _test_element(eval(e))
        
if __name__ == '__main__':
    _tests()
    
                           
