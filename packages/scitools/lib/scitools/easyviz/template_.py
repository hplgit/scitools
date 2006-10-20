"""Show how a template is implemented"""
from common import *



class DerivedClass(BaseClass):
    """Template for creating new backends."""
    
    def __init__(self):
        BaseClass.__init__(self)
        self.init()
        
    def init(self):
        # Set docstrings of all functions to the docstrings of BaseClass
        # The exception is if something is very different
        # Alex had a nice function for this.
        
        #Do initialization special for this backend
        pass
    
    def _replot(self):
        """
        Update backend
        """
        #Write backend specific plot commands

        # the old (easyplot) way:
        '''
        currentfignumber=self._attr('curfig')
        currentfig=self._figs{currentfignumber}
        1. set correct attributes in backend

        for line in currentfig.lines:
            2 check attributes of line
            3 plot data.
        
        '''

        # the new (easyviz) way:
        '''
        ax = self.gca() # the current axis
        1. set correct properties in backend for the current axis (like axis
           limits, camera view, box, grid, ...), and for the current figure
           (like window size, subplots, ...).

        for item in ax.get('plotitems'):
            2. check the kind of the item object (that is, if it is a Line
               instance, a Surface instance, ...) and act accordingly.
            3. plot data.
        '''
        pass
        
    def hardcopy(self, file='file.ps', **kwargs):
        """
        Save current figure to file
        """
        pass
    
    #def somefunc(self,*args,**kwargs):
    #    BaseClass.somefunc(self,*args,**kwargs)
    #    #Add extra functionality here

debug_ = debug
debug = True

class TemplateBackend(BaseClass):
    def __init__(self):
        BaseClass.init(self)
        self.init()
        
    def init(self, *args, **kwargs):
        # Problem: calling figure method here makes the program halt
        #self.figure(self._attrs['curfig'])

        self._markers = {
            '':  'none',
            '.': 'dot',
            'o': 'circle',
            'x': 'cross',    # or 'linecross'?
            '+': 'plus',     # or 'lineplus'?
            '*': 'asterix',
            's': 'square',
            'd': 'diamond',
            '^': 'triangle',
            'p': 'pentagon', 
            # Some of the markers must be casted:
            'v': 'triangle', # triangle (down) --> triangle
            '<': 'triangle', # triangle (left) --> triangle
            '>': 'triangle', # triangle (right)--> triangle
            'h': 'square',   # hexgram --> square
            }
                        
        self._colors = {
            'y': 'yellow',
            'm': 'magenta',
            'c': 'cyan',
            'r': 'red',
            'g': 'green',
            'b': 'blue',
            'w': 'white',
            'k': 'black',
            }
        
        self._line_styles = {
            '': 'solid',
            '-': 'solid',
            ':': 'dotted',
            '-.': 'dash-dot',
            '--': 'dashed',
            }

        if debug:
            print "Setting backend standard variables"
            for disp in 'self._markers self._colors self._line_styles'.split():
                print disp, eval(disp)
                
    def figure(self, *args, **kwargs):
        """Extension of BaseClass.figure:"""        
        BaseClass.figure(self, *args, **kwargs) 
        fig = self.gcf()
        try:
            fig._g
        except:
            name = 'Fig ' + str(self._attrs['curfig'])

            # Create figure and save backend figure instance as fig._g
            if debug:
                print "creating figure %s in backend" %name

            class fig__:
                pass
            fig._g = fig__()
            
        self._g = fig._g # Creates link for faster access

    def _set_graph_margins(self, ax):
        left, bottom, right, top = ax.get('viewport')
        left_margin = left + 0.1
        if left_margin < 0 or left_margin > 1:
            left_margin = 0.1
        right_margin = 1.0 - right + 0.01
        if right_margin < 0 or right_margin > 1:
            right_margin = 0.01
        top_margin = 1.0 - top - 0.01
        if top_margin < 0 or top_margin > 1:
            top_margin = 0.01
        bottom_margin = bottom + 0.1
        if bottom_margin < 0 or bottom_margin > 1:
            bottom_margin = 0.1

        if debug:
            print "Setting figure margins in self._g"
            print 'left:', left, left_margin
            print 'bottom:', bottom, bottom_margin
            print 'right:', right, right_margin
            print 'top:', top, top_margin
          
    def _set_scale(self, ax):
        if debug:
            print "Setting scales"
        implement = """
        scale = ax.get('scale')
        if scale == 'loglog':
            self._g.Set('x/log', True)
            self._g.Set('y/log', True)
        elif scale == 'logx':
            self._g.Set('x/log', True)
            self._g.Set('y/log', False)
        elif scale == 'logy':
            self._g.Set('x/log', False)
            self._g.Set('y/log', True)
        elif scale == 'linear':
            self._g.Set('x/log', False)
            self._g.Set('y/log', False)
        """

    def _set_labels(self, ax):
        if debug:
            print "Setting labels"
        implement = """
        self._g.Set('x/label', ax.get('xlabel'))
        self._g.Set('y/label', ax.get('ylabel'))
        """
        
    def _set_title(self, ax):
        if debug:
            print "Setting title:"
        implement = """
        label = self._g.Add('label')
        self._g.Set('%s/label' % label, ax.get('title'))
        self._g.Set('%s/xPos' % label, 0.4)
        self._g.Set('%s/yPos' % label, 0.9)
        """
    def _set_limits(self, ax):
        if debug:
            print "Setting axis limits"
        implement = """
        fail = False
        for item in ['xmin', 'xmax']:
            if not isinstance(ax.get(item), (float, int)):
                fail = True;  break        
        if not fail:
            self._g.Set('x/min', ax.get('xmin'))
            self._g.Set('x/max', ax.get('xmax'))

        fail = False
        for item in ['ymin', 'ymax']:
            if not isinstance(ax.get(item), (float, int)):
                fail = True;  break
        if not fail:
            self._g.Set('y/min', ax.get('ymin'))
            self._g.Set('y/max', ax.get('ymax'))
        """
        
    def _set_grid(self, ax):
        if debug:
            print "Setting grid"
        implement = """
        hide_grid = not ax.get('grid')
        self._g.Set('x/GridLines/hide', hide_grid)
        self._g.Set('y/GridLines/hide', hide_grid)
        """
        
    def _replot(self):
        fig = self.gcf()
        
        # hack for fixing problem when calling figure() in init:
        try: fig._g
        except: figure(self._attrs['curfig'])

        if debug:
            print "Doing replot it backend"
            if self.get('show'):
                print "\nDumping plot data to screen\n"
                debug_(self)
        implement ="""
        # set figure size:
        self._g.Set('/width', str(fig.get('width')/2.))
        self._g.Set('/height', str(fig.get('height')/2.))

        self._g.To('/page1') # makeing sure we are at page1
        
        # remove all old graphs (if any):
        i = 1 # counter
        while True:
            try: self._g.Remove('/page1/graph%d' % i)
            except ValueError: break

        i = 1
        for ax in fig.get('axes').values():
            use_legends = False
            plotitems = ax.get('plotitems')
            if len(plotitems) > 0:
                self._g.To(self._g.Add('graph'))
                self._set_graph_margins(ax)
                self._set_scale(ax)
                self._set_labels(ax)
                self._set_limits(ax)
                self._set_grid(ax)
                self._set_title(ax)
            
            for item in plotitems:
                if isinstance(item, Line):
                    xy = self._g.Add('xy')
                
                    # set line marker:
                    marker = self._markers[item.get('linemarker')]
                    self._g.Set('%s/marker' % xy, marker)

                    # set line color:
                    color = self._colors.get(item.get('linecolor'), None)
                    if color:
                        self._g.Set('%s/PlotLine/color' % xy, color)
                        self._g.Set('%s/MarkerFill/color' % xy, color)

                    # set line type:
                    style = self._line_styles.get(item.get('linetype'), None)
                    if style:
                        self._g.Set('%s/PlotLine/style' % xy, style)
                    else:
                        self._g.Set('%s/PlotLine/hide' % xy, True)

                    # set data:
                    self._g.SetData('x%d' % i, item.get('xdata'))
                    self._g.SetData('y%d' % i, item.get('ydata'))
                    self._g.Set('%s/xData' % xy, 'x%d' % i)
                    self._g.Set('%s/yData' % xy, 'y%d' % i)

                    # set legend:
                    legend = item.get('legend')
                    if legend:
                        self._g.Set('%s/key' % xy, legend)
                        use_legends = True
                elif isinstance(item, Contours):
                    cntr = self._g.Add('contour')

                    # set data:
                    self._g.SetData2D('values%d' % i, item.get('zdata'))
                    self._g.Set('%s/data' % cntr, 'values%d' % i)

                    # set contour levels:
                    cvector = item.get('cvector')
                    if cvector:
                        cvector = ','.join([str(a) for a in cvector])
                        print cvector
                        self._g.Set('%s/manualLevels' % cntr, cvector)
                    else:
                        self._g.Set('%s/numLevels' % cntr, item.get('clevels'))

##                     self._g.Set('%s/lines' % cntr,
##                                 [('solid', '1pt', u'#5500ff', False),
##                                  ('dotted', '1pt', u'#aa557f', False)])
                else:
                    print "%s is not supported in the Veusz backend" % \
                          type(item)
                i += 1

            if use_legends:
                self._g.Add('key')

            self._g.To('/page1')
            
        if self.get('show'):
            self._g.window.showNormal()
        else:
            self._g.window.hide()

##         # for full gui, we can do something like this:
##         import tempfile, os
##         tempfname = tempfile.mktemp(suffix='.vsz')
##         print "saving file..."
##         self.save(tempfname)
##         print "saved"
##         os.system('veusz %s' % tempfname)
        """

    def hardcopy(self, filename, **kwargs):
        """Supported extensions: '.eps', '.svg', and '.png'."""
        if 'color' in kwargs:
            self.set(color=kwargs['color'])
        color = self.get('color')
        self._replot()

        if debug:
            print "Hardcopy to %s" %filename
        implement = """
        self._g.Export(filename, color=color)
        """

    #????    
    #def save(self, filename):
    #    """Save the current Veusz settings to file."""
    #    self._g.Save(filename)

plt = TemplateBackend()
use(plt, globals()) # Export public namespace of plt to globals()

def get_backend():
    if debug:
        print "Should now return plt._g"
    implement = """
    return plt._g
    """
