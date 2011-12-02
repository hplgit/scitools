"""Test functions for colorbar command."""

from easyviztest import *


class test_colorbar_basic(EasyvizTestCase):
    def check_colorbar_default(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values)
        colorbar()
        title("pcolor(..);colorbar()")
        n()

    def check_colorbar_off(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values)
        colorbar()
        colorbar('off')
        title("pcolor(..);colorbar();colorbar('off')")
        n()

    def check_colorbar_default_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values,colorbar='on')
        title("pcolor(..,colorbar='on')")
        n()

    def check_colorbar_cbtitle(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values,colorbar='on',cbtitle='colorbar title')
        title("pcolor(..,colorbar='on',cbtitle='colorbar title')")
        n()

    def check_colorbar_axes_specified(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values)
        colorbar(gca())
        title("pcolor(..);colorbar(gca())")
        n()

    def check_colorbar_off_axes_specified(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values)
        colorbar(gca())
        colorbar(gca(),'off')
        title("pcolor(..);colorbar(gca());colorbar(gca(),'off')")
        n()


class test_colorbar_location(EasyvizTestCase):
    def check_colorbar_location(self):
        x,y,xv,yv,values = self.get_2D_data()
        cbar = getp(gca(), 'colorbar')
        for location in cbar._locations:
            pcolor(xv,yv,values)
            colorbar(location)
            title("pcolor(..);colorbar('%s')" % location)
            n()
            
    def check_colorbar_location_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        cbar = getp(gca(), 'colorbar')
        for location in cbar._locations:
            pcolor(xv,yv,values,colorbar='on',cblocation='%s' % location)
            title("pcolor(..,colorbar='on',cblocation='%s')" % location)
            n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_colorbar_basic,'check_'))
        suites.append(unittest.makeSuite(test_colorbar_location,'check_'))
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
