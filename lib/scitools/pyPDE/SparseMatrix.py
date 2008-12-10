"""
Experimental implementation of some sparse matrix functionality.
"""

"""
>>> a = {(1,1) : 2, (1,2) : 'sin(x)', ('i','i-1') : 4 }
>>> a
{(1, 1): 2, ('i', 'i-1'): 4, (1, 2): 'sin(x)'}
>>> a.keys()
[(1, 1), ('i', 'i-1'), (1, 2)]
>>> class A:
	def __init__(self, offset=0):
		if offset == 0:
			self.s = 'i'
		else:
			self.s = 'i'
"""

class Index:
    def __init__(self, name='i', start=None, stop=None, offset=0):
        self.name = name
        self.start = start
        self.stop = stop
        self.offset = offset
        if offset == 0:
            self.s = name
        elif offset > 0:
            self.s = name + '+' + str(offset)
        else:
            self.s = name + str(offset)

    def __add__(self, n):
        return Index(name=self.name, offset=self.offset+n,
                     start=self.start, stop=self.stop)

    def __sub__(self, n):
        return Index(name=self.name, offset=self.offset-n,
                     start=self.start, stop=self.stop)

    def __str__(self):
        return self.s

    def __repr__(self):
        return self.s

    # __repr__ should have been this function, but that makes
    # printing of dictionary definition of matrices less readable
    def reconstruct(self):  
        return "Index(name='%s', offset=%d, start=%s, stop=%s)" % \
               (self.name, self.offset, str(self.start), str(self.stop))

    def value(self, i):
        return i + self.offset

class Index_old:
    def __init__(self, index_name='i', offset=0):
        self.name = index_name
        self.offset = offset
        if offset == 0:
            self.s = index_name
        elif offset > 0:
            self.s = index_name + '+' + str(offset)
        else:
            self.s = index_name + str(offset)

    def __add__(self, n):
        return Index(index_name=self.name, offset=self.offset+n)

    def __sub__(self, n):
        return Index(index_name=self.name, offset=self.offset-n)

    def __str__(self):
        return self.s

    def __repr__(self):
        return self.s

    def value(self, i):
        return i + self.offset


def db(comment, var=None):
    if os.environ.get('PYDEBUG','0') == '1':
        print comment, var
        
from py4cs.numpytools import *

class StructuredSparseMatrix:
    def __init__(self,
                 size=0,          
                 diagonals=3,     
                 matrix=None,     
                 initial_code=None,
                 index_code=None,
                 **user_kw
                 ):
        """
        size              no of unknowns
        diagonals         no of non-zero diagonals in matrix
        matrix            symbolic specification of matrix entries
                          or all diagonals filled with values
        initial_code      code to be executed initially
        index_code        code to be executed for each index value
        user_kw           user-defined keyword arguments
        """
        self.matrix = zeros((size, diagonals), Float)
        if isinstance(matrix, dict):
            self.make_matrix(matrix,
                             initial_code, user_kw, index_code)
        else:
            self.matrix = matrix

    def matrix_index(self, i, j):
        """
        Convert a mathematical index (i,j), i,j=0,...,n,
        to the corresponding index in self.matrix.
        Subclasses implement various storage formats
        and versions of this function.
        """
        raise TypeError, 'class Matrix is a virtual base class'
        
    def make_matrix(self, matrix,
                    initial_code, user_kw, index_code):
        # execute user's initial code:
        if initial_code is not None:
            exec initial_code in globals()
        # turn user's keyword arguments into local variables:
        for key in user_kw:
            exec "%s=user_kw['%s']" % (key,key)
            db(key+'=', eval(key))
            
        index_formulas = []
        self.matrix[:,:] = 0
        for pair in matrix:  # go through the keys
            if not isinstance(pair, tuple):
                raise TypeError, \
                      'matrix keys must be tuples, not %s' % type(pair)
            if len(pair) != 2:
                raise ValueError, \
                      'matrix keys are %d-tuples, not 2-tuples' % len(pair)
            r, s = pair
            if isinstance(r, Index):
                index_formulas.append(pair)  # store all index formulas
        # first generate entries from index_formulas:
        db('matrix',matrix)
        db('self.matrix',self.matrix)
        for pair in index_formulas:
            r, s = pair
            db('index formula', (r,s))

            index_start = r.start; index_stop = r.stop
            for i in isequence(index_start, index_stop, 1):
                ii = self.matrix_index(r.value(i),s.value(i))
                db('i=',i)

                if index_code is not None:
                    # name of for loop index must match the one
                    # used in index_code, or we may introduce
                    # the index of r,s here:
                    exec r.name + '=' + str(i)
                    exec index_code
                    db('setting i:',r.name + '=' + str(i))
                    db('index_code:', index_code)
                value = matrix[r,s]
                db('insert:','i=%d: self.matrix[%s]="%s"' % \
                   (i, str(ii),str(value)))
                if isinstance(value, str):
                    db('evaluating',value)
                    value = eval(value)
                try:
                    self.matrix[ii] = value
                except IndexError: pass
                db('self.matrix:\n', self.matrix)
        # then insert integer indices and corresponding values:
        for pair in matrix:
            r, s = pair
            if isinstance(r, int):
                # insert index and value directly in the matrix:
                db('int index:', (r,s))
                value = matrix[pair]
                # assume no index_code applies to integer indices
                if isinstance(value, str):
                    value = eval(value)
                try:
                    self.matrix[self.matrix_index(r,s)] = value
                except IndexError: pass


    def solve(self, rhs):
        raise TypeError, 'class Matrix is a virtual base class'


class TriDiagMatrix(StructuredSparseMatrix):
    def __init__(self,
                 size=0,          
                 matrix=None,     
                 initial_code=None,
                 index_code=None,
                 **user_kw
                 ):
        StructuredSparseMatrix.__init__(self,
        initial_code=initial_code, index_code=index_code,
        matrix=matrix, diagonals=3, size=size, **user_kw)

    def matrix_index(self, i, j):
        if j == i:
            return i,1
        elif j == i-1:
            return i,0
        elif j == i+1:
            return i,2
        else:
            raise IndexError, '(%d,%d) not legal index' % (i,j)

    def solve(self, rhs):
        if not isinstance(rhs, Vector):
            raise TypeError, "rhs must be of type Vector"
        try:
            import F77_tridiagsolve
            x = F77_tridiagsolve.solve(self.matrix, rhs.vector)
        except:
            # use Python code from NumPy (slow?)
            x = solve_tridiag_linear_system(self.matrix, rhs.vector)
        return x

    def __div__(self, rhs):
        return self.solve(rhs)

    def __str__(self):
        """print matrix as square matrix table"""
        n = len(self.matrix[:,1])
        if n > 10: return ''
        s = ''
        field_width = 9  # with of each number field
        format = '%' + '%dg' % field_width
        indent = 0
        A = self.matrix
        s += '%s %s\n' % (format, format) % (A[0,1],A[0,2])
        field_width += 1  # adjustment for nice layout
        for i in range(1,n-1,1):
            s += ' '*indent + '%s %s %s\n' % (format, format, format) % \
                 (A[i,0],A[i,1],A[i,2])
            indent += field_width
        s += ' '*indent + '%s %s\n' % (format, format) % \
             (A[n-1,0],A[n-1,1])
        return s
        
        
class DenseMatrix(StructuredSparseMatrix):
    def matrix_index(self, i, j):
        """
        Convert a mathematical index (i,j), i,j=0,...,n,
        to the corresponding index in self.matrix.
        The resulting index depends on the storage scheme.
        For a simple dense matrix, self.matrix applies (i,j)
        directly.
        For a tridiagonal matrix and other formats, some testing
        is necessary. Subclasses implement various storage formats
        and versions of this function.
        """
        # assume dense matrix:
        return i, j


class Vector:
    def __init__(self,
                 size=0,          
                 vector=None,     
                 initial_code=None,
                 index_code=None,
                 **user_kw
                 ):
        """
        size              no of unknowns
        vector            symbolic specification of vector entries
                          or array filled with numerical values
        initial_code      code to be executed initially
        index_code        code to be executed for each index value
        user_kw           user-defined keyword arguments
        """
        self.vector = zeros(size, Float)
        if isinstance(vector, dict):
            self.make_vector(vector,
                             initial_code, user_kw, index_code)
        else:
            self.vector = vector

    def vector_index(self, i):
        # 0 is base index in math & arrays
        return i  
        
    def make_vector(self, vector,
                    initial_code, user_kw, index_code):
        # execute user's initial code:
        if initial_code is not None:
            exec initial_code in globals()
        # turn user's keyword arguments into local variables:
        for key in user_kw:
            exec "%s=user_kw['%s']" % (key,key)
            
        index_formulas = []
        self.vector[:] = 0.0
        for entry in vector:  # go through the keys
            if isinstance(entry, Index):
                index_formulas.append(entry)  # store all index formulas
            elif isinstance(entry, int):
                pass # ok
            else:
                raise TypeError, 'wrong key type %s' % type(entry)
        # first generate entries from index_formulas:
        db('vector',vector)
        db('self.vector',self.vector)
        for entry in index_formulas:
            db('index formula', entry)

            index_start = entry.start; index_stop = entry.stop
            for i in isequence(index_start, index_stop, 1):
                ii = self.vector_index(entry.value(i))

                if index_code is not None:
                    # name of for loop index must match the one
                    # used in index_code, or we may introduce
                    # the index of r,s here:
                    exec entry.name + '=' + str(i)
                    exec index_code
                    db('exec:',entry.name + '=' + str(i))
                    db('exec:',index_code)
                value = vector[entry]
                db('i=%d: self.vector[%s]=%s' % (i, str(ii),str(value)))
                if isinstance(value, str):
                    db('evaluating',value)
                    value = eval(value)
                try:
                    self.vector[ii] = value
                except IndexError: pass
                db('self.vector:\n', self.vector)
        # then insert integer indices and corresponding values:
        for entry in vector:
            if isinstance(entry, int):
                db('int index:', entry)
                value = vector[entry]
                # assume no index_code applies to integer indices
                if isinstance(value, str):
                    value = eval(value)
                try:
                    self.vector[self.vector_index(entry)] = value
                except IndexError: pass

# wrap a tuple such that A(i,j) is the same as (i,j)
# (A is of type MatrixEntry)
class MatrixEntry:
    def __init__(self):
        return
    def __call__(self, i, j):
        return (i,j)

class RHSEntry:
    def __init__(self):
        return
    def __call__(self, i):
        return i

class LinearSystem:
    def __init__(self, coefficient_matrix, right_hand_side):
        self.A = coefficient_matrix
        self.b = right_hand_side

    def solve(self):
        # algorithm depends on matrix type:
        self.x = self.A.solve(self.b)
        return self.x

def test():
    i=Index('i', start=0, stop=10)
    print i
    print i-1
    print i-4-2
    print i+1

    a = {
        (i,i+1) : 2,
        (i,i-1) : -2,
        (1,2) : 3,
        }
    print a
    
    n = 12  # no of cells; points are 0,...,n
    size = n*n

    i = Index('i', start=1, stop=n-1)
    a = TriDiagMatrix(\
    initial_code="""\
n=%d; h=1.0/n;
""" % n,
    size=n+1,
    matrix={ (0,0) : 1, (i,i-1) : 1 , (i,i) : -2,
    (i,i+1) : 1, (n,n) : 1 }
    )
    print a.matrix
    print a

    b = Vector(\
    initial_code="""\
n=%d; h=1.0/n;
def F(x):
    return h*h
""" % n,
    index_code="""\
xi = i*h;
""",
    size=n+1,
    vector={ 0: 0, i : 'F(xi)', n: 0 }
    )
    print "b=",b.vector
    u = a/b
    print u
    x = seq(0,1,1.0/n)
    from CurveViz import CurveViz as C
    g = C(x)
    g.plotcurve(u)

    sys.exit(1)

    i = Index('i')
    #a = DenseMatrix(\
    a = TriDiagMatrix(\
    initial_code="""\
    h = 1.0/n;
    def K(x):
        r = x*x
        db("K(%g)=" % x,r)
        return r
    """,
    index_code="""\
    xp = (i+0.5)*h;
    xm = (i-0.5)*h;
    """,
    size=n,
    index_start=2,
    index_stop=n-1,
    matrix={ (1,1) : 1, (i,i-1) : 'K(xm)' , (i,i) : '-K(xm)-K(xp)',
    (i,i+1) : 'K(xp)', (n,n) : 1 }
    )
    print a.matrix

    b = Vector(\
    initial_code="""\
    h = 1.0/n;
    def F(x):
        r = sin(x)
        db("K(%g)=" % x,r)
        return r
    """,
    index_code="""\
    xi = i*h;
    """,
    size=n,
    index_start=2,
    index_stop=n-1,
    vector={ 1: 0, i : 'F(xi)', n: 10 }
    )
    print b.vector


    sys.exit(1)
    rhs = { 1: 0, i: 0, n: 1 }

    A = MatrixEntry()
    matrix={ A(1,1) : 1, A(i,i-1) : 'K(xm)' , A(i,i) : '-K(xm)-K(xp)',
    A(i,i+1) : 'K(xp)', A(n,n) : 1 }
    print 'Matrix with A:', matrix

    k = Index('k')
    a = DenseMatrix(\
    initial_code="""\
    h = 1.0/n;
    def K(x):
        return x*x
    """,
    index_code="""\
    xp = (k+0.5)*h;
    xm = (k-0.5)*h;
    """,
    diagonals=n,
    size=n,
    index_start=2,
    index_stop=n-1,
    matrix={ (1,1) : 1, (k,k-1) : 'K(xm)' , (k,k) : '-K(xm)-K(xp)',
    (k,k+1) : 'K(xp)', (n,n) : 1 }
    )
    print a.matrix

if __name__ == '__main__':
    test()
    
