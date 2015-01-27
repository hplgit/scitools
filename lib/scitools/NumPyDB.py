#!/usr/bin/env python
"""
Efficient database for NumPy objects.
"""

import sys, os, pickle, re
from scitools.numpytools import *

class NumPyDB:
    def __init__(self, database_name, mode='store'):
        self.filename = database_name
        self.dn = self.filename + '.dat' # NumPy array data
        self.pn = self.filename + '.map' # positions & identifiers
        if mode == 'store':
            # bring files into existence:
            fd = open(self.dn, 'w');  fd.close()
            fm = open(self.pn, 'w');  fm.close()
        elif mode == 'load':
            # check if files are there:
            if not os.path.isfile(self.dn) or \
               not os.path.isfile(self.pn):
                raise IOError("Could not find the files %s and %s" %\
                              (self.dn, self.pn))
            # load mapfile into list of tuples:
            fm = open(self.pn, 'r')
            lines = fm.readlines()
            self.positions = []
            for line in lines:
                # first column contains file positions in the
                # file .dat for direct access, the rest of the
                # line is an identifier
                c = line.split()
                # append tuple (position, identifier):
                self.positions.append((int(c[0]),
                                       ' '.join(c[1:]).strip()))
            fm.close()

    def locate(self, identifier, bestapprox=None): # base class
        """
        Find position in files where data corresponding
        to identifier are stored.
        bestapprox is a user-defined function for computing
        the distance between two identifiers.
        """
        identifier = identifier.strip()
        # first search for an exact identifier match:
        selected_pos = -1
        selected_id = None
        for pos, id in self.positions:
            if id == identifier:
                selected_pos = pos;  selected_id = id; break
        if selected_pos == -1: # 'identifier' not found?
            if bestapprox is not None:
                # find the best approximation to 'identifier':
                min_dist = \
                    bestapprox(self.positions[0][1], identifier)
                for pos, id in self.positions:
                    d = bestapprox(id, identifier)
                    if d <= min_dist:
                        selected_pos = pos;  selected_id = id
                        min_dist = d
        return selected_pos, selected_id

    def dump(self, a, identifier):  # empty base class func.
        """Dump NumPy array a with identifier."""
        raise NameError("dump is not implemented; must be impl. in subclass")

    def load(self, identifier, bestapprox=None):
        """Load NumPy array with identifier or find best approx."""
        raise NameError("load is not implemented; must be impl. in subclass")


class NumPyDB_text(NumPyDB):
    """Use plain ASCII string representation."""

    def __init__(self, database_name, mode='store'):
        NumPyDB.__init__(self, database_name, mode)

    # simple dump:
    def dump(self, a, identifier):
        """Dump NumPy array a with identifier."""
        fd = open(self.dn, 'a');  fm = open(self.pn, 'a')
        fm.write("%d\t\t %s\n" % (fd.tell(), identifier))
        fd.write(repr(a))
        fd.close();  fm.close()

    # more efficient dump (due to Mario Pernici <Mario.Pernici@mi.infn.it>)
    def dump(self, a, identifier):
        """Dump NumPy array a with identifier."""
        fd = open(self.dn, 'a');  fm = open(self.pn, 'a')
        fm.write("%d\t\t %s\n" % (fd.tell(), identifier))
        fmt = 'array([' + '%s,'*(a.size-1) + '%s])\n'
        fd.write(fmt % tuple(ravel(a)))
        fd.close();  fm.close()


    def load(self, identifier, bestapprox=None):
        """
        Load NumPy array with a given identifier. In case the
        identifier is not found, bestapprox != None means that
        an approximation is sought. The bestapprox argument is
        then taken as a function that can be used for computing
        the distance between two identifiers id1 and id2.
        """
        pos, id = self.locate(identifier, bestapprox)
        if pos < 0: return [None, "not found"]
        fd = open(self.dn, 'r')
        fd.seek(pos)
        # load the correct number of bytes; look at the next pos
        # value in self.positions (impossible if a dictionary is
        # used for self.positions - we need the order of the items!)
        for j in range(len(self.positions)):
            p = self.positions[j][0]
            if p == pos:
                try:
                    s = fd.read(self.positions[j+1][0] - p)
                except IndexError:
                    # last self.positions entry reached,
                    # just read the rest of the file:
                    s = fd.read()
                break
        a = eval(s)
        fd.close()
        return [a, id]


class NumPyDB_pickle (NumPyDB):
    """Use basic Pickle class."""

    def __init__(self, database_name, mode='store'):
        NumPyDB.__init__(self,database_name, mode)

    def dump(self, a, identifier):
        """Dump NumPy array a with identifier."""
        fd = open(self.dn, 'a');  fm = open(self.pn, 'a')
        fm.write("%d\t\t %s\n" % (fd.tell(), identifier))
        pickle.dump(a, fd, 1)  # 1: binary storage
        fd.close();  fm.close()

    def load(self, identifier, bestapprox=None):
        """
        Load NumPy array with a given identifier. In case the
        identifier is not found, bestapprox != None means that
        an approximation is sought. The bestapprox argument is
        then taken as a function that can be used for computing
        the distance between two identifiers id1 and id2.
        """
        pos, id = self.locate(identifier, bestapprox)
        if pos < 0: return None, "not found"
        fd = open(self.dn, 'r')
        fd.seek(pos)
        a = pickle.load(fd)
        fd.close()
        return a, id

import cPickle

class NumPyDB_cPickle (NumPyDB):
    """Use basic cPickle class."""

    def __init__(self, database_name, mode='store'):
        NumPyDB.__init__(self,database_name, mode)

    def dump(self, a, identifier):
        """Dump NumPy array a with identifier."""
        # fd: datafile, fm: mapfile
        fd = open(self.dn, 'a');  fm = open(self.pn, 'a')
        # fd.tell(): return current position in datafile
        fm.write("%d\t\t %s\n" % (fd.tell(), identifier))
        cPickle.dump(a, fd, 1)  # 1: binary storage
        fd.close();  fm.close()

    def load(self, identifier, bestapprox=None):
        """
        Load NumPy array with a given identifier. In case the
        identifier is not found, bestapprox != None means that
        an approximation is sought. The bestapprox argument is
        then taken as a function that can be used for computing
        the distance between two identifiers id1 and id2.
        """
        pos, id = self.locate(identifier, bestapprox)
        if pos < 0: return [None, "not found"]
        fd = open(self.dn, 'r')
        fd.seek(pos)
        a = cPickle.load(fd)
        fd.close()
        return [a, id]


import shelve

class NumPyDB_shelve:
    """Implement the database via shelving."""

    def __init__(self, database_name, mode='store'):
        self.filename = database_name # no suffix, only one file
        if mode == 'load':
            # since the keys() function in a shelf object
            # is slow, we store the keys:
            fd = shelve.open(self.filename)
            self.keys = list(fd.keys())
            fd.close()

    def dump(self, a, identifier):
        """Dump NumPy array a with identifier."""
        identifier = identifier.strip()
        fd = shelve.open(self.filename)
        fd[identifier] = a
        fd.close()

    def locate(self, identifier, bestapprox=None):
        """Return identifier key in shelf."""
        selected_id = None
        identifier = identifier.strip()
        if identifier in self.keys:
            selected_id = identifier
        else:
            if bestapprox:
                # find the best approximation to 'identifier':
                min_dist = bestapprox(self.keys[0], identifier)
                for id in self.keys:
                    d = bestapprox(id, identifier)
                    if d <= min_dist:
                        selected_id = id
                        min_dist = d
        return selected_id

    def load(self, identifier, bestapprox=None):
        """
        Load NumPy array with a given identifier. In case the
        identifier is not found, bestapprox != None means that
        an approximation is sought. The bestapprox argument is
        then taken as a function that can be used for computing
        the distance between two identifiers id1 and id2.
        """
        id = self.locate(identifier, bestapprox)
        if not id: return None, "not found"
        fd = shelve.open(self.filename)
        a = fd[id]
        fd.close()
        return a, id

# np.load/dump
# joblib.load/dump

def float_dist(id1, id2):
    """
    Compute distance between two identities for NumPyDB.
    Assumption: id1 and id2 are real numbers (but always sent
    as strings).
    This function is typically used when time values are
    used as identifiers.
    """
    return abs(float(id1) - float(id2))


def _test_dist(id1, id2):
    """
    Return distance between identifiers id1 and id2.
    The identifiers are of the form 'time=some number'.
    """
    # extract the numbers using regex:
    #t1 = re.search(r"time=(.*)", id1).group(1)
    #t2 = re.search(r"time=(.*)", id2).group(1)
    t1 = id1[5:];  t2 = id2[5:]
    d = abs(float(t1) - float(t2))
    return d

def main(n, length, method, name):
    out = "dumping/loading %d %d-arrays data with the %s method took" \
          % (n,length,method)
    if method == "pickle":
        dataout = NumPyDB_pickle(name, 'store')
    elif method == "cPickle":
        dataout = NumPyDB_cPickle(name, 'store')
    elif method == "shelve":
        dataout = NumPyDB_shelve(name, 'store')
    elif method == "text":
        dataout = NumPyDB_text(name, 'store')
    else:
        raise ValueError("illegal method name='%s'" % method)

    import time
    t0 = time.clock()
    for i in range(n):
        u = arange(i, length/2+i, 0.4999999)
        # (generate numbers with many digits so repr(u) has
        # a representative size (not just integers, for instance))

        dataout.dump(u, 'time=%e' % float(i))

    if method == "pickle":
        datain = NumPyDB_pickle(name, 'load')
    elif method == "cPickle":
        datain = NumPyDB_cPickle(name, 'load')
    elif method == "shelve":
        datain = NumPyDB_shelve(name, 'load')
    elif method == "text":
        datain = NumPyDB_text(name, 'load')
    else:
        raise ValueError("illegal method name='%s'" % method)

    w = datain.load('time=4')
    print "identifier='time=4':", w
    # not found, no exact match for 't=4', should have
    # 'time=4.000000e+00'
    w = datain.load('time=4.000000e+00')
    print "identifier='time=4.000000e+00': found"
    if len(w[0]) < 20: print w[0]

    w = datain.load('time=5', bestapprox=_test_dist)
    print "identifier='time=5' and bestapprox=_test_dest found"
    if len(w[0]) < 20: print w[0]
    t1 = time.clock()
    print "%s %.2f s" % (out, t1-t0)
    if os.path.isfile(name+'.dat'):
        filesize = os.path.getsize(name+'.dat')/1000000.0
    elif os.path.isfile(name):  # shelve technique leads to no extension
        filesize = os.path.getsize(name)/1000000.0
    print "filesize=%.2fMb\n\n" % filesize
    for filename in (name+'.dat', name+'.map', name):
        if os.path.isfile(filename):
            os.remove(filename)

if __name__ == '__main__':
    try:     n = int(sys.argv[1])
    except:  n = 12
    try:     length = int(sys.argv[2])
    except:  length = 10
    try:     methods = [sys.argv[3]]
    except:  methods = ['pickle','cPickle','shelve','text']
    print 'NumPy array type:', basic_NumPy
    for method in methods:
        main(n, length, method, "tmpdata_" + method)
