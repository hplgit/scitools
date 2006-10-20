#!/usr/bin/env python
"""
Read tabular data from file into NumPy arrays and vice versa.

This module provides functions for

  * reading row-column table data from file into NumPy arrays
  * writing two-dimensional NumPy arrays to file in a table fashion.

read:
    Load a table with numbers into a two-dim. NumPy array.
    file            file object
    commentchar     files starting with commentchar are skipped
                    (a blank line is an array data delimiter and stops reading)
    output          two-dimensional (row-column) NumPy array.

write:
    Write a two-dim. NumPy array a in tabular form.
    file             file object
    a                two-dim. NumPy array

read_columns:
    As read, but the columns are returned as separate arrays instead
    of a two-dimensional array.

write_columns:
    As write, but the arguments are comma-separated one-dimensional
    arrays, one for each column, instead of a two-dimensional array.
"""
# author: Hans Petter Langtangen <hpl@ifi.uio.no>

import sys, os, re
from Numeric import *

__all__ = ['read', 'read2', 'read_columns', 'readfile',
           'write', 'write2', 'write3', 'write4', 'write_columns',]

def read(file, commentchar='#'):
    """Load a table with numbers into a two-dim. NumPy array."""
    # read until next blank line:
    r = []  # total set of numbers (r[i]: numbers in i-th row)
    while 1:  # might call read several times for a file
        line = file.readline()
        if not line: break  # end of file
        if line.isspace(): break  # blank line
        if line[0] == commentchar: continue # treat next line
        r.append([float(s) for s in line.split()])
    return array(r, Float)

# faster read:
def read2(file, commentchar='#'):
    """Load a table with numbers into a two-dim. NumPy array."""
    # based on a version by Mario Pernici <Mario.Pernici@mi.infn.it>
    location = file.tell()
    import re
    commentchar = re.escape(commentchar)
    while 1:  # might call read several times for a file
        line = file.readline()
        if not line: break  # end of file
        elif line.isspace(): break  # blank line
        elif re.match(commentchar, line): continue # treat next line
        else: break

    shape1 = len(line.split())
    if shape1 == 0: return None
    file.seek(location)

    blankline = re.compile('\n\s*\n',  re.M)
    commentline = re.compile('^%s[^\n]*\n' % commentchar, re.M)
    filestr = file.read()
    # remove lines after a blank line
    m = re.search(blankline, filestr)
    if m:
        filestr = filestr[:m.start()+1]
    # skip lines starting with the comment character
    filestr = re.sub(commentline, '', filestr)
    a = [float(x) for x in filestr.split()]
    data = array(a, Float)
    data.shape = (len(a)/shape1, shape1)
    return data

read = read2  # the fast version is the default

def read_columns(file, commentchar='#'):
    """As read. Return columns as separate arrays."""
    a = read(file, commentchar)
    return [a[:,i] for i in range(a.shape[1])]

# for backward compatibility:
def readfile(filename, commentchar='#'):
    """As read. Return columns as separate arrays."""
    f = open(filename, 'r')
    a = read(f, commentchar)
    r = [a[:,i] for i in range(a.shape[1])]
    return r




def write(file, a):
    """Write a two-dim. NumPy array a in tabular form."""
    if len(a.shape) != 2:
        raise TypeError, \
              "a 2D array is required, shape now is "+str(a.shape)
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            file.write(str(a[i,j]) + "\t")
        file.write("\n")

# faster write:
def write2(file, a):
    """Write a two-dim. NumPy array a in tabular form."""
    # written by Mario Pernici <Mario.Pernici@mi.infn.it>
    if a.shape[1] == 1:
        for i in xrange(a.shape[0]): file.write('%g\n' % a[i,0])
    elif a.shape[1] == 2:
        for i in xrange(a.shape[0]): file.write('%g\t%g\n' % \
                                                (a[i,0],a[i,1]))
    elif a.shape[1] == 3:
        for i in xrange(a.shape[0]): file.write('%g\t%g\t%g\n' % \
                                                (a[i,0],a[i,1],a[i,2]))
    else:
        str_fmt = '%g\t'*(a.shape[1] - 1) + '%g\n'
        for i in xrange(a.shape[0]):
            file.write(str_fmt % tuple(a[i]))

    # don't think about
    # out = str(a).replace('[','').replace(',', '\t')
    # file.write(out + '\n')
    # the str(a) conversion is *extremely* expensive

def write3(file, a):
    """Short and fast version, compared to write and write2."""
    # written by Mario Pernici <Mario.Pernici@mi.infn.it>
    file.write(('%g\t'*(a.shape[1]-1) + '%g\n')*a.shape[0] % tuple(ravel(a)))

def write4(file, a):
    """Write a two-dim. NumPy array a in tabular form."""
    # fastest version (of the write family of functions) so far...
    # written by Mario Pernici <Mario.Pernici@mi.infn.it>
    
    if len(a.shape) != 2:
        raise TypeError, \
              "a 2D array is required, shape now is "+str(a.shape)
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
      file.write(str_fmt_N % tuple(a1))
    for i in range(shape0 - shape0%N, shape0):
      file.write(str_fmt % tuple(a[i]))

write = write4  # the fast version is the default

def write_columns(file, *columns):
    """As write, but the data are represented as one-dimensional columns."""
    a = transpose(array(columns))
    write(file, a)
    
    
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
    


