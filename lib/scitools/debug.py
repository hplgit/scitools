"""
Debugging tools.

  - watch(var): print out the name, type, and value of a variable and
    where in a program this output was requested (used to monitor variables).

  - trace(message): print a message and where in the program this
    message was requested (used to trace the execution).

  - dump(obj, hide_underscore=True): print a dump of the object obj
    (attributes, methods, etc.).

  - debugregex(pattern, string): print match, groups, etc. when the
    regular expression pattern is applied to string.

watch and trace prints information only if the module variable
DEBUG has a true value. DEBUG can be initialized from an environment
variable PYDEBUG, otherwise it is set to 1 by default. Other
modules can monitor their debugging by setting debug.DEBUG = 0
or debug.DEBUG = 1 (note that a single such setting has a "global" effect;
it turns off debugging everywhere).
"""
import os, sys, string, re, inspect

__all__ = ['watch', 'trace', 'dump', 'debugregex']

if 'PYDEBUG' in os.environ:
    DEBUG = int(os.environ['PYDEBUG'])
else:
    # import user?
    DEBUG = 1

if not __debug__:  # python -O
    DEBUG = 0      # turn off debugging

import traceback
from . import errorcheck

def watch(variable, output_medium=sys.stdout):
    """
    Print out the name, type, and value of a variable and
    where in a program this output was requested.
    Used to monitor variables during debugging.
    As an example, watch(myprm) may lead to this output::

      myprm <int> in ./myscript.py(56): myfunction
        = 3

    The variable is returned to the caller, thus it can be used
    inside expressions:
      myobj.setCallback(lambda self: self.setstate(watch(self.mystate)))
    or
      dosomething(*watch((arg1, arg2, arg3)))

    (This function is a modified version of a function taken
    from the online Python Cookbook::

      http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52314/index_txt

    The original code was written by Olivier Dagenais).
    """
    if not DEBUG:
        return variable
    stack = traceback.extract_stack()[-2:][0]
    actual_call = stack[3]
    if actual_call is None:
        actual_call = "watch([unknown])"
    left = string.find(actual_call, '(' )
    right = string.rfind(actual_call, ')')
    prm = {}
    # variable name is extracted from actual_call:
    # everything between '(' and ')'
    prm["variable_name"] = string.strip(actual_call[left+1:right])
    prm["variable_type"] = errorcheck.get_type(variable)  # str(type(variable))[7:-2]
    if isinstance(variable, str):
        print_variable = str(variable)
    else:
        print_variable = repr(variable)
    prm["value"]       = print_variable
    prm["method_name"]  = stack[2]
    prm["line_number"] = stack[1]
    prm["filename"]    = stack[0]
    prm["shortfile"]   = shorten_path(stack[0])
    if prm["method_name"] == '?':
        prm["method_name"] = 'main'
        #outstr = 'watch: %(shortfile)s(%(line_number)d): '\
        #     '%(method_name)s\n  %(variable_name)s '\
        #     '<%(variable_type)s> = %(value)s\n'
    outstr = '%(variable_name)s <%(variable_type)s>'\
             ' in %(shortfile)s(%(line_number)d): %(method_name)s\n'\
             '  = %(value)s\n'
    output_medium.write(outstr % prm)
    return variable

def shorten_path(path, abb_len=20):
    """Shorten a path to relative (./rel_path) or abbreviated (...rest_of_path)
    form. abb_len=0 for no abbreviation of the second form."""
    cwd = os.environ.get('PWD') or os.getcwd()
    if path.startswith(cwd):
        return "."+path[len(cwd):]
    else:
        return path[-abb_len:]


def trace(message='', output_medium=sys.stdout, frameno=-2):
    """
    Print a message and where in the program this
    message was requested (as in the function watch).
    Used to trace the program flow during debugging.

    If called from constructors, and sometimes also other class
    methods with "generic" names, it may be smart to let the message
    be the classname::

      class A:
        def __init__(self):
          debug.trace(self.__class__.__name__)

        def write(self):
          debug.trace(self.__class__.__name__)

    With frameno=-2 the place where this debug.trace function is called is
    printed, while smaller values gives printout of previous calls on the call
    stack. In the previous example, we could look further back to say:

      class A:
        def __init__(self):
            debug.trace('Instantiation of '+self.__class__.__name__, frameno=-3)

        def write(self):
            debug.trace('A.write() call', frameno=-3)

    Setting frameno=-4 may also be useful in some particular cases, for example
    in a baseclass __init__ which is usually overridden. But there is danger
    that we then look too far back in the call stack.

    (This function is a modified version of one taken from the
     Python Cookbook, see the watch function.)
  """
    if not DEBUG:
        return
    stack = traceback.extract_stack()[frameno:][0]
    prm = {}
    prm["method_name"] = stack[2]
    prm["line_number"] = stack[1]
    prm["filename"]    = stack[0]
    prm["shortfile"]   = shorten_path(stack[0])
    prm["message"]     = message
    outstr = '%(shortfile)s(%(line_number)d) %(method_name)s: %(message)s\n'
    output_medium.write(outstr % prm)

def dump(obj, hide_nonpublic=True):
    """
    Inspect an object obj by the dir function.
    This dump function first prints the repr(obj) of the object,
    then all data attributes and their values are
    listed, and finally a line listing all functions/methods
    is printed.
    """
    print '\n', '*'*60, '\n'
    try:  # dump class name if it exists
        print 'object of class', obj.__class__.__name__
    except:
        pass
    try:
        print 'object with name %s' % obj.__name__
    except:
        pass
    methods = [];  attrs = []
    for a in dir(obj):
        if a.startswith('_') and hide_nonpublic:
            pass
        else:
            try:
                attr = getattr(obj, a)
                s = a + '=' + str(attr)
                if s.find(' method ') != -1 or \
                   s.find('function ') != -1 or \
                   s.find('method-wrapper ') != -1 or \
                   s.find('ufunc ') != -1:
                    try:
                        # add argument list (args, varargs, kwargs, defaults)
                        a = '%-15s%s' % (a, inspect.formatargspec(inspect.getargspec(attr)))
                    except:
                        pass
                    methods.append(a) # skip function addresses
                else:
                    s += '  (' + errorcheck.get_type(attr) + ')'
                    attrs.append(s)  # variable=value
            except Exception, msg:
                pass
    print '******** data attributes:\n', '\n'.join(attrs)
    print '\n******** methods:\n', '\n'.join(methods)
    print '*'*60, '\n\n\n',


def debugregex(pattern, string):
    "debugging of regular expressions: write the match and the groups"
    s = "does '" + pattern + "' match '" + string + "'?\n"
    match = re.search(pattern, string)
    if match:
        s += string[:match.start()] + '[' + \
             string[match.start():match.end()] + \
             ']' + string[match.end():]
        if len(match.groups()) > 0:
            for i in range(len(match.groups())):
                s += '\ngroup %d: [%s]' % (i+1,match.groups()[i])
    else:
        s += 'No match'
    return s

def setprofile(include='', exclude=None, output=sys.stdout):
    """
    Print a message on method call/return/exception.

    @param include: A regular expression for output filtering. The regular
    expression is applied to the output string, which is on the format 'event
    filename(line): classname.methodname'.

    For example, setprofile(os.getcwd()) prints only methods that are defined
    in python files in this directory and subdirectories. setprofile('^c_')
    prints only C invocations. And so on.

    @param exclude: Another regular expression.
    """
    include = re.compile(include)
    exclude = exclude and re.compile(exclude)
    def prof(frame, event, arg):
        meth = frame.f_code.co_name
        try:
            cls = frame.f_locals['self']
            if isinstance(cls, object):
                cls = cls.__class__
            meth = '.'.join([cls.__name__, meth])
        except KeyError:
            pass
        s = '%s: %s(%s): %s\n' % (event, frame.f_code.co_filename,
                                  frame.f_lineno, meth)
        if include.search(s) and not (exclude and exclude.search(s)):
            output.write(s)
    sys.setprofile(prof)
