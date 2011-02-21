"""Test functions for axis command."""

from easyviztest import *


class test_axis_limits(EasyvizTestCase):
    def check_axis_limits_small(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        axis(2,10,-5,5)
        title("plot(..);axis(2,10,-5,5)")
        n()

    def check_axis_limits_large(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        axis(-5,20,-15,20)
        title("plot(..);axis(-5,20,-15,20)")
        n()

    def check_axis_limits_list(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        axis([-1,16,-12,16])
        title("plot(..);axis([-1,16,-12,16])")
        n()

    def check_axis_limits_kwargs(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        axis(xmin=-1,xmax=16,ymin=-12,ymax=16)  # FIXME: this is broken
        title("plot(..);axis(xmin=-1,xmax=16,ymin=-12,ymax=16)")
        n()


class test_axis_method(EasyvizTestCase):
    def check_axis_method_equal(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        axis('equal')
        title("plot(..);axis('equal')")
        n()

    def check_axis_method_equal_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,axis='equal')
        title("plot(..,axis='equal')")
        n()

    def check_axis_method_square(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        axis('square')
        title("plot(..);axis('square')")
        n()

    def check_axis_method_square_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,axis='square')
        title("plot(..,axis='square')")
        n()

    def check_axis_method_image(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        axis('image')
        title("plot(..);axis('image')")
        n()

    def check_axis_method_image_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,axis='image')
        title("plot(..,axis='image')")
        n()

    def check_axis_method_ij(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        axis('ij')
        title("plot(..);axis('ij')")
        n()

    def check_axis_method_ij_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,axis='ij')
        title("plot(..,axis='ij')")
        n()

    def check_axis_method_manual(self):
        pass


class test_axis_mode(EasyvizTestCase):
    def check_axis_mode_tight(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        axis('tight')
        title("plot(..);axis('tight')")
        n()

    def check_axis_mode_tight_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,axis='tight')
        title("plot(..,axis='tight')")
        n()

    def check_axis_mode_auto(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        axis(2,10,-5,5)
        axis('auto')
        title("plot(..);axis(2,10,-5,5);axis('auto')")
        n()

    def check_axis_mode_normal(self):
        pass


class test_axis_misc(EasyvizTestCase):
    def check_axis_no_args(self):
        x,y,v,w = self.get_line_data()
        setp(show=False)
        plot(x,y)
        limits = [-1,16,-16,16]
        axis(limits)
        limits2 = axis()
        assert len(limits)==len(limits2)
        assert allclose(limits, limits2)
        setp(show=screenplot)
    
    def check_axis_no_args_3D(self):
        x,y,xv,yv,values = self.get_2D_data()
        setp(show=False)
        surf(xv,yv,values)
        limits = [-2,2,-1,3,-10,10]
        axis(limits)
        limits2 = axis()
        assert len(limits)==len(limits2)
        assert allclose(limits, limits2)
        setp(show=screenplot)


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_axis_limits,'check_'))
        suites.append(unittest.makeSuite(test_axis_method,'check_'))
        suites.append(unittest.makeSuite(test_axis_mode,'check_'))
        suites.append(unittest.makeSuite(test_axis_misc,'check_'))
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
