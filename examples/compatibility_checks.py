from numpy import linspace
from scitools.errorcheck import *
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

"""
ValueError file "compatibility_checks.py", line 5, main program
q1 has length 5, which is not compatible with assumed length 2
ValueError file "compatibility_checks.py", line 9, main program
q1 has size (5,), which is not compatible with assumed size (2, 2)
ValueError file "compatibility_checks.py", line 17, main program
q1 has size (5,), which is not compatible with size (6,) of q2
TypeError file "compatibility_checks.py", line 21, main program
q2 is of type ndarray, while we expected <type 'list'>
TypeError q1 is of wrong type (ndarray).
"""
