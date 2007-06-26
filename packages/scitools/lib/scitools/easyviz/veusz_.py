"""
This backend is based on the scientific plotting package Veusz. One can use
this backend by

  python somefile.py --SCITOOLS_easyviz_backend veusz

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = veusz

and then

  from scitools.all import *

or if just easyviz is needed

  from scitools.easyviz import *

REQUIREMENTS:

Veusz 0.10

TODO:

- update to version 0.99 of Veusz

Known issues:

- If an image of a 2D dataset (for instance created by pcolor) is drawn before
  a curve or contour lines, then these will be completely hidden by the image.
  This can be fixed by moving the image down the tree in the Veusz gui.

- savefig does not work

Tip:

- Here is an example on how to create axes at arbitrary positions in the
  Veusz backend:

    >>> x = linspace(0,1,51)
    >>> y1 = sin(2*pi*x)
    >>> y2 = cos(4*pi*x)
    >>> plot(x, y1, 'rd-')
    [<scitools.easyviz.common.Line object at 0xb65694ac>]
    >>> hold('on')
    >>> ax = axes(viewport=['9cm','9cm','1cm','2cm'])
    >>> plot(ax, x, y2, 'b--')
    [<scitools.easyviz.common.Line object at 0xb2c36d0c>]
    >>> 

  The optional argument viewport to the axes command must specify a list with
  four elements [left,bottom,right,top] where each of the elements defines
  the margins around the axes.

"""

from __future__ import division

from common import *
from scitools.globaldata import DEBUG, VERBOSE
from misc import _cmpPlotProperties

import veusz.embed
import os


def _cmpPlotProperties(a,b):
    """Sort cmp-function for PlotProperties"""
    plotorder = [Volume, Streams, Surface, Contours, VelocityVectors, Line] 
    assert isinstance(a, PlotProperties)
    assert isinstance(b, PlotProperties)
    assert len(PlotProperties.__class__.__subclasses__(PlotProperties)) == \
               len(plotorder) # Check all subclasses is in plotorder
    return cmp(plotorder.index(a.__class__),plotorder.index(b.__class__))


class VeuszBackend(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self._init()
        
    def _init(self, *args, **kwargs):
        """Perform initialization that is special for this backend."""
        
        # Set docstrings of all functions to the docstrings of BaseClass
        # The exception is if something is very different
        

        # Calling figure method here makes the program halt.
        #self.figure(self.get('curfig'))

        # conversion tables for format strings:
        self._markers = {
            '': None,            # no marker
            '.': 'dot',          # dot
            'o': 'circle',       # circle
            'x': 'linecross',    # cross
            '+': 'lineplus',     # plus sign
            '*': 'asterisk',     # asterisk
            's': 'square',       # square
            'd': 'diamond',      # diamond
            '^': 'triangle',     # triangle (up)
            'v': 'triangledown', # triangle (down) 
            '<': 'triangle',     # triangle (left) --> up
            '>': 'triangledown', # triangle (right) --> down
            'p': 'star',         # pentagram
            'h': 'cross',        # hexagram --> filled cross
            }
                                 
        self._colors = {
            '': None,       # no color --> blue
            'r': 'red',     # red
            'g': 'green',   # green
            'b': 'blue',    # blue
            'c': 'cyan',    # cyan
            'm': 'magenta', # magenta
            'y': 'yellow',  # yellow
            'k': 'black',   # black
            'w': 'white',   # white
            }

        self._line_styles = {
            '': None,         # no line 
            '-': 'solid',     # solid line
            ':': 'dotted',    # dotted line
            '-.': 'dash-dot', # dash-dot line
            '--': 'dashed',   # dashed line
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
        """Set linear or logarithmic (base 10) axis scale."""
        if DEBUG:
            print "Setting scales"
        scale = ax.get('scale')
        if scale == 'loglog':
            # use logarithmic scale on both x- and y-axis
            self._g.Set('x/log', True)
            self._g.Set('y/log', True)
        elif scale == 'logx':
            # use logarithmic scale on x-axis and linear scale on y-axis
            self._g.Set('x/log', True)
            self._g.Set('y/log', False)
        elif scale == 'logy':
            # use linear scale on x-axis and logarithmic scale on y-axis
            self._g.Set('x/log', False)
            self._g.Set('y/log', True)
        elif scale == 'linear':
            # use linear scale on both x- and y-axis
            self._g.Set('x/log', False)
            self._g.Set('y/log', False)

    def _set_labels(self, ax):
        """Add text labels for x-, y-, and z-axis."""
        if DEBUG:
            print "Setting labels"
        xlabel = ax.get('xlabel')
        ylabel = ax.get('ylabel')
        zlabel = ax.get('zlabel')
        fontsize = ax.get('fontsize')
        if xlabel:
            # add a text label on x-axis
            self._g.Set('x/label', xlabel)
            self._g.Set('x/Label/size', str(fontsize))
        if ylabel:
            # add a text label on y-axis
            self._g.Set('y/label', ylabel)
            self._g.Set('y/Label/size', str(fontsize))
        if zlabel:
            # add a text label on z-axis
            pass
        
    def _set_title(self, ax):
        """Add a title at the top of the axis."""
        if DEBUG:
            print "Setting title"
        title = ax.get('title')
        if title:
            # set title
            label = self._g.Add('label')
            self._g.Set('%s/label' % label, title)
            self._g.Set('%s/xPos' % label, 0.1)
            self._g.Set('%s/yPos' % label, 1.01)
    
    def _set_limits(self, ax):
        """Set axis limits in x, y, and z direction."""
        if DEBUG:
            print "Setting axis limits"
        mode = ax.get('mode')
        if mode == 'auto':
            # let plotting package set 'nice' axis limits in the x, y,
            # and z direction. If this is not automated in the plotting
            # package, one can use the following limits:
            #xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            pass
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.get('xmin')
            xmax = ax.get('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits
                self._g.Set('x/min', xmin)
                self._g.Set('x/max', xmax)
            else:
                # let plotting package set x-axis limits or use
                #xmin, xmax = ax.get('xlim')
                pass

            ymin = ax.get('ymin')
            ymax = ax.get('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                self._g.Set('y/min', ymin)
                self._g.Set('y/max', ymax)
            else:
                # let plotting package set y-axis limits or use
                #ymin, ymax = ax.get('ylim')
                pass

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
            self._g.Set('x/min', xmin)
            self._g.Set('x/max', xmax)
            self._g.Set('y/min', ymin)
            self._g.Set('y/max', ymax)
        elif mode == 'fill':
            # not sure about this
            pass

    def _set_position(self, ax):
        """Set axes position."""
        rect = ax.get('viewport')
        if not ax.get('pth'):
            if rect:
                # axes position is defined. In Matlab rect is defined as
                # [left,bottom,width,height], where the four parameters are
                # location values between 0 and 1 ((0,0) is the lower-left
                # corner and (1,1) is the upper-right corner).
                # NOTE: This can be different in the plotting package.
                # In Veusz, rect should be defined as [left,bottom,right,top]
                # left, bottom, right, and top are strings defining the
                # graph margins.
                left, bottom, right, top = rect
                self._g.Set('leftMargin', str(left))
                self._g.Set('rightMargin', str(right))
                self._g.Set('topMargin', str(top))
                self._g.Set('bottomMargin', str(bottom))
            else:
                self._g.Set('leftMargin', '1.5cm')
                self._g.Set('rightMargin', '0.1cm')
                self._g.Set('topMargin', '0.9cm')
                self._g.Set('bottomMargin', '1.5cm')

    def _set_daspect(self, ax):
        """Set data aspect ratio."""
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
        """
        Use either the default Cartesian coordinate system or a
        matrix coordinate system.
        """
        
        direction = ax.get('direction')
        if direction == 'ij':
            # Use matrix coordinates. The origin of the coordinate
            # system is the upper-left corner. The i-axis should be
            # vertical and numbered from top to bottom, while the j-axis
            # should be horizontal and numbered from left to right.
            pass
        elif direction == 'xy':
            # use the default Cartesian axes form. The origin is at the
            # lower-left corner. The x-axis is vertical and numbered
            # from left to right, while the y-axis is vertical and
            # numbered from bottom to top.
            pass

    def _set_box(self, ax):
        """Turn box around axes boundary on or off."""
        if DEBUG:
            print "Setting box"
        if ax.get('box'):
            # display box 
            pass
        else:
            # do not display box
            pass
        
    def _set_grid(self, ax):
        """Turn grid lines on or off."""
        if DEBUG:
            print "Setting grid"
        if ax.get('grid'):
            # turn grid lines on
            self._g.Set('x/GridLines/hide', False)
            self._g.Set('y/GridLines/hide', False)
        else:
            # turn grid lines off
            self._g.Set('x/GridLines/hide', True)
            self._g.Set('y/GridLines/hide', True)

    def _set_hidden_line_removal(self, ax):
        """Turn on/off hidden line removal for meshes."""
        if DEBUG:
            print "Setting hidden line removal"
        if ax.get('hidden'):
            # turn hidden line removal on
            pass
        else:
            # turn hidden line removal off
            pass

    def _set_colorbar(self, ax):
        """Add a colorbar to the axis."""
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
        """Set the color axis scale."""
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
        """Set the colormap."""
        if DEBUG:
            print "Setting colormap"
        cmap = ax.get('colormap')
        # cmap is plotting package dependent

    def _set_view(self, ax):
        """Set viewpoint specification."""
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
            fontsize = ax.get('fontsize')
            self._g.Set('x/TickLabels/size', '%spt' % fontsize)
            self._g.Set('y/TickLabels/size', '%spt' % fontsize)
        else:
            # turn off all axis labeling, tickmarks, and background
            self._g.Set('x/Line/hide', True)
            self._g.Set('y/Line/hide', True)
            self._g.Set('x/MajorTicks/hide', True)
            self._g.Set('y/MajorTicks/hide', True)
            self._g.Set('x/MinorTicks/hide', True)
            self._g.Set('y/MinorTicks/hide', True)
            self._g.Set('x/TickLabels/hide', True)
            self._g.Set('y/TickLabels/hide', True)
            self._g.Set('Border/hide', True)
        # set background color off:
        self._g.Set('Background/hide', True)

    def _get_linespecs(self, item):
        """
        Return the line marker, line color, line style, and
        line width of the item.
        """
        
        marker = self._markers[item.get('linemarker')]
        color = self._colors[item.get('linecolor')]
        style = self._line_styles[item.get('linetype')]
        width = item.get('linewidth')
        return marker, color, style, width

    def _add_line(self, item, name):
        """Add a 2D or 3D curve to the scene."""
        if DEBUG:
            print "Adding a line"
        # get data:
        x = item.get('xdata')
        y = item.get('ydata')
        z = item.get('zdata')
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        xy = self._g.Add('xy')
        if marker:
            self._g.Set('%s/marker' % xy, marker)
            self._g.Set('%s/MarkerLine/color' % xy, color)
            self._g.Set('%s/MarkerFill/hide' % xy, True)
            if not style:
                self._g.Set('%s/PlotLine/hide' % xy, True)
            else:
                self._g.Set('%s/PlotLine/style' % xy, style)
        else:
            self._g.Set('%s/marker' % xy, 'none')
            if not style:
                style = 'solid'
            self._g.Set('%s/PlotLine/style' % xy, style)
        self._g.Set('%s/PlotLine/color' % xy, color)
        if not width:
            width = 0.5
        self._g.Set('%s/PlotLine/width' % xy, str(width)+'pt')
        
        if z is not None:
            # zdata is given, add a 3D curve:
            pass
        else:
            # no zdata, add a 2D curve:
            self._g.SetData('x%s' % name, x)
            self._g.SetData('y%s' % name, y)
            self._g.Set('%s/xData' % xy, 'x%s' % name)
            self._g.Set('%s/yData' % xy, 'y%s' % name)

        legend = item.get('legend')
        if legend:
            self._g.Set('%s/key' % xy, legend)

    def _add_surface(self, item, name, shading='faceted', cmap=None):
        if DEBUG:
            print "Adding a surface"
        x = item.get('xdata')  # grid component in x-direction
        y = item.get('ydata')  # grid component in y-direction
        z = item.get('zdata')  # scalar field
        c = item.get('cdata')  # pseudocolor data (can be None)
        
        img = self._g.Add('image')
                    
        contours = item.get('contours')
        if contours:
            # the current item is produced by meshc or surfc and we
            # should therefore add contours at the bottom:
            #self._add_contours(contours, placement='bottom')
            pass

        self._g.SetData2D('values%s' % name, z)

        if item.get('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            pass
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            self._g.Set('%s/data' % img, 'values%s' % name)
        if cmap is None:
            cmap = 'spectrum'
        self._g.Set('%s/colorMap' % img, cmap)
        
        legend = item.get('legend')
        if legend:
            self._g.Set('%s/key' % img, legend)

    def _add_contours(self, item, name, placement=None):
        # The placement keyword can be either None or 'bottom'. The
        # latter specifies that the contours should be placed at the
        # bottom (as in meshc or surfc).
        if DEBUG:
            print "Adding contours"
        x = item.get('xdata')  # grid component in x-direction
        y = item.get('ydata')  # grid component in y-direction
        z = item.get('zdata')  # scalar field
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        filled = item.get('filled')  # draw filled contour plot if True
        
        cntr = self._g.Add('contour')

        # set line properties:
        if not width:
            width = 0.5
        width = str(width) + 'pt'
        if not style:
            style = 'solid'
        if not color:
            color = 'black'
        self._g.Set('%s/lines' % cntr, [(style, width, color, False)])

        if filled:
            self._g.Set('%s/fills' % cntr,
                        [('solid', color, False), ('solid', 'white', False)])

        cvector = item.get('cvector')
        clevels = item.get('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            self._g.Set('%s/numLevels' % cntr, clevels)
        else:
            #self._g.Set('%s/manualLevels' % cntr, cvector)
            # setting manual levels doesn't seem to work
            self._g.Set('%s/numLevels' % cntr, len(cvector))

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

        self._g.SetData2D('values%s' % name, z)
        self._g.Set('%s/data' % cntr, 'values%s' % name)

        legend = item.get('legend')
        if legend:
            self._g.Set('%s/key' % cntr, legend)
    
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
            self._g.Set('/width', str(width))
            self._g.Set('/height', str(height))
        else:
            # use the default width and height in plotting package
            pass

    def figure(self, *args, **kwargs):
        # Extension of BaseClass.figure:
        # add a plotting package figure instance as fig._g and create a
        # link to it as self._g
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

            name = 'Fig ' + str(self.get('curfig'))
            fig._g = veusz.embed.Embedded(name)
            fig._g.EnableToolbar(enable=True)
            fig._g.window.hide()
            
        self._g = fig._g # link for faster access

    figure.__doc__ = BaseClass.figure.__doc__
        
    def _replot(self):
        """Replot all axes and all plotitems in the backend."""
        # NOTE: only the current figure (gcf) is redrawn.
        if DEBUG:
            print "Doing replot in backend"

        fig = self.gcf()
        # add Veusz attributes to current figure (if not already added):
        try:
            fig._g
        except: 
            self.figure(self.get('curfig'))
        
        self._g.To('/') # make sure we are at root before we start
        
        # reset the plotting package instance in fig._g now if needed
        try:
            self._g.Remove('/page1')
        except:
            pass
        self._g.To(self._g.Add('page'))
        
        self._set_figure_size(fig)

        i = 1
        nrows, ncolumns = fig.get('axshape')
        if nrows != 1 or ncolumns != 1:
            self._g.To(self._g.Add('grid'))
            self._g.Set('rows', nrows)
            self._g.Set('columns', ncolumns)
            self._g.Set('leftMargin', '0.4cm')
            self._g.Set('rightMargin', '0.1cm')
            self._g.Set('topMargin', '0.7cm')
            self._g.Set('bottomMargin', '0.1cm')
        for axnr, ax in fig.get('axes').items():
            legends = False
            pth = ax.get('pth')
            if pth:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,pth)
                self._g.To('/page1/grid1')
            else:
                self._g.To('/page1')
            self._g.To(self._g.Add('graph'))
            plotitems = ax.get('plotitems')
            plotitems.sort(_cmpPlotProperties)
            for item in plotitems:
                name = str(i)
                func = item.get('function') # function that produced this item
                if isinstance(item, Line):
                    self._add_line(item, name)
                elif isinstance(item, Surface):
                    self._add_surface(item, name,
                                      shading=ax.get('shading'),
                                      cmap=ax.get('colormap'))
                elif isinstance(item, Contours):
                    self._add_contours(item, name)
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
                    legends = True
                i += 1

            if legends:
                key = self._g.Add('key')
                self._g.Set('%s/horzPosn' % key, 'right')
                self._g.Set('%s/vertPosn' % key, 'top')
                self._g.Set('%s/Text/size' % key, ax.get('fontsize'))
            self._set_axis_props(ax)
                    
        if self.get('show'):
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            self._g.window.showNormal()
        else:
            self._g.window.hide()

    def hardcopy(self, filename, **kwargs):
        """
        Supported extensions:

          '.eps'  (Encapsulated PostScript)
          '.svg'  (Scalable Vector Graphics)
          '.png'  (Portable Network Graphics)

        Optional keyword arguments:

          color -- True (colors) or False (gray-scale).
          
        """
        self.set(**kwargs)
        color = self.get('color')
        self._replot()

        if DEBUG:
            print "Hardcopy to %s" % filename
            
        self._g.Export(filename, color=color)

    hardcopy.__doc__ = BaseClass.hardcopy.__doc__ + hardcopy.__doc__

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

    # implement colormap functions here
    def jet(self, m=None):
        return 'spectrum'

    def hot(self, m=None):
        return 'heat'

    def gray(self, m=None):
        return 'grey'
    

plt = VeuszBackend()  # create backend instance
use(plt, globals())   # export public namespace of plt to globals()
