"""
This backend uses the Gnuplot plotting program together with the
Gnuplot.py Python module. One can use this backend by

  python somefile.py --SCITOOLS_easyviz_backend gnuplot

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = gnuplot

and then

  from scitools.all import *

or if just easyviz is needed

  from scitools.easyviz import *

REQUIREMENTS:

Gnuplot >= 4.0
Gnuplot.py

Tip:

  To close a figure window, press <q> when active

"""

from __future__ import division

from common import *
from scitools.numpytools import ones, ravel, shape, NewAxis, rank, transpose, \
     linspace
from scitools.globaldata import DEBUG, VERBOSE
from misc import _cmpPlotProperties, arrayconverter

import Gnuplot
import tempfile
import os
import sys
import operator

if sys.platform == "darwin" and "TERM_PROGRAM" not in os.environ:
    Gnuplot.GnuplotOpts.default_term = "x11"

def _cmpPlotProperties(a,b):
    """Sort cmp-function for PlotProperties"""
    plotorder = [Volume, Streams, Surface, Contours, VelocityVectors, Line] 
    assert isinstance(a, PlotProperties)
    assert isinstance(b, PlotProperties)
    assert len(PlotProperties.__class__.__subclasses__(PlotProperties)) == \
               len(plotorder) # Check all subclasses is in plotorder
    return cmp(plotorder.index(a.__class__),plotorder.index(b.__class__))

class GnuplotBackend(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self._init()
        
    def _init(self, *args, **kwargs):
        # Necessary to add a Gnuplot Session  as _g to the Figure instance
        # self._g will now point to the correct intance saved as _g in curfig 
        self.figure(self.get('curfig'))
        
        # convert tables for formatstrings:
        self._markers = {
            '': None,   # no marker
            '.': 0,  # dot
            'o': 6,  # circle
            'x': 2,  # cross
            '+': 1,  # plus sign
            '*': 3,  # asterisk
            's': 4,  # square
            'd': 12, # diamond
            '^': 8,  # triangle (up)
            'v': 10, # triangle (down)
            '<': 10, # triangle (left) --> (down)
            '>': 10, # triangle (right) --> (down)
            'p': 5,  # pentagram --> square
            'h': 5,  # hexagram --> square
            }
         
        self._colors = {
            '': 3,   # no color --> blue
            'r': 1,  # red
            'g': 2,  # green
            'b': 3,  # blue
            'c': 5,  # cyan --> aqua
            'm': 4,  # magenta --> purple
            'y': 7,  # yellow --> orange
            'k': -1, # black
            'w': 7,  # white --> orange
            }
        
        self._line_styles = {
            '': None,       # no line --> point
            '-': 'lines',   # solid line
            ':': 'lines',   # dotted line --> solid line
            '-.': 'lines',  # dash-dot line --> solid line
            '--': 'lines',  # dashed line --> solid line
            }

        # convert table for colorbar location:
        self._colorbar_locations = {
            'North': ('horizontal',.2,.74,.6,.04),
            'South': ('horizontal',.2,.26,.6,.04),
            'East': ('vertical',.76,.21,.03,.6),
            'West': ('vertical',.21,.21,.03,.6),
            'NorthOutside': ('horizontal',.2,.92,.6,.04),
            'SouthOutside': ('horizontal',.2,.06,.6,.04),
            'EastOutside': ('vertical',.9,.21,.03,.6),
            'WestOutside': ('vertical',.01,.21,.03,.6)
            }

        if DEBUG:
            print "Setting backend standard variables"
            for disp in 'self._markers self._colors self._line_styles'.split():
                print disp, eval(disp)

    def _set_scale(self, ax):
        scale = ax.get('scale')
        if scale == 'loglog':
            self._g('set logscale x')
            self._g('set logscale y')
            self._g('set autoscale')
        elif scale == 'logx':
            self._g('set logscale x')
            self._g('set nologscale y')
            self._g('set autoscale')
        elif scale == 'logy':
            self._g('set logscale y')
            self._g('set nologscale x')
            self._g('set autoscale')
        elif scale == 'linear':
            self._g('set nologscale y')
            self._g('set nologscale x')
            self._g('set autoscale')

    def _set_scale(self, ax):
        # set linear or logarithmic (base 10) axis scale
        if DEBUG:
            print "Setting scales"
        scale = ax.get('scale')
        if scale == 'loglog':
            # use logarithmic scale on both x- and y-axis
            self._g('set logscale xy')
            self._g('set autoscale')
        elif scale == 'logx':
            # use logarithmic scale on x-axis and linear scale on y-axis
            self._g('set logscale x')
            self._g('unset logscale y')
            self._g('set autoscale')
        elif scale == 'logy':
            # use linear scale on x-axis and logarithmic scale on y-axis
            self._g('unset logscale x')
            self._g('set logscale y')
            self._g('set autoscale')
        elif scale == 'linear':
            # use linear scale on both x- and y-axis
            self._g('unset logscale x')
            self._g('unset logscale y')
            self._g('set autoscale')

    def _set_labels(self, ax):
        # add text labels for x-, y-, and z-axis
        if DEBUG:
            print "Setting labels"
        xlabel = ax.get('xlabel')
        ylabel = ax.get('ylabel')
        zlabel = ax.get('zlabel')
        if xlabel:
            # add a text label on x-axis
            self._g('set xlabel "%s"' % xlabel)
        else:
            self._g('unset xlabel')
        if ylabel:
            # add a text label on y-axis
            self._g('set ylabel "%s"' % ylabel)
        else:
            self._g('unset ylabel')
        if zlabel:
            # add a text label on z-axis
            self._g('set zlabel "%s"' % zlabel)
        else:
            self._g('unset zlabel')
        
    def _set_title(self, ax):
        # add a title at the top of the axis
        if DEBUG:
            print "Setting title"
        title = ax.get('title')
        if title:
            self._g('set title "%s"' % title)
        else:
            self._g('unset title')
    
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
            self._g('set xrange[*:*]')
            self._g('set yrange[*:*]')
            self._g('set zrange[*:*]')
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.get('xmin')
            xmax = ax.get('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits
                self._g('set xrange[%g:%g]' % (xmin, xmax))
            else:
                # let plotting package set x-axis limits or use
                #xmin, xmax = ax.get('xlim')
                self._g('set xrange[*:*]')

            ymin = ax.get('ymin')
            ymax = ax.get('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                self._g('set yrange[%g:%g]' % (ymin, ymax))
            else:
                # let plotting package set y-axis limits or use
                #ymin, ymax = ax.get('ylim')
                self._g('set yrange[*:*]')

            zmin = ax.get('zmin')
            zmax = ax.get('zmax')
            if zmin is not None and zmax is not None:
                # set z-axis limits
                self._g('set zrange[%g:%g]' % (zmin, zmax))
            else:
                # let plotting package set z-axis limits or use
                #zmin, zmax = ax.get('zlim')
                self._g('set zrange[*:*]')
        elif mode == 'tight':
            # set the limits on the axis to the range of the data. If
            # this is not automated in the plotting package, one can
            # use the following limits:
            xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            self._g('set xrange[%g:%g]' % (xmin, xmax))
            self._g('set yrange[%g:%g]' % (ymin, ymax))
            self._g('set zrange[%g:%g]' % (zmin, zmax))
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
            self._g('set size ratio -1')
        elif method == 'image':
            # same effect as axis('equal') and axis('tight')
            self._g('set size ratio -1')
        elif method == 'square':
            # make the axis box square in size
            self._g('set size square')
        elif method == 'normal':
            # full size axis box
            self._g('set size noratio')
            self._g('set size nosquare')
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
            self._g('set yrange [] reverse')
        elif direction == 'xy':
            # use the default Cartesian axes form. The origin is at the
            # lower-left corner. The x-axis is vertical and numbered
            # from left to right, while the y-axis is vertical and
            # numbered from bottom to top.
            self._g('set yrange [] noreverse')

    def _set_box(self, ax):
        # turn box around axes boundary on or off
        if DEBUG:
            print "Setting box"
        if ax.get('box'):
            # display box 
            self._g('set border 4095 linetype -1 linewidth .4')
        else:
            # do not display box
            pass
        
    def _set_grid(self, ax):
        # turn grid lines on or off
        if DEBUG:
            print "Setting grid"
        if ax.get('grid'):
            # turn grid lines on
            self._g('set grid')
        else:
            # turn grid lines off
            self._g('unset grid')

    def _set_hidden_line_removal(self, ax):
        # turn on/off hidden line removal for meshes
        if DEBUG:
            print "Setting hidden line removal"
        if ax.get('hidden'):
            # turn hidden line removal on
            self._g('set hidden3d')
        else:
            # turn hidden line removal off
            self._g('unset hidden3d')

    def _set_colorbar(self, ax):
        # add a colorbar to the axis
        if DEBUG:
            print "Setting colorbar"
        cbar = ax.get('colorbar')
        if cbar.get('visible'):
            # turn on colorbar
            cbar_title = cbar.get('cbtitle')
            # TODO: set title on the colorbox (see cblabel)
            #self._g('set clabel %s')
            cbar_location = self._colorbar_locations[cbar.get('cblocation')]
            self._g('set style line 2604 linetype -1 linewidth .4')
            self._g('set colorbox %s user border 2604 origin %g,%g size %g,%g'\
                    % cbar_location)
        else:
            # turn off colorbar
            self._g('unset colorbox')

    def _set_caxis(self, ax):
        # set the color axis scale
        if DEBUG:
            print "Setting caxis"
        if ax.get('caxismode') == 'manual':
            cmin, cmax = ax.get('caxis')
            # NOTE: cmin and cmax might be None:
            if not cmin or not cmax:
                cmin, cmax = [0,1]
            # set color axis scaling according to cmin and cmax
            self._g('set cbrange [%d:%d]' % (int(cmin),int(cmax)))
        else:
            # use autoranging for color axis scale
            self._g('set cbrange [*:*]')

    def _set_colormap(self, ax):
        # set the colormap
        if DEBUG:
            print "Setting colormap"
        cmap = ax.get('colormap')
        # cmap is plotting package dependent
        if isinstance(cmap, str):
            self._g(cmap)
        elif isinstance(cmap, (tuple,list)) and len(cmap) == 3 and \
                 isinstance(cmap[0], int) and \
                 isinstance(cmap[1], int) and \
                 isinstance(cmap[2], int):
            self._g('set palette rgbformulae %d,%d,%d' % cmap) # model RGB?
        elif operator.isSequenceType(cmap) and rank(cmap) == 2:
            m, n = shape(cmap)
            assert n==3, "colormap must be %dx3, not %dx%d." % (m,m,n)
            tmpf = tempfile.mktemp(suffix='.map')
            f = open (tmpf, "w")
            for i in range(m):
                f.write('%g %g %g\n' % (cmap[i,0],cmap[i,1],cmap[i,2]))
            f.close()
            self._g('set palette file "%s"' % tmpf)
        else: # use default colormap
            self._g('set palette model RGB defined (0 "blue", 3 "cyan", ' \
                    '4 "green", 5 "yellow", 8 "red", 10 "black")')        

    def _set_view(self, ax):
        # set viewpoint specification
        if DEBUG:
            print "Setting view"
        self._g('unset view')
        cam = ax.get('camera')
        view = cam.get('view')
        if view == 2:
            # setup a default 2D view
            self._g('set view map')
        elif view == 3:
            az = cam.get('azimuth')
            el = cam.get('elevation')
            if not az or not el:
                # azimuth or elevation is not given. Set up a default
                # 3D view (az=-37.5 and el=30 is the default 3D view in
                # Matlab).
                az, el = (60,325) # default 3D view in Gnuplot
            if (az >= 0 and az <= 180) and (el >= 0 and el <= 360):
                self._g('set view %d,%d' % (az,el))
            else:
                print 'view (%s,%s) out of range [0:180,0:360]' % (az,el)
            
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
            self._g('set xtics')
            self._g('set ytics')
            self._g('set ztics')
            # set up some nice default graph borders:
            self._g('set border 1+2+4+8+16 linetype -1 linewidth .4')
            self._set_labels(ax)
            self._set_box(ax)
            self._set_grid(ax)
        else:
            # turn off all axis labeling, tickmarks, and background
            self._g('unset border')
            self._g('unset grid')
            self._g('unset xtics')
            self._g('unset ytics')
            self._g('unset ztics')

    def _get_linespecs(self, item):
        # return the item's line marker, line color, line style, and
        # line width.
        marker = self._markers[item.get('linemarker')]
        color = self._colors[item.get('linecolor')]
        style = self._line_styles[item.get('linetype')]
        width = item.get('linewidth')
        return marker, color, style, width

    def _get_withstring(self, marker, color, style, width):
        if not width:
            width = 1
        else:
            width = int(width)

        withstring = ''
        if not style:
            if marker:
                withstring = "points lt %d pt %d ps %d " \
                             % (color, marker, width)
            else:
                withstring = "lines lt %d lw %d" % (color, width)
        elif style == 'lines':
            if not marker: 
                withstring = "lines lt %d lw %d" % (color, width)
            else: 
                withstring = "linespoints lt %d lw %d pt %d" % \
                             (color, width, marker)
        return withstring

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
        
        withstring = self._get_withstring(marker, color, style, width)
        if z is not None:
            # zdata is given, add a 3D curve:
            data = None  # not yet implemented
        else:
            # no zdata, add a 2D curve:
            data = Gnuplot.Data(arrayconverter(x),
                                arrayconverter(y),
                                title=item.get('legend'), with=withstring)
        return data

    def _add_surface(self, item, shading='faceted'):
        if DEBUG:
            print "Adding a surface"
        x = item.get('xdata')  # grid component in x-direction
        y = item.get('ydata')  # grid component in y-direction
        z = item.get('zdata')  # scalar field
        c = item.get('cdata')  # pseudocolor data (can be None)
        
        self._g('set surface')
        if item.get('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            self._g('unset pm3d')
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            if shading == 'flat':
                self._g('set pm3d at s solid')
            elif shading == 'faceted':
                self._g('set pm3d at s solid hidden3d 100')
                self._g('set style line 100 lt -1 lw 0.5')
            elif shading == 'interp':
                # TODO: test interpolated shading mode in Gnuplot 4.2
                #self._g('set pm3d interpolate 10,1 flush begin ftriangles nohidden3d corners2color mean')
                pass

        if item.get('memoryorder') == 'yxz':
            if rank(x) == 2 and rank(y) == 2:
                x = x[0,:];  y = y[:,0]
            z = transpose(z, [1,0])
        else:
            if rank(x) == 2 and rank(y) == 2:
                x = x[:,0];  y = y[0,:]
        data = Gnuplot.GridData(arrayconverter(z),
                                arrayconverter(x),
                                arrayconverter(y),
                                title=item.get('legend'),
                                with='l palette',
                                binary=0)
        return data

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
        if filled:
            #self._g('set style fill pattern')
            #self._g('set pm3d at s solid')
            #self._g('set palette maxcolors %d' % item.get('clevels'))
            pass

        cvector = item.get('cvector')
        clevels = item.get('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            self._g('set cntrparam levels auto %d' % clevels)
        else:
            cvector = ','.join(['%s' % i for i in cvector])
            self._g('set cntrparam levels discrete %s' % cvector)

        location = item.get('clocation')
        if location == 'surface':
            # place the contours at the corresponding z level (contour3)
            self._g('set contour surface')
            self._g('unset surface')
            self._g('unset pm3d')
        elif location == 'base':
            if placement == 'bottom':
                # place the contours at the bottom (as in meshc or surfc)
                self._g('set contour base')
            else:
                # standard contour plot
                self._g('set contour base')
                self._g('unset surface')
                self._g('unset pm3d')

        if item.get('clabels'):
            # add labels on the contour curves
            self._g('set clabel')
        else:
            self._g('unset clabel')

        if item.get('memoryorder') == 'yxz':
            z = transpose(z, [1,0])
            if rank(x) == 2 and rank(y) == 2:
                x = x[0,:];  y = y[:,0]
        else:
            if rank(x) == 2 and rank(y) == 2:
                x = x[:,0];  y = y[0,:]
        data = Gnuplot.GridData(arrayconverter(z),
                                arrayconverter(x),
                                arrayconverter(y),
                                title=item.get('legend'),
                                binary=0,
                                with='l palette')
        return data

    def _add_vectors(self, item):
        if DEBUG:
            print "Adding vectors"
        # uncomment the following command if there is no support for
        # automatic scaling of vectors in the current plotting package:
        item.scale_vectors()

        # grid components:
        x, y, z = item.get('xdata'), item.get('ydata'), item.get('zdata')
        # vector components:
        u, v, w = item.get('udata'), item.get('vdata'), item.get('wdata')
        # get line specifiactions (marker='.' means no marker):
        marker, color, style, width = self._get_linespecs(item)
        
        withstring = 'vectors'
        if color:
            withstring += ' lt %d' % color
        if width:
            withstring += ' lw %d' % int(width)

        # scale the vectors according to this variable (scale=0 should
        # turn off automatic scaling):
        scale = item.get('arrowscale')

        filled = item.get('filledarrows') # draw filled arrows if True

        if z is not None and w is not None and False: # NOTE: <-- FIX!!!
            # draw velocity vectors as arrows with components (u,v,w) at
            # points (x,y,z):
            data = None  # no support for vectors in 3D space in Gnuplot
        else:
            # draw velocity vectors as arrows with components (u,v) at
            # points (x,y):
            if shape(x) != shape(u):
                if rank(x) == 2:
                    x = x*ones(shape(u))
                else:
                    if item.get('memoryorder') == 'yxz':
                        x = x[NewAxis,:]*ones(shape(u))
                    else:
                        x = x[:,NewAxis]*ones(shape(u))
            if shape(y) != shape(u):
                if rank(y) == 2:
                    y = y*ones(shape(u))
                else:
                    if item.get('memoryorder') == 'yxz':
                        y = y[:,NewAxis]*ones(shape(u))
                    else:
                        y = y[NewAxis,:]*ones(shape(u))
            data = Gnuplot.Data(arrayconverter(ravel(x)),
                                arrayconverter(ravel(y)),
                                arrayconverter(ravel(u)),
                                arrayconverter(ravel(v)),
                                title=item.get('legend'),
                                with=withstring)
        return data

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

        msg = "Currently no support for '%s' in the Gnuplot backend." % \
              item.get('function')
        raise NotImplementedError, msg

    def _add_isosurface(self, item):
        if DEBUG:
            print "Adding a isosurface"
        # grid components:
        x, y, z = item.get('xdata'), item.get('ydata'), item.get('zdata')
        v = item.get('vdata')  # volume
        c = item.get('cdata')  # pseudocolor data
        isovalue = item.get('isovalue')

        msg = "Currently no support for '%s' in the Gnuplot backend." % \
              item.get('function')
        raise NotImplementedError, msg

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

        msg = "Currently no support for '%s' in the Gnuplot backend." % \
              item.get('function')
        raise NotImplementedError, msg

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

        msg = "Currently no support for '%s' in the Gnuplot backend." % \
              item.get('function')
        raise NotImplementedError, msg

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
            try:
                fig._g = Gnuplot.Gnuplot(persist=1)
                # Plotwindow will now persist
                # To close the gnuplot session run fig._g('quit')
                # Python will only remove the binding to the session and not
                # stop it when _g is deleted            
                # This is due to the persist=1 parameter
            except:
                fig._g = Gnuplot.Gnuplot() # Persist is not supported under win
            
        self._g = fig._g # link for faster access

    figure.__doc__ = BaseClass.figure.__doc__
        
    def _replot(self):
        # Replot all axes and all plotitems in the backend.
        # NOTE: only the current figure (gcf) is redrawn.
        if DEBUG:
            print "Doing replot in backend"
        
        fig = self.gcf()
        # reset the plotting package instance in fig._g now if needed
        self._g.reset()
        self._g('set size 1.0, 1.0')
        self._g('set origin 0.0, 0.0')
        self._g('unset multiplot')
        
        self._set_figure_size(fig)

        if len(fig.get('axes').items()) > 1:
            # multiple axes
            self._g('set multiplot')
        nrows, ncolumns = fig.get('axshape')
        for axnr, ax in fig.get('axes').items():
            gdata = []
            self._use_splot = False
            if nrows != 1 or ncolumns != 1:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,axnr)
                viewport = ax.get('viewport')
                if not viewport:
                    viewport = (0,0,1,1)
                origin = viewport[:2]
                size = 1/ncolumns, 1/nrows
                self._g('set origin %g,%g' % origin)
                self._g('set size %g,%g' % size)
            plotitems = ax.get('plotitems')
            plotitems.sort(_cmpPlotProperties)
            for item in plotitems:
                func = item.get('function') # function that produced this item
                if isinstance(item, Line):
                    gdata.append(self._add_line(item))
                elif isinstance(item, Surface):
                    gdata.append(self._add_surface(item,
                                                   shading=ax.get('shading')))
                    contours = item.get('contours')
                    if contours:
                        # the current item is produced by meshc or surfc
                        # and we should therefore add contours at the
                        # bottom:
                        gdata.append(self._add_contours(contours,
                                                        placement='bottom'))
                    self._use_splot = True
                elif isinstance(item, Contours):
                    gdata.append(self._add_contours(item))
                    self._g('unset surface')
                    self._use_splot = True
                elif isinstance(item, VelocityVectors):
                    gdata.append(self._add_vectors(item))
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

            self._set_axis_props(ax)
            
            if gdata:
                if self._use_splot:
                    self._g.splot(gdata[0])
                else:
                    self._g.plot(gdata[0])
            
            if len(gdata) > 1:
                for data in gdata[1:]:
                    self._g.replot(data)

        if self.get('show'):
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            pass

    def hardcopy(self, filename, **kwargs):
        """
        Currently supported extensions in Gnuplot backend:

          '.ps'  (PostScript)
          '.eps' (Encapsualted PostScript)
          '.png' (Portable Network Graphics)

        Optional arguments:

          color       -- True (colors) or False (black and white).
          fontname    -- default is Helvetica.
          fontsize    -- default is 16.
          orientation -- 'portrait' or 'landscape' (default). Only available
                         for PostScript output.
        """
        if DEBUG:
            print "Hardcopy to %s" % filename

        ext2term = {'.ps': 'postscript',
                    '.eps': 'postscript',
                    '.png': 'png'}
        basename, ext = os.path.splitext(filename)
        if not ext:
            # no extension given, assume .ps:
            ext = '.ps'
            filename += ext
        elif ext not in ext2term:
            raise ValueError, "hardcopy: extension must be %s, not '%s'" % \
                  (ext2term.keys(), ext)
        terminal = ext2term.get(ext, 'postscript')
        
        self.set(**kwargs)
        fontname = kwargs.get('fontname', 'Helvetica')
        fontsize = kwargs.get('fontsize', 16)
        orientation = kwargs.get('orientation', 'landscape')
        color = self.get('color')
                  
        self._g('unset multiplot') # is this necessary?
        
        if self.get('show'): # OK to display to screen
            self._replot()
            kwargs = {'filename': filename, 'terminal': terminal}
            if terminal == 'postscript':
                kwargs.update({'color': color, 'enhanced': True,
                               'fontname': fontname, 'fontsize': fontsize})
                if ext == '.eps':
                    kwargs['mode'] = 'eps'
                else:
                    kwargs['mode'] = orientation
            self._g.hardcopy(**kwargs)
        else: # Manually set terminal and don't show windows
            if color:
                colortype = 'color'
            else:
                colortype = 'monochrome'
                        
            # Create a new Gnuplot instance only for now
            self._g = Gnuplot.Gnuplot()
            kwargs = {'filename': filename, 'terminal': terminal}
            if terminal == 'postscript':
                kwargs.update({'color': color, 'enhanced': True, 
                               'fontname': fontname, 'fontsize': fontsize})
                if ext == '.eps':
                    self._g('set term postscript eps %s' % colortype)
                    kwargs['mode'] = 'eps'
                else:
                    self._g('set term postscript %s %s' % \
                            (orientation,colortype))
                    kwargs['mode'] = orientation
            elif terminal == 'png':
                self._g('set term png')
            self._g('set output "%s"' % filename)
            self._replot()
            self._g.hardcopy(**kwargs)
            self._g('quit')
            self._g = self.gcf()._g # set _g to the correct instance again

    hardcopy.__doc__ = BaseClass.hardcopy.__doc__ + hardcopy.__doc__

    # reimplement methods like clf, closefig, closefigs
    def clf(self):
        """Clear current figure."""
        BaseClass.clf(self)
        self._g.reset() # reset gnuplot instance

    def closefig(self, num=None):
        """Close figure window."""
        if not num:
            pass
        elif num in self._figs.keys():
            pass
        else:
            pass
        pass

    def closefigs(self):
        """Close figure windows and stop gnuplot."""
        for key in self._figs.keys():
            self._figs[key]._g('quit')
        del self._g
        self._figs = {1:Figure()}
        self._figs[1]._g = Gnuplot.Gnuplot()
        self._g = self._figs[1]._g

    # Colormaps:
    def hsv(self, m=0):
        c = 'rgbformulae 3,2,2'
        return 'set palette model HSV maxcolors %d %s' % (m,c)
    
    def hot(self, m=0):
        c = 'rgbformulae 21,22,23'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def gray(self, m=0):
        c = 'defined (0 "black", 1 "white")'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def bone(self, m=0):
        c = 'defined (0 "black", 4 "light-blue", 5 "white")'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def copper(self, m=0):
        c = 'defined (0 "black", 1 "coral")'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def pink(self, m=0):
        c = 'defined (0 "black", 1 "pink", 8 "pink", 10 "white")'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def white(self, m=64):
        c = 'defined (0 "white", 1 "white")'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
##         if m > 0:
##             cmap = ones((m, 3), float)
##         else:
##             cmap = []
##         return cmap
    
    def flag(self, m=0):
        colors = "red,white,blue,black".split(',')
        j=k=0
        c = 'defined ('
        while k < 16:
            i = 0
            while i < len(colors)-1:
                j += 1;  i += 2
                c += '%d "%s", %d "%s", ' % (j-1,colors[i-2],j,colors[i-1])
            k += 1
        c = c[:-2]+')'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
                
    def lines(self, m=0):
        # NOTE: not finished
        colors = "blue,green,red,cyan,magenta,yellow,black".split(',')
        j=k=0
        c = 'defined ('
        while k < 9:
            i = 0
            c += '%d "%s"' % (j,colors[0])
            while i < len(colors)-1:
                j += 1;  i += 2
                c += ', %d "%s", %d "%s"' % (j,colors[i-1],j,colors[i])
            k += 1
            c += ', '
        c = c[:-2]+')'
        #print c
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def colorcube(self, m=0):
        colors = "white,black,gray0,gray10,grey20,grey30,gray40,gray50,"\
                 "gray60,grey70,grey80,gray90,grey100,grey,light-grey,"\
                 "dark-grey,red,light-red,dark-red,yellow,light-yellow,"\
                 "dark-yellow,green,light-green,dark-green,spring-green,"\
                 "forest-green,sea-green,blue,light-blue,dark-blue,"\
                 "midnight-blue,navy,medium-blue,royalblue,skyblue,cyan,"\
                 "light-cyan,dark-cyan,magenta,light-magenta,dark-magenta,"\
                 "turquoise,light-turquoise,dark-turquoise,pink,light-pink,"\
                 "dark-pink,coral,light-coral,orange-red,salmon,light-salmon,"\
                 "dark-salmon,aquamarine,khaki,dark-khaki,gold,goldenrod,"\
                 "light-goldenrod,dark-goldenrod,beige,brown,orange,"\
                 "dark-orange,violet,dark-violet,plum,purple".split(',')
        i=j=0
        c = 'defined (%d "%s"' % (i,colors[0])
        while i < len(colors)-1:
            j += 1;  i += 2
            c += ', %d "%s", %d "%s"' % (j,colors[i-1],j,colors[i])
        c += ')'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def vga(self, m=0):
        return None
    
    def jet(self, m=0):
        c = 'defined (0 "blue", 3 "cyan", 4 "green", 5 "yellow", '\
            '8 "red", 10 "black")' # stop at red (remove black)
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def prism(self, m=0):
        return None

    def cool(self, m=0):
        c = 'defined (0 "cyan", 1 "magenta")'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def autumn(self, m=0):
        c = 'defined (0 "red", 1 "yellow")'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def spring(self, m=0):
        c = 'defined (0 "magenta", 1 "yellow")'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def winter(self, m=0):
        c = 'defined (0 "blue", 1 "spring-green")'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    
    def summer(self, m=0):
        c = 'defined (0 "green", 1 "yellow")'
        return 'set palette model RGB maxcolors %d %s' % (m,c)
    

plt = GnuplotBackend()  # create backend instance
use(plt, globals())     # export public namespace of plt to globals()
