"""Test functions for view command."""

from easyviztest import *


class test_view(EasyvizTestCase):
    def check_view_default_2D_view(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        view(2)
        title('surf(..);view(2)')
        n()

    def check_view_default_2D_view_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values,view=2)
        title('surf(..,view=2)')
        n()
    
    def check_view_default_3D_view(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        view(3)
        title('surf(..);view(3)')
        n()
    
    def check_view_default_3D_view_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values,view=3)
        title('surf(..,view=3)')
        n()

    def check_view_azimuth_and_elevation(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        view(40,70)
        title('surf(..);view(40,70)')
        n()

    def check_view_azimuth_and_elevation_list(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        view([25,60])
        title('surf(..);view([25,60])')
        n()

    def check_view_azimuth_and_elevation_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values,view=(30,30))
        title('surf(..,view=(30,30))')
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_view,'check_'))
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
