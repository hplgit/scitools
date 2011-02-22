"""Test functions for x-, y-, and zlabel commands."""

from easyviztest import *


class test_xlabel_simple(EasyvizTestCase):
    def check_xlabel(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        xlabel('XLABEL')
        title("plot(..);xlabel('XLABEL')")
        n()

    def check_xlabel_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,xlabel='XLABEL')
        title("plot(..,xlabel='XLABEL')")
        n()


class test_ylabel_simple(EasyvizTestCase):
    def check_ylabel(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        ylabel('YLABEL')
        title("plot(..);ylabel('YLABEL')")
        n()

    def check_ylabel_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,ylabel='YLABEL')
        title("plot(..,ylabel='YLABEL')")
        n()


class test_zlabel_simple(EasyvizTestCase):
    def check_zlabel(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        zlabel('ZLABEL')
        title("surf(..);zlabel('ZLABEL')")
        n()

    def check_zlabel_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values,zlabel='ZLABEL')
        title("surf(..,zlabel='ZLABEL')")
        n()


class test_xylabels_combined(EasyvizTestCase):
    def check_xylabel(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        xlabel('XLABEL')
        ylabel('YLABEL')
        title("plot(..);xlabel('XLABEL');ylabel('YLABEL')")
        n()

    def check_xylabel_kwargs(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,xlabel='XLABEL',ylabel='YLABEL')
        title("plot(..,xlabel='XLABEL',ylabel='YLABEL')")
        n()


class test_xyzlabels_combined(EasyvizTestCase):
    def check_xyzlabel(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        xlabel('XLABEL')
        ylabel('YLABEL')
        zlabel('ZLABEL')
        title("surf(..);xlabel('XLABEL');ylabel(YLABEL');zlabel('ZLABEL')")
        n()

    def check_xyzlabel_kwargs(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values,xlabel='XLABEL',ylabel='YLABEL',zlabel='ZLABEL')
        title("surf(..,xlabel='XLABEL',ylabel='YLABEL',zlabel='ZLABEL')")
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_xlabel_simple,'check_'))
        suites.append(unittest.makeSuite(test_ylabel_simple,'check_'))
        suites.append(unittest.makeSuite(test_zlabel_simple,'check_'))
        suites.append(unittest.makeSuite(test_xylabels_combined,'check_'))
        suites.append(unittest.makeSuite(test_xyzlabels_combined,'check_'))
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
