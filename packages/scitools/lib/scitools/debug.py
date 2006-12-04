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
import os, sys, string

__all__ = ['watch', 'trace', 'dump', 'debugregex']

if 'PYDEBUG' in os.environ:
    DEBUG = int(os.environ['PYDEBUG'])
else:
    # import user?
    DEBUG = 1

if not __debug__:  # python -O
    DEBUG = 0      # turn off debugging
    
import traceback
import errorcheck

def watch(variable, output_medium=sys.stdout):
    """
    Print out the name, type, and value of a variable and
    where in a program this output was requested.
    Used to monitor variables during debugging.
    As an example, watch(myprm) may lead to this output::

      File "myscript.py", line 56, in myfunction
        myprm, type "int" = 3

    Taken from the online Python Cookbook::

      http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52314/index_txt
      
    (original code written by Olivier Dagenais)
    """
    if not DEBUG:
        return
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
    prm["value"]       = repr(variable)
    prm["method_name"]  = stack[2]
    prm["line_number"] = stack[1]
    prm["filename"]    = stack[0]
    outstr = 'watch: file "%(filename)s", line %(line_number)d, '\
             'in %(method_name)s\n  %(variable_name)s, '\
             'type "%(variable_type)s" = %(value)s\n\n'
    output_medium.write(outstr % prm)


def trace(message='', output_medium=sys.stdout):
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
  """
    if not DEBUG:
        return
    stack = traceback.extract_stack()[-2:][0]
    prm = {}
    prm["method_name"] = stack[2]
    prm["line_number"] = stack[1]
    prm["filename"]    = stack[0]
    prm["message"]     = message
    outstr = 'trace: file "%(filename)s", line %(line_number)d, '\
             'in %(method_name)s: %(message)s\n\n'
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
                s = a + '=' + str(getattr(obj,a))
                if s.find(' method ') != -1 or \
                   s.find('function ') != -1 or \
                   s.find('method-wrapper ') != -1 or \
                   s.find('ufunc ') != -1:
                    methods.append(a) # skip function addresses
                else:
                    s += '  (' + errorcheck.get_type(getattr(obj,a)) + ')'
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

