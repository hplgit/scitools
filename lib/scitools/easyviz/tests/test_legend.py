"""Test functions for legend command."""

from easyviztest import *


class test_legend_basic(EasyvizTestCase):
    def check_legend_simple(self):
        x,y,v,w = self.get_line_data()
        plot(x,y)
        legend('sin(x)*x')
        title("plot(..);legend('sin(x)*x')")
        n()

    def check_legend_simple_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,legend='sin(x)*x')
        title("plot(..,legend='sin(x)*x')")
        n()

    def check_legend_two_lines(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,x,v)
        legend('sin(x)*x','sin(x)*sqrt(x)')
        title("plot(..);legend('sin(x)*x','sin(x)*sqrt(x)'")
        n()

    def check_legend_two_lines_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(x,y,x,v,legend=('sin(x)*x','sin(x)*sqrt(x)'))
        title("plot(..,legend=('sin(x)*x','sin(x)*sqrt(x)')")
        n()

    def check_legend_two_lines_with_hold(self):
        x,y,v,w = self.get_line_data()
        setp(show=False)
        plot(x,y,'r:')
        legend('sin(x)*x')
        hold('on')
        plot(x,v,'b-o')
        legend('sin(x)*sqrt(x)')
        title("plot();legend();hold('on');plot();legend()")
        hold('off')
        setp(show=screenplot)
        show()
        n()

    def check_legend_three_lines(self):
        x,y,v,w = self.get_line_data()
        plot(y,v,w,x=x)
        legend('sin(x)*x','sin(x)*sqrt(x)','sin(x)*x**0.33333333')
        title("legend('sin(x)*x','sin(x)*sqrt(x)','sin(x)*x**0.33333333')")
        n()

    def check_legend_three_lines_kwarg(self):
        x,y,v,w = self.get_line_data()
        plot(y,v,w,x=x,
             legend=('sin(x)*x','sin(x)*sqrt(x)','sin(x)*x**0.33333333'))
        title("plot(..,legend=('sin(x)*x','sin(x)*sqrt(x)','sin(x)*x**0.33333333'))")
        n()

    def check_legend_multiple_lines(self):
        format = self.get_format_string_data()
        m = len(format)
        x = linspace(0,1,m)
        setp(show=False)
        for i in range(1,m+1):
            y = linspace(i,m/2.0,m)
            plot(x,y,format[i-1],hold='on')
            legend('line%d' % i)
        title("legends on multiple lines")
        hold('off')
        setp(show=screenplot)
        show()
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_legend_basic,'check_'))
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
