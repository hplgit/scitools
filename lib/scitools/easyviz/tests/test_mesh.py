"""Test functions for mesh command."""

# Same as surf command. See test_surf.py for more tests.

from easyviztest import *


class test_mesh_basic(EasyvizTestCase):
    def check_mesh_default(self):
        x,y,xv,yv,values = self.get_2D_data()
        mesh(xv,yv,values)
        title("mesh(xv,yv,values)")
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_mesh_basic,'check_'))
    total_suite = unittest.TestSuite(suites)
    return total_suite

def test(level=10):
    all_tests = test_suite()
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()
    raw_input("press enter to exit")
