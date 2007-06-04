"""
This backend is based on the 2D graphics package Grace (available at
http://plasma-gate.weizmann.ac.il/Grace). The connection with Python is
handled by the grace_np.py module written by Michael Haggerty. This module
is for instance available in the pygrace module by Mike McKerns (see
http://www.its.caltech.edu/~mmckerns/software.html). Only curve plotting is
currently available, however, histograms and pie charts might be added in
the future. The Grace backend can be used by

  python somefile.py --SCITOOLS_easyviz_backend grace

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = grace

and then

  from scitools.all import *

or if just easyviz is needed

  from scitools.easyviz import *

REQUIREMENTS:

Grace
grace_np.py

Known issues:

- To be able to store a copy of a plot with the hardcopy command, one must
  disable safe mode with the -nosafe option when running Grace. One can do
  this by adding the following line to GraceProcess.__init__ in grace_np.py
  (e.g. at line 130):

    cmd = cmd + ('-nosafe',)

- PDF output does not seem to work (at least on my configuration).

Tip:

- One way to create axes at arbitrary positions is to use the axes command
  together with the viewport optional argument. In the Grace backend this
  argument should be given as the list [xmin,ymin,xmax,ymax] where (xmin,ymin)
  is the lower-left corner and (xmax,ymax) is the upper-right corner. An 
  example is provided next.

    >>> x = seq(-3,3,0.1)
    >>> subplot(2,2,3)
    >>> plot(x,x**2,'ro:2',x,8*sin(2*pi*x),'g',x,x**3,'mx')
    [<scitools.easyviz.common.Line object at 0xb15645ac>]
    >>> subplot(2,2,4)
    >>> plot(x,x**3,'r+',title='subplot(2,2,4)')
    [<scitools.easyviz.common.Line object at 0xb31596ac>]
    >>> ax = axes(viewport=[0.1, 0.55, 0.9, 0.9])
    >>> plot(ax,x,cos(x),'bd--',axis=[-2,4,-1,2]')

"""

from __future__ import division

from common import *
from scitools.globaldata import DEBUG, VERBOSE
from misc import _cmpPlotProperties

try:
    import grace_np
except ImportError:
    try:
        from pygrace import grace_np
    except ImportError:
        # grace_np is not available
        pass  # will fail later

def _cmpPlotProperties(a,b):
    """Sort cmp-function for PlotProperties"""
    plotorder = [Volume, Streams, Surface, Contours, VelocityVectors, Line] 
    assert isinstance(a, PlotProperties)
    assert isinstance(b, PlotProperties)
    assert len(PlotProperties.__class__.__subclasses__(PlotProperties)) == \
               len(plotorder) # Check all subclasses is in plotorder
    return cmp(plotorder.index(a.__class__),plotorder.index(b.__class__))


class GraceBackend(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self._init()
        
    def _init(self, *args, **kwargs):
        # Do initialization that is special for this backend
        
        # Set docstrings of all functions to the docstrings of BaseClass
        # The exception is if something is very different
        # Alex had a nice function for this.
        
        self.figure(self.get('curfig'))

        # convert tables for formatstrings:
        self._markers = {
            '': 0,   # no marker
            '.': 0,  # dot --> no marker
            'o': 1,  # circle
            'x': 9,  # cross
            '+': 8,  # plus sign
            '*': 10, # asterisk
            's': 2,  # square
            'd': 3,  # diamond
            '^': 4,  # triangle (up)
            'v': 6,  # triangle (down)
            '<': 5,  # triangle (left)
            '>': 7,  # triangle (right)
            'p': 2,  # pentagram --> square
            'h': 3,  # hexagram --> diamond
            }
                        
        self._colors = {
            '': 4,   # no color --> blue
            'r': 2,  # red
            'g': 3,  # green
            'b': 4,  # blue
            'c': 9,  # cyan
            'm': 10, # magenta
            'y': 5,  # yellow
            'k': 1,  # black
            'w': 0,  # white
            }
        
        self._line_styles = {
            '': None, # no line 
            '-': 1,   # solid line
            ':': 2,   # dotted line
            '-.': 6,  # dash-dot line
            '--': 4,  # dashed line
            }

        # convert table for colorbar location:
        self._colorbar_locations = {
            'North': None,
            'South': None,
            'East': None,
            'West': None,
            'NorthOutside': None,
            'SouthOutside': None,
            'EastOutside': None,
            'WestOutside': None,
            }

        if DEBUG:
            print "Setting backend standard variables"
            for disp in 'self._markers self._colors self._line_styles'.split():
                print disp, eval(disp)

    def _set_scale(self, ax):
        # set linear or logarithmic (base 10) axis scale
        if DEBUG:
            print "Setting scales"
        scale = ax.get('scale')
        if scale == 'loglog':
            # use logarithmic scale on both x- and y-axis
            self._g('xaxes scale logarithmic')
            self._g('yaxes scale logarithmic')
        elif scale == 'logx':
            # use logarithmic scale on x-axis and linear scale on y-axis
            self._g('xaxes scale logarithmic')
            self._g('yaxes scale normal')
            pass
        elif scale == 'logy':
            # use linear scale on x-axis and logarithmic scale on y-axis
            self._g('xaxes scale normal')
            self._g('yaxes scale logarithmic')
        elif scale == 'linear':
            # use linear scale on both x- and y-axis
            self._g('xaxes scale normal')
            self._g('yaxes scale normal')

    def _set_labels(self, ax):
        # add text labels for x-, y-, and z-axis
        if DEBUG:
            print "Setting labels"
        xlabel = ax.get('xlabel')
        ylabel = ax.get('ylabel')
        zlabel = ax.get('zlabel')
        self._g('xaxis label "%s"' % xlabel)
        self._g('yaxis label "%s"' % ylabel)
        if zlabel:
            # add a text label on z-axis
            pass
        
    def _set_title(self, ax):
        # add a title at the top of the axis
        if DEBUG:
            print "Setting title"
        title = ax.get('title')
        self._g('subtitle "%s"' % title)  # set title
    
    def _set_limits(self, ax):
        # set axis limits in x, y, and z direction
        if DEBUG:
            print "Setting axis limits"
        mode = ax.get('mode')
        if mode == 'auto':
            # let plotting package set 'nice' axis limits in the x, y,
            # and z direction. If this is not automated in the plotting
            # package, one can use the following limits:
            #xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            self._g('autoscale xaxes')
            self._g('autoscale yaxes')
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.get('xmin')
            xmax = ax.get('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits
                self._g('world xmin %s' % xmin)
                self._g('world xmax %s' % xmax)
            else:
                # let plotting package set x-axis limits or use
                #xmin, xmax = ax.get('xlim')
                self._g('autoscale xaxes')

            ymin = ax.get('ymin')
            ymax = ax.get('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                self._g('world ymin %s' % ymin)
                self._g('world ymax %s' % ymax)
            else:
                # let plotting package set y-axis limits or use
                #ymin, ymax = ax.get('ylim')
                self._g('autoscale yaxes')

            zmin = ax.get('zmin')
            zmax = ax.get('zmax')
            if zmin is not None and zmax is not None:
                # set z-axis limits
                pass
            else:
                # let plotting package set z-axis limits or use
                #zmin, zmax = ax.get('zlim')
                pass
        elif mode == 'tight':
            # set the limits on the axis to the range of the data. If
            # this is not automated in the plotting package, one can
            # use the following limits:
            xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            self._g('world xmin %s' % xmin)
            self._g('world xmax %s' % xmax)
            self._g('world ymin %s' % ymin)
            self._g('world ymax %s' % ymax)
        elif mode == 'fill':
            # not sure about this
            pass

    def _set_position(self, ax):
        # set axes position
        rect = ax.get('viewport')
        if rect:
            # axes position is defined. In Matlab rect is defined as
            # [left,bottom,width,height], where the four parameters are
            # location values between 0 and 1 ((0,0) is the lower-left
            # corner and (1,1) is the upper-right corner).
            # NOTE: This can be different in the plotting package.
            # In Grace the position is specified as [xmin,ymin,xmax,ymax],
            # where (xmin,ymin) is the lower-left corner and (xmax,ymin)
            # is the top-right corner.
            xmin, ymin, xmax, ymax = rect
            if not ax.get('pth'):
                self._g('view %s, %s, %s, %s' % (xmin, ymin, xmax, ymax))

    def _set_daspect(self, ax):
        # set data aspect ratio
        if ax.get('daspectmode') == 'manual':
            dar = ax.get('daspect')  # dar is a list (len(dar) is 3).
            pass
        else:
            # daspectmode is 'auto'. Plotting package handles data
            # aspect ratio automatically.
            pass
        
    def _set_axis_method(self, ax):
        method = ax.get('method')
        if method == 'equal':
            # tick mark increments on the x-, y-, and z-axis should
            # be equal in size.
            pass
        elif method == 'image':
            # same effect as axis('equal') and axis('tight')
            pass
        elif method == 'square':
            # make the axis box square in size
            pass
        elif method == 'normal':
            # full size axis box
            pass
        elif method == 'vis3d':
            # freeze data aspect ratio when rotating 3D objects
            pass

    def _set_coordinate_system(self, ax):
        # use either the default Cartesian coordinate system or a
        # matrix coordinate system.
        direction = ax.get('direction')
        if direction == 'ij':
            # use matrix coordinates. The origin of the coordinate
            # system is the upper-left corner. The i-axis should be
            # vertical and numbered from top to bottom, while the j-axis
            # should be horizontal and numbered from left to right.
            self._g('yaxes invert on')
        elif direction == 'xy':
            # use the default Cartesian axes form. The origin is at the
            # lower-left corner. The x-axis is vertical and numbered
            # from left to right, while the y-axis is vertical and
            # numbered from bottom to top.
            self._g('yaxes invert off')

    def _set_box(self, ax):
        # turn box around axes boundary on or off
        if DEBUG:
            print "Setting box"
        if ax.get('box'):
            # display box 
            pass
        else:
            # do not display box
            pass
        
    def _set_grid(self, ax):
        # turn grid lines on or off
        if DEBUG:
            print "Setting grid"
        if ax.get('grid'):
            # turn grid lines on
            self._g('xaxis tick major linestyle 2')
            self._g('xaxis tick major grid on')
            self._g('yaxis tick major linestyle 2')
            self._g('yaxis tick major grid on')
        else:
            # turn grid lines off
            self._g('xaxis tick major linestyle 1')
            self._g('xaxis tick major grid off')
            self._g('yaxis tick major linestyle 1')
            self._g('yaxis tick major grid off')

    def _set_hidden_line_removal(self, ax):
        # turn on/off hidden line removal for meshes
        if DEBUG:
            print "Setting hidden line removal"
        if ax.get('hidden'):
            # turn hidden line removal on
            pass
        else:
            # turn hidden line removal off
            pass

    def _set_colorbar(self, ax):
        # add a colorbar to the axis
        if DEBUG:
            print "Setting colorbar"
        cbar = ax.get('colorbar')
        if cbar.get('visible'):
            # turn on colorbar
            cbar_title = cbar.get('cbtitle')
            cbar_location = self._colorbar_locations[cbar.get('cblocation')]
            # ...
        else:
            # turn off colorbar
            pass

    def _set_caxis(self, ax):
        # set the color axis scale
        if DEBUG:
            print "Setting caxis"
        if ax.get('caxismode') == 'manual':
            cmin, cmax = ax.get('caxis')
            # NOTE: cmin and cmax might be None:
            if cmin is None or cmax is None:
                cmin, cmax = [0,1]
            # set color axis scaling according to cmin and cmax
            pass
        else:
            # use autoranging for color axis scale
            pass

    def _set_colormap(self, ax):
        # set the colormap
        if DEBUG:
            print "Setting colormap"
        cmap = ax.get('colormap')
        # cmap is plotting package dependent

    def _set_view(self, ax):
        # set viewpoint specification
        if DEBUG:
            print "Setting view"
        cam = ax.get('camera')
        view = cam.get('view')
        if view == 2:
            # setup a default 2D view
            pass
        elif view == 3:
            az = cam.get('azimuth')
            el = cam.get('elevation')
            if az is None or el is None:
                # azimuth or elevation is not given. Set up a default
                # 3D view (az=-37.5 and el=30 is the default 3D view in
                # Matlab).
                pass
            else:
                # set a 3D view according to az and el
                pass
            
            if cam.get('cammode') == 'manual':
                # for advanced camera handling:
                roll = cam.get('camroll')
                zoom = cam.get('camzoom')
                dolly = cam.get('camdolly')
                target = cam.get('camtarget')
                position = cam.get('campos')
                up_vector = cam.get('camup')
                view_angle = cam.get('camva')
                projection = cam.get('camproj')

    def _set_axis_props(self, ax):
        if DEBUG:
            print "Setting axis properties"
        self._set_title(ax)
        self._set_scale(ax)
        self._set_limits(ax)
        self._set_position(ax)
        self._set_axis_method(ax)
        self._set_daspect(ax)
        self._set_coordinate_system(ax)
        self._set_hidden_line_removal(ax)
        self._set_colorbar(ax)
        self._set_caxis(ax)
        self._set_colormap(ax)
        self._set_view(ax)
        if ax.get('visible'):
            self._set_labels(ax)
            self._set_box(ax)
            self._set_grid(ax)
            self._g('xaxis bar on')
            self._g('xaxis tick on')
            self._g('xaxis ticklabel on')
            self._g('yaxis bar on')
            self._g('yaxis tick on')
            self._g('yaxis ticklabel on')
        else:
            # turn off all axis labeling, tickmarks, and background
            self._g('xaxis bar off')
            self._g('xaxis label ""')
            self._g('xaxis tick off')
            self._g('xaxis ticklabel off')
            self._g('yaxis bar off')
            self._g('yaxis label ""')
            self._g('yaxis tick off')
            self._g('yaxis ticklabel off')
            self._g('xaxis tick major linestyle 1')
            self._g('xaxis tick major grid off')
            self._g('yaxis tick major linestyle 1')
            self._g('yaxis tick major grid off')
            # TODO: How do we turn off axes lines?

    def _get_linespecs(self, item):
        # return the item's line marker, line color, line style, and
        # line width.
        marker = self._markers[item.get('linemarker')]
        color = self._colors[item.get('linecolor')]
        style = self._line_styles[item.get('linetype')]
        width = item.get('linewidth')
        return marker, color, style, width

    def _add_line(self, item, name):
        # add a 2D or 3D curve to the scene
        if DEBUG:
            print "Adding a line"
        # get data:
        x = item.get('xdata')
        y = item.get('ydata')
        z = item.get('zdata')
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)
 
        self._g('s%s on' % name)
        self._g('s%s symbol %s' % (name,marker))
        self._g('s%s symbol fill pattern 0' % name)
        self._g('s%s symbol size 0.6' % name)
        self._g('s%s symbol color %s' % (name,color))
        self._g('s%s line color %s' % (name,color))
        if style is not None:
            self._g('s%s linestyle %s' % (name,style))
        else:
            if not marker:
                self._g('s%s linestyle 1' % name)  # solid line
            else:
                self._g('s%s linestyle 0' % name)  # no line
        if not width:
            width = 1.0
        self._g('s%s linewidth %s' % (name,width))

        if z is not None:
            # zdata is given, add a 3D curve:
            pass
        else:
            # no zdata, add a 2D curve:
            for i in range(len(x)):
                self._g('s%s point %s, %s' % (name, x[i], y[i]))

        legend = item.get('legend')
        self._g('s%s legend "%s"' % (name,legend))
           
    def _add_surface(self, item, shading='faceted'):
        if DEBUG:
            print "Adding a surface"
        x = item.get('xdata')  # grid component in x-direction
        y = item.get('ydata')  # grid component in y-direction
        z = item.get('zdata')  # scalar field
        c = item.get('cdata')  # pseudocolor data (can be None)
        
        contours = item.get('contours')
        if contours:
            # the current item is produced by meshc or surfc and we
            # should therefore add contours at the bottom:
            self._add_contours(contours, placement='bottom')

        if item.get('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            pass
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            pass

    def _add_contours(self, item, placement=None):
        # The placement keyword can be either None or 'bottom'. The
        # latter specifies that the contours should be placed at the
        # bottom (as in meshc or surfc).
        if DEBUG:
            print "Adding contours"
        x = item.get('xdata')  # grid component in x-direction
        y = item.get('ydata')  # grid component in y-direction
        z = item.get('zdata')  # scalar field

        filled = item.get('filled')  # draw filled contour plot if True

        cvector = item.get('cvector')
        clevels = item.get('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            pass

        location = item.get('clocation')
        if location == 'surface':
            # place the contours at the corresponding z level (contour3)
            pass
        elif location == 'base':
            if placement == 'bottom':
                # place the contours at the bottom (as in meshc or surfc)
                pass
            else:
                # standard contour plot
                pass

        if item.get('clabels'):
            # add labels on the contour curves
            pass
    
    def _add_vectors(self, item):
        if DEBUG:
            print "Adding vectors"
        # uncomment the following command if there is no support for
        # automatic scaling of vectors in the current plotting package:
        #item.scale_vectors()

        # grid components:
        x, y, z = item.get('xdata'), item.get('ydata'), item.get('zdata')
        # vector components:
        u, v, w = item.get('udata'), item.get('vdata'), item.get('wdata')
        # get line specifiactions (marker='.' means no marker):
        marker, color, style, width = self._get_linespecs(item)

        # scale the vectors according to this variable (scale=0 should
        # turn off automatic scaling):
        scale = item.get('arrowscale')

        filled = item.get('filledarrows') # draw filled arrows if True

        if z is not None and w is not None:
            # draw velocity vectors as arrows with components (u,v,w) at
            # points (x,y,z):
            pass
        else:
            # draw velocity vectors as arrows with components (u,v) at
            # points (x,y):
            pass

    def _add_streams(self, item):
        if DEBUG:
            print "Adding streams"
        # grid components:
        x, y, z = item.get('xdata'), item.get('ydata'), item.get('zdata')
        # vector components:
        u, v, w = item.get('udata'), item.get('vdata'), item.get('wdata')
        # starting positions for streams:
        sx, sy, sz = item.get('startx'), item.get('starty'), item.get('startz')

        if item.get('tubes'):
            # draw stream tubes from vector data (u,v,w) at points (x,y,z)
            n = item.get('n') # no points along the circumference of the tube
            scale = item.get('tubescale')
            pass
        elif item.get('ribbons'):
            # draw stream ribbons from vector data (u,v,w) at points (x,y,z)
            width = item.get('ribbonwidth')
            pass
        else:
            if z is not None and w is not None:
                # draw stream lines from vector data (u,v,w) at points (x,y,z)
                pass
            else:
                # draw stream lines from vector data (u,v) at points (x,y)
                pass
            pass

    def _add_isosurface(self, item):
        if DEBUG:
            print "Adding a isosurface"
        # grid components:
        x, y, z = item.get('xdata'), item.get('ydata'), item.get('zdata')
        v = item.get('vdata')  # volume
        c = item.get('cdata')  # pseudocolor data
        isovalue = item.get('isovalue')

    def _add_slices(self, item):
        if DEBUG:
            print "Adding slices in a volume"
        # grid components:
        x, y, z = item.get('xdata'), item.get('ydata'), item.get('zdata')
        v = item.get('vdata')  # volume

        sx, sy, sz = item.get('slices')
        if rank(sz) == 2:
            # sx, sy, and sz defines a surface
            pass
        else:
            # sx, sy, and sz is either numbers or vectors with numbers
            pass
        pass

    def _add_contourslices(self, item):
        if DEBUG:
            print "Adding contours in slice planes"
        # grid components:
        x, y, z = item.get('xdata'), item.get('ydata'), item.get('zdata')
        v = item.get('vdata')  # volume

        sx, sy, sz = item.get('slices')
        if rank(sz) == 2:
            # sx, sy, and sz defines a surface
            pass
        else:
            # sx, sy, and sz is either numbers or vectors with numbers
            pass

        cvector = item.get('cvector')
        clevels = item.get('clevels')  # number of contour levels per plane
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            pass
        pass

    def _set_figure_size(self, fig):
        if DEBUG:
            print "Setting figure size"
        width, height = fig.get('size')
        if width and height:
            # set figure width and height
            self._g('page resize %s, %s' % (width,height))
        else:
            # use the default width and height in plotting package
            pass

    def figure(self, *args, **kwargs):
        # Extension of BaseClass.figure:
        # add a plotting package figure instance as fig._g and create a
        # link to it as object._g
        BaseClass.figure(self, *args, **kwargs) 
        fig = self.gcf()
        try:
            fig._g
        except:
            # create plotting package figure and save figure instance
            # as fig._g
            if DEBUG:
                name = 'Fig ' + str(self.get('curfig'))
                print "creating figure %s in backend" % name

            fig._g = grace_np.GraceProcess()
            fig._g._no_lines_in_graph = []
            
        self._g = fig._g # link for faster access

    figure.__doc__ = BaseClass.figure.__doc__
        
    def _replot(self):
        # Replot all axes and all plotitems in the backend.
        # NOTE: only the current figure (gcf) is redrawn.
        if DEBUG:
            print "Doing replot in backend"
        
        fig = self.gcf()
        # add Grace attributes to current figure (if not already added):
        try:
            fig._g
        except: 
            self.figure(self.get('curfig'))
            
        # reset the plotting package instance in fig._g:
        no_lines = fig._g._no_lines_in_graph
        no_graphs = len(no_lines)
        # erase all lines in every graph:
        for g in range(no_graphs):
            for i in range(no_lines[g]):
                fig._g('kill g%s.s%s' % (g,i))
        no_graphs = len(fig.get('axes'))
        fig._g._no_lines_in_graph = [0]*no_graphs
        
        self._set_figure_size(fig)
        
        hgap = 0.5
        vgap = 0.6
        offset = 0.1
        nrows, ncolumns = fig.get('axshape')
        fig._g('arrange(%s, %s, %s, %s, %s)' % \
               (nrows, ncolumns, offset, hgap, vgap))
        for axnr, ax in fig.get('axes').items():
            curr_graph = axnr-1
            numberofitems = ax.get('numberofitems')
            pth = ax.get('pth')
            if pth:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,pth)
                fig._g('focus g%s' % curr_graph)
                fig._g('with g%s' % curr_graph)
                if numberofitems == 0:
                    self._g('g%s hidden true' % curr_graph)
            else:
                fig._g('with g%s' % curr_graph)
                fig._g('g%s on' % curr_graph)
            i = 0
            legends = []
            plotitems = ax.get('plotitems')
            plotitems.sort(_cmpPlotProperties)
            for item in plotitems:
                name = str(i)
                func = item.get('function') # function that produced this item
                if isinstance(item, Line):
                    self._add_line(item, name)
                    fig._g._no_lines_in_graph[curr_graph] += 1
                elif isinstance(item, Surface):
                    self._add_surface(item, shading=ax.get('shading'))
                elif isinstance(item, Contours):
                    self._add_contours(item)
                elif isinstance(item, VelocityVectors):
                    self._add_vectors(item)
                elif isinstance(item, Streams):
                    self._add_streams(item)
                elif isinstance(item, Volume):
                    if func == 'isosurface':
                        self._add_isosurface(item)
                    elif func == 'slice_':
                        self._add_slices(item)
                    elif func == 'contourslice':
                        self._add_contourslices(item)
                legend = item.get('legend')
                if legend:
                    # add legend to plot
                    legends.append(legend)
                i += 1
                
            if numberofitems > 0:
                self._g('autoscale')
                self._set_axis_props(ax)
                if legends:
                    self._g('legend on')

        if self.get('show'):
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            pass
        self._g('redraw')

    def hardcopy(self, filename, **kwargs):
        """
        Supported extensions in the Grace backend: 

          '.ps'  (PostScript)
          '.eps' (Encapsualted PostScript)
          '.pdf' (Portable Document Format)
          '.agr' (Grace file format)
          '.jpg' (Joint Photographic Experts Group)
          '.png' (Portable Network Graphics)
          '.pnm' (Portable Any Map)
          '.svg' (Scalable Vector Graphics)
          '.gmf' (Graphics Meta File)
          '.mif' (Maker Interchange Format)

        Optional arguments:

          size        -- A tuple (width,height) to set the size of the image.
                         The default is to use the Grace default.
                         
          dpi         -- Dots per inch (Grace default is used as default).
          
          antialiase  -- Enable (True) or disable (False) font antialiasing.
                         Default is to enable antialiasing.
                         
          color       -- True (colors) or False (grayscale).
          
          orientation -- 'portrait' or 'landscape' (default). Only available
                         for PostScript output.
                         
          quality     -- Integer between 0 and 100 (default). Sets the quality
                         in a JPEG image.

        """
        self.set(**kwargs)
        color = self.get('color')
        self._replot()

        if DEBUG:
            print "Hardcopy to %s" % filename

        ext2dev = {'.agr': 'agr', '.eps': 'EPS', '.jpg': 'JPEG',
                   '.gmf': 'Metafile', '.mif': 'MIF', '.pdf': 'PDF',
                   '.png': 'PNG', '.pnm': 'PNM', '.ps': 'PostScript',
                   '.svg': 'SVG'}

        basename, ext = os.path.splitext(filename)
        if not ext:
            ext = '.ps'  # no extension given, assume .ps
            filename += ext
        elif ext not in ext2dev:
            raise ValueError, "hardcopy: extension must be %s, not '%s'" % \
                  (ext2dev.keys(), ext)

        device = ext2dev[ext]
        if ext == '.agr':
            self._g('saveall "%s"' % filename)
        else:
            self._g('hardcopy device "%s"' % device)
            width, height = kwargs.get('size', (None,None))
            if width and height:
                self._g('device "%s" page size %s, %s' % (device,width,height))
            dpi = kwargs.get('dpi', None)
            if dpi:
                self._g('device "%s" dpi %s' % (device,dpi))
            antialiase = kwargs.get('antialiase', True)
            if antialiase:
                self._g('device "%s" font antialiasing on' % device)
            else:
                self._g('device "%s" font antialiasing off' % device)
            if device in ['EPS', 'PostScript', 'JPEG']:
                colormode = 'color'
                if not color:
                    colormode = 'grayscale'
                self._g('device "%s" op "%s"' % (device,colormode))
            if device in ['EPS', 'PostScript']:
                pass # set orientation
            if device in ['JPEG']:
                quality = kwargs.get('quality', 100)
                self._g('device "%s" op "quality:%d"' % (device,quality))
            if device in ['PNM']:
                format = 'ppm'
                if not color:
                    format = 'pgm'
                self._g('device "%s" op "format:%s"' % (device,format))
            self._g('print to "%s"' % filename)
            self._g('print')

    hardcopy.__doc__ = BaseClass.hardcopy.__doc__ + hardcopy.__doc__

    def _close(self, fig):
        try:
            fig._g.exit()
        except OSError, msg:
            print msg
    
    def clf(self):
        fig = gcf()
        self._close(fig)
        del fig._g
        BaseClass.clf(self)

    def closefig(self, num=None):
        if not num:  # no figure given, close current figure
            num = self._attrs['curfig']
        fig = self._figs[num]
        self._close(fig)
        del fig._g

    def closefigs(self):
        for num in self._figs.keys():
            self.closefig(num)
        BaseClass.closefigs(self)

    # implement colormap functions here
    #def jet(self, m=None):
    #    """Variant of hsv."""
    #    pass
    

plt = GraceBackend()  # create backend instance
use(plt, globals())   # export public namespace of plt to globals()
