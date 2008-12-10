"""Test functions for plot3 command."""

from easyviztest import *


class test_plot3_basic(EasyvizTestCase):
    def check_plot3_default(self):
        x,y,z = self.get_3D_line_data()
        plot3(x,y,z)
        title("plot3(x,y,z)")
        n()

    def check_plot3_only_z(self):
        x,y,z = self.get_3D_line_data()
        plot3(z)
        title("plot3(z)")
        n()
        
    def check_plot3_kwarg_x_and_y(self):
        x,y,z = self.get_3D_line_data()
        plot3(z,x=x,y=y)
        title("plot3(z,x=x,y=y)")
        n()
        
    def check_plot3_kwarg_auto_x_and_y(self):
        x,y,z = self.get_3D_line_data()
        plot3(z,x='auto',y='auto')
        title("plot3(z,x='auto',y='auto')")
        n()
        
    def check_plot3_two_lines(self):
        x,y,z = self.get_3D_line_data()
        plot3(x,y,z,x,y,-z)
        title("plot3(x,y,z,x,y,-z)")
        n()
        
    def check_plot3_two_lines_kwarg_x_and_y(self):
        x,y,z = self.get_3D_line_data()
        plot3(z,-z,x=x,y=y)
        title("plot3(z,-z,x=x,y=y)")
        n()
        
    def check_plot3_two_lines_kwarg_auto_x_and_y(self):
        x,y,z = self.get_3D_line_data()
        plot3(z,-z,x='auto',y='auto')
        title("plot3(z,-z,x='auto',y='auto')")
        n()

    def check_plot3_multiple_lines(self):
        x,y,z = self.get_3D_line_data()
        plot3(x,y,z,x,y,-z,x,y,2*z,x,y,-2*z)
        title("plot3(x,y,z,x,y,-z,x,y,2*z,x,y,-2*z)")
        n()
        
    def check_plot3_multiple_lines_kwarg_x_and_y(self):
        x,y,z = self.get_3D_line_data()
        plot3(z,-z,2*z,-2*z,x=x,y=y)
        title("plot3(z,-z,2*z,-2*z,x=x,y=y)")
        n()
        
    def check_plot3_multiple_lines_kwarg_auto_x(self):
        x,y,z = self.get_3D_line_data()
        plot3(z,-z,2*z,-2*z,x='auto',y='auto')
        title("plot3(z,-z,2*z,-2*z,x='auto',y='auto')")
        n()


class test_plot3_format_string(EasyvizTestCase):
    def check_plot3_multiple_lines_fmt(self):
        x,y,z = self.get_3D_line_data()
        plot3(x,y,z,'r-',x,y,-z,'b--',x,y,2*z,'g--',x,y,-2*z,'x')
        title("plot3(x,y,z,'r-',x,y,-z,'b--',x,y,2*z,'g--',x,y,-2*z,'x')")
        n()

    def check_plot3_multiple_lines_fmt_kwarg_x(self):
        x,y,z = self.get_3D_line_data()
        plot3(z,'r-',-z,'b--',2*x,'g--',-2*x,'x',x=x,y=y)
        title("plot3(z,'r-',-z,'b--',2*x,'g--',-2*x,'x',x=x,y=y)")
        n()

    def check_plot3_multiple_lines_fmt_kwarg_auto_x(self):
        x,y,z = self.get_3D_line_data()
        plot3(z,'r-',-z,'b--',2*z,'g--',-2*z,'x',x='auto',y='auto')
        title("plot3(z,'r-',-z,'b--',2*z,'g--',-2*z,'x',x='auto',y='auto')")
        n()

    def check_plot3_linecolors(self):
        x,y,z = self.get_3D_line_data()
        setp(show=False)
        colors = Line._colors
        for i,color in enumerate(colors):
            plot3(x,y,z+i,color,hold='on')
        title("different line colors")
        hold('off')
        setp(show=screenplot)
        show()
        n()

    def check_plot3_linestyles(self):
        x,y,z = self.get_3D_line_data()
        setp(show=False)
        styles = Line._linestyles
        for i,style in enumerate(styles):
            plot3(x,y,z+i,style,hold='on')
        title("different line styles")
        hold('off')
        setp(show=screenplot)
        show()
        n()

    def check_plot3_linemarkers(self):
        x,y,z = self.get_3D_line_data()
        setp(show=False)
        markers = Line._markers
        for i,marker in enumerate(markers):
            plot3(x,y,z+i,marker,hold='on')
        title("different line markers")
        hold('off')
        setp(show=screenplot)
        show()
        n()

    def check_plot3_linewidth(self):
        x,y,z = self.get_3D_line_data()
        setp(show=False)
        for i in range(1,10):
            plot3(x,y,z+i,str(i),hold='on')
        title("different line widths")
        hold('off')
        setp(show=screenplot)
        show()
        n()


class test_plot3_with_NaNs(EasyvizTestCase):
    def check_plot3_NaN_in_list(self):
        plot3([0,1,NaN,3,4])
        title("plot3([0,1,NaN,3,4])")
        n()
        
    def check_plot3_NaN_in_array(self):
        plot3(array([0,1,NaN,3,4],float))
        title("plot3(array([0,1,NaN,3,4],float))")
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_plot3_basic,'check_'))
        suites.append(unittest.makeSuite(test_plot3_format_string,'check_'))
        suites.append(unittest.makeSuite(test_plot3_with_NaNs,'check_'))
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
