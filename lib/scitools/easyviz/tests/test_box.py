"""Test functions for <template> command."""

from easyviztest import *


class test_box_basic(EasyvizTestCase):
    def check_box_on(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        box('on')
        title("surf(..);box('on')")
        n()

    def check_box_on_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values,box='on')
        title("surf(..,box='on')")
        n()

    def check_box_off(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        box('on')
        box('off')
        title("surf(..);box('on');box('off')")
        n()

    def check_box_toggle_on(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        box()
        title("surf(..);box()")
        n()

    def check_box_toggle_off(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        box()
        box()
        title("surf(..);box();box()")
        n()

    def check_box_on_specify_axis(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        box(gca(),'on')
        title("surf(..);box(gca(),'on')")
        n()

    def check_box_toggle_on_specify_axis(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        box(gca())
        title("surf(..);box(gca())")
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_box_basic,'check_'))
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
