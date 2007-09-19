#!/usr/bin/env python
"""If the word 'with', which is a reserved keyword from python version 2.6,
is used in python2.5 code then a warning will be printed to sys.stderr
when the code is bytecompiled.

In this example we look at capturing the warning messages
"""
import __future__
import StringIO 
import sys
assert sys.version[:3] == '2.5'
    
# Force Error
statement = 'with=3'
try:
    c = compile(statement, '/dev/null', 'exec',
                __future__.with_statement.compiler_flag)
except SyntaxError:
    print "Success: '%s' did not compile" %statement
else: 
    raise Exception, "Statement: '%s' should not have been compiled" %statement

# Setup error redirection
std_err = sys.stderr
tmp_err = StringIO.StringIO()

def redirect_err():
    sys.stderr = tmp_err

def return_err():
    sys.stderr = std_err

# Compile with error redirection
statement1 = 'with=3'
statement2 = 'print "with>>", with'
print '>>>', statement1
print '>>>', statement2

# Test compilation of code using the reserved keyword with
# Redirection standard error under compilation to prevent warning
redirect_err()
try:
    c = compile(statement1, '/dev/null', 'single')
finally:
    return_err()

# No warning here
exec c

redirect_err()
try:
    # This one will give a warning
    exec statement2     
finally:
    return_err()
print "Here is the redirected error stream:\n",  tmp_err.getvalue()


# 'with'-example
print "Testing the use of the 'with'-statement"
c = compile(r"""'''In this example we test the use of the 'with'-statement'''

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
    
exec c

print "\nIt appears the with_statement worked."
print "Here is the redirected error stream:\n",  err_.getvalue()
