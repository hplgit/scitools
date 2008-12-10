import numpy as N
import operator, os

#---------------------------------------------------------------------
# ----- helper functions for detecting right object type ------------

# test that a variable v is a function or None:
_func_type = lambda v: v is None or callable(v)

# test that a variable v is a function, None, or source code of a
# function in a file:
_func_or_file_type = lambda v: v is None or callable(v) or \
                     (isinstance(v, basestring) and os.path.isdir(v))

# test that a variable v is array/list-like, a number, or None:
_array_or_number_type = lambda v: v is None or \
      isinstance(v, (list, tuple, N.ndarray, float, complex, int))


# test that a variable v is a function or the string 'built-in'
# (used for linear or nonlinear solvers that can be part of the
# ODE routine or supplied as a user-defined algorithm):
_user_alg_type = lambda v: callable(v) or v == 'built-in'
#---------------------------------------------------------------------

def indent(text, indent_size=4):
    """
    Indent each line in the string text by indent_size spaces.
    """
    # indent each line properly:
    ind = ' '*indent_size
    lines = text.splitlines()
    for i in range(len(lines)):
        lines[i] = ind + lines[i]
    text = '\n'.join(lines)
    return text

def _doc_format(*classes_or_list_of_prm_dicts):
    """
    Combine all dictionaries _solver_prm, solver_prm_help, etc. in
    the arguments, and print the information in a nice
    way suitable for a doc string. That is, this function is used to
    update a doc string of a solver with all available parameters
    registered in _solver_prm etc. of a class and its base class.

    The classes_or_list_of_prm_dicts argument may hold either class
    objects (typical the base class of a solver) or a list of dictionaries
    (typical the local _solver_prm etc.).

    Example on call::
    
      __doc__ += _doc_format(ImplicitSolver,
                             [_solver_prm, _solver_prm_help, _solver_prm_type,
                              _solver_out, _solver_out_help])
    """
    all_prm = {}
    all_prm_help = {}
    all_prm_type = {}
    all_out = {}
    all_out_help = {}
    for c in classes_or_list_of_prm_dicts:
        if isinstance(c, type):
            all_prm.update(getattr(c, '_solver_prm'))
            all_prm_help.update(getattr(c, '_solver_prm_help'))
            all_prm_type.update(getattr(c, '_solver_prm_type'))
            all_out.update(getattr(c, '_solver_out'))
            all_out_help.update(getattr(c, '_solver_out_help'))
        elif isinstance(c, (list,type)):
            # list of dictionaries _solver_prm etc.
            try:
                _solver_prm, _solver_prm_help, _solver_prm_type, \
                             _solver_out, _solver_out_help = c
            except ValueError:
                raise TypeError, 'not right arguments to _doc_format'
            
            all_prm.update(_solver_prm)
            all_prm_help.update(_solver_prm_help)
            all_prm_type.update(_solver_prm_type)
            all_out.update(_solver_out)
            all_out_help.update(_solver_out_help)
            
    if len(all_prm) > 0:
        #s = '\n\nValid Parameter Names for the "set" Method (or Attributes)\n'
        #s +=    '----------------------------------------------------------\n'
        s = '\n\nValid parameter names for the "set" method (or attributes):\n'
    else:
        s = ''
    names = all_prm.keys()
    names.sort()
    for name in names:
        help = all_prm_help[name]
        # left strip all help lines and indent with list (required by Epydoc):
        help = '\n'.join(['    '+line.lstrip() for line in help.split('\n')])
        s += '\n  - %s: (default %s)\n%s\n' % \
             (name, all_prm[name], help)
    if len(all_out) > 0:
        #s += '\nOutput Parameters from Solver\n'
        #s +=   '-----------------------------\n'
        s += '\nOutput parameters from solver:\n'
    names = all_out.keys()
    names.sort()
    for name in names:
        help = all_out_help[name]
        # left strip all help lines and indent with list (required by Epydoc):
        help = '\n'.join(['    '+line.lstrip() for line in help.split('\n')])
        s += '\n  - %s: %s\n' % (name, help)

    # indent each line to be aligned with the rest of the doc string:
    return indent(s, 4)




def _constant_step_size_prm(_solver_prm, _solver_prm_help, _solver_prm_type):
    """
    In-place update of dictionaries with typical parameters for a
    constant step-size solver.
    """
    _solver_prm.update({'dt': 1.0,})
    _solver_prm_type.update({'dt': float,})
    _solver_prm_help.update({'dt' : 'constant/initial time step size',})
    

