
from scitools.errorcheck import right_type
__all__ = ['BoundaryIndicators', 'to_FEM_array', 'to_FDM_array']

class BoundaryIndicators:
    class Indicator:
        def __init__(self, name, where=[]):
            """
            Define a boundary indicator with a name and a list (where)
            of data structures defining where in a grid the
            indicator applies (this data structure depends of course on
            the type of grid; it might be a list of node numbers in a
            finite element mesh or a list of slices in a finite difference
            mesh).
            """
            if not isinstance(name, basestring):
                name = str(name)
            if not isinstance(where, (list,tuple)):
                where = [where]  # just wrap in list
            
            self.name = name
            self.where = where
            

        def __add__(self, other):
            """
            Add two indicators. The result has the name from the left
            operand, but the self.where attribute is the
            union of the self.where attributes of the two operands.
            """
            # recall to copy lists; otherwise the new object will
            # refer to old lists and modify these!
            i = BoundaryIndicators.Indicator(self.name, self.where[:])
            i.where.extend(other.where[:])
            return i

        def __repr__(self):
            return 'Indicator(%s, where=%s)' % (self.name, str(self.where))

        def __str__(self):
            return self.__repr__()
        
        
    def __init__(self, name2where, ordering=None):
        """
        name2where is a dictionary mapping a boundary indicator name
        to a data structure that represents a part of
        the grid (e.g., a list of node numbers in finite element
        meshes, or a list of slices in a finite difference mesh).

        Subclasses add functionality for finite element meshes, finite
        differences meshes, etc.

        ordering is an optional list specifying a certain sequence
        of the indicators in iterations.
        Subclasses may convert the boundary indicator information to
        array representations. The indicator names will then be
        integers corresponding to the index in the ordering list.
        An empty ordering list results in a default ordering corresponding
        to the indices in an alphabetically sorted list of names.

        Attributes:
        boind : dictionary of Indicator instances
        ordering : list of indicator names, implies the ordering of names
        name2int : map a name to a corresponding indicator integer value
        int2name : map an integer indicator value to its corresponding name

        Subscription:
        __getitem__(self,name) returns the "where" specification (list)
        corresponding to the given name.
        
        """

        # The basic data structure is a dictionary of Indicator instances:
        self.boind = {}
        for name in name2where:
            self.boind[name] = \
                 BoundaryIndicators.Indicator(name, name2where[name])

        self.ordering = ordering
        if not ordering:
            # generate a default set of integer indicators:
            ordering = name2where.keys()
            ordering.sort()
        self.name2int = {}
        self.int2name = {}
        for i in range(len(ordering)):
            self.name2int[ordering[i]] = i
            self.int2name[i] = ordering[i]

        self._iterate_over = 'name'  # iterators iterate over names by default

    def __getitem__(self, name):
        """List data holding grid parts subject to indicator given by name."""
        return self.boind[name].where

    def __str__(self):
        """Pretty print."""
        import pprint
        s = 'Boundary indicators:\n'
        for name in self.boind:
            s += '%-10s %s\n' % (name, pprint.pformat(self.boind[name].where))
        return s

    def __repr__(self):
        # need to build a straight dictionary to print with pprint.pformat
        bidict = {}
        for name in self.boind:
            bidict[name] = self.boind[name].where
        s = 'BoundaryIndicators('
        import pprint
        s += pprint.pformat(bidict)
        if s.find('\n') != -1:
            s += ',\n'
        else:
            s += ', '
        s += 'ordering=' + str(self.ordering) + ')'
        return s

    def numbers(self):
        """
        Used in
          for ind, where in boundary_indicators.numbers():
        for iterating over the integer indicators.
        """
        self._iterate_over = 'ind'
        return self

    def names(self):
        """
        Used in
          for name, where in boundary_indicators.names():
        for iterating over the names of the indicators.
        """
        self._iterate_over = 'name'
        return self

    def __iter__(self):
        """
        Iterate of indicators:
        for name, where in boundary_indicators.names():
        or
        for indicator_no, where in boundary_indicators.numbers():
        or just
        for name, where in boundary_indicators:
        """
        if self._iterate_over == 'ind':
            for name in self.ordering:
                yield self.name2int[name], self.boind[name].where
        else:
            for name in self.ordering:
                yield name, self.boind[name].where

    def __len__(self):
        """Returns the number of indicators."""
        return len(self.boind)

    def new(self, specification, add=True):
        """
        Redefine a set of boundary indicators. specification is a string
        specifying the new composition of indicators. Its syntax goes
        as follows:
        newind1 <- oldind_i + oldind_j + oldind_k; newind2 <- ;
        add=True means that the new indicators are added to the set
        of indicators, while add=False means that old indicators are erased.
        """
        if specification and specification.find('<-') == -1:
            raise SyntaxError, \
                  'redef_str="%s" has no <- assignment' % redef_str
        newboind = {}
        specs = specification.split(';')
        for spec in specs:
            spec = spec.strip()
            if spec:  # might be double ;; and empty specifications...
                newname, addop = spec.split('<-')
                newname = newname.strip()
                operands = addop.split('+')
                operands = [op.strip() for op in operands]
                cmd = 'newboind["""%s"""] = ' % newname
                if operands != ['']:
                    cmd += ' + '.join(['self.boind["""%s"""]' % name \
                                       for name in operands])
                else:
                    cmd += 'BoundaryIndicators.Indicator("""%s""", where=[])' \
                           % name
                #print cmd
                exec cmd
        if add:
            self.boind.update(newboind)
        else:
            self.boind = newboind

    def validate(self, where_type='FEM'):
        """
        Validate the data structures contained in the self.where
        attribute (provided as the where keyword argument to the
        constructor).

        where_type='FEM' implies that where is a list of ints (node numbers).
        where_type='FDM' implies that where is a list of tuples, where
        each item is either an int or a slice object.
        """
        for name in self.boind:
            if where_type == 'FEM':
                for i in self.boind[name].where:
                    if not isinstance(i, int):
                        return False
            elif where_type == 'FDM':
                for i in self.boind[name].where:
                    if not isinstance(i, (int, tuple, list)):
                        return False
            else:
                raise ValueError, 'where_type=%s is not impl.' \
                      % repr(where_type)
            

def to_FEM_array(bi, nno):
    """
    Transform BoundaryIndicators object to a 2-dim int array a
    such that a[n,ind]=1 if indicator no ind is on at node no n.
    a has size (nno, len(bi)) (number of nodes, number of indicators).
    The relation between integer indicator numbers and names is
    given by bi.name2int[name] and bi.ind2name[ind].
    """
    from scitools_core import arr
    a = arr((nno, len(bi)), element_type=Int)  # could go with Bool too
    legal = bi.validate('FEM')  # check that bi.where is ok
    if not legal:
        raise TypeError, 'items in the list bi.where are of wrong type'
    from scitools_core import basic_NumPy
    if basic_NumPy == 'Numeric':
        for name in bi:
            ind = bi.name2int[name]
            for node in bi[name]:
                a[node, ind] = 1
    else:
        # this vectorized version works in numarray or Numeric3:
        for name in bi:
            a[bi[name], bi.name2int[name]] = 1  

def to_FDM_array(bi):
    # some fixed Int array for fast representation of boundary info
    # in F77 and C/C++ codes
    pass

def _test1():
    n = 10
    bi = BoundaryIndicators(name2where={'u=0': [(slice(0,n-1), 1)],
                                        'u=1': [],
                                        "u'=0": [1,8,9]},
                            ordering=['u=0', 'u=1', "u'=0"])
    print str(bi)
    print repr(bi)
    print '\niterate of names, then over indicator numbers:'
    for name, where in bi.names():
        print name, where
    print
    for ind, where in bi.numbers():
        print ind, where

    bi.new("""
u_given <- u=0 + u'=0 + u=1;
dudx <- u=1;
new1<-; ; ;
new2 <- u=0
""")
    print str(bi)

if __name__ == '__main__':
    _test1()
    
                            
            


