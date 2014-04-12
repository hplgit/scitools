"""
Import a set of modules. If modules are missing,
one can get these as a comma-separated string, or
one can raise exceptions.

See test block for demo of how this module can be used.
"""

def missing(*module_names):
    """
    Check if modules can be imported.
    Return a string containing the missing modules.
    """
    missing_modules = []
    for module in module_names:
        try:
            exec("import " + module)
        except:
            missing_modules.append(module)
    s = ", ".join(missing_modules)
    return s


def exception(msg, *module_names):
    """
    Raise an ImportError exception if modules
    are missing. Print the names of the missing modules.
    """
    s = missing(*module_names)
    if s:
        raise ImportError("%s missing the module(s) %s" % (msg,s))

def message(module, critical=1, msg=None):
    """
    Import a module and write a message if it is missing.
    critical=0 means that the module is not critical
    (programs may work without). critical=1 means that the
    module must be installed.
    msg is an optional description of the module.
    """
    try:
        exec("import "+ module)
        print "You have the Python", module, "module installed..."
        success = True
    except:
        print "*** The", module, "Python module is not available..."
        success = False
        if msg: print "    (%s)" % msg
        if not critical:
            print "       ....but this is not critical"
            success = False
    return success

# Pmw.Blt.Graph requires a special treatment:
def PmwBlt(verbose=0):
    try:
        # check if we manage to create a Blt graph:
        import Pmw;  s = Pmw.Blt.Graph
        if verbose:
            print "You have the Python Pmw.Blt.Graph widget available..."
        return True
    except:
        if verbose:
            print "*** Python is not correctly linked with BLT (no Pmw.Blt.Graph widget)"
        return False


if __name__ == '__main__':
    # Suppose we have a class SomeClass requiring the modules
    # A, B, and C. The following code segment shows how you can
    # import SomeClass silently if one or more of the modules A, B, or
    # C are missing, and then get the error message of a missing
    # module when you create an instance of the class

    try:
        import A, B, C
    except:
        pass

    class SomeClass:
        def __init__(self, *args):
            import modulecheck
            modulecheck.exception("SomeClass:", "A", "B", "C")

            # if we come here, no exception from modulecheck.exception
            # was raised so we can continue with the constructor statements,
            # e.g.
            a = 1
            b = 2

    # this should raise an exeption! (as the modules A, B, and C are missing)
    try:
        a = SomeClass()
    except:
        import sys
        print "Test worked; ", "\n", sys.exc_type, "\n", sys.exc_value

    # this should work fine:
    if exception("just testing...", "os"):  print "bug!"
