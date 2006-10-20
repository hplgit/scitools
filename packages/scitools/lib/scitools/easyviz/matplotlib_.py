"""Show how a template is implemented"""
from common import *

import matplotlib
import matplotlib.colors
# Override system defaults before importing pylab
matplotlib.use('TkAgg')  # matplotlib.use('Agg')
matplotlib.rc('text', usetex=True)
matplotlib.interactive(True)
from matplotlib.font_manager import fontManager, FontProperties
import pylab


from IPython.Shell import IPythonShellEmbed as magic

def _cmpPlotProperties(a,b):
    """Sort cmp-function for PlotProperties"""
    plotorder = [Volume, Streams, Surface, Contours, VelocityVectors, Line] 
    assert isinstance(a, PlotProperties)
    assert isinstance(b, PlotProperties)
    assert len(PlotProperties.__class__.__subclasses__(PlotProperties)) == \
               len(plotorder) # Check all subclasses is in plotorder
    return cmp(plotorder.index(a.__class__),plotorder.index(b.__class__))

class MatplotlibBackend(BaseClass):
    def __init__(self):
        BaseClass.init(self)
        self.init()
        self._g = pylab

        
        # convert tables for formatstrings
        self._markers = {
            '': '',
            '.': '.', # 'point',       
            'o': 'o', # 'circle',      
            'x': 'x', #' x-mark',       
            '+': '+', #'plus',              
            '*': '+', # 'star' --> plus,
            's': 's', # 'square',
            'd': 'd', # 'diamond',
            'v': 'v', # 'triangle (down)',
            '^': '^', # 'triangle (up)',
            '<': '<', # 'triangle (left)',
            '>': '>', # 'triangle (right)',
            'p': 'p', # 'pentagram',
            'h': 'h', # 'hexagram',
            }
        
    def _replot(self):
        """Replot all figures, all axis and all plotitems in backend,
        NOTE: The easyviz way is to only redraw last figure/axis
        """
        print "\nRunning _replot\n" 

        p = self._g
        p.close('all')

        # Update figures
        #for fignr, fig in self._figs.items(): 
        for fignr, fig in (self.get('curfig'), self.gcf()),: # Last figure
            print 'figure', fignr
            p.figure(fignr)
            #p.subplot(*(fig.get('axshape')+(fig.get('curax'),)))
            for axnr, ax  in fig.get('axes').items():
                p.subplot(*(fig.get('axshape')+(axnr,)))
                # Update axes limits
                for i1,i2 in zip(ax._ranges, ax.get_limits()):
                    if i2 != None:
                        if i1 == 'xmin':
                            p.gca().set_xlim(xmin=i2)
                        elif i1 == 'xmax':
                            p.gca().set_xlim(xmax=i2)
                        elif i1 == 'ymin':
                            p.gca().set_ylim(ymin=i2)
                        elif i1 == 'ymax':
                            p.gca().set_ylim(ymax=i2)
                        else:
                            print 'not implemented:',i1,i2
                # Titles
                p.title(ax.get('title'))
                p.xlabel(ax.get('xlabel'))
                p.ylabel(ax.get('ylabel'), rotation='horizontal')
                p.grid(ax.get('grid'))
                    

                #p.axis({'tight':'tight'}[ax.get('mode')])
                

                p.hold(True)
                plotitems = ax.get('plotitems')
                plotitems.sort(_cmpPlotProperties)

                l_ = False # Legend test
                # Plot data
                for item in plotitems:
                    # List not Implemented PlotProperties
                    if isinstance(item, (Volume, Streams)):
                        #Surface, Contours, VelocityVectors)):
                        raise NotImplementedError, \
                              'plotting of %s is not implemented in class %s'\
                              %(str(item.__class__), self.__class__.__name__)
                    elif isinstance(item, Streams):
                        pass

                    elif isinstance(item, Surface):
                        self._plotSurface(item, ax.get('shading'))
                        
                    elif isinstance(item, Contours):
                        x, y = meshgrid(item.get('xdata'), item.get('ydata'),
                                        sparse=False)
                        # filled?
                        contour = p.contour
                        if item.get('filled'):
                            contour = p.contourf
                        cs = contour(x, y , item.get('zdata'), item.get('clevels'))
                        if item.get('clabels'):
                            p.clabel(cs)

                    elif isinstance(item, VelocityVectors):
                        self._plotVector(item)
                    # Lines
                    elif isinstance(item, Line):
                        try:
                            fmt = item.get('linecolor') + \
                                  self._markers[item.get('linemarker')] + \
                                  item.get('linetype')
                        except KeyError, e:
                            pass#magic()('keyerror %s' %str(e))
                        
                        linewidth=item.get('linewidth')
                        if not linewidth:
                            linewidth=item.get('pointsize')
                        _plot = {'loglog': p.loglog,
                                 'semilogx': p.semilogx,
                                 'semilogy': p.semilogy,
                                 'linear': p.plot}[ax.get('scale')]
                        args = item.get('xdata'), item.get('ydata'), 
                        if fmt:
                            args = args + (fmt,)
                        l = item.get('legend')
                        if not len(l):
                            l = '_nolegend_'
                        else:
                            l_ = True
                        kwargs = {'label': l,
                                  'linewidth': linewidth,
                                  }
                        _plot(*args, **kwargs)
                # Legend
                if l_:
                    p.legend()

                # Colorbar
                if ax.get('colorbar').get('visible'):
                    cb = ax.get('colorbar')
                    print "Implement colorbar"
                    """p.colorbar(mappable=None,
                               cax=None,
                               orientation='vertical',
                               tickfmt='%1.1f',
                               cspacing='proportional',
                               clabels=None,
                               drawedges=False,
                               edgewidth=0.5,
                               edgecolor='k')
                               """
                                        
    def _plotVector(self,item):
        """Helper function for _replot"""
        p = self._g
        assert item.get('function') != 'quiver3'
        x, y = self._meshgrid_xy(item)
        u, v = item.get('udata'), item.get('vdata')
        # Nice trick to normalize
        #fac = arrmax(arrmax(u**2+v**2))**.5 + 10**-15
        #def subtract(a,b):
        #    return a-b
        #fac2 = subtract(*item.get('xlim'))**2+subtract(*item.get('ylim'))**2
        #u /= fac
        #v /= fac

        # set arrowscale to 0 to prevent matplotlib's automatic tuning
        lc = item.get('linecolor')
        if not lc:
            lc = u**2+v**2 # color arrows by magnitude
        p.quiver(x, y, u, v, item.get('arrowscale'), color=lc, width=1.0)

    def _plotSurface(self, item, shading):
        print item.__class__, "is implemented soon"
        p = self._g
        assert item.get('function') == 'pcolor'
        x, y = self._meshgrid_xy(item)
        self._g.pcolor(x, y, item.get('zdata'), shading=shading,)
        #import sys; sys.argv = []; magic()('magic in Contour')

    def _meshgrid_xy(self, item):
        # Get dense 2d arrays for x,y-coordinates
        x, y = item.get('xdata'), item.get('ydata')
        if rank(x) == 2:
            assert rank(y) == 2
        x = squeeze(x)
        y = squeeze(y)
        if rank(x) == 1:
            assert rank(y) == 1
            x, y = meshgrid(x, y, sparse=False)
        return x, y
        
    def _magic(self):
        """Start ipython session with namespace of instance"""
        magic()('Starting ipython session with namespace of instance\n'\
                +repr(self)
                )
        
    def hardcopy(self, filename=None, **kwargs ):
        self._replot()
        if filename:
            self._g.savefig(filename, dpi=150, facecolor='w', edgecolor='w',
                            orientation='portrait'
                            )
        print "In hardcopy matplotlib"
        
plt = MatplotlibBackend()
use(plt, globals()) # Export public namespace of plt to globals()
