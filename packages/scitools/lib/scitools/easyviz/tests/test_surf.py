"""Test functions for surf command."""

from easyviztest import *


class test_surf_basic(EasyvizTestCase):
    def check_surf_default(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        title("surf(xv,yv,values)")
        n()

    def check_surf_no_grid_components(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(values)
        title("surf(values)")
        n()
        
    def check_surf_1D_grid_components(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(x,y,values)
        title("surf(x,y,values)")
        n()
        
    def check_surf_not_sparse_grid(self):
        x,y,xv,yv,values = self.get_2D_data(sparse=False)
        surf(xv,yv,values)
        title("surf(xv,yv,values) (xv and yv not sparse)")
        n()
        
    def check_surf_indexing_xy(self):
        x,y,xv,yv,values = self.get_2D_data(indexing='xy')
        surf(xv,yv,values,indexing='xy')
        title("surf(xv,yv,values,indexing='xy')")
        n()


class test_surf_rectangular_grid(EasyvizTestCase):
    def check_surf_rectangular_grid(self):
        x = linspace(-2,2,21)
        y = linspace(-3,3,13)
        xv, yv = ndgrid(x, y)
        values = peaks(xv,yv)
        surf(xv,yv,values)
        title("surf(xv,yv,values) (rectangular grid)")
        n()

    def check_surf_rectangular_grid_no_grid_components(self):
        x = linspace(-2,2,21)
        y = linspace(-3,3,13)
        xv, yv = ndgrid(x, y)
        values = peaks(xv, yv)
        surf(values)
        title("surf(values) (rectangular grid)")
        n()
       
    def check_surf_rectangular_grid2(self):
        x = linspace(-5,5,41)
        y = linspace(-2,2,9)
        xv, yv = ndgrid(x, y)
        values = peaks(xv, yv)
        surf(xv,yv,values)
        title("surf(xv,yv,values) (rectangular grid)")
        n()
       
    def check_surf_rectangular_grid2_no_grid_components(self):
        x = linspace(-5,5,41)
        y = linspace(-2,2,9)
        xv, yv = ndgrid(x, y)
        values = peaks(xv, yv)
        surf(xv,yv,values)
        title("surf(xv,yv,values) (rectangular grid)")
        n()
        
    def check_surf_rectangular_grid_indexing_xy(self):
        x = linspace(-2,2,21)
        y = linspace(-3,3,13)
        xv, yv = meshgrid(x, y, indexing='xy')
        values = peaks(xv, yv)
        surf(xv,yv,values,indexing='xy')
        title("surf(xv,yv,values,indexing='xy') (rectangular grid)")
        n()
        
    def check_surf_rectangular_grid2_indexing_xy(self):
        x = linspace(-5,5,41)
        y = linspace(-2,2,9)
        xv, yv = meshgrid(x, y, indexing='xy')
        values = peaks(xv, yv)
        surf(xv,yv,values,indexing='xy')
        title("surf(xv,yv,values,indexing='xy') (rectangular grid)")
        n()


## class test_surf_multiple_surfaces(EasyvizTestCase):
##     def check_surf_two_surfaces(self):
##         x,y,xv,yv,values = self.get_2D_data(sparse=False)
##         setp(show=False)
##         surf(xv,yv,xv*yv)
##         hold('on')
##         surf(xv,yv,xv**2+yv**2)
##         title("surf(xv,yv,xv*yv);hold('on');surf(xv,yv,xv**2+yv**2)")
##         hold('off')
##         setp(show=screenplot)
##         if screenplot:
##             show()
##         n()


class test_surf_cdata(EasyvizTestCase):
    def check_surf_with_cdata(self):
        x,y,xv,yv,values = self.get_2D_data(sparse=False)
        cdata = xv
        surf(xv,yv,values,cdata)
        title("cdata=xv;surf(xv,yv,values,cdata)")
        n()

    def check_surf_with_cdata2(self):
        x,y,xv,yv,values = self.get_2D_data(sparse=False)
        cdata = values
        values = xv
        surf(xv,yv,values,cdata)
        title("cdata=values;values=xv;surf(xv,yv,values,cdata)")
        n()


class test_surf_shading(EasyvizTestCase):
    def check_surf_shading_faceted(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        shading('faceted')
        title("surf(xv,yv,values);shading('faceted')")
        n()

    def check_surf_shading_faceted_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values,shading='faceted')
        title("surf(xv,yv,values,shading='faceted')")
        n()

    def check_surf_shading_flat(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        shading('flat')
        title("surf(xv,yv,values);shading('flat')")
        n()

    def check_surf_shading_flat_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values,shading='flat')
        title("surf(xv,yv,values,shading='flat')")
        n()
        
    def check_surf_shading_interp(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values)
        shading('interp')
        title("surf(xv,yv,values);shading('interp')")
        n()

    def check_surf_shading_interp_kwarg(self):
        x,y,xv,yv,values = self.get_2D_data()
        surf(xv,yv,values,shading='interp')
        title("surf(xv,yv,values,shading='interp')")
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_surf_basic,'check_'))
        suites.append(unittest.makeSuite(test_surf_rectangular_grid,'check_'))
        suites.append(unittest.makeSuite(test_surf_cdata,'check_'))
        suites.append(unittest.makeSuite(test_surf_shading,'check_'))
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
