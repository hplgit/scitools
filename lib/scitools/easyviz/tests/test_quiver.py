"""Test functions for quiver command."""

from easyviztest import *


class test_quiver_basic(EasyvizTestCase):
    def check_quiver_default(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv)
        title("quiver(xv,yv,uv,vv)")
        n()

    def check_quiver_not_sparse_grid(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data(sparse=False)
        quiver(xv,yv,uv,vv)
        title("quiver(xv,yv,uv,vv) (xv and yv not sparse)")
        n()

    def check_quiver_1D_grid_components(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(x,y,uv,vv)
        title("quiver(x,y,uv,vv)")
        n()
    
    def check_quiver_no_grid_components(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(uv,vv)
        title("quiver(uv,vv)")
        n()

    def check_quiver_1D_vector_components(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(x,y,x,y**2)
        title("quiver(x,y,x,y**2)")
        n()
    

class test_quiver_scaling(EasyvizTestCase):
    def check_quiver_no_automatic_scaling(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv,0)
        title("quiver(xv,yv,uv,vv,0)")
        n()

    def check_quiver_half_size(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv,0.5)
        title("quiver(xv,yv,uv,vv,0.5)")
        n()

    def check_quiver_double_size(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv,2)
        title("quiver(xv,yv,uv,vv,2)")
        n()

    def check_quiver_quadruple_size(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv,4)
        title("quiver(xv,yv,uv,vv,4)")
        n()


class test_quiver_indexing_xy(EasyvizTestCase):
    def check_quiver_indexing_xy_default(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data(indexing='xy')
        quiver(xv,yv,uv,vv,indexing='xy')
        title("quiver(xv,yv,uv,vv,indexing='xy')")
        n()

    def check_quiver_indexing_xy_no_grid_components(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data(indexing='xy')
        quiver(uv,vv,indexing='xy')
        title("quiver(uv,vv,indexing='xy')")
        n()    

    def check_quiver_indexing_xy_1D_grid_components(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data(indexing='xy')
        quiver(x,y,uv,vv,indexing='xy')
        title("quiver(x,y,uv,vv,indexing='xy')")
        n()


class test_quiver_misc(EasyvizTestCase):
    def check_quiver_scaling_fmt(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv,2,'ko')
        title("quiver(xv,yv,uv,vv,2,'ko')")
        n()

    def check_quiver_scaling_filled(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv,2.8,'filled')
        title("quiver(xv,yv,uv,vv,2.8,'filled')")
        n()

    def check_quiver_scaling_filled_fmt(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv,3,'filled','m')
        title("quiver(xv,yv,uv,vv,3,'filled','m')")
        n()

    def check_quiver_scaling_fmt_filled(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv,3,'cd','filled')
        title("quiver(xv,yv,uv,vv,3,'cd','filled')")
        n()

    def check_quiver_no_grid_components_scaling_filled_fmt(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(uv,vv,2,'filled','g3')
        title("quiver(uv,vv,2,'filled','g3')")
        n()

    def check_quiver_filled_fmt(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv,'filled','ko')
        title("quiver(xv,yv,uv,vv,'filled','ko')")
        n()

    def check_quiver_fmt_filled(self):
        x,y,xv,yv,values,uv,vv = self.get_2D_vector_data()
        quiver(xv,yv,uv,vv,'y--','filled')
        title("quiver(xv,yv,uv,vv,'y--','filled')")
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_quiver_basic,'check_'))
        suites.append(unittest.makeSuite(test_quiver_scaling,'check_'))
        suites.append(unittest.makeSuite(test_quiver_indexing_xy,'check_'))
        suites.append(unittest.makeSuite(test_quiver_misc,'check_'))
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
