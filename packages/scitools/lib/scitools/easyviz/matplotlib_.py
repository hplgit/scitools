"""
This backend uses the Python 2D plotting library Matplotlib (available from
http://matplotlib.sourceforge.net). One can specify this backend by 

  python somefile.py --SCITOOLS_easyviz_backend matplotlib

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = matplotlib

and then

  from scitools.all import *

or if just easyviz is needed

  from scitools.easyviz import *

REQUIREMENTS:

Matplotlib

"""

from __future__ import division

from common import *
from scitools.globaldata import DEBUG, VERBOSE

import matplotlib
import matplotlib.colors
# Override system defaults before importing pylab
matplotlib.use('TkAgg')
matplotlib.rc('text', usetex=True)
matplotlib.interactive(True)
from matplotlib.font_manager import fontManager, FontProperties
import pylab


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
        BaseClass.__init__(self)
        self._init()
        
    def _init(self, *args, **kwargs):
        """Perform initialization that is special for this backend."""
        
        # Set docstrings of all functions to the docstrings of BaseClass
        # The exception is if something is very different
        # Alex had a nice function for this.
        
        self.figure(self.get('curfig'))

        # convert tables for format strings:
        self._markers = {
            '': '',   # no marker
            '.': '.', # dot
            'o': 'o', # circle
            'x': 'x', # cross
            '+': '+', # plus sign
            '*': '+', # asterisk --> plus
            's': 's', # square,
            'd': 'd', # diamond,
            'v': 'v', # triangle (down),
            '^': '^', # triangle (up),
            '<': '<', # triangle (left),
            '>': '>', # triangle (right),
            'p': 'p', # pentagram,
            'h': 'h', # hexagram,
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
            for disp in 'self._markers'.split():
                print disp, eval(disp)

    def _set_scale(self, ax):
        """Set linear or logarithmic (base 10) axis scale."""
        if DEBUG:
            print "Setting scales"
        scale = ax.get('scale')
        if scale == 'loglog':
            # use logarithmic scale on both x- and y-axis
            self._g.gca().set_xscale('log')
            self._g.gca().set_yscale('log')
        elif scale == 'logx':
            # use logarithmic scale on x-axis and linear scale on y-axis
            self._g.gca().set_xscale('log')
            self._g.gca().set_yscale('linear')
        elif scale == 'logy':
            # use linear scale on x-axis and logarithmic scale on y-axis
            self._g.gca().set_xscale('linear')
            self._g.gca().set_yscale('log')
        elif scale == 'linear':
            # use linear scale on both x- and y-axis
            self._g.gca().set_xscale('linear')
            self._g.gca().set_yscale('linear')

    def _set_labels(self, ax):
        """Add text labels for x-, y-, and z-axis."""
        if DEBUG:
            print "Setting labels"
        xlabel = ax.get('xlabel')
        ylabel = ax.get('ylabel')
        zlabel = ax.get('zlabel')
        if xlabel:
            # add a text label on x-axis
            self._g.xlabel(xlabel)
        if ylabel:
            # add a text label on y-axis
            self._g.ylabel(ylabel, rotation='horizontal')
        if zlabel:
            # add a text label on z-axis
            pass
        
    def _set_title(self, ax):
        """Add a title at the top of the axis."""
        if DEBUG:
            print "Setting title"
        title = ax.get('title')
        if title:
            self._g.title(title)
    
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
            self._g.axis('auto')
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.get('xmin')
            xmax = ax.get('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits
                self._g.gca().set_xlim(xmin, xmax)
            else:
                # let plotting package set x-axis limits or use
                #xmin, xmax = ax.get('xlim')
                pass

            ymin = ax.get('ymin')
            ymax = ax.get('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                self._g.gca().set_ylim(ymin, ymax)
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
            #xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            self._g.axis('tight')
        elif mode == 'fill':
            # not sure about this
            pass

    def _set_position(self, ax):
        """Set axes position."""
        rect = ax.get('viewport')
        if rect:
            # axes position is defined. In Matlab rect is defined as
            # [left,bottom,width,height], where the four parameters are
            # location values between 0 and 1 ((0,0) is the lower-left
            # corner and (1,1) is the upper-right corner).
            # NOTE: This can be different in the plotting package.
            pass

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
            self._g.axis('equal')
        elif method == 'image':
            # same effect as axis('equal') and axis('tight')
            self._g.axis('image')
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
            self._g.box(on=True)
        else:
            # do not display box
            self._g.box(on=False)
        
    def _set_grid(self, ax):
        """Turn grid lines on or off."""
        if DEBUG:
            print "Setting grid"
        if ax.get('grid'):
            # turn grid lines on
            self._g.grid(b=True)
        else:
            # turn grid lines off
            self._g.grid(b=False)

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
            cbar2 = self._g.colorbar(orientation='vertical')
            if cbar_title:
                cbar2.set_label(cbar_title)
            #pos = [0.78, 0.1, 0.12, 0.8]
            #cbar2.ax.set_position(pos)
            #print cbar2.ax.get_position()
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
            self._g.clim(cmin,cmax)
        else:
            # use autoranging for color axis scale
            pass

    def _set_colormap(self, ax):
        """Set the colormap."""
        if DEBUG:
            print "Setting colormap"
        cmap = ax.get('colormap')
        # cmap is plotting package dependent
        # the colormap is set in 

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
        else:
            # turn off all axis labeling, tickmarks, and background
            self._g.axis('off')

    def _get_linespecs(self, item):
        """
        Return the line marker, line color, line style, and
        line width of the item.
        """
        
        marker = self._markers[item.get('linemarker')]
        color = item.get('linecolor')
        style = item.get('linetype')
        width = item.get('linewidth')
        return marker, color, style, width

    def _add_line(self, item):
        """Add a 2D or 3D curve to the scene."""
        if DEBUG:
            print "Adding a line"
        # get data:
        x = item.get('xdata')
        y = item.get('ydata')
        z = item.get('zdata')
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        fmt = marker+color+style
        if not width:
            width = 1.0

        if z is not None:
            # zdata is given, add a 3D curve:
            print "No support for plot3 in Matplotlib."
        else:
            # no zdata, add a 2D curve:
            l, = self._g.plot(x,y,fmt,linewidth=width)
            legend = item.get('legend')
            if legend:
                l.set_label(legend)

    def _add_surface(self, item, shading='faceted', colormap=None):
        if DEBUG:
            print "Adding a surface"
        x = squeeze(item.get('xdata'))  # grid component in x-direction
        y = squeeze(item.get('ydata'))  # grid component in y-direction
        z = item.get('zdata')           # scalar field
        c = item.get('cdata')           # pseudocolor data (can be None)
        legend = item.get('legend')

        if colormap is None:
            colormap = hot()
        
        contours = item.get('contours')
        if contours:
            # the current item is produced by meshc or surfc and we
            # should therefore add contours at the bottom:
            #self._add_contours(contours, placement='bottom')
            print "No support for meshc/surfc in Matplotlib."

        if item.get('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            print "No support for mesh/meshc in Matplotlib."
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            h = self._g.pcolor(x,y,z,shading=shading,cmap=colormap)
            if legend:
                h.set_label(legend)

    def _add_contours(self, item, placement=None, colormap=None):
        # The placement keyword can be either None or 'bottom'. The
        # latter specifies that the contours should be placed at the
        # bottom (as in meshc or surfc).
        if DEBUG:
            print "Adding contours"
        x = squeeze(item.get('xdata'))  # grid component in x-direction
        y = squeeze(item.get('ydata'))  # grid component in y-direction
        z = item.get('zdata')           # scalar field
        legend = item.get('legend')

        if colormap is None:
            colormap = jet()
        
        filled = item.get('filled')  # draw filled contour plot if True

        cvector = item.get('cvector')
        clevels = item.get('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            pass
        else:
            clevels = cvector

        contour_cmd = self._g.contour
        location = item.get('clocation')
        if location == 'surface':
            # place the contours at the corresponding z level (contour3)
            print "No support for contour3 in Matplotlib."
        elif location == 'base':
            if placement == 'bottom':
                # place the contours at the bottom (as in meshc or surfc)
                pass
            else:
                # standard contour plot
                pass
        if filled:
            contour_cmd = self._g.contourf
        kwargs = {'cmap': colormap}
        if legend:
            kwargs['label'] = legend
        cs = contour_cmd(x,y,z,clevels,**kwargs)

        if item.get('clabels'):
            # add labels on the contour curves
            self._g.clabel(cs)
    
    def _add_vectors(self, item):
        if DEBUG:
            print "Adding vectors"
        # uncomment the following command if there is no support for
        # automatic scaling of vectors in the current plotting package:
        #item.scale_vectors()

        # grid components:
        x = squeeze(item.get('xdata'))
        y = squeeze(item.get('ydata'))
        z = item.get('zdata')
        # vector components:
        u, v, w = item.get('udata'), item.get('vdata'), item.get('wdata')
        # get line specifiactions (marker='.' means no marker):
        marker, color, style, width = self._get_linespecs(item)

        legend = item.get('legend')

        # scale the vectors according to this variable (scale=0 should
        # turn off automatic scaling):
        scale = item.get('arrowscale')

        filled = item.get('filledarrows') # draw filled arrows if True

        if z is not None and w is not None and False:
            # draw velocity vectors as arrows with components (u,v,w) at
            # points (x,y,z):
            print "No support for quiver3 in Matplotlib."
        else:
            # draw velocity vectors as arrows with components (u,v) at
            # points (x,y):
            if not color:
                color = u**2+v**2  # color arrows by magnitude
            h = self._g.quiver(x,y,u,v,scale,color=color,width=1.0)
            if legend:
                h.set_label(legend)

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
            pass
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

            fig._g = pylab
            
        self._g = fig._g # link for faster access

    figure.__doc__ = BaseClass.figure.__doc__
        
    def _replot(self):
        """Replot all axes and all plotitems in the backend."""
        # NOTE: only the current figure (gcf) is redrawn.
        if DEBUG:
            print "Doing replot in backend"

        # turn off interactive in pylab temporarily:
        pylab_interactive_state = self._g.isinteractive()
        self._g.ioff()
        
        fig = self.gcf()
        self._g.figure(self.get('curfig'))

        # reset the plotting package instance in fig._g now if needed
        self._g.clf()

        # turn on hold in pylab temporarily:
        pylab_hold_state = self._g.ishold()
        self._g.hold(True)
        
        self._set_figure_size(fig)
        
        nrows, ncolumns = fig.get('axshape')
        for axnr, ax in fig.get('axes').items():
            if nrows != 1 or ncolumns != 1:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,axnr)
                self._g.subplot(nrows,ncolumns,axnr)
            legends = False
            plotitems = ax.get('plotitems')
            plotitems.sort(_cmpPlotProperties)
            for item in plotitems:
                func = item.get('function') # function that produced this item
                if isinstance(item, Line):
                    self._add_line(item)
                elif isinstance(item, Surface):
                    self._add_surface(item,
                                      shading=ax.get('shading'),
                                      colormap=ax.get('colormap'))
                elif isinstance(item, Contours):
                    self._add_contours(item, colormap=ax.get('colormap'))
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

            if legends:
                self._g.legend()
            self._set_axis_props(ax)
                    
        # set back the hold and interactive states in pylab:
        self._g.hold(pylab_hold_state)
        if pylab_interactive_state:
            self._g.ion()

        if self.get('show'):
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            self._g.draw()
            self._g.show()

    def hardcopy(self, filename, **kwargs):
        """
        Supported extensions: .eps, .jpg, .pdf, .png, .ps, and .svg
        This is dependent on the Matplotlib backend.

        Optional arguments:

          dpi         -- image resolution. Default is 150.
          orientation -- 'portrait' (default) or 'landscape'. Only available
                         for PostScript output.

        """
        self.set(**kwargs)
        color = self.get('color')
        self._replot()

        if DEBUG:
            print "Hardcopy to %s" % filename

        dpi = kwargs.get('dpi', 150)
        orientation = kwargs.get('orientation', 'portrait')

        self._replot()
        self._g.savefig(filename,
                        facecolor='w',
                        edgecolor='w',
                        orientation=orientation)

    hardcopy.__doc__ = BaseClass.hardcopy.__doc__ + hardcopy.__doc__

    def clf(self): 
        self._g.clf()
        BaseClass.clf(self)

    def closefig(self, num=None): 
        if not num:
            # close current figure
            pass
        elif num in self._figs.keys():
            self._figs[num].close()
        else:
            pass
        pass
    
    def closefigs(self):
        for key in self._figs.keys():
            self._figs[key]._g.close()
            del self._figs[key]._g
        del self._g
        BaseClass.closefigs(self)

    # Colormap methods:
    def hsv(self, m=None):
        return self._g.cm.get_cmap('hsv', m)

    def hot(self, m=None):
        return self._g.cm.get_cmap('hot', m)
    
    def gray(self, m=None):
        return self._g.cm.get_cmap('gray', m)
    
    def bone(self, m=None):
        return self._g.cm.get_cmap('bone', m)

    def copper(self, m=None):
        return self._g.cm.get_cmap('copper', m)

    def pink(self, m=None):
        return self._g.cm.get_cmap('pink', m)
    
    def white(self, m=None):
        raise NotImplementedError, 'white not implemented in class %s' % \
              self.__class__.__name__
    
    def flag(self, m=None):
        return self._g.cm.get_cmap('flag', m)
    
    def lines(self, m=None):
        raise NotImplementedError, 'lines not implemented in class %s' % \
              self.__class__.__name__
    
    def colorcube(self, m=None):
        raise NotImplementedError, 'colorcube not implemented in class %s' % \
              self.__class__.__name__
    
    def vga(self, m=None):
        raise NotImplementedError, 'vga not implemented in class %s' % \
              self.__class__.__name__
    
    def jet(self, m=None):
        return self._g.cm.get_cmap('jet', m)
    
    def prism(self, m=None):
        return self._g.cm.get_cmap('prism', m)
    
    def cool(self, m=None):
        return self._g.cm.get_cmap('cool', m)
    
    def autumn(self, m=None):
        return self._g.cm.get_cmap('autumn', m)
    
    def spring(self, m=None):
        return self._g.cm.get_cmap('spring', m)
    
    def winter(self, m=None):
        return self._g.cm.get_cmap('winter', m)
    
    def summer(self, m=None):
        return self._g.cm.get_cmap('summer', m)
    

plt = MatplotlibBackend()  # create backend instance
use(plt, globals())        # export public namespace of plt to globals()
