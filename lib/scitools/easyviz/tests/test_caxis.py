"""Test functions for caxis command."""

from easyviztest import *


class test_caxis_basic(EasyvizTestCase):
    def check_caxis(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values,colorbar='on')
        caxis(-2,2)
        title("pcolor(..);caxis(-2,2)")
        n()

    def check_caxis_list(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values,colorbar='on')
        caxis([-5,5])
        title("pcolor(..);caxis([-5,5])")
        n()

    def check_caxis_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values,colorbar='on',caxis=[0,8])
        title("pcolor(..,caxis=[0,8])")
        n()

    def check_caxis_auto(self):
        x,y,xv,yv,values = self.get_2D_data()
        setp(show=False)
        pcolor(xv,yv,values,colorbar='on')
        caxis(-2,2)
        caxis('auto')
        title("pcolor(..);caxis(-2,2);caxis('auto')")
        setp(show=True)
        show()
        n()

    def check_caxis_manual(self):
        x,y,xv,yv,values = self.get_2D_data()
        setp(show=False)
        surf(xv,yv,xv**2+yv**2,colorbar='on')
        caxis('manual')
        hold('on')
        surf(xv,yv,xv+yv)
        title("surf(..);caxis('manual');hold('on');surf(..)")
        hold('off')
        setp(show=True)
        show()
        n()

    def check_caxis_list(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values,colorbar='on')
        caxis(gca(), [-8,1])
        title("pcolor(..);caxis(gca(), [-8,1])")
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_caxis_basic,'check_'))
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
