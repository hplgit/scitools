"""Test functions for plot command."""

from easyviztest import *


class test_plot_basic(EasyvizTestCase):
    def check_plot_default(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        title("plot(x,y)")
        n()

    def check_plot_only_y(self):
        x,y,v,w = self.get_line_data()
        plot(y)
        title("plot(y)")
        n()
        
    def check_plot_kwarg_x(self):
        x,y,v,w = self.get_line_data()
        plot(y,x=x)
        title("plot(y,x=x)")
        n()
        
    def check_plot_kwarg_auto_x(self):
        x,y,v,w = self.get_line_data()
        plot(y,x='auto')
        title("plot(y,x='auto')")
        n()
        
    def check_plot_two_lines(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,x,v)
        title("plot(x,y,x,v)")
        n()
        
    def check_plot_two_lines_kwarg_x(self):
        x,y,v,w = self.get_line_data()
        plot(y,v,x=x)
        title("plot(y,v,x=x)")
        n()
        
    def check_plot_two_lines_kwarg_auto_x(self):
        x,y,v,w = self.get_line_data()
        plot(y,v,x='auto')
        title("plot(y,v,x='auto')")
        n()

    def check_plot_multiple_lines(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,x,v,x,w,x,x,x,-x)
        title("plot(x,y,x,v,x,w,x,x,x,-x)")
        n()
        
    def check_plot_multiple_lines_kwarg_x(self):
        x,y,v,w = self.get_line_data()
        plot(y,v,w,x,-x,x=x)
        title("plot(y,v,w,x,-x,x=x)")
        n()
        
    def check_plot_multiple_lines_kwarg_auto_x(self):
        x,y,v,w = self.get_line_data()
        plot(y,v,w,x,-x,x='auto')
        title("plot(y,v,w,x,-x,x='auto')")
        n()


class test_plot_format_string(EasyvizTestCase):
    def check_plot_multiple_lines_fmt(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,'r-',x,v,'b--',x,w,'g--',x,x,'x',x,-x,'k:')
        title("plot(x,y,'r-',x,v,'b--',x,w,'g--',x,x,'x',x,-x,'k:')")
        n()

    def check_plot_multiple_lines_fmt_kwarg_x(self):
        x,y,v,w = self.get_line_data()
        plot(y,'r-',v,'b--',w,'g--',x,'x',-x,'k:',x=x)
        title("plot(y,'r-',v,'b--',w,'g--',x,'x',-x,'k:',x=x)")
        n()

    def check_plot_multiple_lines_fmt_kwarg_auto_x(self):
        x,y,v,w = self.get_line_data()
        plot(y,'r-',v,'b--',w,'g--',x,'x',-x,'k:',x='auto')
        title("plot(y,'r-',v,'b--',w,'g--',x,'x',-x,'k:',x='auto')")
        n()

    def check_plot_linecolors(self):
        x = linspace(0,1,13)
        setp(show=False)
        colors = Line._colors
        for i,color in enumerate(colors):
            plot(x,x+i,color,hold='on')
        title("different line colors")
        hold('off')
        setp(show=screenplot)
        show()
        n()

    def check_plot_linestyles(self):
        x = linspace(0,1,13)
        setp(show=False)
        styles = Line._linestyles
        for i,style in enumerate(styles):
            plot(x,x+i,style,hold='on')
        title("different line styles")
        hold('off')
        setp(show=screenplot)
        show()
        n()

    def check_plot_linemarkers(self):
        x = linspace(0,1,13)
        setp(show=False)
        markers = Line._markers
        for i,marker in enumerate(markers):
            plot(x,x+i,marker,hold='on')
        title("different line markers")
        hold('off')
        setp(show=screenplot)
        show()
        n()

    def check_plot_linewidth(self):
        x = linspace(0,1,13)
        setp(show=False)
        for i in range(1,10):
            plot(x,x+i,str(i),hold='on')
        title("different line widths")
        hold('off')
        setp(show=screenplot)
        show()
        n()


class test_plot_with_NaNs(EasyvizTestCase):
    def check_plot_NaN_in_list(self):
        plot([0,1,NaN,3,4])
        title("plot([0,1,NaN,3,4])")
        n()
        
    def check_plot_NaN_in_array(self):
        plot(array([0,1,NaN,3,4],float))
        title("plot(array([0,1,NaN,3,4],float))")
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_plot_basic,'check_'))
        suites.append(unittest.makeSuite(test_plot_format_string,'check_'))
        suites.append(unittest.makeSuite(test_plot_with_NaNs,'check_'))
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
