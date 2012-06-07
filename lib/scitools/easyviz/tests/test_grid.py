"""Test functions for grid command."""

from easyviztest import *


class test_grid_basic(EasyvizTestCase):
    def check_grid_on(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        grid('on')
        title("plot(..);grid('on')")
        n()
        
    def check_grid_on_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,grid='on')
        title("plot(..,grid='on')")
        n()
        
    def check_grid_off(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        grid('on')
        grid('off')
        title("plot(..);grid('on');grid('off')")
        n()
        
    def check_grid_toggle_on(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        grid()
        title("plot(..);grid() (toggle on)")
        n()

    def check_grid_toggle_off(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        grid()
        grid()
        title("plot(..);grid();grid() (toggle off)")
        n()

    def check_grid_on_specify_axis(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        grid(gca(),'on')
        title("plot(..);grid(gca(),'on')")
        n()

    def check_grid_toggle_on_specify_axis(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        grid(gca())
        title("plot(..);grid(gca()) (toggle on)")
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_grid_basic,'check_'))
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
