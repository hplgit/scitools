"""
Functions for checking compatibility of data structures,
right type of data etc.

Example: given a program "check.py"::

    from numpy import linspace
    q1 = linspace(0, 1, 5)
    try:
        right_length(q1, 2)
    except Exception, e:
        print e.__class__.__name__, e
    try:
        right_size1(q1, (2,2))
    except Exception, e:
        print e.__class__.__name__, e
    try:    
        q2 = linspace(0, 1, 6)
    except Exception, e:
        print e.__class__.__name__, e
    try:
        right_size2(q1, q2)
    except Exception, e:
        print e.__class__.__name__, e
    try:
        right_type(q2, list)
    except Exception, e:
        print e.__class__.__name__, e
    try:
        wrong_type(q1)
    except Exception, e:
        print e.__class__.__name__, e

Here is the output (each call triggers the exception)::

    ValueError file "check.py", line 5, main program
    q1 has length 5, which is not compatible with assumed length 2
    ValueError file "check.py", line 9, main program
    q1 has size (5,), which is not compatible with assumed size (2, 2)
    ValueError file "check.py", line 17, main program
    q1 has size (5,), which is not compatible with size (6,) of q2
    TypeError file "check.py", line 21, main program
    q2 is of type ndarray, while we expected <type 'list'>
    TypeError q1 is of wrong type (ndarray).

"""

import types, re, inspect

__all__ = ['right_length', 'right_size1', 'right_size2',
           'get_type', 'right_type', 'wrong_type']

def get_argname_in_call(call_name, arg_no):
    """
    Utility function for extracting the name of an argument in a function
    call.

    Caveat: the function call is obtained as a string, and the arguments
    obtained by splitting that string with respect to comma.
    This can easily lead to errors, e.g., 'myfunc(a, (list,tuple), b)'
    will lead to the arguments 'a', '(list', 'tuple)', and 'b'.
    'b' is not obtained as argument 3.
    
    @param call_name: name of the function in the call.
    @param arg_no: argument number to extract (1, 2, ...).
    @return: name of the argument and a string ("where") describing
    the original call's filename, line number and function.
    """
    
    stack = inspect.stack()
    #import pprint; pprint.pprint(stack)
    #print 'frameinfo:\n', inspect.getframeinfo(stack[3][0])

    # call from some function:
    filename, line_number, func_name, func_call = stack[2][1:5]
    if func_name == '?':
        func_name = 'main program'
    if func_call is None:
        return 'variable', \
               '(info on variable names are missing since the call was made from an interpreter)'

    func_call = func_call[0]
    where = 'file "%s", line %d, %s' % (filename, line_number, func_name)
    pattern = r'%s\s*\((.*)\)' % call_name
    m = re.search(pattern, func_call)
    if m:
        args = m.group(1)
        # assume comma is separator (will not work if one of the args
        # is a tuple, dict or list explicitly listed with its value
        # in the call...)
        argname = args.split(',')[arg_no-1].strip()
        return argname, where
    else:
        raise ValueError, 'pattern="%s" does not match "%s"' % \
              (pattern, func_call)


def right_length(a, length):
    """
    Check that len(a) == length.

    @param a: any variable for which len(a) is meaningful.
    @param length: the expected length of a (integer).
    """
    if len(a) != length:
        a_name, where = get_argname_in_call('right_length', 1)
        raise ValueError, \
        '%s\n%s has length %s, which is not compatible with '\
        'assumed length %s' % (where, a_name, len(a), length)
    else:
        return True

def right_size1(a, shape):
    """
    Check that a has correct shape.

    @param a: NumPy array.
    @param shape: the expected shape of a. @type shape: int or tuple
    """
    if not hasattr(a, 'shape'):
        raise TypeError, '%s is %s and not a NumPy array' % \
              (a_name, type(a))
    if isinstance(shape, int):
        shape = (shape,)  # wrap in tuple
    if a.shape != shape:
        a_name, where = get_argname_in_call('right_size1', 1)
        raise ValueError, \
        '%s\n%s has size %s, which is not compatible with assumed size %s' \
                      % (where, a_name, a.shape, shape)
    else:
        return True

def right_size2(a1, a2):
    """
    Check that a1 and a2 have equal shapes.

    @param a1,a2: NumPy arrays.
    """
    if hasattr(a1, 'shape') and hasattr(a2, 'shape'):
        pass # ok, a1 and a2 are NumPy arrays
    else:
        raise TypeError, '%s is %s and %s is %s - both must be NumPy arrays' \
              % (a1_name, type(a1), a2_name, type(a2))
    if a1.shape != a2.shape:
        a1_name, where = get_argname_in_call('right_size2', 1)
        a2_name, where = get_argname_in_call('right_size2', 2)
        raise ValueError, \
        '%s\n%s has size %s, which is not compatible with size %s of %s' \
          % (where, a1_name, a1.shape, a2.shape, a2_name)
    else:
        return True


def get_type(a):
    """
    Extract a's type. First, try to extract a's class name. If this
    is unsuccessful, return type(a).

    The session below illustrates differences between type(a) nad
    get_type(a) for standard classes, instances of user-defined classes,
    and class objects (new style and classic classes).

    >>> # standard built-in types:
    >>> c = [1,2,3]
    >>> d = 'my string'
    >>> type(c)
    <type 'list'>
    >>> get_type(c)
    'list'
    >>> type(d)
    <type 'str'>
    >>> get_type(d)
    'str'
    >>> 
    >>> # user-defined classes and instances:
    >>> class A:          # classic class
    ...     pass
    ... 
    >>> class B(object):  # new style class
    ...     pass
    ... 
    >>> a = A()
    >>> type(a)
    <type 'instance'>
    >>> get_type(a)
    'A'
    >>> 
    >>> b = B()
    >>> type(b)
    <class '__main__.B'>
    >>> get_type(b)
    'B'
    >>>
    >>> # class objects A and B:
    >>> type(A)
    <type 'classobj'>
    >>> get_type(A)
    'classobj (i.e. a class object)'
    >>> type(B)
    <type 'type'>
    >>> get_type(B)
    'type (i.e. a class object)'
    >>> 
    
    """
    try:
        # try to get a's class name (if possible)
        tp = a.__class__.__name__
        if tp == 'type':  # new style class object?
            # add some explanation (can get output "a is of type type")
            tp += ' (i.e. a class object)'
    except:
        # rely on the type (would be less informative if a is instance)
        tp = str(type(a))
        # if a is a classic class object, tp is "<type 'classobj'>"
        # which we translate into something more readable:
        if tp == "<type 'classobj'>":
            tp = "classobj (i.e. a class object)"
    return tp


def right_type(a, expected_types):
    """
    Check that variable a is of the type(s) specified by expected_types.

    @param a: variable to be checked.
    @type  a: any
    @param expected_types: class name(s) of the expected type(s).
    @type  expected_types: class name or list/tuple of class names
    @return: None. The function raises a TypeError exception if a
    is not of right type.
    """
    if not isinstance(expected_types, (list,tuple)):
        expected_types = [expected_types]  # wrap in list if just single type
    t = get_type(a)
    if 'a class object' in t:
        a_is_class = True
    else:
        a_is_class = False
    match = False
    for tp in expected_types:
        if a_is_class:
            # a is a class object
            if type(a) == types.ClassType:
                try:
                    if issubclass(a, tp):
                        match = True
                        break
                except:
                    pass
        else:
            try:
                if isinstance(a, tp):
                    match = True
                    break
            except TypeError:
                if isinstance(a, type(tp)):
                    match = True
                    break
    if not match:
        a_name, where = get_argname_in_call('right_type', 1)
        raise TypeError, '%s\n%s is of type %s, while we expected %s' % \
          (where, a_name, t, ' or '.join([str(e) for e in expected_types]))
    else:
        return True
        

def wrong_type(a, comment=''):
    """
    Raise a TypeError exception expressing the type of variable a
    and that this type is wrong.

    @param a: any variable. @type a: any
    @param comment: optional comment to be added to the exception string.
    @type  comment: string
    @return: None, the function raises an exception.
    """
    tp = get_type(a)
    a_name, where = get_argname_in_call('wrong_type', 1)
    raise TypeError, '%s is of wrong type (%s). %s' % (a_name, tp, comment)


_SAFECODE = True
try:
    from globaldata import SAFECODE as _SAFECODE
except ImportError:
    pass
if not _SAFECODE:
    # define (efficient) empty check functions:
    for func in __all__:
        efficient_version = 'def %s(*args): return True' % func
        exec efficient_version

