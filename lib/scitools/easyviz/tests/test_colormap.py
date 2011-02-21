"""Test functions for colormap command."""

from easyviztest import *


class test_colormap_basic(EasyvizTestCase):
    def check_colormap_default(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values)
        colormap('default')
        title("pcolor(..);colormap('default')")
        n()

    def check_colormap_default_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values,colormap='default')
        title("pcolor(..,colormap='default')")
        n()

    def check_colormap_jet(self):
        x,y,xv,yv,values = self.get_2D_data()
        pcolor(xv,yv,values)
        colormap(jet())
        title("pcolor(..);colormap(jet())")
        n()

##     def check_colormap_jet_string(self):
##         x,y,xv,yv,values = self.get_2D_data()
##         pcolor(xv,yv,values)
##         colormap('jet')
##         title("colormap('jet')")
##         n()


class test_colormap_jet(EasyvizTestCase):
    def check_colormap_jet_4_colors(self):
        x,y,xv,yv,values = self.get_2D_data(n=31)
        pcolor(xv,yv,values)
        colormap(jet(4))
        title("pcolor(..);colormap(jet(4))")
        n()
        
    def check_colormap_jet_16_colors(self):
        x,y,xv,yv,values = self.get_2D_data(n=31)
        pcolor(xv,yv,values)
        colormap(jet(16))
        title("pcolor(..);colormap(jet(16))")
        n()

    def check_colormap_jet_128_colors(self):
        x,y,xv,yv,values = self.get_2D_data(n=31)
        pcolor(xv,yv,values)
        colormap(jet(128))
        title("pcolor(..);colormap(jet(128))")
        n()


class test_colormap_hsv(EasyvizTestCase):
    def check_colormap_hsv_4_colors(self):
        x,y,xv,yv,values = self.get_2D_data(n=31)
        pcolor(xv,yv,values,colormap=hsv(4))
        title("pcolor(..,colormap=hsv(4))")
        n()

    def check_colormap_hsv_16_colors(self):
        x,y,xv,yv,values = self.get_2D_data(n=31)
        pcolor(xv,yv,values,colormap=hsv(16))
        title("pcolor(..,colormap=hsv(16))")
        n()

    def check_colormap_hsv_128_colors(self):
        x,y,xv,yv,values = self.get_2D_data(n=31)
        pcolor(xv,yv,values,colormap=hsv(128))
        title("pcolor(..,colormap=hsv(128))")
        n()

class test_colormap_hot(EasyvizTestCase):
    def check_colormap_hot_4_colors(self):
        x,y,xv,yv,values = self.get_2D_data(n=31)
        pcolor(xv,yv,values,colormap=hot(4))
        title("pcolor(..,colormap=hot(4))")
        n()

    def check_colormap_hot_16_colors(self):
        x,y,xv,yv,values = self.get_2D_data(n=31)
        pcolor(xv,yv,values,colormap=hot(16))
        title("pcolor(..,colormap=hot(16))")
        n()

    def check_colormap_hot_128_colors(self):
        x,y,xv,yv,values = self.get_2D_data(n=31)
        pcolor(xv,yv,values,colormap=hot(128))
        title("pcolor(..,colormap=hot(128))")
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_colormap_basic,'check_'))
        suites.append(unittest.makeSuite(test_colormap_jet,'check_'))
        suites.append(unittest.makeSuite(test_colormap_hsv,'check_'))
        suites.append(unittest.makeSuite(test_colormap_hot,'check_'))
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
