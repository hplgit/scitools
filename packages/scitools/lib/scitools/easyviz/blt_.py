"""
This backend uses Blt through Pmw (Python Mega Widgets). One can use this
backend by 

  python somefile.py --SCITOOLS_easyviz_backend blt

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = blt

and then

  from scitools.all import *

or if just easyviz is needed

  from scitools.easyviz import *


The Pmw.Blt user's guide is located at
http://folk.uio.no/hpl/Pmw.Blt/doc/

The documentation of the module is located at
http://folk.uio.no/hpl/Pmw.Blt/doc/reference.html

REQUIREMENTS:

Pmw
BLT

TODO:

- add support for multiple axes (what about hardcopy then?)

"""

from __future__ import division

from common import *
from scitools.globaldata import DEBUG, VERBOSE
from misc import _cmpPlotProperties

import Pmw
import Tkinter

def _cmpPlotProperties(a,b):
    """Sort cmp-function for PlotProperties"""
    plotorder = [Volume, Streams, Surface, Contours, VelocityVectors, Line] 
    assert isinstance(a, PlotProperties)
    assert isinstance(b, PlotProperties)
    assert len(PlotProperties.__class__.__subclasses__(PlotProperties)) == \
               len(plotorder) # Check all subclasses is in plotorder
    return cmp(plotorder.index(a.__class__),plotorder.index(b.__class__))


class BltBackend(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self._init()
        
    def _init(self, *args, **kwargs):
        # Do initialization that is special for this backend
        
        # Set docstrings of all functions to the docstrings of BaseClass
        # The exception is if something is very different
        # Alex had a nice function for this.

        self._master = Tkinter.Tk()
        self._master.withdraw()
        self.figure(self.get('curfig'))

        # convert tables for formatstrings:
        self._markers = {
            '': None,        # no marker
            '.': 'splus',    # dot --> small plus sign
            'o': 'circle',   # circle
            'x': 'cross',    # cross
            '+': 'plus',     # plus sign
            '*': 'scross',   # asterisk --> small cross
            's': 'square',   # square
            'd': 'diamond',  # diamond
            '^': 'triangle', # triangle (up)
            'v': 'triangle', # triangle (down) --> up
            '<': 'triangle', # triangle (left) --> up
            '>': 'triangle', # triangle (right) --> up
            'p': 'diamond',  # pentagram --> diamond
            'h': 'diamond',  # hexagram --> diamond
            }

        self._colors = {
            '': None,       # no color
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
            '': None,        # no line 
            '-': '',         # solid line
            ':': [1,5],      # dotted line
            '-.': [5,5,1,5], # dash-dot line
            '--': [5,5],     # dashed line
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
            self._g.axis_configure('x', logscale=1)
            self._g.axis_configure('y', logscale=1)
        elif scale == 'logx':
            # use logarithmic scale on x-axis and linear scale on y-axis
            self._g.axis_configure('x', logscale=1)
            self._g.axis_configure('y', logscale=0)
        elif scale == 'logy':
            # use linear scale on x-axis and logarithmic scale on y-axis
            self._g.axis_configure('x', logscale=0)
            self._g.axis_configure('y', logscale=1)
        elif scale == 'linear':
            # use linear scale on both x- and y-axis
            self._g.axis_configure('x', logscale=0)
            self._g.axis_configure('y', logscale=0)

    def _set_labels(self, ax):
        # add text labels for x-, y-, and z-axis
        if DEBUG:
            print "Setting labels"
        xlabel = ax.get('xlabel')
        ylabel = ax.get('ylabel')
        zlabel = ax.get('zlabel')
        if xlabel:
            # add a text label on x-axis
            pass
        self._g.axis_configure('x', title=xlabel)
        if ylabel:
            # add a text label on y-axis
            pass
        self._g.axis_configure('y', title=ylabel)
        if zlabel:
            # add a text label on z-axis
            pass
        
    def _set_title(self, ax):
        # add a title at the top of the axis
        if DEBUG:
            print "Setting title"
        title = ax.get('title')
        self._g.configure(title=title)
    
    def _set_limits(self, ax):
        # set axis limits in x, y, and z direction
        if DEBUG:
            print "Setting axis limits"
        mode = ax.get('mode')
        if mode == 'auto':
            # let plotting package set 'nice' axis limits in the x, y,
            # and z direction. If this is not automated in the plotting
            # package, one can use the following limits:
            xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            self._g.axis_configure('x', min=xmin, max=xmax)
            self._g.axis_configure('y', min=ymin, max=ymax)
            #self._g.axis_configure(['x', 'y'], autorange=0.0)
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.get('xmin')
            xmax = ax.get('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits    
                self._g.axis_configure('x', min=xmin, max=xmax)
            else:
                # let plotting package set x-axis limits or use
                xmin, xmax = ax.get('xlim')
                self._g.axis_configure('x', min=xmin, max=xmax)

            ymin = ax.get('ymin')
            ymax = ax.get('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                self._g.axis_configure('y', min=ymin, max=ymax)
            else:
                # let plotting package set y-axis limits or use
                ymin, ymax = ax.get('ylim')
                self._g.axis_configure('y', min=ymin, max=ymax)

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
            self._g.axis_configure('x', min=xmin, max=xmax)
            self._g.axis_configure('y', min=ymin, max=ymax)
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
            pass

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
            pass
        elif direction == 'xy':
            # use the default Cartesian axes form. The origin is at the
            # lower-left corner. The x-axis is vertical and numbered
            # from left to right, while the y-axis is vertical and
            # numbered from bottom to top.
            pass

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
            self._g.grid_on()
        else:
            # turn grid lines off
            self._g.grid_off()

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
            self._g.axis_configure(["x", "y"], hide=False)
        else:
            # turn off all axis labeling, tickmarks, and background
            self._g.axis_configure(['x', 'y'], hide=True)
        #self._g.configure(plotbackground="white")
        #self._g.axis_configure(color='black')  # color on axis and tick labels
        #self._g.axis_configure(titlecolor='black')

    def _get_linespecs(self, item):
        # return the item's line marker, line color, line style, and
        # line width.
        marker = self._markers[item.get('linemarker')]
        color = self._colors[item.get('linecolor')]
        style = self._line_styles[item.get('linetype')]
        width = item.get('linewidth')
        return marker, color, style, width

    def _add_line(self, item):
        # add a 2D or 3D curve to the scene
        if DEBUG:
            print "Adding a line"
        # get data:
        x = item.get('xdata')
        y = item.get('ydata')
        z = item.get('zdata')
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        kwargs = {}
        if color:
            kwargs['color'] = color
        if not width:
            width = 1.0
        else:
            kwargs['linewidth'] = float(width)
        if marker is not None:
            kwargs['symbol'] = marker
            kwargs['fill'] = ''  # transparent in the interior of the marker
            if style is not None:
                if isinstance(style, list):
                    style = tuple([s*width for s in style])
                kwargs['dashes'] = style
            else:
                kwargs['linewidth'] = 0.0
        else:
            kwargs['symbol'] = ''  # no marker
            if style is None:
                style = ''  # solid line
            elif isinstance(style, list):
                style = tuple([s*width for s in style])
            kwargs['dashes'] = style
        if z is not None:
            # zdata is given, add a 3D curve:
            pass
        else:
            # no zdata, add a 2D curve:
            kwargs['xdata'] = tuple(x)
            kwargs['ydata'] = tuple(y)
        kwargs['label'] = item.get('legend')
        return kwargs

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
            fig._root.geometry("%dx%d" % (int(width),int(height)))
        else:
            # use the default width and height in plotting package
            #self._master.geometry("640x480")
            pass

    def figure(self, *args, **kwargs):
        # Extension of BaseClass.figure:
        # add a plotting package figure instance as fig._g and create a
        # link to it as object._g
        BaseClass.figure(self, *args, **kwargs) 
        fig = self.gcf()
        name = 'Fig ' + str(self.get('curfig'))
        try:
            fig._g
        except:
            # create plotting package figure and save figure instance
            # as fig._g
            if DEBUG:
                print "creating figure %s in backend" % name
                
            fig._root = Tkinter.Toplevel(self._master)
            fig._root.title(name)
            def _close_fig(event=None):
                self.clf()
                fig._root.withdraw()
            fig._root.protocol("WM_DELETE_WINDOW", _close_fig)
            fig._root.minsize(200, 200)
            fig._root.geometry('640x480')
            fig._root.bind("<KeyPress-q>", _close_fig)
            fig._root.withdraw()
            mframe = Tkinter.Frame(fig._root, relief='sunken', bd=2)
            mframe.pack(side='top', fill='both', expand=1)
            wframe = Tkinter.Frame(mframe)
            wframe.pack(side='left', fill='both', expand=1)
            frame = Tkinter.Frame(wframe)
            frame.pack(side='top', fill='both', expand=1)
            fig._g = Pmw.Blt.Graph(frame)
            fig._g.pack(expand=1, fill='both')
            
        self._g = fig._g # link for faster access

    figure.__doc__ = BaseClass.figure.__doc__
        
    def _replot(self):
        # Replot all axes and all plotitems in the backend.
        # NOTE: only the current figure (gcf) is redrawn.
        if DEBUG:
            print "Doing replot in backend"
        
        fig = self.gcf()
        # reset the plotting package instance in fig._g now if needed
        for elm in self._g.element_names():
            if self._g.element_exists(elm):
                self._g.element_delete(elm)
        
        self._set_figure_size(fig)
        
        nrows, ncolumns = fig.get('axshape')
        for axnr, ax in fig.get('axes').items():
            if nrows != 1 or ncolumns != 1:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,axnr)
                pass
            plotitems = ax.get('plotitems')
            plotitems.sort(_cmpPlotProperties)
            i = 1
            for item in plotitems:
                name = 'item' + str(i)
                func = item.get('function') # function that produced this item
                if isinstance(item, Line):
                    kwargs = self._add_line(item)
                    g = self._g.line_create(name, **kwargs)
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
                    pass
                i += 1

            self._set_axis_props(ax)
            self._g.update()
                    
        if self.get('show'):
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            fig._root.deiconify() # raise window
            fig._root.update()

    def hardcopy(self, filename, **kwargs):
        """
        Supported extensions:

          '.ps'   (PostScript)
          '.eps'  (Encapsulated PostScript)

        Optional arguments:

          color       -- True (colors) or False (gray-scale).
          orientation -- 'portrait' (default) or 'landscape'.
        """
        self.set(**kwargs)
        color = self.get('color')
        self._replot()

        if DEBUG:
            print "Hardcopy to %s" % filename

        orientation = kwargs.get('orientation', False)
        if orientation == 'portrait':
            orientation = False
        elif orientation == 'landscape':
            orientation == True

        colormode = 'color'
        if not self.get('color'):
            colormode = 'gray'

        self._g.postscript_configure(center=0,
                                     colormode=colormode,
                                     decorations=0,
                                     landscape=orientation)
        self._ps = self._g.postscript_output()
        self._g.postscript_output(filename)

    hardcopy.__doc__ = BaseClass.hardcopy.__doc__ + hardcopy.__doc__

    def clf(self):
        fig = self.gcf()
        fig._root.withdraw()
        del fig._g
        BaseClass.clf(self)

    def closefig(self, num):
        """Close figure window with number 'num'."""
        if num in self._figs:
            curfig = self._attrs['curfig']
            self.figure(num) # set figure with 'num' as current figure
            self.clf()
            del self._figs[num]
            self.figure(curfig) # put back the current figure
        else:
            print 'no such figure with number', num

    def closefigs(self):
        """Close all figure windows."""
        keys = self._figs.keys()
        for key in keys:
            closefig(key)
        BaseClass.closefigs(self)
        self.figure(self._attrs['curfig'])

    # implement colormap functions here
    #def jet(self, m=None):
    #    """Variant of hsv."""
    #    pass
    

plt = BltBackend()   # create backend instance
use(plt, globals())  # export public namespace of plt to globals()
