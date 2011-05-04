#!/usr/bin/env python
"""
Read tabular data from file into NumPy arrays and vice versa.

This module provides functions for
1) reading row-column table data from file into NumPy arrays, and
2) writing two-dimensional NumPy arrays to file in a table fashion.

  - read: Load a table with numbers into a two-dim. NumPy array.

  - write: Write a two-dim. NumPy array a in tabular form.

  - read_columns:
    As read, but the columns are returned as separate arrays instead
    of a two-dimensional array.

  - write_columns:
    As write, but the arguments are comma-separated one-dimensional
    arrays, one for each column, instead of a two-dimensional array.

The file format requires the same number of "words" (numbers)
on each line. Comment lines are allowed, but a blank line
indicates a delimiter in the data set, and lines after the blank
line will not be read.

Example: Assume we have a data file `tmp.dat` with the numbers::

  0        0.0        0.0        1.0
  1        1.0        1.0        2.0
  2        4.0        8.0       17.0
  3        9.0       27.0       82.0
  4       16.0       64.0      257.0
  5       25.0      125.0      626.0

The following session demonstrates key functions in this module::

    >>> import scitools.filetable as ft
    >>> s = open('tmp.dat', 'r')
    >>> table = ft.read(s)
    >>> s.close()
    >>> print table
    [[   0.    0.    0.    1.]
     [   1.    1.    1.    2.]
     [   2.    4.    8.   17.]
     [   3.    9.   27.   82.]
     [   4.   16.   64.  257.]
     [   5.   25.  125.  626.]]

    >>>
    >>> s = open('tmp.dat', 'r')
    >>> x, y1, y2, y3 = ft.read_columns(s)
    >>> s.close()
    >>> print x
    [ 0.  1.  2.  3.  4.  5.]
    >>> print y1
    [  0.   1.   4.   9.  16.  25.]
    >>> print y2
    [   0.    1.    8.   27.   64.  125.]
    >>> print y3
    [   1.    2.   17.   82.  257.  626.]
    >>>
    >>> s = open('tmp2.dat','w')
    >>> ft.write(s, table)
    >>> s.close()

The `tmp2.dat` file looks as follows::

    0       0       0       1
    1       1       1       2
    2       4       8       17
    3       9       27      82
    4       16      64      257
    5       25      125     626

"""
# author: Hans Petter Langtangen <hpl@ifi.uio.no>

import sys, os, re
from numpy import *

__all__ = ['read', 'read_columns', 'readfile',
           'write', 'write_columns',]

# simple version (not as effective as function read):
def read_v1(fileobj, commentchar='#'):
    """Load a table with numbers into a two-dim. NumPy array."""
    # read until next blank line:
    r = []  # total set of numbers (r[i]: numbers in i-th row)
    while True:  # might call read several times for a file
        line = fileobj.readline()
        if not line: break  # end of file
        if line.isspace(): break  # blank line
        if line[0] == commentchar: continue # treat next line
        r.append([float(s) for s in line.split()])
    return array(r)


def read(fileobj, commentchar='#'):
    """
    Load a table with numbers into a two-dim. NumPy array.
    @param fileobj: open file object.
    @param commentchar: lines starting with commentchar are skipped
    (a blank line is an array data delimiter and stops reading).
    @return: two-dimensional (row-column) NumPy array.
    """
    # based on a version by Mario Pernici <Mario.Pernici@mi.infn.it>
    location = fileobj.tell()
    import re
    commentchar = re.escape(commentchar)
    while True:
        line = fileobj.readline()
        if not line: break  # end of file
        elif line.isspace(): break  # blank line
        elif re.match(commentchar, line): continue # treat next line
        else: break

    shape1 = len(line.split())
    if shape1 == 0: return None
    fileobj.seek(location)

    blankline = re.compile('\n\s*\n',  re.M)
    commentline = re.compile('^%s[^\n]*\n' % commentchar, re.M)
    filestr = fileobj.read()
    # remove lines after a blank line
    m = re.search(blankline, filestr)
    if m:
        filestr = filestr[:m.start()+1]
    # skip lines starting with the comment character
    filestr = re.sub(commentline, '', filestr)
    a = [float(x) for x in filestr.split()]
    data = array(a)
    data.shape = (len(a)/shape1, shape1)
    return data


def read_columns(fileobj, commentchar='#'):
    """As read. Return columns as separate arrays."""
    a = read(fileobj, commentchar)
    return [a[:,i] for i in range(a.shape[1])]

# for backward compatibility:
def readfile(filename, commentchar='#'):
    """
    As read, but a filename (and not a file object) can be given.
    Return: columns as separate arrays.
    """
    f = open(filename, 'r')
    a = read(f, commentchar)
    r = [a[:,i] for i in range(a.shape[1])]
    return r



# simple write version:
def write_v1(fileobj, a):
    """Write a two-dim. NumPy array a in tabular form to fileobj."""
    if len(a.shape) != 2:
        raise TypeError("a 2D array is required, shape now is "+str(a.shape))
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            fileobj.write(str(a[i,j]) + "\t")
        fileobj.write("\n")

# faster write version:
def write_v2(fileobj, a):
    """Write a two-dim. NumPy array a in tabular form to fileobj."""
    # written by Mario Pernici <Mario.Pernici@mi.infn.it>
    if a.shape[1] == 1:
        for i in xrange(a.shape[0]): fileobj.write('%g\n' % a[i,0])
    elif a.shape[1] == 2:
        for i in xrange(a.shape[0]): fileobj.write('%g\t%g\n' % \
                                                (a[i,0],a[i,1]))
    elif a.shape[1] == 3:
        for i in xrange(a.shape[0]): fileobj.write('%g\t%g\t%g\n' % \
                                                (a[i,0],a[i,1],a[i,2]))
    else:
        str_fmt = '%g\t'*(a.shape[1] - 1) + '%g\n'
        for i in xrange(a.shape[0]):
            fileobj.write(str_fmt % tuple(a[i]))

    # don't think about
    # out = str(a).replace('[','').replace(',', '\t')
    # fileobj.write(out + '\n')
    # the str(a) conversion is *extremely* expensive

def write_v3(fileobj, a):
    """Short and fast version, compared to write_v1 and write_v2."""
    # written by Mario Pernici <Mario.Pernici@mi.infn.it>
    fileobj.write(('%g\t'*(a.shape[1]-1) + '%g\n')*a.shape[0] % tuple(ravel(a)))

def write(fileobj, a):
    """Write a two-dim. NumPy array a in tabular form to fileobj."""
    # fastest version (of the write family of functions) so far...
    # written by Mario Pernici <Mario.Pernici@mi.infn.it>
    
    if len(a.shape) != 2:
        raise TypeError("a 2D array is required, shape now is "+str(a.shape))
    N = 512
    shape0 = a.shape[0]
    shape1 = a.shape[1]
    str_fmt = '%g\t'*(shape1 - 1) + '%g\n'
    # use a big format string
    str_fmt_N = str_fmt * N
    for i in xrange(shape0/N):
      a1 = a[i:i+N,:]
      # put a1 in  1D array form; ravel better than reshape for
      # non-contiguous arrays.
      a1 = ravel(a1)
      fileobj.write(str_fmt_N % tuple(a1))
    for i in range(shape0 - shape0%N, shape0):
      fileobj.write(str_fmt % tuple(a[i]))


def write_columns(fileobj, *columns):
    """
    As write, but the column data are represented as one-dimensional
    arrays.
    """
    a = array(columns).transpose()
    write(fileobj, a)
    
    
# testing:
def _generate(nrows, ncolumns, filename):
    f = open(filename, 'w')
    a = fromfunction(lambda i,j: i+j*j, (nrows,ncolumns))
    narrays = 3  # no of arrays in the file
    f.write('# %d arrays in this file\n#\n' % narrays)
    for i in range(narrays):
        f.write('# a new array with %d rows:  \n' % nrows)
        f.write('#\n')
        write(f, a)
        f.write('\n')  # array delimiter

def _test(n):
    _generate(n, 3, "tmp.1")
    import time
    t0 = time.clock()
    f = open("tmp.1", "r")
    narrays = int(f.readline().split()[1])
    print 'found %d arrays in file' % narrays
    for i in range(narrays):
        q = read(f)
        print 'read an array with shape', q.shape
    t1 = time.clock()
    print "read:", t1-t0, "seconds\n"
    f.close()
    t0 = time.clock()
    f = open("tmp.2", "w")
    write(f,q)
    t1 = time.clock()
    print "write:", t1-t0, "seconds"
    
    # compare with TableIO:
    try:
        import TableIO.TableIO as TableIO
    except:
        sys.exit(0) # exit silently
    t0 = time.clock()
    p = TableIO.readColumns("tmp.1", "#")
    #print 'p:', p
    t1 = time.clock()
    print "TableIO.readColumns:", t1-t0, "seconds\n"
    t0 = time.clock()
    TableIO.writeArray("tmp.3", array(p))
    t1 = time.clock()
    print "TableIO.writeArray:", t1-t0,"seconds"

if __name__ == '__main__':
    _test(100000)
    


