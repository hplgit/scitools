"""Tests of the easyplot package"""

import unittest
import glob
import random
import os

from time import sleep
import Image

#from Numeric import *
from scitools.numpytools import *

# Try to import backends
_plts = {}
_suites = []
# Gnuplot
try:
    from scitools.easyviz.gnuplot_ import plt
    _plts['gnuplot'] = plt
    del(plt)
    
    class gnuplotTest(unittest.TestCase):
        """Gnuplot specific tests"""

        def setUp(self):
            self.x1 = arange(0, 1, 0.01)
            self.y1 = sin(2*pi*self.x1)
            self.x2 = arange(0, 2, 0.01)
            self.y2 = cos(2*pi*self.x2)
            self.time = 1.0
            use(_plts['gnuplot'],globals())
            #use(_plts['matplotlib'],globals())
            set(interactive=False,
                color=True)
            set(show=False)

        def test1(self):
            print 'test1'
            clf()
            plot((1,2,3), (4,5,4), 'bo-')
            #plt.legend('1')
            hold('on')
            plt.plot((1, 2, 3), 'ko-', (3, 1, 1), 'r.-', x=(1, 2, 3))
            axis(0, 6, 0, 6)
            legend('1', '2', '3')
            title('y(x)')
            xlabel('x')
            ylabel('y')
            filename = 'gnuplottest1.eps' # Either ps or eps.
            plot((1,2,3), 'r:', (2,3,4), 'b-', (3,4,5), 'k-.', (4,6,6), 'g--',\
                 x='auto')
            hardcopy(filename, color=True)

        def test2(self):
            print 'test2'
            set(color=True)
            clf()
            #print plt._figs
            #print get('curfig')
            plot((1,2,3), '.', (2,3,4), 'ro--',  xlabel='xlabel',  \
                 ylabel='ylabel', title='title', legend=('1','2'))
            x = arange(0, 10, 0.1)
            y1 = cos(x)
            y2 = sin(x)
            axis([0, 3, -1, 6])
            plot(y1, 'r.', y2, 'bo', x=x, legend=('cos(x)','sin(x)'),
                 color=True,
                 show=False, hardcopy='gnuplottest2.ps',)

            plt._g('quit')
            #show()
    _suites.append(unittest.makeSuite(gnuplotTest))
    
except ImportError, e:
    print e

# Pyx
try:
    from easyviz.pyx_ import plt
    
    _plts['pyx_'] = plt
    
    class pyxTest(unittest.TestCase):
        """Pyx specifig test"""
        def test1(self):
            try:
                if  'pyx_' in _plts:
                    use(_plts['pyx_'], globals())
                    figure()
                    plot((2, 2, 3, 4), 'kv-', (3, 3, 4, 6), 'kv', x='auto')
                    axis(-1, 5, -1, 10)
                    title('A very long title')
                    legend('line 1', 'line 2')
                    #latextext = r"$2\pi\gamma k\Omega$"
                    #$plt._g.text(0, 0, latextext)
                    hold('on')
                    plot((5, 3, 5, 5))
                    legend('line 3')
                    hardcopy('testpyx.eps')
            except:
                print 'pyx_ error: \nDebugging plt'
                #debug(plt)
    _suites.append(unittest.makeSuite(pyxTest))
    
except ImportError, e:
    print e
    #print "pyx not tested"
    
# BLT
try:
    raise ImportError # Blt windows appears when tk is started from matplotlib
    from scitools.easyviz.blt_ import * 
    _plts['blt'] = plt
  
    class bltTest(unittest.TestCase):
        """Blt specific tests"""
        def setUp(self):
            self.x1 = arange(0, 1, 0.01)
            self.y1 = sin(2*pi*self.x1)
            self.x2 = arange(0, 2, 0.01)
            self.y2 = cos(2*pi*self.x2)
            self.time = 1.0

            use(_plts['blt'], globals())
            set(interactive=True,
                color=True) 

        def test(self):
            self.setUp()
            try:
                figure()
                plot((1,2,3), (4,6,5), 'ro--')
                legend('tril')
                axis(0, 5, 0, 10)
                hold('on')
                plot((2,4,5), (4,4,4), '')
                legend('notrill', 'trill2')
                plot((1,2,3,4,5,6), (1,3,2,4,3,6), 'k:x')
                legend('nils')
                import Numeric
                x=Numeric.array((1,2,3,4))
                plot(x, x**2, 'y')
                axis(0, 10, 0, 10)
                hardcopy('blt_test1.ps')
                figure()
                plot((1,2,3), 'r:', (2,3,4), 'b-', (3,4,5), 'k-.',\
                     (4,6,6), 'g--')#, x='auto')
                legend('dotted', 'solid', 'dotdashed', 'dashed')
                hardcopy('blt_test2.ps')    
                figure()
                plot((1,10,100), log='y')
                hold('on')
                loglog((1,19,199), (10,100,1000))
                legend('loglog', 'loglog')
                title('one scale')
                xlabel('x')
                ylabel('y')
                hardcopy('blt_test3.ps')
            except:
                print "Error: running debug(plt)"
                #debug(plt)
    _suites.append(unittest.makeSuite(bltTest))
except ImportError,e:
    print "blt not tested"

# Matplotlib
try:
    from scitools.easyviz.matplotlib_ import plt
    _plts['matplotlib'] = plt
    del(plt)
    class matplotlibTest(unittest.TestCase):
        pass
    _suites.append(unittest.makeSuite(matplotlibTest))
except ImportError, e:
    print e

# Load default backend
from scitools.easyviz.examples import * 

# Common 1d test
class easyvizTest(unittest.TestCase):
    """These tests are run for all implemented backends."""
    
    def setUp(self):
        pass

    def runTest(self):
        print 'runTest'
        self.testStyle()
                
    def testStyle(self):
        """Test linestyles"""
        print "Now testing %s" %plt.__module__.split('.')[1]
        #_colors = "b g r m c y k".split()
        #_markers = "o + x * s d v ^ < > p h .".split()
        #_linestyles = "- : -. --".split()
        _colors = Line._colors
        _markers = Line._markers
        _linestyles = Line._linestyles
        #_linestyles.append('') # No Linestyle option
        # Note if no marker or no linestyle, default '-x' is used
        if plt.__module__.split('.')[1] in ('pyx_', 'blt'):
            _markers = ['v','+','s','x','^','o'] 
        x = seq(0, 2, 0.2)
        y = sin(x)*x
        # Generate formatstrings
        format = []
        for item in _markers:
            format.append(''.join([random.choice(_colors), item,
                                   random.choice(_linestyles)]))
        figure()
        hold('on')
        set(color=True)
        set(show=False)
        set(interactive=False)
        for i in range(len(format)):
            y = sin(x+i)*x
            fmt = format[i]
            plot(x, y, fmt, legend=fmt)
        #legend(fmt)
        #print plt._figs[1].lines[i].attrs['legend']
        #legend(*format)
        plot((1,2,3), (2,3,4), x='auto', legend=('nestsist', 'sist'))
        #axis([0,2,0,5]) # Prefered way of using the axis command
        axis(min(x), max(x)+1, -2, 5) # Note there is no tuple here
                
        f = '%sstyle_test.png' %plt.__module__.split('.')[1]
        hardcopy(f)
        clf()
        im = Image.open(f) # Check if output is a valid image file
        try: assert im.format.lower() == im.filename.split('.')[-1]
        except AssertionError, e:
            print e
            print im.filename, im.format, im.format_description
            assert im.format.lower() == im.filename.split('.')[-1]

class easyviz2dTest(unittest.TestCase):
    """Test Contour, pcolor, quiver and other two-dimensional tests"""

    def setUp(self):
        # command-line arguments: n screenplot flash psplot
        # screenplot: show plots on the screen?
        # flash: drop prompt between plots and clf, everything goes into one plot
        # psplot: make hardcopy of each plot?
        global hardcopy_counter, clear_figure, prompt, pause, psplot, screenplot
        n = 1
        screenplot = True
        flash = True
        psplot = True
        hardcopy_counter = 0
    
    #def runTest(self):
    #    self.testContour()
    #    self.testQuiver()
    
    def testQuiver(self):
        xx,yy,zz = get_data()
        xv = xx*ones(zz.shape)
        yv = yy*ones(zz.shape)
        uu = xv+1
        vv = yv+1
        backend = plt.__module__.split('.')[1]
        print "testing quiver..."
        arrowscale=1/4.
        quiver(xx,yy,uu*0+.9,vv*0+.4, title="quiver(xx,yy,uu*0+.9,vv*0+.4)",
               hardcopy='%squiver1.png' %backend,
               arrowscale=arrowscale)
        quiver(yv,xv,vv*0+.9,uu*0+.9, title="quiver(yv,xv,vv*0+.9,uu*0+.9)",
               show=False,hardcopy='quiver2.png',arrowscale=arrowscale)
        quiver(xx,yy,uu,vv, title="quiver(xx,yy,uu,vv)", show=False,
               hardcopy='quiver3.png')
        quiver(uu,vv,'filled', 'g', title="quiver(uu,vv,'filled','g')",
               show=False,hardcopy='quiver4.png')
        quiver(uu,vv,'r:.', title="quiver(uu,vv,'r:.')",
               hardcopy='quiver5.png', show=False)
        
    def testContours(self):
        xx,yy,zz = get_data()
        screenplot=False
        print "testing contours..."
        contour(xx,yy,zz,title="2D contour plot using contour(xx,yy,zz)",
                show=False, hardcopy='contour1.png')
        contour(xx,yy,zz,20,title=\
                "2D contour plot with 20 levels using contour(xx,yy,zz,20)",
                hardcopy='contour2.png')
        contourf(xx,yy,zz,seq(arrmin(zz),arrmax(zz),1), 
                title="contourf(xx,yy,zz,seq(arrmin(zz),arrmax(zz),1))",
                show=screenplot,hardcopy='contour3.png')
        contour(xx,yy,zz,[-0.2,-0.5,0.2,0.5], 
                title="contour(xx,yy,zz,[-0.2,-0.5,0.2,0.5])",
                show=screenplot,hardcopy='contour4.png')
        contour(zz,15, clabels='on', title="contour(zz,clabels='on')",
                show=screenplot,hardcopy='contour5.png')
        
        #plt._magic()

    def testSurface(self):
        f = 'pcolor1.png'
        if os.path.isfile(f):
            os.remove(f)
        n = 6;
        r = seq(0,n,1)[:,NewAxis]/n;
        theta = pi*seq(-n,n)/n;
        X = r*cos(theta);
        Y = r*sin(theta);
        C = r*cos(2*theta);
        
        shading('interp')
        colorbar()
        axis('off')
        pcolor(X,Y,C,
               axis='image',
               title='pcolor plot',
               hardcopy=f)
        self.failUnless(Image.open(f))
        
def main():    
    postscriptfiles = '' + \
                      " ".join(glob.glob('*.eps')) + \
                      " ".join(glob.glob('*.ps'))
    if len(postscriptfiles) > 0:
        print "Warning: you have old ps/eps files in testdir."
        print "These files might be overwritten by this test"
        print "The files are: ",postscriptfiles    
        #rm *.ps *.eps *.pyc *~ -f
    
    #unittest.main() # There is a sys.exit() inside here....
    if False:
        os.system(
            "python -c '''from scitools.easyviz.unittest_ import *;unittest.main()'''")
        suite = unittest.makeSuite(easyvizTest, 'test')
        suite = unittest.makeSuite(bltTest, 'test')
        suite = unittest.makeSuite(gnuplotTest, 'test')
    else:
        unittest.TextTestRunner(verbosity=2).run(
            unittest.makeSuite(easyvizTest))
    if False:
        if os.uname()[0] == 'Linux':
            psviewer = 'gv'
            for file in glob.glob('*.ps'):
                os.system('%s %s &' %(psviewer, file))
            for file in glob.glob('*.eps'):
                os.system('%s %s &' %(psviewer, file))
            #raw_input('Press return when files are examined')
        else:
            show()
       
if __name__ == "__main__":
    #os.system("python -c 'from easyviz.unittest_ import *; unittest.main()'")

    #use(_plts['gnuplot'], globals())
    #suite = easyvizTest()
    #suite.runTest()

    # Specific test
    if 'easyviz_backend' in  os.environ.keys():
        suite = unittest.makeSuite(easyvizTest)
        unittest.TextTestRunner(verbosity=2).run(suite)
        suite = unittest.makeSuite(easyviz2dTest)
        unittest.TextTestRunner(verbosity=2).run(suite)
        
    # Test all possible
    else:
        # Backend Specific tests
        for suite in _suites:
            unittest.TextTestRunner(verbosity=2).run(suite)
        # Common tests
        for plt_ in _plts:
            use(plt, globals())
            suite = unittest.makeSuite(easyvizTest)
            unittest.TextTestRunner(verbosity=2).run(suite)
            
    
