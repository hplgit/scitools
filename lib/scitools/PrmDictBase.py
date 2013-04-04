#!/usr/bin/env python
"""
Module for managing parameters.
"""
import re, os, sys
import collections
import numbers

def message(m):
    if os.environ.get('DEBUG', '0') == '1':
        print m


class PrmDictBase(object):
    """
Base class for managing parameters stored in dictionaries.
Typical use includes data or solver classes for solving physical
problems numerically. One may then choose to hold all physical
parameters in a dictionary physical_prm, containing
(parameter name, value) pairs, and all numerical parameters in
a dictionary numerical_prm. The physical_prm and numerical_prm
dictionaries can then be defined in a subclass of PrmDictBase
and managed by PrmDictBase. The management includes several
convenient features:

 - keeping all input data in one place
 - setting of one or more parameters where the type of the value
   must match the type of the previous (initial) value
 - pretty print of all defined parameters
 - copying parameters from dictionaries to, e.g., local variables
   and back again, or to local namespaces and back again
 - easy transition from parameter dictionaries to more sophisticated
   handling of input data, e.g., class scitools.ParameterInterface
   (GUI, CGI, command-line args)

The subclass typically defines the dictionaries, say
self.physical_prm and self.numerical_prm. Then these are
appended to the inherited self._prm_list list to be registered.
All members of this list are dictionaries that will not accept
new keys (i.e., all parameters must be defined prior to registering
them in self._prm_list). With this list one has a collection of all
parameter dictionaries in the application.

self._type_check[prm] is defined if we want to type check
a parameter prm.
if self._type_check[prm] is True (or False), prm must either
be None, of the same type as the previously registered
value of prm, or any number (float, int, complex) if
the previous value prm was any number. Instead of a boolean
value, self._type_check[prm] may hold a tuple of class types
(to be used in isinstance checks), or a function which takes
the value as argument and returns True if the that value is
of the right type (otherwise False).


In addition to the parameter dictionaries with fixed keys, class
PrmDictBase also holds a self.user_prm, which is a dictionary
of "meta data", i.e., an arbitrary set of keys and values that
can arbitrarily extended anywhere. If self.user_prm is None,
no such meta data can exists (implying that only parameters
registered in the dictionaries in self._prm_list are allowed - the
programmer of subclasses can of course extend these parameter
sets whenever desired; disallowing a parameter name is only a
feature of the set function for setting the value of a (registered)
parameter).

Here is an example::

    from scitools.PrmDictBase import PrmDictBase

    class SomeSolver(PrmDictBase):
        def __init__(self, **kwargs):
            PrmDictBase.__init__(self)
            # register parameters in dictionaries:
            self.physical_prm = {'density': 1.0, 'Cp': 1.0,
                                       'k': 1.0, 'L': 1.0}
            self.numerical_prm =  {'n': 10, 'dt': 0.1, 'tstop': 3}

            # attach dictionaries to base class list (required):
            self._prm_list = [self.physical_prm, self.numerical_prm]

            # specify parameters to be type checked when set:
            self._type_check.update({'n': True, 'dt': (float,),
                  'k': lambda k: isinstance(int,float) and k>0})

            # disallow arbitrary meta data
            self.user_prm = None # set to {} if meta data are allowed

            # initialize parameters according to keyword arguments:
            self.set(**kwargs)


        def _update(self):
            # dt depends on n, L, k; update dt in case the three
            # others parameters have been changed
            # (in general this method is used to check consistency
            # between parameters and perform updates if necessary)
            n = self.numerical_prm['n']
            L = self.physical_prm['L']
            k = self.physical_prm['k']

            self.u = zeros(n+1, Float)
            h = L/float(n)
            dt_limit = h**2/(2*k)
            if self.numerical_prm['dt'] > dt_limit:
                self.numerical_prm['dt'] = dt_limit

        def compute1(self):
            # compute something
            return self.physical_prm['k']/self.physical_prm['Cp']

        def compute2(self):
            # turn numerical parameters into local variables:
            exec self.dicts2variables(self._prm_list)
            # or exec self.dicts2variables(self.numerical_prm)  # selected prms

            # now we have local variables n, dt, tstop, density, Cp, k, L
            # that we can compute with, say

            Q = k/Cp
            dt = 0.9*dt

            # if some of the local variables are changed, say dt, they must
            # be inserted back into the parameter dictionaries:
            self.variables2dicts(self.numerical_prm, dt=dt)

    """

    def __init__(self):
        # dicts whose keys are fixed (non-extensible):
        self._prm_list = []     # fill in subclass
        self.user_prm = None    # user's meta data
        self._type_check = {}   # fill in subclass

    def _prm_dict_names(self):
        """Return the name of all self.*_prm dictionaries."""
        return [attr for attr in self.__dict__ if \
                re.search(r'^[^_].*_prm$', attr)]

    def usage(self):
        """Print the name of all parameters that can be set."""
        prm_dict_names = self._prm_dict_names()
        prm_names = []
        for name in prm_dict_names:
            d = self.__dict__[name]
            if isinstance(d, dict):
                k = list(d.keys())
                k.sort(lambda a,b: cmp(a.lower(),b.lower()))
                prm_names += k
        print 'registered parameters:\n'
        for i in prm_names:
            print i
        # alternative (sort all in one bunch):
        # names = []
        # for d in self._prm_list:
        #     names += list(d.keys())
        # names.sort
        # print names

    def dump(self):
        """Dump all parameters and their values."""
        for d in self._prm_list:
            keys = list(d.keys())
            keys.sort(lambda a,b: cmp(a.lower(),b.lower()))
            for prm in keys:
                print '%s = %s' % (prm, d[prm])

    def set(self, **kwargs):
        """Set kwargs data in parameter dictionaries."""
        # print usage message if no arguments:
        if len(kwargs) == 0:
            self.usage()
            return

        for prm in kwargs:
            _set = False
            for d in self._prm_list:
                if len(list(d.keys())) == 0:
                    raise ValueError('self._prm_list is wrong (empty)')
                try:
                    if self.set_in_dict(prm, kwargs[prm], d):
                        _set = True
                        break
                except TypeError, msg:
                    print msg
                    #break
                    sys.exit(1)  # type error is fatal

            if not _set:   # maybe set prm as meta data?
                if isinstance(self.user_prm, dict):
                    # not a registered parameter:
                    self.user_prm[prm] = kwargs[prm]
                    message('%s=%s assigned in self.user_prm' % \
                            (prm, kwargs[prm]))
                else:
                    raise NameError('parameter "%s" not registered' % prm)
        self._update()

    def set_in_dict(self, prm, value, d):
        """
        Set d[prm]=value, but check if prm is registered in class
        dictionaries, if the type is acceptable, etc.
        """
        can_set = False
        # check that prm is a registered key
        if prm in d:
            if prm in self._type_check:
                # prm should be type-checked
                if isinstance(self._type_check[prm], (int,float)):
                    # (bool is subclass of int)
                    if self._type_check[prm]:
                        # type check against prev. value or None:
                        if isinstance(value, (type(d[prm]), None)):
                            can_set = True
                        # allow mixing int, float, complex:
                        elif isinstance(value, numbers.Number) and\
                                 isinstance(d[prm], numbers.Number):
                            can_set = True
                elif isinstance(self._type_check[prm], (tuple,list,type)):
                    # self._type_check[prm] holds either the type or
                    # a tuple/list of types; test against them
                    #print 'testing %s=%s against type %s' % (prm,value,self._type_check[prm])
                    if isinstance(value, self._type_check[prm]):
                        can_set = True
                    else:
                        raise TypeError('\n\n%s=%s: %s has type %s, not %s' % \
                                        (prm, value, prm, self._type_check[prm],
                                         type(value)))

                elif callable(self._type_check[prm]):
                    can_set = self._type_check[prm](value)
                else:
                    raise TypeError('self._type_check["%s"] has an '\
                                    'illegal value %s' % \
                                    (prm, self._type_check[prm]))
            else:
                can_set = True
        else:
            message('%s is not registered in\n%s' % (prm, d))
        if can_set:
            d[prm] = value
            message('%s=%s is assigned' % (prm, value))
            return True
        return False


    def _update(self):
        """Check data consistency and make updates."""
        # to be implemented in subclasses
        pass

    def get(self, **kwargs):
        return [self._solver_prm[prm] \
                for prm in kwargs if prm in self._solver_prm]

    def properties(self, global_namespace):
        """Make properties out of local dictionaries."""
        for ds in self._prm_dict_names():
            d = eval('self.' + ds)
            for prm in d: # or for prm in self.__dict__[ds]
                # properties cannot have whitespace:
                prm = prm.replace(' ', '_')
                cmd = '%s.%s = property(fget='\
                      'lambda self: self.%s["%s"], %s)' % \
                      (self.__class__.__name__, prm, ds, prm,
                       ' doc="read-only property"')
                print cmd
                exec(cmd, global_namespace, locals())

    def dicts2namespace(self, namespace, dicts, overwrite=True):
        """
        Make namespace variables out of dict items.
        That is, for all dicts, insert all (key,value) pairs in
        the namespace dict.
        namespace is a dictionary, dicts is a list of dictionaries.
        """
        # can be tuned in subclasses

        # allow dicts to be a single dictionary:
        if not isinstance(dicts, (list,tuple)):
            dicts = [dicts]

        for d in dicts:
            if overwrite:
                namespace.update(d)
            else:
                for key in d:
                    if key in namespace and not overwrite:
                        print 'cannot overwrite %s' % key
                    else:
                        namespace[key] = d[key]

    def dicts2namespace2(self, namespace, dicts):
        """As dicts2namespace2, but use exec."""
        # can be tuned in subclasses

        # allow dicts to be a single dictionary:
        if not isinstance(dicts, (list,tuple)):
            dicts = [dicts]

        for d in dicts:
            for key in d:
                exec('%s=%s' % (key,repr(d[key])), globals(), namespace)

    def namespace2dicts(self, namespace, dicts):
        """
        Update dicts from variables in a namespace.
        That is, for all keys in namespace, insert (key,value) pair
        in the dict in dicts that has the same key registered.
        namespace is a dictionary, dicts is a list of dictionaries.
        """
        # allow dicts to be a single dictionary:
        if not isinstance(dicts, (list,tuple)):
            dicts = [dicts]

        keys = []    # all keys in namespace that are keys in dicts
        for key in namespace:
            for d in dicts:
                if key in d:
                    d[key] = namespace[key]  # update value
                    keys.append(key)         # mark for delete
        # clean up what we made in self.dicts2namespace:
        for key in keys:
            del namespace[key]

    def dicts2variables(self, dicts):
        """
        Make Python code string that defines local variables from
        all parameters in dicts (list of dictionaries of parameters).
        For example, if dicts[1] has a key n with value 1.0, the
        statement 'n=1.0' will be included in the returned string.
        The calling code will typically exec this returned string
        to make local variables (short hands) from parameters stored
        in dictionaries. (Note that such local variables are read-only,
        changing their values will not be reflected in the dictionaries!).
        """
        # allow dicts to be a single dictionary:
        if not isinstance(dicts, (list,tuple)):
            dicts = [dicts]

        s = ''
        for d in dicts:
            for name in d:
                s += '%s = %s\n' % (name, d[name])
        return s

    def variables2dicts(self, dicts, **variables):
        """
        Insert the name=value keyword arguments in variables into
        the dictionaries in dicts (list of dictionaries).
        This is the inverse of the dicts2variables function.

        Usage:
        exec self.dicts2variables(self.numerical_prm)
        # work with read-only n, dt, tstop
        ...
        # update (in case n, dt, tstop was changed):
        self.variables2dicts(self.numerical_prm, n=n, dt=dt, tstop=tstop)
        """
        for name in variables:
            for d in dicts:
                if name in d:
                    d[name] = variables[name]


# initial tests are found in src/py/examples/classdicts.py
