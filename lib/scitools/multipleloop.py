#!/usr/bin/env python
"""
This module provides a tool for handling computer experiments with
of a set of input parameters, where each input parameter
is varied in a prescribed fashion.

In short, the parameters are held in a dictionary where the keys are
the names of the parameters and the values are the numerical, string
or other values of the parameters.  The value can take on multiple
values: e.g., an integer parameter 'a' can have values -1, 1 and
10. Similarly, a string parameter 'method' can have values 'Newton'
and 'Bisection'. The module will generate all combination of all
parameters and values, which in the mentioned example will be
(-1, 'Newton'), (1, 'Newton'), (10, 'Newton'), (-1, 'Bisection'),
(1, 'Bisection'), and (10, 'Bisection'). Particular combination
of values can easily be removed.

The usage and implementation of the module are documented in the
book "Python Scripting for Computational Science" (H. P. Langtangen,
Springer, 2009), Chapter 12.1.


Simple use of basic functionality in the module are shown below.
See the book for explanations and more comprehensive examples.

>>> from scitools.multipleloop import *
>>>
>>> # parameter names and multiple values,
>>> # using the special multipleloop syntax:
>>> p = {'A': '1 & 2 & 5', 'B': 'hello & world'}
>>>
>>> # turn multiple values syntax like 1 & 2 & 5 into list of values
>>> input2values(p['A'])
[1, 2, 5]
>>>
>>> prm_values = [(name, input2values(p[name])) for name in p]
>>> import pprint
>>> pprint.pprint(prm_values)
[('A', [1, 2, 5]), ('B', ['hello', 'world'])]
>>>
>>> # main function:
>>> all, names, varied = combine(prm_values)
>>>
>>> # all[i] holds all parameter values in experiment no i,
>>> # names holds the parameter names, and varied holds the
>>> # parameter names that are actually varied (not fixed values)
>>> print names
['A', 'B']
>>> print varied
['A', 'B']
>>> pprint.pprint(all)
[[1, 'hello'],
 [2, 'hello'],
 [5, 'hello'],
 [1, 'world'],
 [2, 'world'],
 [5, 'world']]
>>>
>>> e = 1
>>> for experiment in all:
...     print 'Experiment %4d:' % e,
...     for name, value in zip(names, experiment):
...         print '%s: %s' % (name, value),
...     print # newline
...     e += 1  # experiment counter
...
Experiment    1: A: 1 B: hello
Experiment    2: A: 2 B: hello
Experiment    3: A: 5 B: hello
Experiment    4: A: 1 B: world
Experiment    5: A: 2 B: world
Experiment    6: A: 5 B: world
>>>
>>> # turn parameter names and values into command-line options
>>> # (useful for running a program that takes parameter names prefixed
>>> # by - or -- as command-line options):
>>> cmd = options(all, names, prefix='-')
>>> for c in cmd:
...     print c
...     #commands.getstatusoutput(programname + ' ' + c)
...
-A True -B 'hello'
-A True -B 'hello'
-A True -B 'hello'
-A True -B 'world'
-A True -B 'world'
-A True -B 'world'
>>>
>>> print 'all combinations: %d' % len(all)
all combinations: 6
>>>
>>> # compute pairs:
>>> all = pairs(prm_values)
>>> print 'all pairs: %d' % len(all); pprint.pprint(all)
all pairs: 6
[[1, 'hello'],
 [2, 'hello'],
 [5, 'hello'],
 [5, 'world'],
 [2, 'world'],
 [1, 'world']]
>>>
>>> # alternative class interface:
>>> experiments = MultipleLoop(option_prefix='-')
>>> for name in p:
...     experiments.register_parameter(name, p[name])
...
>>> experiments.combine()  # compute all combinations
>>>
>>> # remove all experiments corresponding to a condition:
>>> nremoved = experiments.remove('A == 5')
>>>
>>> # look at the attributes of this instance:
>>> pprint.pprint(experiments.all)
[[1, 'hello'], [2, 'hello'], [1, 'world'], [2, 'world']]
>>> print experiments.names
['A', 'B']
>>> print experiments.varied
['A', 'B']
>>> print experiments.options
["-A True -B 'hello'", "-A True -B 'hello'", "-A True -B 'world'",
 "-A True -B 'world'"]
>>> pprint.pprint(experiments.prm_values)
[('A', [1, 2, 5]), ('B', ['hello', 'world'])]

Here is another example with more experiments::

>>> p = {'b': '1 & 0 & 0.5', 'func': 'y & siny', 'w': '[1:1.3,0.1]'}
>>> prm_values = [(name, input2values(p[name])) for name in p]
>>> import pprint
>>> pprint.pprint(prm_values)
[('b', [1, 0, 0.5]),
 ('w', [1, 1.1000000000000001, 1.2000000000000002]),
 ('func', ['y', 'siny'])]
>>>
>>> # main function:
>>> all, names, varied = combine(prm_values)
>>>
>>> print names
['b', 'w', 'func']
>>> print varied
['b', 'w', 'func']
>>> pprint.pprint(all)
[[1, 1, 'y'],
 [0, 1, 'y'],
 [0.5, 1, 'y'],
 [1, 1.1000000000000001, 'y'],
 [0, 1.1000000000000001, 'y'],
 [0.5, 1.1000000000000001, 'y'],
 [1, 1.2000000000000002, 'y'],
 [0, 1.2000000000000002, 'y'],
 [0.5, 1.2000000000000002, 'y'],
 [1, 1, 'siny'],
 [0, 1, 'siny'],
 [0.5, 1, 'siny'],
 [1, 1.1000000000000001, 'siny'],
 [0, 1.1000000000000001, 'siny'],
 [0.5, 1.1000000000000001, 'siny'],
 [1, 1.2000000000000002, 'siny'],
 [0, 1.2000000000000002, 'siny'],
 [0.5, 1.2000000000000002, 'siny']]
>>>
>>> print 'all combinations: %d' % len(all)
all combinations: 18
>>>
>>> # compute pairs:
>>> all = pairs(prm_values)
>>> print 'all pairs: %d' % len(all); pprint.pprint(all)
all pairs: 9
[[1, 1, 'y'],
 [0, 1.1000000000000001, 'y'],
 [0.5, 1.2000000000000002, 'y'],
 [0.5, 1.1000000000000001, 'siny'],
 [0, 1, 'siny'],
 [1, 1.2000000000000002, 'siny'],
 [1, 1.1000000000000001, 'siny'],
 [0, 1.2000000000000002, 'siny'],
 [0.5, 1, 'siny']]
>>>
>>> # alternative class interface:
>>> experiments = MultipleLoop(option_prefix='-')
>>> for name in p:
...     experiments.register_parameter(name, p[name])
...
>>> experiments.combine()
>>>
>>> # remove all experiments corresponding to a condition:
>>> nremoved = experiments.remove('b == 1')
>>>
>>> # look at the attributes of this instance:
>>> pprint.pprint(experiments.all)
[[0, 1, 'y'],
 [0.5, 1, 'y'],
 [0, 1.1000000000000001, 'y'],
 [0.5, 1.1000000000000001, 'y'],
 [0, 1.2000000000000002, 'y'],
 [0.5, 1.2000000000000002, 'y'],
 [0, 1, 'siny'],
 [0.5, 1, 'siny'],
 [0, 1.1000000000000001, 'siny'],
 [0.5, 1.1000000000000001, 'siny'],
 [0, 1.2000000000000002, 'siny'],
 [0.5, 1.2000000000000002, 'siny']]

>>> # explore the response of varied parameters:
>>> # function = []  # list of (response, (param1, param2, ...))
>>> # the (param1, param2, ...) list equals the varied parameter values
>>> # in each experiment (varied_parameters in the loop below)
>>>
>>> for cmlargs, parameters, varied_parameters in experiments:
...     args = ', '.join(['%s=%s' % (name,value) for name, value in zip(experiments.names, parameters)])
...     print
...     print 'can call some function:'
...     print 'response = myfunc(%s)' % args
...     print 'or run some program with options:'
...     print 'prompt> myprog ', cmlargs
...     print 'and extract a response from the program output'
...     print 'function.append((response, varied_parameters))'
...
can call some function:
response = myfunc(b=0, w=1, func=y)
or run some program with options:
prompt> myprog  -b False -w True -func 'y'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0.5, w=1, func=y)
or run some program with options:
prompt> myprog  -b 0.5 -w True -func 'y'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0, w=1.1, func=y)
or run some program with options:
prompt> myprog  -b False -w 1.1000000000000001 -func 'y'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0.5, w=1.1, func=y)
or run some program with options:
prompt> myprog  -b 0.5 -w 1.1000000000000001 -func 'y'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0, w=1.2, func=y)
or run some program with options:
prompt> myprog  -b False -w 1.2000000000000002 -func 'y'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0.5, w=1.2, func=y)
or run some program with options:
prompt> myprog  -b 0.5 -w 1.2000000000000002 -func 'y'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0, w=1, func=siny)
or run some program with options:
prompt> myprog  -b False -w True -func 'siny'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0.5, w=1, func=siny)
or run some program with options:
prompt> myprog  -b 0.5 -w True -func 'siny'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0, w=1.1, func=siny)
or run some program with options:
prompt> myprog  -b False -w 1.1000000000000001 -func 'siny'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0.5, w=1.1, func=siny)
or run some program with options:
prompt> myprog  -b 0.5 -w 1.1000000000000001 -func 'siny'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0, w=1.2, func=siny)
or run some program with options:
prompt> myprog  -b False -w 1.2000000000000002 -func 'siny'
and extract a response from the program output
function.append((response, varied_parameters))
can call some function:
response = myfunc(b=0.5, w=1.2, func=siny)
or run some program with options:
prompt> myprog  -b 0.5 -w 1.2000000000000002 -func 'siny'
and extract a response from the program output
function.append((response, varied_parameters))
"""
# see also http://pyslice.sourceforge.net/HomePage

import re, operator
from scitools.misc import str2obj

def input2values(s):
    """
    Translate a string s with multiple loop syntax into
    a list of single values (for the corresponding parameter).

    Multiple loop syntax:
    '-1 & -3.4 & 20 & 70 & [0:10,1.3] & [0:10] & 11.76'

    That is, & is delimiter between different values, [0:10,1.3]
    generates a loop from 0 up to and including 10 with steps 1.3,
    [0:10] generates the integers 1,2,...,10.

    Interactive session::

    >>> input2values('-1 & -3.4 & 20 & 70 & [0:10,1.3] & [0:10] & 11.76')
    [-1, -3.3999999999999999, 20, 70, 0, 1.3, 2.6000000000000001,
     3.9000000000000004, 5.2000000000000002, 6.5, 7.7999999999999998,
     9.0999999999999996, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11.76]

    >>> p = {'w': '[0.7:1.3,0.1]', 'b': '1 & 0.3 & 0', 'func': 'y & siny'}
    >>> print input2values(p['w'])
    [0.69999999999999996, 0.79999999999999993, 0.89999999999999991,
     0.99999999999999989, 1.0999999999999999, 1.2, 1.3]
    >>> print input2values(p['b'])
    [1, 0.29999999999999999, 0]
    >>> print input2values(p['func'])
    ['y', 'siny']
    >>> prm_values = [(name, input2values(p[name])) for name in p]
    >>> prm_values
    [('b', [1, 0.29999999999999999, 0]),
     ('func', ['y', 'siny']),
     ('w', [0.69999999999999996, 0.79999999999999993, 0.89999999999999991,
            0.99999999999999989, 1.0999999999999999, 1.2, 1.3])]

    """
    if not isinstance(s, str):
        return s

    items = s.split('&')

    values = []
    for i in items:
        i = i.strip()  # white space has no meaning
        # is i a loop?
        m = re.search(r'\[(.+):([^,]+),?(.*)\]',i)
        if m:
            # the group are numbers, take eval to get right type
            start = eval(m.group(1))
            stop  = eval(m.group(2))
            try:
                incr = m.group(3).strip()
                incr_op = operator.add
                if incr[0] == '*':
                    incr_op = operator.mul
                    incr = incr[1:]
                elif incr[0] == '+' or incr[0] == '-':
                    incr = incr[1:]
                incr = eval(incr)
            except:
                incr = 1
            r = start
            while (r <= stop and start <= stop) or \
                  (r >= stop and start >= stop):
                values.append(r)
                r = incr_op(r, incr)
        else:
            # just an ordinary item, convert i to right type:
            values.append(str2obj(i))
    # return list only if there are more than one item:
    if len(values) == 1:
        return values[0]
    else:
        return values

def _outer(a, b):
    """
    Return the outer product/combination of two lists.
    a is a multi- or one-dimensional list,
    b is a one-dimensional list, tuple, NumPy array or scalar (new parameter)
    Return:  outer combination 'all'.

    The function is to be called repeatedly::

        all = _outer(all, p)
    """
    all = []
    if not isinstance(a, list):
        raise TypeError('a must be a list')
    if isinstance(b, (float,int,complex,str)):  b = [b]  # scalar?

    if len(a) == 0:
        # first call:
        for j in b:
            all.append([j])
    else:
        for j in b:
            for i in a:
                if not isinstance(i, list):
                    raise TypeError('a must be list of list')
                # note: i refers to a list; i.append(j) changes
                # the underlying list (in a), which is not what
                # we want, we need a copy, extend the copy, and
                # add to all
                k = i + [j]  # extend previous prms with new one
                all.append(k)
    return all

def combine(prm_values):
    """
    Compute the combination of all parameter values in the prm_values
    (nested) list. Main function in this module.

    param prm_values: nested list ``(parameter_name, list_of_parameter_values)``
    or dictionary ``prm_values[parameter_name] = list_of_parameter_values``.
    return: (all, names, varied) where

      - all contains all combinations (experiments)
        all[i] is the list of individual parameter values in
        experiment no i

      - names contains a list of all parameter names

      - varied holds a list of parameter names that are varied
        (i.e. where there is more than one value of the parameter,
        the rest of the parameters have fixed values)


    Code example:

    >>> dx = array([1.0/2**k for k in range(2,5)])
    >>> dt = 3*dx;  dt = dt[:-1]
    >>> p = {'dx': dx, 'dt': dt}
    >>> p
    {'dt': [ 0.75 , 0.375,], 'dx': [ 0.25  , 0.125 , 0.0625,]}
    >>> all, names, varied = combine(p)
    >>> all
    [[0.75, 0.25], [0.375, 0.25], [0.75, 0.125], [0.375, 0.125],
     [0.75, 0.0625], [0.375, 0.0625]]
    """
    if isinstance(prm_values, dict):
        # turn dict into list [(name,values),(name,values),...]:
        prm_values = [(name, prm_values[name]) \
                      for name in prm_values]
    all = []
    varied = []
    for name, values in prm_values:
        all = _outer(all, values)
        if isinstance(values, list) and len(values) > 1:
            varied.append(name)
    names = [name for name, values in prm_values]
    return all, names, varied

def pairs(prm_values, n=2):
    """
    Compute parameter combinations of the parameter values in
    prm_values (list of (name, values) pairs, where values is
    a list of values). Not all combinations are computed (as
    in function combine), but only a subset so that all pairs
    of all parameter values appear once. This gives a substantially
    smaller set of combinations than when all parameter values
    are combined with all others. n=2 correspond to pairs,
    n=3 to triplets, and so on.

    The computations are performed with the aid of the AllPairs
    package developed and maintained by MetaCommunications Engineering,
    see http://pypi.python.org/pypi/AllPairs/2.0.1.
    Only input and output are adapted here to the
    syntax of the multipleloop module.
    """
    try:
        import metacomm.combinatorics.all_pairs2
        all_pairs = metacomm.combinatorics.all_pairs2.all_pairs2
    except ImportError:
        print """
The pairs functions in the scitools.multipleloop module requires
the AllPairs package by MetaCommunications Engineering.
Go to see http://pypi.python.org/pypi/AllPairs/2.0.1, download
and install the package (python setup.py install).
"""
        sys.exit(1)

    list_of_values = [values for name, values in prm_values]
    combinations = all_pairs(list_of_values, n=n)
    # the output of AllPairs is a generator:
    all = [v for v in combinations]
    return all


def options(all, names, prefix='--'):
    """
    Return a list of command-line options and their values.

    =======     ===========================================================
    all         all[i] holds a list of parameter values in experiment no i
    names       names[i] holds name of parameter no. i
    prefix      an option equals prefix + name (prefix is '--' or '-')
    return      cmd[i] holds -name value pairs of all parameters in
                experiment no. i
    =======     ===========================================================
    """
    cmd = []
    for experiment in all:
        cmd.append(' '.join([prefix + name + ' ' + repr(str2obj(value)) \
                   for name, value in zip(names, experiment)]))
    return cmd

def _varied_parameters(parameters, varied, names):
    """
    Help function for identifying parameters that are varied (or fixed)
    in experiments. (Not used anymore in this module.)

    ==========  ===========================================================
    names       names of parameters.
    parameters  values of parameters.
    varied      subset of names (the parameters that are varied elsewhere).
    return      a list of the indices in parameters corresponding varied.
    ==========  ===========================================================

    An example may help to show the idea. Assume we have three parametes
    named 'a', 'b', and 'c'. Their values are 1, 5, and 3, i.e.,
    'a' is 1, 'b' is 5, and 'c' is 3. In a loop elsewhere we assume
    that 'a' and 'c' are varied while 'b' is fixed. This function
    returns a list of the parameter values that correspond to varied
    parameters, i.e., [1,3] in this case, corresponding to the names
    'a' and 'c':

    >>> parameters = [1,5,3]
    >>> names = ['a','b','c']
    >>> varied = ['a','c']
    >>> varied_parameteres(parameters, varied, names)
    [1,3]
    """
    indices_varied = [names.index(i) for i in varied]
    varied_parameters = [parameters[i] for i in indices_varied]
    return varied_parameters

def remove(condition, all, names):
    """
    Remove experiments that fulfill a boolean condition.
    Example::

      all = remove('w < 1.0 and p = 1.2) or (q in (1,2,3) and f < 0.1', all, names)

    (names of the parametes must be used)
    """
    import copy
    for ex in copy.deepcopy(all):  # iterate over a copy of all!
        c = condition
        for n in names:  # replace names by actual values
            #print 'replace "%s" by "%s"' % (n, repr(ex[names.index(n)]))
            c = c.replace(n, repr(ex[names.index(n)]))
            # note the use of repr: strings must be quoted
            #print 'remove ',remove
        if eval(c):  # if condition
            all.remove(ex)
    return all  # modified list


def _demo(p, one_name, one_value):
    code = """
from scitools.multipleloop import *

# parameter names and multiple values,
# using the special multipleloop syntax:
p = %s

# turn multiple values syntax like %s into list of values
input2values(p['%s'])

prm_values = [(name, input2values(p[name])) for name in p]
import pprint
pprint.pprint(prm_values)

# main function:
all, names, varied = combine(prm_values)

# all[i] holds all parameter values in experiment no i,
# names holds the parameter names, and varied holds the
# parameter names that are actually varied (not fixed values)
print names
print varied
pprint.pprint(all)

e = 1
for experiment in all:
    print 'Experiment %%4d:' %% e,
    for name, value in zip(names, experiment):
        print '%%s: %%s' %% (name, value),
    print # newline
    e += 1  # experiment counter


# turn parameter names and values into command-line options
# (useful for running a program that takes parameter names prefixed
# by - or -- as command-line options):
cmd = options(all, names, prefix='-')
for c in cmd:
    print c
    #commands.getstatusoutput(programname + ' ' + c)


print 'all combinations: %%d' %% len(all)

# compute pairs:
all = pairs(prm_values)
print 'all pairs: %%d' %% len(all); pprint.pprint(all)

# alternative class interface:
experiments = MultipleLoop(option_prefix='-')
for name in p:
    experiments.register_parameter(name, p[name])

experiments.combine()   # compute all combinations

# remove all experiments corresponding to a condition:
nremoved = experiments.remove('%s == %s')

# look at the attributes of this instance:
pprint.pprint(experiments.all)
print experiments.names
print experiments.varied
print experiments.options
pprint.pprint(experiments.prm_values)

# explore the response of varied parameters:
# function = []  # list of (response, (param1, param2, ...))
# the (param1, param2, ...) list equals the varied parameter values
# in each experiment (varied_parameters in the loop below)

for cmlargs, parameters, varied_parameters in experiments:
    args = ', '.join(['%%s=%%s' %% (name,value) for name, value in zip(experiments.names, parameters)])
    print
    print 'can call some function:'
    print 'response = myfunc(%%s)' %% args
    print 'or run some program with options:'
    print 'prompt> myprog ', cmlargs
    print 'and extract a response from the program output'
    print 'function.append((response, varied_parameters))'

""" % (p, p[one_name], one_name, one_name, one_value)
    f = open('_tmp.py', 'w')
    f.write(code)
    f.close()
    import commands
    failure, output = commands.getstatusoutput('scitools file2interactive _tmp.py')
    if not failure:
        return output
    else:
        print '_demo: could not run command'
    print output

def _doc_str_example():
    p = {'A': '1 & 2 & 5', 'B': 'hello & world'}
    text1 = _demo(p, 'A', '5')
    p = {'w': '[1:1.3,0.1]', 'b': '1 & 0 & 0.5', 'func': 'y & siny'}
    text2 = _demo(p, 'b', '1')
    return text1 + text2


def _dump(all, names, varied):
    e = 1
    for experiment in all:
        print 'Experiment %4d:' % e,
        for name, value in zip(names, experiment):
            print '%s:' % name, value,
        print # newline
        e += 1  # experiment counter

def _test1():
    s1 = ' -3.4 & [0:4,1.2] & [1:4,*1.5] & [0.5:6E-2,  *0.5]'
    #s2 = "method1 &  abc  & 'adjusted method1' "
    s2 = 0.22
    s3 = 's3'
    l1 = input2values(s1)
    l2 = input2values(s2)
    l3 = input2values(s3)
    p = [('prm1', l3), ('prm2', l2), ('prm3', l1)]
    all, names, varied = combine(p)
    _dump(all, names, varied)
    p = {'w': [0.7, 1.3, 0.1], 'b': [1, 0], 'func': ['y', 'siny']}
    all, names, varied = combine(p)
    print '\n\n\n'
    _dump(all, names, varied)
    print options(all, names, prefix='-')

def _test2():
    p = {'w': '[0.7:1.3,0.1]', 'b': '1 & 0.3 & 0', 'func': 'y & siny'}
    print input2values(p['w'])
    print input2values(p['b'])
    print input2values(p['func'])
    prm_values = [(name, input2values(p[name])) \
                  for name in p]
    print 'prm_values:', prm_values
    all, names, varied = combine(prm_values)
    print 'all:', all

    # rule out b=0 when w>1
    all_restricted = [];
    bi = names.index('b'); wi = names.index('w')
    for e in all:
        if e[bi] == 0 and e[wi] > 1:
            pass # rule out
        else:
            all_restricted.append(e)  # del would be dangerous!
    # b->damping, w->omega:
    names2 = names[:]
    names2[names.index('b')] = 'damping'
    names2[names.index('w')] = 'omega'
    print options(all, names, prefix='--')
    conditions = (('b',operator.eq,0), ('w',operator.gt,1))
    def rule_out(all, conditions):
        all_restricted = []
        for e in all:
            for name, op, r in conditions:
                pass

class MultipleLoop:
    """
    High-level, simplified interface to the functionality in
    the multipleloop module.

    Typical application::

      p = {'name1': 'multiple values', 'name2': 'values', ...}
      experiments = scitools.multipleloop.MultipleLoop(option_prefix='-')
      for name in p:
          experiments.register_parameter(name, p[name])
      experiments.combine()  # find all combinations of all parameters
      for cmlargs, parameters, varied_parameters in experiments:
          <run experiment: some program + cmlargs>
          <extract response, varied_parameters holds the values of
           the parameters that were varied in this experiment (the
           independent variables mapping onto the response)

    Attributes (m is some MultipleLoop object):

    =============  =================================================
    m.names        names of all parameters
    m.varied       names of parameters with multiple values
                   (the rest of the parameters have constant values
                   throughout the experiments)
    m.options      list of strings of all command-line arguments
                   (-name value), one for each experiment
    m.all          list of all experiments
    m.prm_values   list of (name, valuelist) tuples
    =============  =================================================

    Example:

    >>> p = {'b': '1 & 0 & 0.5', 'func': 'y & siny', 'w': '[1:1.3,0.1]'}
    >>> experiments = MultipleLoop(option_prefix='-')
    >>> for name in p:
    ...     experiments.register_parameter(name, p[name])
    ...
    >>> experiments.combine()
    >>>
    >>> # remove all experiments corresponding to a condition:
    >>> nremoved = experiments.remove('b == 1')
    >>>
    >>> # look at the attributes of this instance:
    >>> pprint.pprint(experiments.all)
    [[0, 1, 'y'],
     [0.5, 1, 'y'],
     [0, 1.1000000000000001, 'y'],
     [0.5, 1.1000000000000001, 'y'],
     [0, 1.2000000000000002, 'y'],
     [0.5, 1.2000000000000002, 'y'],
     [0, 1, 'siny'],
     [0.5, 1, 'siny'],
     [0, 1.1000000000000001, 'siny'],
     [0.5, 1.1000000000000001, 'siny'],
     [0, 1.2000000000000002, 'siny'],
     [0.5, 1.2000000000000002, 'siny']]
    """
    def __init__(self, option_prefix='--'):
        """
        option_prefix is the prefix that will be used in command-line
        options (typically '-' or '--').
        """
        self.option_prefix = option_prefix
        self.prm_values = []
        self.combined = False

    def register_parameter(self, name, values):
        """Register a parameter and its value or multiple values."""
        self.prm_values.append((name, input2values(values)))

    add = register_parameter

    def combine(self):
        """Compute all combinations of all parameters."""
        self.all, self.names, self.varied = combine(self.prm_values)
        self.indices_varied = [self.names.index(i) for i in self.varied]
        self.options = options(self.all, self.names, prefix=self.option_prefix)
        self.combined = True

    def remove(self, condition):
        """
        Remove experiments that fulfill a boolean condition.
        Example::

          e.remove('w < 1.0 and p = 1.2) or (q in (1,2,3) and f < 0.1')

        (names of the parametes must be used)
        """
        self.combine() # compute all combinations
        nex_orig = len(self.all)
        self.all = remove(condition, self.all, self.names)
        # self.options depend on self.all, which might be alterend:
        self.options = options(self.all, self.names, prefix=self.option_prefix)
        # return no of removed experiments:
        return nex_orig-len(self.all)

    def __iter__(self):
        if not self.combined: self.combine()
        self.counter = 0
        return self

    def next(self):
        if self.counter > len(self.options)-1:
            raise StopIteration()
        self.cmlargs = self.options[self.counter]
        self.parameters = self.all[self.counter]
        self.varied_parameters = \
             [self.parameters[i] for i in self.indices_varied]
        self.counter += 1
        return self.cmlargs, self.parameters, self.varied_parameters

class ReportHTML:
    def __init__(self, filename):
        self.filename = filename
        f = open(self.filename, 'w') # new file
        f.write("""<html><body>\n""")
        f.close()
        self._experiment_section_counter = 0

    def dump(self, text):
        f = open(self.filename, 'a')
        f.write(text)
        f.close()

    def experiment_section(self, parameters, names, varied):
        """
        Start new H1 section in the HTML document.
        parameters is a list of the values of all parameters
        in an experiment, names holds the names of all
        parameters, and varied holds the names of the
        parameters that are actually varied.
        The three input lists are computed by functions in
        this module (or the MultipleLoops class).
        """
        self._experiment_section_counter += 1
        t = """
<h1>Experiment no. %d</h1>
Varied parameters:
<ul>
""" % self._experiment_section_counter
        for n in varied:
            i = names.index(n)
            t += """\n<li> %s: %s""" % (n, parameters[i])
        t += """
</ul>
Fixed parameters:
"""
        for n in names:
            if n not in varied:  # not treated above?
                i = names.index(n)
                t += """%s=%s, """ % (n, parameters[i])
        t = t[:-2]  # strip the last ', '
        self.dump(t)

        def __del__(self):
            self.dump("""\n</body></html>\n""")

if __name__ == '__main__':
    print _doc_str_example()
    #_test1()
    #_test2()


