"""
Finite element grid class.
"""

from scitools.errorcheck import *
from scitools.basics import arr, seq, Int, OPTIMIZATION, SAFECODE, check
import Element
import pprint

__all__ = ['Grid', 'SubGrid']
__author__ = 'Hans Petter Langtangen <hpl@simula.no>, www.simula.no'

class Grid:
    """
    Finite element grid. The grid represents the geometry.
    Basis functions are defined elsewhere.
    """
    def __init__(self, coor=None, loc2glob=None,
                 element_types=None,
                 material_names={'domain': 0}, materials=0,
                 no_of_physical_space_dim=None):
        """
        element_types:
          List of element types (instances of classes from the Element module).
          Basically, these element types are used to describe the geometry
          of the element (one may think of this geometry element as the
          mapping from a reference element to a global, physical element).
          A finite element field can override the grid element types if
          the basis functions needed in the field do not coincide with
          the basis functions implied by the grid element type (this
          is the case for non-isoparametric elements).
          
          element_types is either a subclass instance of Element,
          or an array specifying for each element a subclass instance
          of Element to map that particular element, or None (in that
          case the right Element subclass is guessed from the number
          of space dimensions and number of nodes in each element).
          (Note that the geometry mapping is defined through a Mapping
          class, consisting of an Element instance and some coordinate
          information in the element.)

        material_names is a dictionary mapping material names (strings)
        to integers. These integers just provide an alternative material
        indicator (for computational efficiency).

        materials is either an int (material indicator) in case of one
        material, or a sequence of material indicators, one for each
        element. These indicators are also associated with names (string)
        stored in material_names.

        """
        
        self.coor = arr(data=coor, copy=False)
        self.loc2glob = arr(data=loc2glob, copy=False)
        nel = loc2glob.shape[0]

        right_type(element_types, (None,Element.Element,list,tuple))
        if element_types is None:
            print 'No default mapping yet from nsd, loc_nno to elm tp'
        elif isinstance(element_types, Element.Element):
            self.elm_tp = [element_types]*nel
            # note: [instance]*n creates n *references* to instance
            # so no copying takes place above
        elif isinstance(element_types, (list,tuple)):
            self.elm_tp = element_types
        else:
            # self.elm_tp is not created, abort
            raise TypeError, 'element_types must be None, ' \
                  'instance of subclass Element, or list of such instances,' \
                  ' not %s' % type(element_types)

        # subgrid concept for handling all elms of a type at once
        # in vectorized expr? look at examples

        if isinstance(materials, int):
            self.mat = arr(self.nel, element_type=Int) + int
        else:  # assume materials is a sequence
            right_size1(materials, loc2glob.shape[0])
            self.mat = arr(data=materials, copy=False, element_type=Int)
            
        if material_names:
            self.mat_names = material_names
            # check for consistency: all values in self.mat must also
            # be values in self.mat_names
        else:
            self.mat_names = {}
            for e in self.mat:
                self.mat_names[self.mat[e]] = str(self.mat[e])
        self.mat_ind2names = {}
        for name in self.mat_names:
            self.mat_ind2names[self.mat_names[name]] = name

        if len(self.coor.shape) == 1:
            self.nsd = 1
        else:
            self.nsd = self.coor.shape[1]
        if no_of_physical_space_dim is not None:
            self.nsd_physical = no_of_physical_space_dim
        else:
            self.nsd_physical = self.nsd
            
        # could have additional info, set with setattr from some
        # other class

    nel = property(fget=lambda self: self.loc2glob.shape[0])
    nno = property(fget=lambda self: self.coor.shape[0])
    
    def dump(self):
        #from py4cs.misc import dump
        #print dump(self)
        s = ''
        s += '\ncoordinates:\n' + str(self.coor)
        s += '\n\nelement connectivity:\n'
        for e in xrange(self.nel):
            s += '%5d: %s ' % (e, self.elm_tp[e].__class__.__name__)
            s += str(self.loc2glob[e,:])
            s += ' material=' + str(self.mat[e])
            s += ' (name=' + str(self.mat_ind2names[self.mat[e]]) + ')\n'
        return s

    def __str__(self):
        return self.dump()

    def __repr__(self):
        s = 'Grid(\\\n'
        # data consists of tuples (constructor argument name,
        # class attribute name):
        data = (('coor', 'coor'),
                ('loc2glob', 'loc2glob'),
                ('materials', 'mat'),
                ('material_names', 'mat_names'),
                ('no_of_physical_space_dim', 'nsd_physical'),
                )
        for arg, attr in data:
            s += arg + '=' + pprint.pformat(eval('self.'+attr)) + '\n'
        s += '\n)\n'
        return s


class SubGrid:
    """
    Extract a subgrid from a Grid. The elements forming the subgrid
    are picked either from given material type(s) and/or given
    element type(s).
    """
    def __init__(self, original_grid,
                 element_types=None,
                 material_types=None,
                 all=False):
        self.original_grid = original_grid
        if all:
            self.elm_glob2sub = arr(data=range(self.original_grid.nel),
                                    element_type=Int)
            self.elm_sub2glob = self.elm_glob2sub.copy()
            self.grid = original_grid
            return

        # else (not all elements are selected):
        self.elm_glob2sub = arr(self.original_grid.nel, element_type=Int)
        self.elm_glob2sub += -1  # default
        self.elm_sub2glob = []
        i = []  # indices for vectorized version
        # compute subgrid:
        if material_types is not None:
            if not isinstance(material_types, (list,tuple)):
                material_types = [material_types]  # wrap in list
            if not OPTIMIZTION:
                counter = 0
                for e in xrange(self.original_grid.nel):
                    if self.original_grid.material_types[e] in material_types:
                        self.elm_glob2sub[e] = counter
                        self.elm_sub2glob.append(e)
                        counter += 1
            elif OPTIMIZATION == 'vectorization':
                for m in material_types:
                    i.append(nonzero(equal(self.original_grid.material_types, m)))
        if element_types is not None:
            if not isinstance(element_types, (list,tuple)):
                element_types = [element_types]
            if not OPTIMIZTION:
                counter = 0
                for e in xrange(self.original_grid.nel):
                    if self.original_grid.element_types[e] in element_types:
                        self.elm_glob2sub[e] = counter
                        self.elm_sub2glob.append(e)
                        counter += 1
            elif OPTIMIZATION == 'vectorization':
                for e in element_types:
                    i.append(nonzero(equal(self.original_grid.element_types, e)))
        if not OPTIMIZATION:
            self.elm_sub2glob = arr(data=self.elm_sub2glob)  # list -> array
        elif OPTIMIZATION == 'vectorization':
            self.elm_sub2glob = sort(concatenate(i))
            self.elm_glob2sub = put(self.elm_glob2sub, self.elm_sub2glob,
                                    range(len(self.elm_sub2glob)))

        # make new grid...
        loc2glob = take(self.original_grid.loc2glob, self.elm_sub2glob)
        _nodes = ravel(loc2glob)
        # there are multiple values in nodes, use a dict (in C...) to
        # find the unique node numbers, extract from coor, etc.
        if not OPTIMIZATION:
            nodes = {}
            counter = 0
            for n in _nodes:
                nodes[n] = counter
                counter += 1

    def insert(self, subgrid_array, globalgrid_array):
        """
        Insert a subgrid array in the right locations in an array
        associated with the global grid.
        Should be extended with dof info...
        """
        put(globalgrid_array, self.node_sub2glob, subgrid_array)
    
    # get more from Diffpack SubGridFE class...

# boundary indicators must be separate!

def _test1D():
    # first a uniform grid:
    coor = seq(-1, 2, 0.5)
    from Element import ElmInterval2n
    loc2glob = arr(data=[(e, e+1) for e in range(len(coor)-1)])
    materials = arr(len(coor)-1, element_type=Int)
    middle = int((len(coor)-1)/2.0)
    print middle
    materials[middle:] = 1
    print materials
    g = Grid(coor=coor,
             loc2glob=loc2glob,
             element_types=ElmInterval2n(),
             material_names={'left': 0, 'right': 1},
             materials=materials
             )
    print g.dump()
    boinds = {'left': 0, 'right': len(coor)-1}
    from pyPDE.BoundaryIndicators import BoundaryIndicators
    bi = BoundaryIndicators(boinds)
    print bi
    return g, bi

def _tests():
    _test1D()

if __name__ == '__main__':
    _tests()
    
