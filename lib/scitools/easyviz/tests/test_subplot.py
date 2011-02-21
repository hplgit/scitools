"""Test functions for subplot command."""

from easyviztest import *


class test_subplot(EasyvizTestCase):
    def check_subplot_two_rows_one_column(self):
        x,y,v,w = self.get_line_data()
        setp(show=False)
        subplot(2,1,1)
        plot(x,y,'b:')
        title("subplot(2,1,1);plot(..)")
        subplot(2,1,2)
        plot(x,y,'b:',x,v,'r-o')
        title("subplot(2,1,2);plot(..)")
        setp(show=screenplot)
        show()
        n()

    def check_subplot_one_row_two_columns(self):
        x,y,v,w = self.get_line_data()
        setp(show=False)
        subplot(1,2,1)
        plot(x,y,'b:')
        title("subplot(1,2,1);plot(..)")
        subplot(1,2,2)
        plot(x,y,'b:',x,v,'r-o')
        title("subplot(1,2,2);plot(..)")
        setp(show=screenplot)
        show()
        n()

    def check_subplot_two_rows_two_columns(self):
        x,y,v,w = self.get_line_data()
        setp(show=False)
        subplot(2,2,1)
        plot(x,y,'b:')
        title("subplot(2,2,1);plot(..)")
        subplot(2,2,2)
        plot(x,y,'b:',x,v,'r-o')
        title("subplot(2,2,2);plot(..)")
        subplot(2,2,3)
        plot(x,y,'b:',x,v,'r-o',x,w,'c+')
        title("subplot(2,2,3);plot(..)")
        subplot(2,2,4)
        plot(x,y,'b:',x,v,'r-o',x,w,'c+',x,x,'m--')
        title("subplot(2,2,4);plot(..)")
        setp(show=screenplot)
        show()
        n()

    def check_subplot_two_rows_two_columns_mixed(self):
        x,y,v,w = self.get_line_data()
        setp(show=False)
        ax1 = subplot(2,2,1)
        subplot(2,2,3)
        plot(x,y,'b:',x,v,'r-o',x,w,'c+')
        title("subplot(2,2,3);plot(..) (mixed)")
        ax4 = subplot(2,2,4)
        plot(x,y,'b:',x,v,'r-o',x,w,'c+',x,x,'m--')
        setp(ax4,title="subplot(2,2,4);plot(..) (mixed)")
        subplot(2,2,2)
        plot(x,y,'b:',x,v,'r-o')
        title("subplot(2,2,2);plot(..) (mixed)")
        plot(ax1,x,y,'b:')
        title(ax1,"subplot(2,2,1);plot(..) (mixed)")
        setp(show=screenplot)
        show()
        n()

    def check_subplot_31p(self):
        x,y,v,w = self.get_line_data()
        setp(show=False)
        subplot(311)
        plot(x,y,'b:')
        title("subplot(311);plot(..)")
        subplot(312)
        plot(x,y,'b:',x,v,'r-o')
        title("subplot(312);plot(..)")
        subplot(313)
        plot(x,y,'b:',x,v,'r-o',x,w,'c+')
        title("subplot(313);plot(..)")
        setp(show=screenplot)
        show()
        n()

    def check_subplot_23p(self):
        x,y,v,w = self.get_line_data()
        setp(show=False)
        subplot(231)
        plot(x,y,'b:')
        title("subplot(231);plot(..)")
        subplot(232)
        plot(x,y,'b:',x,v,'r-o')
        title("subplot(232);plot(..)")
        subplot(233)
        plot(x,y,'b:',x,v,'r-o',x,w,'c+')
        title("subplot(233);plot(..)")
        subplot(234)
        plot(x,y,'b:',x,v,'r-o',x,w,'c+',x,x,'m--')
        title("subplot(234);plot(..)")
        subplot(235)
        plot(x,y,'b:',x,v,'r-o',x,w,'c+',x,x,'m--',x,-x,'k-.')
        title("subplot(235);plot(..)")
        subplot(236)
        plot(x,y,'b:',x,v,'r-o',x,w,'c+',x,x,'m--',x,-x,'k-.',x,-v,'y2')
        title("subplot(236);plot(..)")
        setp(show=screenplot)
        show()
        n()


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append(unittest.makeSuite(test_subplot,'check_'))
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
