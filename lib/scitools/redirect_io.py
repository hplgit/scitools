#!/usr/bin/env python
r"""

Example usage:
--------------

Redirect stderr using the 'with'-statement:

>>> from redirect_io import *
>>> with hidden_stderr():
...     print >> sys.stderr, 'Divide By Cucumber Error'
>>>

Redirect stderr to stout:

>>> with hidden_stderr(sys.stdout):
...     print >> sys.stderr, 'Where am I ?'
Where am I ?
>>>

Optinal usage without 'with'-statement:

>>> _redirect_err()
>>> try:
...     print >> sys.stderr, " +++ Divide by Cucumber Error, "\
...                          "Please ReInstall Universe And Reboot +++"
... finally:
...     _return_err()
>>>

Fetch previous error messages:

>>> print _tmp_err.getvalue()
Divide By Cucumber Error
 +++ Divide by Cucumber Error, Please ReInstall Universe And Reboot +++
<BLANKLINE>
>>>
"""
__author__ = 'Rolv Erlend Bredesen <rolv@simula.no>'
__all__ = ['sys', '_tmp_err', 'hidden_stderr', '_redirect_err', '_return_err']

import __future__
import StringIO
import sys
from contextlib import contextmanager

if float(sys.version[:3]) < 2.5:
    raise ImportError("This module requires version >= 2.5 of python")

_std_err = sys.stderr
_tmp_err =  StringIO.StringIO() # stream for hidden stderr
_tmp_err.__exit__ = _tmp_err.flush # Add __exit__ method

@contextmanager # 'with' requires __enter__ and __exit__
def hidden_stderr(stream=_tmp_err):
    sys.stderr = stream
    try:
        yield None
    finally:
        sys.stderr = _std_err

# For error stream with python version < 2.5
def _redirect_err():
    sys.stderr = _tmp_err

def _return_err():
    sys.stderr = _std_err


def _test_with_statement():
    """
    If the word 'with', which is a reserved keyword from python version 2.6,
    is used in python2.5 code then a warning will be printed to sys.stderr
    when the code is bytecompiled.

    In this example we look at capturing the warning messages
    """
    assert 'with_statement' not in globals()
    assert sys.version[:3] == '2.5'
    # Force Error
    statement = 'with=3'
    try:
        c = compile(statement, '/dev/null', 'exec',
                    __future__.with_statement.compiler_flag)
    except SyntaxError:
        print "Success: '%s' did not compile" %statement
    else:
        raise Exception("Statement: '%s' should not have been compiled" \
                        % statement)

    # Setup error redirection
    std_err = sys.stderr
    tmp_err = StringIO.StringIO()
    if float(sys.version[:3]) < 2.5:
        raise ImportError, "This module requires version 2.5 of python"

    # Compile with error redirection
    statement1 = 'with=3'
    statement2 = 'print "with>>", with'
    print '>>>', statement1
    print '>>>', statement2

    # Test compilation of code using the reserved keyword with
    # Redirection standard error under compilation to prevent warning
    _redirect_err()
    try:
        c = compile(statement1, '/dev/null', 'single')
    finally:
        _return_err()

    # No warning here
    exec(c, {}, locals())

    _redirect_err()
    try:
        # This one will give a warning
        exec(statement2)
    finally:
        _return_err()
    print "Here is the redirected error stream:\n",  tmp_err.getvalue()

    # 'with'-example
    print "Testing the use of the 'with'-statement"
    c = compile(
        r"""'''In this example we test the use of the 'with'-statement'''

#from __future__ import with_statement # using proper compile flag instead
from contextlib import contextmanager  # 'with' requires __enter__ and __exit__

err_ = StringIO.StringIO()

@contextmanager
def stderr_redirected(stream):
    err = sys.stderr
    sys.stderr = stream
    try:
        yield None
    finally:
        sys.stderr = err

statement = 'with_=3' # we have imported the with_statement

with stderr_redirected(err_):
    print >> sys.stderr, "Can you see me?"
    c_ = compile(statement, '/dev/null', 'single', 0, 0)


""", '/dev/null', 'exec', __future__.with_statement.compiler_flag)
    exec(c)

    print "\nIt appears the with_statement worked."
    print "Here is the redirected error stream:\n",  err_.getvalue()


if __name__ == '__main__':
    import doctest
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite())
    runner = unittest.TextTestRunner(sys.stdout, verbosity=1)
    runner.run(suite)

