"""
Run all tests in the current directory.
"""

import os, sys
import unittest

def test_suite(level=1):
    suite = unittest.TestSuite()
    files = os.listdir(os.curdir)
    tests = []
    for f in files:
        if f.startswith('test_') and f.endswith('.py'):
            tests.append(f[:-3])

    for test in tests:
        m = __import__(test)
        if hasattr(m, 'test_suite'):
            suite.addTest(m.test_suite())
    return suite

def test(level=10):
    all_tests = test_suite()
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == '__main__':
    test()
    raw_input("press enter to exit")
