"""
Functions for checking compatibility of data structures,
right type of data etc.
"""

from numpytools import NumPyArray
import types

__all__ = ['right_length', 'right_size1', 'right_size2',
           'get_type', 'right_type', 'wrong_type']


def right_length(a, a_name, length):
    """
    Check that len(a) == length.

    @param a: any variable for which len(a) is meaningful.
    @param a_name: the name of a.
    @param length: the expected length of a (integer).
    """
    if len(a) != length:
        raise ValueError, \
        '%s has length %s, which is not compatible with assumed length %s' \
                      % (a_name, len(a), length)
    else:
        return True

def right_size1(a, a_name, shape):
    """
    Check that a has correct shape.

    @param a: NumPy array.
    @param a_name: the name of variable a.
    @param shape: the expected shape of a. @type shape: int or tuple
    """
    if not isinstance(a, NumPyArray):
        raise TypeError, '%s is %s and not a NumPy array' % \
              (a_name, type(a))
    if isinstance(shape, int):
        shape = (shape,)  # wrap in tuple
    if a.shape != shape:
        raise ValueError, \
        '%s has size %s, which is not compatible with assumed size %s' \
                      % (a_name, 'x'.join(a.shape), 'x'.join(shape))
    else:
        return True

def right_size2(a1, a1_name, a2, a2_name):
    """
    Check that a1 and a2 have equal shapes.

    @param a1,a2: NumPy arrays.
    @param a1_name, a2_name: names of a1 and a2 (strings).
    """
    if isinstance(a1, NumPyArray) and isinstances(a2, NumPyArray):
        pass # ok
    else:
        raise TypeError, '%s is %s and %s is %s - both must be NumPy arrays' \
              % (a1_name, type(a1), a2_name, type(a2))
    if a1.shape != a2.shape:
        raise ValueError, \
        '%s has size %s, which is not compatible with size %s of %s' \
                      % (a1_name, 'x'.join(a1.shape),
                         'x'.join(a2_shape), a2_name)
    else:
        return True


def get_type(a):
    """
    Extract a's type. First, try to extract a's class name. If this
    is unsuccessful, return type(a).
    """
    try:
        # try to get a's class name (if possible)
        tp = a.__class__.__name__
        if tp == 'type':  # class object?
            # add some explanation (can get output "a is of type type")
            tp += ' (i.e. a class object)'
    except:
        # rely on the type (would be less informative if a is instance)
        tp = str(type(a))
    return tp

    
def right_type(a, a_name, expected_types, a_can_be_class=False):
    """
    Check that variable a is of the type(s) specified by expected_types.

    @param a: variable to be checked.
    @type  a: any
    @param a_name: name of a.
    @type  a_name: string
    @param expected_types: class name(s) of the expected type(s).
    @type  expected_types: class name or list/tuple of class names
    @param a_can_be_class: True if a is a class object, False if a
    is an instance of a class.
    @type  a_can_be_class: bool
    @return: None. The function raises a TypeError exception if a
    is not of right type.
    """
    if not isinstance(expected_types, (list,tuple)):
        expected_types = [expected_types]  # wrap in list if just single type
    match = False
    for tp in expected_types:
        if a_can_be_class:
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
        tp = get_type(a)
        raise TypeError, '%s is of type %s, while we expected %s' % \
              (a_name, tp, ' or '.join([str(e) for e in expected_types]))
    else:
        return True
        

def wrong_type(a, a_name, comment=''):
    """
    Raise a TypeError exception expressing the type of variable a
    and that this type is wrong.

    @param a: any variable. @type a: any
    @param a_name: the name of a. @type a_name: string
    @param comment: optional comment to be added to the exception string.
    @type  comment: string
    @return: None, the function raises an exception.
    """
    tp = get_type(a)
    raise TypeError, '%s is of wrong type (%s). %s' % (a_name, tp, comment)


try:
    from scitools import SAFECODE
    if not SAFECODE:
        # define (efficient) empty check functions:
        for func in __all__:
            efficient_version = 'def %s(*args): return True' % func
            exec efficient_version
except ImportError:
    pass

