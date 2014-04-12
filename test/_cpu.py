#!/usr/bin/env python
"""Test scitools profiler by calling two functions that take some time."""

import os, sys
N = 10000  # big number

def f1():
    for i in range(N):
        # do something
        os.path.isfile(sys.argv[0])

def f2():
    for i in range(N+10):
        # do something
        os.path.isdir(os.pardir)

for i in range(4):
    f1()
f2()

