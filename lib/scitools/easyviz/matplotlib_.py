"""
This backend uses the Python 2D plotting library Matplotlib (available from
http://matplotlib.sourceforge.net). To use this backend, one can run a
script somefile.py like

  python somefile.py --SCITOOLS_easyviz_backend matplotlib

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = matplotlib

and then

  from scitools.std import *

or if just easyviz is needed

  from scitools.easyviz import *

REQUIREMENTS:

Matplotlib

"""
from __future__ import division

from .common import *
from scitools.numpyutils import floor, linspace, array
from scitools.globaldata import DEBUG, VERBOSE
from scitools.misc import check_if_module_exists
from .misc import _update_from_config_file

check_if_module_exists('matplotlib', msg='You need to install the Matplotlib package.', abort=False)

import matplotlib
import matplotlib.colors
# Override values from the matplotlib configuration file with values
# from scitools.cfg before importing pylab
_update_from_config_file(matplotlib.rcParams, section='matplotlib')
matplotlib.interactive(True)
from matplotlib.font_manager import fontManager, FontProperties
import matplotlib.pyplot as pylab
from mpl_toolkits.mplot3d import axes3d, Axes3D
import re


class MatplotlibBackend(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self._init()

    def _init(self, *args, **kwargs):
        """Perform initialization that is special for this backend."""

        self.figure(self.getp('curfig'))

        # conversion tables for format strings:
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
        scale = ax.getp('scale')
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
            #self._g.gca().set_xscale('linear')
            #self._g.gca().set_yscale('linear')
            pass

    def _set_labels(self, ax):
        """Add text labels for x-, y-, and z-axis."""
        if DEBUG:
            print "Setting labels"
        xlabel = ax.getp('xlabel')
        ylabel = ax.getp('ylabel')
        zlabel = ax.getp('zlabel')
        xlabel = self._fix_latex(xlabel)
        ylabel = self._fix_latex(ylabel)
        zlabel = self._fix_latex(zlabel)
        if xlabel:
            # add a text label on x-axis
            self._g.xlabel(xlabel)
        if ylabel:
            # add a text label on y-axis
            self._g.ylabel(ylabel, rotation='vertical')
        if zlabel:
            # add a text label on z-axis
            pass

    def _set_title(self, ax):
        """Add a title at the top of the axis."""
        if DEBUG:
            print "Setting title"
        title = ax.getp('title')
        # The title can be a mix of math and text, leave this
        # to the user
        #title = self._fix_latex(title)
        if title:
            self._g.title(title)

    def _set_limits(self, ax):
        """Set axis limits in x, y, and z direction."""
        if DEBUG:
            print "Setting axis limits"
        mode = ax.getp('mode')
        if mode == 'auto':
            # let plotting package set 'nice' axis limits in the x, y,
            # and z direction. If this is not automated in the plotting
            # package, one can use the following limits:
            #xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            #self._g.axis('auto')
            pass
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.getp('xmin')
            xmax = ax.getp('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits
                self._g.gca().set_xlim(xmin, xmax)
            else:
                # let plotting package set x-axis limits or use
                #xmin, xmax = ax.getp('xlim')
                pass

            ymin = ax.getp('ymin')
            ymax = ax.getp('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                self._g.gca().set_ylim(ymin, ymax)
            else:
                # let plotting package set y-axis limits or use
                #ymin, ymax = ax.getp('ylim')
                pass

            zmin = ax.getp('zmin')
            zmax = ax.getp('zmax')
            if zmin is not None and zmax is not None:
                # set z-axis limits
                pass
            else:
                # let plotting package set z-axis limits or use
                #zmin, zmax = ax.getp('zlim')
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
        rect = ax.getp('viewport')
        if rect:
            # axes position is defined. In Matlab rect is defined as
            # [left,bottom,width,height], where the four parameters are
            # location values between 0 and 1 ((0,0) is the lower-left
            # corner and (1,1) is the upper-right corner).
            # NOTE: This can be different in the plotting package.
            pass

    def _set_daspect(self, ax):
        """Set data aspect ratio."""
        if ax.getp('daspectmode') == 'manual':
            dar = ax.getp('daspect')  # dar is a list (len(dar) is 3).
            xmin = ax.getp('xmin')
            xmax = ax.getp('xmax')
            ymin = ax.getp('ymin')
            ymax = ax.getp('ymax')
            r = float(xmax-xmin)/(ymax-ymin)
            self._g.gca().set_aspect(r*dar[0])
        elif ax.getp('daspectmode') == 'equal':
            self._g.gca().set_aspect('equal')
        else:
            # daspectmode is 'auto'. Plotting package handles data
            # aspect ratio automatically.
            self._g.gca().set_aspect('auto')

    def _set_axis_method(self, ax):
        method = ax.getp('method')
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

        direction = ax.getp('direction')
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
        if ax.getp('box'):
            # display box
            self._g.box(on=True)
        else:
            # do not display box
            self._g.box(on=False)

    def _set_grid(self, ax):
        """Turn grid lines on or off."""
        if DEBUG:
            print "Setting grid"
        if self._mpl3D:
            # Do not call self._g.grid for 3D surf plots
                return

        if ax.getp('grid'):
            # turn grid lines on
            self._g.grid(b=True)
        else:
            # turn grid lines off
            self._g.grid(b=False)

    def _set_hidden_line_removal(self, ax):
        """Turn on/off hidden line removal for meshes."""
        if DEBUG:
            print "Setting hidden line removal"
        if ax.getp('hidden'):
            # turn hidden line removal on
            pass
        else:
            # turn hidden line removal off
            pass

    def _set_colorbar(self, ax):
        """Add a colorbar to the axis."""
        if DEBUG:
            print "Setting colorbar"
        if self._mpl3D:
            # Do not call self._g.grid for 3D surf plots
                return

        cbar = ax.getp('colorbar')
        if cbar.getp('visible'):
            # turn on colorbar
            cbar_title = cbar.getp('cbtitle')
            cbar_location = self._colorbar_locations[cbar.getp('cblocation')]
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
        if ax.getp('caxismode') == 'manual':
            cmin, cmax = ax.getp('caxis')
            # NOTE: cmin and cmax might be None:
            if cmin is None or cmax is None:
                cmin, cmax = [0,1]
            # set color axis scaling according to cmin and cmax
            if self._mplsurf is not None:
                pass # cannot handle 3D surf
            else:
                self._g.clim(cmin,cmax)
        else:
            # use autoranging for color axis scale
            pass

    def _set_colormap(self, ax):
        """Set the colormap."""
        if DEBUG:
            print "Setting colormap"
        cmap = ax.getp('colormap')
        # cmap is plotting package dependent
        # the colormap is set in

    def _set_view(self, ax):
        """Set viewpoint specification."""
        if DEBUG:
            print "Setting view"
        cam = ax.getp('camera')
        view = cam.getp('view')
        if view == 2:
            # setup a default 2D view
            pass
        elif view == 3:
            az = cam.getp('azimuth')
            el = cam.getp('elevation')
            if az is None or el is None:
                # azimuth or elevation is not given. Set up a default
                # 3D view (az=-37.5 and el=30 is the default 3D view in
                # Matlab).
                pass
            else:
                # set a 3D view according to az and el
                pass

            if cam.getp('cammode') == 'manual':
                # for advanced camera handling:
                roll = cam.getp('camroll')
                zoom = cam.getp('camzoom')
                dolly = cam.getp('camdolly')
                target = cam.getp('camtarget')
                position = cam.getp('campos')
                up_vector = cam.getp('camup')
                view_angle = cam.getp('camva')
                projection = cam.getp('camproj')

    def _set_axis_props(self, ax):
        if DEBUG:
            print "Setting axis properties"
        self._set_title(ax)
        self._set_scale(ax)
        self._set_axis_method(ax)
        self._set_limits(ax)
        self._set_position(ax)
        self._set_daspect(ax)
        self._set_coordinate_system(ax)
        self._set_hidden_line_removal(ax)
        self._set_colorbar(ax)
        self._set_caxis(ax)
        self._set_colormap(ax)
        self._set_view(ax)
        if ax.getp('visible'):
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
        marker = self._markers[item.getp('linemarker')]
        color = item.getp('linecolor')
        style = item.getp('linetype')
        width = item.getp('linewidth')
        if PlotProperties._local_prop['default_lines'] == 'with_markers' \
               and color and marker == '' and style == '' \
               and item.getp('zdata') is None:
            # Add marker so that curves in png/pdf/eps can be distinguised
            # in black-and-white
            #if len(item.getp('xdata')) <= 61:  # this is solved in _add_line
            marker = PlotProperties._colors2markers[color]
            style = '-'
        if width:
            width = float(width)
        return marker, color, style, width

    def _fix_latex(self, legend):
        """Enclose legend in $$ if latex syntax is detected."""
        # We always support latex syntax either through direct
        # use of latex (text.usetex=true) or through the native mathtext.
        #if not matplotlib.rcParams['text.usetex']:
        #    return legend

        legend = legend.strip()
        if len(legend) >= 2 and legend[0] != '$' and legend[-1] != '$':
            # else: assume correct latex syntax, otherwise fix
            #print '....fix', legend,
            if '**' in legend:
                legend = legend.replace('**', '^')
            if '*' in legend:
                #legend = legend.replace('*', '\\cdot')
                legend = legend.replace('*', ' ')

            chars = '\\', '^', '_'
            latex = False
            for c in chars:
                if c in legend:
                    latex = True
                    break
            if latex:
                # make this math:
                legend = '$' + legend + '$'

                # enclose words in \hbox{}'es:
                # (not successful enough)
                #word = r'(\s?[^\\][A-Za-z][a-z]*[ :;,$)] ?)'
                #word = r'(\s?[A-Za-z][a-z]*[ :;,$)])'
                #word = r'(\w[ :;,$)])'
                #word = r'(\b[A-Za-z][a-z]*[ :;,$)]\b)'
                #if re.search(word, legend):
                #    legend = re.sub(word, r'\hbox{\g<1>}', legend)
                # remove internal $ chars:
                legend = legend.replace('$', '')
                legend = '$' + legend + '$'

                # fix sin, cos, exp, ln, log, etc:
                def _fix_func(func, newfunc, legend):
                    if re.search(r'[^\\]'+func, legend):
                        legend = legend.replace(func, '\\'+newfunc)
                    return legend
                funcs = 'sin', 'cos', 'tan', 'exp', 'ln', 'log', \
                        'sinh', 'cosh', 'tanh'
                for func in funcs:
                    legend = _fix_func(func, func, legend)
                funcs = [('atan', 'arctan'), ('asin', 'arcsin'),
                         ('acos', 'arccos'),]
                for func, newfunc in funcs:
                    legend = _fix_func(func, newfunc, legend)
                #print 'after fix:', legend
        return legend

    def _add_line(self, item):
        """Add a 2D or 3D curve to the scene."""
        if DEBUG:
            print "Adding a line"
        # get data:
        x = squeeze(item.getp('xdata'))
        y = squeeze(item.getp('ydata'))
        z = item.getp('zdata')
        if z is not None:
            z = squeeze(z)
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        fmt = marker+color+style
        if not width:
            width = 1.0
        #print 'plt: %s color=[%s] marker=[%s] style=[%s]' % (fmt, color, marker, style), width

        if z is not None:
            # zdata is given, add a 3D curve:
            print "No support for plot3 in Matplotlib."
        else:
            # no zdata, add a 2D curve:
            #l, = self._g.plot(x,y,fmt,linewidth=width)
            l = self._g.plot(x,y,fmt,linewidth=width)
            legend = item.getp('legend')
            legend = self._fix_latex(legend)
            if legend:
                l[0].set_label(legend)
            if marker and width != 1.0:
                # marker size is given in pixels in matplotlib
                markersize = width*5
                l[0].set_markersize(markersize)
                l[0].set_markeredgecolor(color)
                # unfilled markers
                l[0].set_markerfacecolor("None")  # note the quotes!
                # use thicker lines for larger markers
                marker_lw = 1 if width <= 2 else width/2
                l[0].set_markeredgewidth(marker_lw)

            if style == '-' and marker == PlotProperties._colors2markers[color]\
               and len(x) > 61:
                # assume that user has empty format spec and that
                # _get_linespecs has set marker and solid line, then
                # limit to 15 markers for visibility
                every = int(len(x)/15.)
                l[0].set_markevery(every)
                # downside: user has specified line and markers, but with
                # line one should limit the no of markers - if data points
                # are important, the user should use markers only, or
                # dashed lines

    def _add_filled_line(self, item):
        """Add a 2D or 3D filled curve."""
        if DEBUG:
            print "Adding a line"
        # get data:
        x = squeeze(item.getp('xdata'))
        y = squeeze(item.getp('ydata'))
        z = item.getp('zdata')
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        if not width:
            width = 1.0

        facecolor = item.getp('facecolor')
        if not facecolor:
            if not color:
                color = 'b'
            facecolor = color
        edgecolor = item.getp('edgecolor')
        if not edgecolor:
            edgecolor = 'k'  # use black for now
            # FIXME: edgecolor should be ax.getp('fgcolor') by default
        opacity = item.getp('material').getp('opacity')
        if opacity is None:
            opacity = 1.0

        if z is not None:
            # zdata is given, add a filled 3D curve:
            print "No support for fill3 in Matplotlib."
        else:
            # no zdata, add a filled 2D curve:
            l = self._g.fill(x, y, fc=facecolor, ec=edgecolor,
                              linewidth=width, alpha=opacity)
            legend = item.getp('legend')
            legend = self._fix_latex(legend)
            if legend:
                l[0].set_label(legend)

    def _add_bar_graph(self, item, shading='faceted'):
        if DEBUG:
            print "Adding a bar graph"
        # get data:
        x = squeeze(item.getp('xdata'))
        y = squeeze(item.getp('ydata'))
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        edgecolor = item.getp('edgecolor')
        if not edgecolor:
            edgecolor = 'k'  # use black for now
            # FIXME: edgecolor should be same as ax.getp('fgcolor') by default
        facecolor = item.getp('facecolor')
        if not facecolor:
            facecolor = color
        opacity = item.getp('material').getp('opacity')
        if opacity is None:
            opacity = 1.0

        if y.ndim == 1:
            y = reshape(y,(len(y),1))
        nx, ny = shape(y)

        step = item.getp('barstepsize')/10

        center = floor(ny/2)
        start = -step*center
        stop = step*center
        if not ny%2:
            start += step/2
            stop -= step/2
        a = linspace(start,stop,ny)

        barwidth = item.getp('barwidth')/10

        hold_state = self._g.ishold()
        self._g.hold(True)
        colors = PlotProperties._colors + \
                 list(matplotlib.colors.cnames.values())
        for j in range(ny):
            y_ = y[:,j]
            x_ = array(list(range(nx))) + a[j] - barwidth/2
            if not facecolor:
                c = colors[j]
            else:
                c = facecolor
            self._g.bar(x_, y_, width=barwidth, color=c,
                        ec=edgecolor, alpha=opacity)
        self._g.hold(hold_state)

        barticks = item.getp('barticks')
        if barticks is None:
            barticks = x
        if item.getp('rotated_barticks'):
            self._g.xticks(list(range(len(x))), barticks, rotation=90)
        else:
            self._g.xticks(list(range(len(x))), barticks)

    def _add_surface(self, item, shading='faceted', colormap=None,
                     showcolorbar=False, zmin=None, zmax=None):
        if DEBUG:
            print "Adding a surface"
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = item.getp('zdata')           # scalar field
        c = item.getp('cdata')           # pseudocolor data (can be None)
        legend = item.getp('legend')
        legend = self._fix_latex(legend)

        if colormap is None or colormap == 'default':
            colormap = self._g.cm.get_cmap('jet')

        if shape(x) != shape(z) or shape(y) != shape(z):
            x, y = meshgrid(x, y, sparse=False,
                            indexing=item.getp('indexing'))

        opacity = item.getp('material').getp('opacity')
        if opacity is None:
            opacity = 1.0

        contours = item.getp('contours')
        if contours:
            # the current item is produced by meshc or surfc and we
            # should therefore add contours at the bottom:
            #self._add_contours(contours, placement='bottom')
            print "No support for meshc/surfc in Matplotlib."

        if item.getp('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            fig = self._g.gcf()
            #ax = fig.gca(projection='3d') # old syntax
            #ax = Axes3D(fig)
            ax = fig.add_subplot(111, projection='3d')
            h = ax.plot_wireframe(x, y, z)
            if legend:
                h.set_label(legend)
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            function = item.getp('function')
            if function == 'pcolor':
                h = self._g.pcolor(x, y, z, shading=shading,
                                   cmap=colormap, alpha=opacity)
            else:
                # This is really a hack to use 3D surfaces in matplotlib...
                fig = self._g.gcf()
                #ax = fig.gca(projection='3d')
                #ax = Axes3D(fig)
                ax = fig.add_subplot(111, projection='3d')
                if self._mplsurf is not None:
                    try:
                        ax.collections.remove(self._mplsurf)
                    except ValueError:
                        pass
                self._mplsurf = ax.plot_surface(x, y, z, rstride=1, cstride=1,
                                                linewidth=0, cmap=colormap,
                                                antialiased=False)
                if showcolorbar and not self._mpl3D:
                    # Show colorbar only for the first plot in an animation
                    fig.colorbar(self._mplsurf, shrink=1.0, aspect=15,
                                 orientation='vertical',)
                if zmin is not None and zmax is not None:
                    ax.set_zlim3d(zmin, zmax)
                self._mpl3D = True
                # Problem: cannot fix color scale (or?)

            if legend:
                h.set_label(legend)

    def _add_contours(self, item, placement=None, colormap=None):
        # The placement keyword can be either None or 'bottom'. The
        # latter specifies that the contours should be placed at the
        # bottom (as in meshc or surfc).
        if DEBUG:
            print "Adding contours"
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = item.getp('zdata')           # scalar field
        legend = item.getp('legend')
        legend = self._fix_latex(legend)

        if colormap is None or colormap == 'default':
            colormap = self._g.cm.get_cmap('jet')

        if shape(x) != shape(z) or shape(y) != shape(z):
            x, y = meshgrid(x, y, sparse=False,
                            indexing=item.getp('indexing'))

        opacity = item.getp('material').getp('opacity')
        if opacity is None:
            opacity = 1.0

        filled = item.getp('filled')  # draw filled contour plot if True

        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            pass
        else:
            clevels = cvector

        contour_cmd = self._g.contour
        location = item.getp('clocation')
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
        kwargs = {'cmap': colormap, 'alpha': opacity}

        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)
        if color:
            kwargs['colors'] = color
            kwargs['cmap'] = None

        if width:
            kwargs['linewidths'] = width

        if legend:
            kwargs['label'] = legend
        cs = contour_cmd(x,y,z,clevels,**kwargs)

        if item.getp('clabels'):
            # add labels on the contour curves
            self._g.clabel(cs)

    def _add_vectors(self, item):
        if DEBUG:
            print "Adding vectors"
        # uncomment the following command if there is no support for
        # automatic scaling of vectors in the current plotting package:
        #item.scale_vectors()

        # grid components:
        x = squeeze(item.getp('xdata'))
        y = squeeze(item.getp('ydata'))
        z = item.getp('zdata')
        # vector components:
        u, v, w = item.getp('udata'), item.getp('vdata'), item.getp('wdata')
        # get line specifiactions (marker='.' means no marker):
        marker, color, style, width = self._get_linespecs(item)
        indexing = item.getp('indexing')

        legend = item.getp('legend')
        legend = self._fix_latex(legend)

        # scale the vectors according to this variable (scale=0 should
        # turn off automatic scaling):
        scale = item.getp('arrowscale')
        if scale == 0:
            scale = None

        filled = item.getp('filledarrows') # draw filled arrows if True

        if z is not None and w is not None:
            # draw velocity vectors as arrows with components (u,v,w) at
            # points (x,y,z):
            print "No support for quiver3 in Matplotlib."
        else:
            # draw velocity vectors as arrows with components (u,v) at
            # points (x,y):
            if shape(x) != shape(u) and shape(y) != shape(u):
                x, y = meshgrid(x, y, sparse=False, indexing=indexing)
            if not color:
                c = u**2+v**2  # color arrows by magnitude
                h = self._g.quiver(x,y,u,v,c,scale=scale)
            else:
                h = self._g.quiver(x,y,u,v,scale=scale,color=color)
            if legend:
                h.set_label(legend)

    def _add_streams(self, item):
        if DEBUG:
            print "Adding streams"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        # vector components:
        u, v, w = item.getp('udata'), item.getp('vdata'), item.getp('wdata')
        # starting positions for streams:
        sx, sy, sz = item.getp('startx'), item.getp('starty'), item.getp('startz')

        if item.getp('tubes'):
            # draw stream tubes from vector data (u,v,w) at points (x,y,z)
            n = item.getp('n') # no points along the circumference of the tube
            scale = item.getp('tubescale')
            pass
        elif item.getp('ribbons'):
            # draw stream ribbons from vector data (u,v,w) at points (x,y,z)
            width = item.getp('ribbonwidth')
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
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume
        c = item.getp('cdata')  # pseudocolor data
        isovalue = item.getp('isovalue')

    def _add_slices(self, item):
        if DEBUG:
            print "Adding slices in a volume"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume

        sx, sy, sz = item.getp('slices')
        if sz.ndim == 2:
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
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume

        sx, sy, sz = item.getp('slices')
        if sz.ndim == 2:
            # sx, sy, and sz defines a surface
            pass
        else:
            # sx, sy, and sz is either numbers or vectors with numbers
            pass

        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels per plane
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            pass
        pass

    def _set_figure_size(self, fig):
        if DEBUG:
            print "Setting figure size"
        width, height = fig.getp('size')
        if width and height:
            # set figure width and height
            fig = self._g.gcf()
            fig.set_size_inches(width,height)
        else:
            # use the default width and height in plotting package
            pass

    def figure(self, *args, **kwargs):
        # Extension of BaseClass.figure:
        # add a plotting package figure instance as fig._g and create a
        # link to it as self._g
        fignum = BaseClass.figure(self, *args, **kwargs)
        fig = self.gcf()
        try:
            fig._g
        except:
            # create plotting package figure and save figure instance
            # as fig._g
            if DEBUG:
                name = 'Fig ' + str(fignum)
                print "creating figure %s in backend" % name

            fig._g = pylab

        self._g = fig._g # link for faster access
        self._mpl3D = False
        self._mplsurf = None
        self._texts = {}  # store calls to text (for replot)
        return fignum

    def _replot(self):
        """Replot all axes and all plotitems in the backend."""
        # NOTE: only the current figure (gcf) is redrawn.
        if DEBUG:
            print "Doing replot in backend"

        # turn off interactive in pyplot temporarily:
        old_pylab_interactive_state = self._g.isinteractive()
        self._g.ioff()

        fig = self.gcf()
        try:
            fig._g
        except:
            self.figure(self.getp('curfig'))
        self._g.figure(self.getp('curfig'))

        # reset the plotting package instance in fig._g now if needed
        if not self._mpl3D:
            self._g.clf()

        self._set_figure_size(fig)

        nrows, ncolumns = fig.getp('axshape')
        for axnr, ax in list(fig.getp('axes').items()):
            if ax.getp('numberofitems') == 0:
                continue
            if nrows != 1 or ncolumns != 1:
                # create axes in tiled position
                # this is subplot(nrows, ncolumns, axnr)
                self._g.subplot(nrows, ncolumns, axnr)
            else:
                rect = ax.getp('viewport')
                if isinstance(rect, (list,tuple)) and len(rect) == 4 and \
                       ax.getp('pth') is None:
                    self._g.axes(rect)
            legends = False
            plotitems = ax.getp('plotitems')
            plotitems.sort(self._cmpPlotProperties)
            for item in plotitems:
                func = item.getp('function') # function that produced this item
                if isinstance(item, Line):
                    if func == 'fill':
                        self._add_filled_line(item)
                    else:
                        self._add_line(item)
                elif isinstance(item, Bars):
                    self._add_bar_graph(item, shading=ax.getp('shading'))
                elif isinstance(item, Surface):
                    self._add_surface(item,
                      shading=ax.getp('shading'),
                      colormap=ax.getp('colormap'),
                      showcolorbar=ax.getp('colorbar').getp('visible'),
                      zmin=ax.getp('zmin'),
                      zmax=ax.getp('zmax'))
                elif isinstance(item, Contours):
                    self._add_contours(item, colormap=ax.getp('colormap'))
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
                legend = item.getp('legend')
                legend = self._fix_latex(legend)
                if legend:
                    # add legend to plot
                    legends = True
                if ax.getp('numberofitems') > 1 and not self._g.ishold():
                    self._g.hold(True)

            if legends:
                try:
                    loc = ax.getp('legend_loc')
                except KeyError:
                    loc = 'best'
                try:
                    fancybox = ax.getp('legend_fancybox')
                except KeyError:
                    fancybox = True
                self._g.legend(loc=loc, fancybox=fancybox)

            self._set_axis_props(ax)

        # Display texts
        for args in self._texts:
            self.text(args[0], args[1], args[2],
                      fontname=args[3], fontsize=args[4])

        # set back the interactive state in pylab:
        if old_pylab_interactive_state:
            self._g.ion()

        self._g.draw()
        if self.getp('show'):
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            self._g.figure(self.getp('curfig'))  # raise figure
            # Or is there a better way to draw the current figure without
            # calling pylab.show()?
            #self._g.show()

    def text(self, x, y, text,
             fontname=Axis._local_prop['fontname'],
             fontsize=Axis._local_prop['fontsize']):
        """Write text at position (x,y) in a curveplot."""
        self._g.text(x, y, text, family=fontname, size=fontsize)
        self._texts[(x, y, text, fontname, fontsize)] = None


    def hardcopy(self, filename, **kwargs):
        """
        Supported extensions: .eps, .jpg, .pdf, .png, .ps, and .svg
        This is dependent on the Matplotlib backend.

        Optional arguments:

          dpi         -- image resolution. Default is 100.
          orientation -- 'portrait' (default) or 'landscape'. Only available
                         for PostScript output.

        Note: if `filename` is just the file extension, such as ``.svg``,
        the file content is returned as a string *and* saved to
        ``tmp.svg``.
        """
        self.setp(**kwargs)
        color = self.getp('color')
        replot = kwargs.get('replot', True)
        if replot:
            self._replot()

        if DEBUG:
            print "Hardcopy to %s" % filename

        dpi = kwargs.get('dpi', 100)
        orientation = kwargs.get('orientation', 'portrait')

        imgdata = None
        if filename.startswith('.'):
            from StringIO import StringIO
            imgdata = StringIO()
            self._g.savefig(imgdata,
                            format=filename[1:],
                            dpi=dpi,
                            facecolor='w',
                            edgecolor='w',
                            orientation=orientation)
            imgdata.seek(0)
            filename = 'tmp' + filename  # dump to file too

        self._g.savefig(filename,
                        dpi=dpi,
                        facecolor='w',
                        edgecolor='w',
                        orientation=orientation)

        if imgdata is None:
            return None
        else:
            if filename.endswith('.svg'):
                # Strip off the initial XML lines
                figdata = '<svg' + imgdata.buf.split('<svg')[1]
            else:
                figdata = imgdata.buf
            return figdata

    def clf(self):
        self._g.clf()
        BaseClass.clf(self)

    def closefig(self, arg=None):
        if arg is None:
            num = self.getp('curfig')  # close current figure
        elif arg in self._figs:
            num = arg
        elif arg in list(self._figs.values()):
            for fignr, fig in list(self._figs.items()):
                if fig == arg:
                    num = fignr
                    break
        else:
            raise ValueError("closefig: cannot close figure '%s'" % arg)
        self._g.close(num)
        #del self._figs[num]._g
        #del self._figs[num]

    def closefigs(self):
        for key in self._figs:
            self.closefig(key)
        del self._g
        BaseClass.closefigs(self)

    # Colormap methods:
    def hsv(self, m=None):
        return pylab.cm.get_cmap('hsv', m)

    def hot(self, m=None):
        return pylab.cm.get_cmap('hot', m)

    def gray(self, m=None):
        return pylab.cm.get_cmap('gray', m)

    def bone(self, m=None):
        return pylab.cm.get_cmap('bone', m)

    def copper(self, m=None):
        return pylab.cm.get_cmap('copper', m)

    def pink(self, m=None):
        return pylab.cm.get_cmap('pink', m)

    def white(self, m=None):
        raise NotImplementedError('white not implemented in class %s' % \
                                  self.__class__.__name__)

    def flag(self, m=None):
        return pylab.cm.get_cmap('flag', m)

    def lines(self, m=None):
        raise NotImplementedError('lines not implemented in class %s' % \
                                  self.__class__.__name__)

    def colorcube(self, m=None):
        raise NotImplementedError('colorcube not implemented in class %s' % \
                                  self.__class__.__name__)

    def vga(self, m=None):
        raise NotImplementedError('vga not implemented in class %s' % \
                                  self.__class__.__name__)

    def jet(self, m=None):
        return pylab.cm.get_cmap('jet', m)

    def prism(self, m=None):
        return pylab.cm.get_cmap('prism', m)

    def cool(self, m=None):
        return pylab.cm.get_cmap('cool', m)

    def autumn(self, m=None):
        return pylab.cm.get_cmap('autumn', m)

    def spring(self, m=None):
        return pylab.cm.get_cmap('spring', m)

    def winter(self, m=None):
        return pylab.cm.get_cmap('winter', m)

    def summer(self, m=None):
        return pylab.cm.get_cmap('summer', m)


    # Now we add the doc string from the methods in BaseClass to the
    # methods that are reimplemented in this backend:
    for cmd in BaseClass._matlab_like_cmds:
        if not '__' in cmd and hasattr(BaseClass, cmd):
            m1 = eval('BaseClass.%s' % cmd)
            try:
                m2 = eval('%s' % cmd)
            except NameError:
                pass
            else:
                if m1.__doc__ != m2.__doc__:
                    if m2.__doc__ is None:
                        m2.__doc__ = ""
                    m2.__doc__ = m1.__doc__ + m2.__doc__


plt = MatplotlibBackend()  # create backend instance
use(plt, globals())        # export public namespace of plt to globals()

# We should close all figure windows on program exit:
import atexit
atexit.register(close, 'all')

backend = os.path.splitext(os.path.basename(__file__))[0][:-1]
