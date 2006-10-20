from common import *

import veusz.embed
import tempfile, os

"""
Known issues:

- if an image of a 2D dataset (for example created by pcolor) is drawn before
  a curve or contour lines, then these will be completely hidden by the image.
  This can be fixed by moving the image down on the tree in the Veusz gui.

- savefig does not work (gives a segmentation fault)
"""

class VeuszBackend(BaseClass):
    def __init__(self):
        BaseClass.init(self)
        self.init()
        
    def init(self, *args, **kwargs):
        self._markers = {
            '':  'none',
            '.': 'dot',
            'o': 'circle',
            'x': 'cross',
            '+': 'plus',
            '*': 'asterix',
            's': 'square',
            'd': 'diamond',
            '^': 'triangle',
            'p': 'pentagon', 
            # some markers must be casted:
            'v': 'triangle', # triangle (down) --> triangle
            '<': 'triangle', # triangle (left) --> triangle
            '>': 'triangle', # triangle (right)--> triangle
            'h': 'square',   # hexagram --> square
            }
                        
        self._colors = {
            '':  'blue',     # no color --> blue
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
            '': 'solid',     # no line style --> solid
            '-': 'solid',
            ':': 'dotted',
            '-.': 'dash-dot',
            '--': 'dashed',
            }

    def figure(self, num=None, **kwargs):
        # Extension of BaseClass.figure:
        BaseClass.figure(self, num=num, **kwargs) 
        fig = self.gcf()
        try:
            fig._g
        except:
            name = 'Fig ' + str(self._attrs['curfig'])
            fig._g = veusz.embed.Embedded(name)
            fig._g.EnableToolbar(enable=True)
            fig._g.window.hide()
            
        self._g = fig._g # link for faster access
        
    figure.__doc__ = BaseClass.figure.__doc__ 

    def _set_graph_margins(self, ax):
        viewport = ax.get('viewport')
        if not viewport:
            viewport = ['1.7cm', '1.7cm', '0.1cm', '1.0cm']
        left, bottom, right, top = viewport
        self._g.Set('leftMargin', str(left))
        self._g.Set('rightMargin', str(right))
        self._g.Set('topMargin', str(top))
        self._g.Set('bottomMargin', str(bottom))
          
    def _set_scale(self, ax):
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

    def _set_labels(self, ax):
        self._g.Set('x/label', ax.get('xlabel'))
        self._g.Set('y/label', ax.get('ylabel'))

    def _set_title(self, ax):
        title_ = ax.get('title')
        if title_:
            label = self._g.Add('label')
            self._g.Set('%s/label' % label, title_)
            self._g.Set('%s/xPos' % label, 0.4)
            self._g.Set('%s/yPos' % label, 0.9)

    def _set_limits(self, ax):
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

    def _set_grid(self, ax):
        hide_grid = not ax.get('grid')
        self._g.Set('x/GridLines/hide', hide_grid)
        self._g.Set('y/GridLines/hide', hide_grid)

    def _replot(self):
        fig = self.gcf()
        # add Veusz attributes to current figure (if not already added):
        try: fig._g
        except: figure(self._attrs['curfig'])

        # set figure size:
        try:
            width, height = fig.get('size')
            self._g.Set('/width', str(width))
            self._g.Set('/height', str(height))
        except TypeError:
            # figure size is not given, use Veusz default figure size.
            pass

        # remove old page (if any) and create a new one:
        self._g.To('/') # make sure we are at root before we start
        try: self._g.Remove('/page1')
        except: pass
        self._g.To(self._g.Add('page'))

        rows, columns = fig.get('axshape')
        multiple_axes = False
        if not rows == columns == 1:
            self._g.To(self._g.Add('grid'))
            self._g.Set('rows', rows)
            self._g.Set('columns', columns)
            multiple_axes = True

        i = j = 1 # counters
        for ax in fig.get('axes').values():
            if multiple_axes:
                if j > rows*columns:
                    self._g.To('/page1')
                else:
                    self._g.To('/page1/grid1')
            else:
                self._g.To('/page1')
                
            use_legends = False
            plotitems = ax.get('plotitems')
            if len(plotitems) > 0:
                self._g.To(self._g.Add('graph'))
                if not multiple_axes or j > rows*columns:
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
                    color = self._colors[item.get('linecolor')]
                    self._g.Set('%s/PlotLine/color' % xy, color)
                    self._g.Set('%s/MarkerFill/color' % xy, color)

                    # set line type:
                    style = self._line_styles.get(item.get('linetype'), None)
                    if style:
                        self._g.Set('%s/PlotLine/style' % xy, style)
                    else:
                        self._g.Set('%s/PlotLine/hide' % xy, True)

                    # set line width:
                    width = item.get('linewidth')
                    if not width:
                        width = 0.5
                    self._g.Set('%s/PlotLine/width' % xy, str(width)+'pt')

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
                        #self._g.Set('%s/manualLevels' % cntr, cvector)
                        # setting manual levels doesn't seem to work
                        self._g.Set('%s/numLevels' % cntr, len(cvector))
                    else:
                        self._g.Set('%s/numLevels' % cntr, item.get('clevels'))

                    # set line properties:
                    style = self._line_styles.get(item.get('linetype'), None)
                    if not style:
                        style
                    color = self._colors[item.get('linecolor')]
                    width = item.get('linewidth')
                    if not width:
                        width = 1
                    self._g.Set('%s/lines' % cntr,
                                [(style, str(width)+'pt', color, False)])
                    
                    # set legend:
                    legend = item.get('legend')
                    if legend:
                        self._g.Set('%s/key' % srf, legend)
                        use_legends = True
                elif isinstance(item, Surface):
                    img = self._g.Add('image')

                    # set data:
                    self._g.SetData2D('values%d' % i, item.get('zdata'))
                    self._g.Set('%s/data' % img, 'values%d' % i)

                    self._g.Set('%s/colorMap' % img, 'spectrum')
                    
                    # set legend:
                    legend = item.get('legend')
                    if legend:
                        self._g.Set('%s/key' % img, legend)
                        use_legends = True
                else:
                    print "%s is not supported in the Veusz backend" % \
                          type(item)
                i += 1

            if use_legends:
                self._g.Add('key')

            j += 1
            
        if self.get('show'):
            self._g.window.showNormal()
        else:
            self._g.window.hide()

    def hardcopy(self, filename, **kwargs):
        """Supported extensions: '.eps', '.svg', and '.png'."""
        if 'color' in kwargs:
            self.set(color=kwargs['color'])
        color = self.get('color')
        if self.get('show'):
            self._replot()
        self._g.Export(filename, color=color)

    def show(self, full_gui=True, filename=None):
        """Redraw the current figure.

        Optional arguments:

        full_gui -- If this is True (default), the data in the current figure
                    will be stored in a veusz file (given in filename) and
                    then displayed in a full Veusz gui window.

        filename -- Sets the filename that is used for storing the temporary
                    veusz file (should be a '.vsz' extension).
        """
        self._replot()
        if full_gui:
            self._g.window.hide()
            if not filename:
                # no file given, create a temporary file:
                filename = tempfile.mktemp(suffix='.vsz')
            self.save(filename)
            os.system('veusz %s' % filename)

    def clf(self):
        """Clear current figure."""
        self._g.Close()
        BaseClass.clf(self)

    def closefig(self, fignr=None):
        """Close figure window."""
        if not fignr: # no figure given, close current figure
            fignr = self._attrs['curfig']
        fig = self._figs[fignr]
        fig._g.Close()
        del fig._g

    def closefigs(self):
        """Close all figure windows."""
        for fig in self._figs.values():
            fig._g.Close()
            del fig._g
        BaseClass.closefigs(self)

    def save(self, filename):
        """Save the current Veusz settings to file."""
        self._g.Save(filename)

plt = VeuszBackend()
use(plt, globals()) # Export public namespace of plt to globals()

def get_backend():
    return plt._g
