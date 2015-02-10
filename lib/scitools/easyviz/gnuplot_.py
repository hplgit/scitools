"""
This backend uses the Gnuplot plotting program together with the
Gnuplot.py Python module. One can specify this backend by

  python somefile.py --SCITOOLS_easyviz_backend gnuplot

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = gnuplot

and then

  from scitools.std import *

or if just easyviz is needed

  from scitools.easyviz import *

REQUIREMENTS:

Gnuplot >= 4.0
Gnuplot.py

Tip:

  To close a figure window, press <q> when active

"""

from __future__ import division

from .common import *
from scitools.numpyutils import ones, ravel, shape, newaxis, transpose, \
     linspace, floor, array
from scitools.globaldata import DEBUG, VERBOSE
from scitools.misc import check_if_module_exists , system
from .misc import _update_from_config_file, _check_type
import collections

check_if_module_exists('Gnuplot', msg='You need to install the Gnuplot.py package.', abort=False)
import Gnuplot
import tempfile
import os
import sys
import operator
import string
import time

# Update Gnuplot.GnuplotOpts according to scitools.cfg
_update_from_config_file(Gnuplot.GnuplotOpts.__dict__, section='gnuplot')

def _check_terminal(term):
    """Return True if the given terminal work with Gnuplot, otherwise False."""
    f = open(tempfile.mktemp(suffix='.gnuplot'), 'w')
    f.write('set term %s\n' % term)
    f.close()
    cmd = '%s < %s' % (Gnuplot.GnuplotOpts.gnuplot_command, f.name)
    failure, output = system(cmd, verbose=False, failure_handling='silent')
    os.remove(f.name)
    return not failure

def _check_terminals(terms):
    """Check if the default terminal (Gnuplot.GnuplotOpts.default_term)
    work with Gnuplot. If not, try any of the terminals given in terms.
    Change the default terminal as necessary. Gnuplot will fail later if
    a working terminal can't be found.
    """
    _check_type(terms, 'terms', (list, tuple))
    working_term = None
    default_term = Gnuplot.GnuplotOpts.default_term
    if len(terms) == 0 or default_term != terms[0]:
        terms = [default_term] + terms
    for term in terms:
        term_ok = _check_terminal(term)
        if term_ok:
            working_term = term
            break
    if working_term is not None:
        if working_term == default_term:
            # Gnuplot is built with the chosen terminal and it seems to be
            # working so we don't need to do anything.
            pass
        else:
            Gnuplot.GnuplotOpts.default_term = working_term
            if VERBOSE:
                print "Note: Default terminal for Gnuplot changed from " \
                      "%s to %s." % (default_term, working_term)
    else:
        # no working terminals found, will probably fail later
        print "Warning: Unable to find a working terminal for use with %s" % \
              Gnuplot.GnuplotOpts.gnuplot_command

if sys.platform == "darwin":
    _check_terminals(['aqua', 'wxt', 'x11'])
elif sys.platform == "linux2":
    _check_terminals(['wxt', 'qt', 'x11'])

_gnuplotpy_major = Gnuplot.__version__[0]
_gnuplotpy_minor = Gnuplot.__version__[2]
if _gnuplotpy_major == 1 and _gnuplotpy_minor <= 7:
    if os.uname()[-1] == 'x86_64':
        # Gnuplot.py <= 1.7 only supports Numeric (not NumPy) and Numeric
        # does not work on 64 bits platform.
        print ("Warning: Gnuplot.py version %s is not support on 64 bits " \
               "platform. Please upgrade to Gnuplot.py 1.8 or newer.") % \
               Gnuplot.__version__

def get_gnuplot_version():
    """Return Gnuplot version used in Gnuplot.py."""
    f = os.popen('%s --version' % Gnuplot.GnuplotOpts.gnuplot_command)
    return f.readline().split()[1]

# This function is taken from utils.py in Gnuplot.py and modified to fix
# the problem with this message when plotting contours:
#
#   Notice: Cannot contour non grid data. Please use "set dgrid3d"
#
def write_array(f, set,
                item_sep=' ',
                nest_prefix='', nest_suffix='\n', nest_sep=''):
    """Write an array of arbitrary dimension to a file.

    A general recursive array writer.  The last four parameters allow
    a great deal of freedom in choosing the output format of the
    array.  The defaults for those parameters give output that is
    gnuplot-readable.  But using '(",", "{", "}", ",\n")' would output
    an array in a format that Mathematica could read.  'item_sep'
    should not contain '%' (or if it does, it should be escaped to
    '%%') since it is put into a format string.

    The default 2-d file organization::

        set[0,0] set[0,1] ...
        set[1,0] set[1,1] ...

    The 3-d format::

        set[0,0,0] set[0,0,1] ...
        set[0,1,0] set[0,1,1] ...

        set[1,0,0] set[1,0,1] ...
        set[1,1,0] set[1,1,1] ...

    """

    if len(set.shape) == 1:
        (columns,) = set.shape
        assert columns > 0
        fmt = string.join(['%s'] * columns, item_sep)
        f.write(nest_prefix)
        f.write(fmt % tuple(set.tolist()))
        f.write(nest_suffix)
    elif len(set.shape) == 2:
        # This case could be done with recursion, but `unroll' for
        # efficiency.
        (points, columns) = set.shape
        assert points > 0 and columns > 0
        fmt = string.join(['%s'] * columns, item_sep)
        f.write(nest_prefix + nest_prefix)
        f.write(fmt % tuple(set[0].tolist()))
        f.write(nest_suffix)
        for point in set[1:]:
            f.write(nest_sep + nest_prefix)
            f.write(fmt % tuple(point.tolist()))
            f.write(nest_suffix)
        f.write(nest_suffix)
    else:
        # Use recursion for three or more dimensions:
        assert set.shape[0] > 0
        f.write(nest_prefix)
        write_array(f, set[0],
                    item_sep, nest_prefix, nest_suffix, nest_sep)
        for subset in set[1:]:
            f.write(nest_sep)
            write_array(f, subset,
                        item_sep, nest_prefix, nest_suffix, nest_sep)
        # Here is the fix: We comment out the next line so that we have
        # only one newline character at the end of the temporary files:
        #f.write(nest_suffix)

Gnuplot.utils.write_array = write_array

# Change the order in which to cycle through line colors when plotting multiple
# lines with the plot (or plot3) command. In Gnuplot we start with red since
# this gives a solid line in black and white hardcopies:
Axis._local_prop['colororder'] = 'r b g c m y'.split()
# sequence in other backends: b r g m c y k

class GnuplotBackend(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self._init()

    def _init(self, *args, **kwargs):
        """Perform initialization that is special for this backend."""

        # Necessary to add a Gnuplot Session as _g to the Figure instance.
        # self._g will now point to the correct instance saved as _g in
        # curfig.
        self.figure(self.getp('curfig'))

        # conversion tables for format strings:
        self._markers = {
            '': None,# no marker
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
            '' : 1,  # no color --> red (gives solid line)
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

        self._doing_PS = False  # indicator for PostScript hardcopy

        if DEBUG:
            print "Setting backend standard variables"
            for disp in 'self._markers self._colors self._line_styles'.split():
                print disp, eval(disp)

    def _set_scale(self, ax):
        """Set linear or logarithmic (base 10) axis scale."""
        if DEBUG:
            print "Setting scales"
        scale = ax.getp('scale')
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
        """Add text labels for x-, y-, and z-axis."""
        if DEBUG:
            print "Setting labels"
        xlabel = ax.getp('xlabel')
        ylabel = ax.getp('ylabel')
        zlabel = ax.getp('zlabel')
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
        """Add a title at the top of the axis."""
        if DEBUG:
            print "Setting title"
        title = self._fix_latex(ax.getp('title'))
        if title:
            self._g('set title "%s"' % title)
        else:
            self._g('unset title')

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
            self._g('set xrange[*:*]')
            self._g('set yrange[*:*]')
            self._g('set zrange[*:*]')
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.getp('xmin')
            xmax = ax.getp('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits
                self._g('set xrange[%g:%g]' % (xmin, xmax))
            else:
                # let plotting package set x-axis limits or use
                #xmin, xmax = ax.getp('xlim')
                self._g('set xrange[*:*]')

            ymin = ax.getp('ymin')
            ymax = ax.getp('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                self._g('set yrange[%g:%g]' % (ymin, ymax))
            else:
                # let plotting package set y-axis limits or use
                #ymin, ymax = ax.getp('ylim')
                self._g('set yrange[*:*]')

            zmin = ax.getp('zmin')
            zmax = ax.getp('zmax')
            if zmin is not None and zmax is not None:
                # set z-axis limits
                self._g('set zrange[%g:%g]' % (zmin, zmax))
            else:
                # let plotting package set z-axis limits or use
                #zmin, zmax = ax.getp('zlim')
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
        """Set axes position."""
        rect = ax.getp('viewport')
        if isinstance(rect, (list,tuple)) and len(rect) == 4 and \
               ax.getp('pth') is None:
            # axes position is defined. In Matlab rect is defined as
            # [left,bottom,width,height], where the four parameters are
            # location values between 0 and 1 ((0,0) is the lower-left
            # corner and (1,1) is the upper-right corner).
            # NOTE: This can be different in the plotting package.
            self._g('set origin %g,%g' % tuple(rect[:2]))
            self._g('set size %g,%g' % tuple(rect[2:]))

    def _set_daspect(self, ax):
        """Set data aspect ratio."""
        if ax.getp('daspectmode') == 'manual':
            dar = ax.getp('daspect')  # dar is a list (len(dar) is 3).
            # In Gnuplot we cannot set individual aspects for the different
            # axes. Therefore we use dar[0] as the aspect ratio:
            self._g('set size ratio %s' % dar[0])
        elif ax.getp('daspectmode') == 'equal':
            xmin = ax.getp('xmin')
            xmax = ax.getp('xmax')
            ymin = ax.getp('ymin')
            ymax = ax.getp('ymax')
            try:
                r = (ymax-ymin)/float(xmax-xmin)
            except TypeError:
                raise ValueError('daspectmode="equal" requires the axes to be explicitly set')
            self._g('set size ratio %g' % r)
        else:
            # daspectmode is 'auto'. Plotting package handles data
            # aspect ratio automatically.
            pass

    def _set_axis_method(self, ax):
        method = ax.getp('method')
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
            self._g('set yrange [] reverse')
        elif direction == 'xy':
            # use the default Cartesian axes form. The origin is at the
            # lower-left corner. The x-axis is vertical and numbered
            # from left to right, while the y-axis is vertical and
            # numbered from bottom to top.
            self._g('set yrange [] noreverse')

    def _set_box(self, ax):
        """Turn box around axes boundary on or off."""
        if DEBUG:
            print "Setting box"
        if ax.getp('box'):
            # display box
            self._g('set border 4095 linetype -1 linewidth .4')
        else:
            # do not display box
            pass

    def _set_grid(self, ax):
        """Turn grid lines on or off."""
        if DEBUG:
            print "Setting grid"
        if ax.getp('grid'):
            # turn grid lines on
            self._g('set grid')
        else:
            # turn grid lines off
            self._g('unset grid')

    def _set_hidden_line_removal(self, ax):
        """Turn on/off hidden line removal for meshes."""
        if DEBUG:
            print "Setting hidden line removal"
        if ax.getp('hidden'):
            # turn hidden line removal on
            self._g('set hidden3d')
        else:
            # turn hidden line removal off
            self._g('unset hidden3d')

    def _set_colorbar(self, ax):
        """Add a colorbar to the axis."""
        if DEBUG:
            print "Setting colorbar"
        cbar = ax.getp('colorbar')
        if cbar.getp('visible'):
            # turn on colorbar
            cbar_title = cbar.getp('cbtitle')
            self._g('set cblabel "%s"' % cbar_title)
            cbar_location = self._colorbar_locations[cbar.getp('cblocation')]
            self._g('set style line 2604 linetype -1 linewidth .4')
            self._g('set colorbox %s user border 2604 origin %g,%g size %g,%g'\
                    % cbar_location)
        else:
            # turn off colorbar
            self._g('unset colorbox')

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
            self._g('set cbrange [%s:%s]' % (cmin,cmax))
        else:
            # use autoranging for color axis scale
            self._g('set cbrange [*:*]')

    def _set_colormap(self, ax):
        """Set the colormap."""
        if DEBUG:
            print "Setting colormap"
        cmap = ax.getp('colormap')
        # cmap is plotting package dependent
        if isinstance(cmap, str) and cmap != 'default':
            self._g(cmap)
        elif isinstance(cmap, (tuple,list)) and len(cmap) == 3 and \
                 isinstance(cmap[0], int) and \
                 isinstance(cmap[1], int) and \
                 isinstance(cmap[2], int):
            self._g('set palette rgbformulae %d,%d,%d' % cmap) # model RGB?
        elif isinstance(cmap, collections.Sequence) and cmap.ndim == 2:
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
        """Set viewpoint specification."""
        if DEBUG:
            print "Setting view"
        self._g('unset view')
        cam = ax.getp('camera')
        view = cam.getp('view')
        if view == 2:
            # setup a default 2D view
            self._g('set view map')
        elif view == 3:
            az = cam.getp('azimuth')
            el = cam.getp('elevation')
            if az is None or el is None:
                # azimuth or elevation is not given. Set up a default
                # 3D view (az=-37.5 and el=30 is the default 3D view in
                # Matlab).
                az, el = (60,325) # default 3D view in Gnuplot
            if (az >= 0 and az <= 180) and (el >= 0 and el <= 360):
                self._g('set view %d,%d' % (az,el))
            else:
                print 'view (%s,%s) out of range [0:180,0:360]' % (az,el)

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
        if ax.getp('visible'):
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

    def _fix_latex(self, legend):
        """
        Translate latex syntax in title and legend to enhanced
        PostScript symbols (enable greek letters, super- and subscripts,
        etc.).
        """
        legend = legend.strip()
        # General fix of latex syntax (more readable)
        legend = legend.replace('**', '^')
        #legend = legend.replace('*', '')
        legend = legend.replace('$', '')
        legend = legend.replace('{', '')
        legend = legend.replace('}', '')
        # Translate greek letters if PostScript output
        if self._doing_PS:
            ps2greek = dict(
                A='Alpha', N='Nu', a='alpha',	n='nu', B='Beta', O='Omicron',
                b='beta', o='omicron', C='Chi', P='Pi', c='chi',	p='pi',
                D='Delta', Q='Theta', d='delta', q='theta', E='Epsilon',
                R='Rho', e='epsilon', r='rho', F='Phi', S='Sigma', f='phi',
                s='sigma', G='Gamma', T='Tau', g='gamma', t='tau',
                H='Eta', U='Upsilon', h='eta', u='upsilon',
                I='iota', W='Omega', i='iota', w='omega',
                K='Kappa', X='Xi', k='kappa', l='lambda', x='xi',
                L='Lambda', Y='Psi', y='psi',
                M='Mu', Z='Zeta', m='mu', z='zeta')
            greek2ps = {}
            for char in ps2greek:
                greek2ps[ps2greek[char]] = char

            for greek_letter in greek2ps:
                glb = '\\' + greek_letter
                if glb in legend:
                    legend = legend.replace(glb, '{/Symbol %s}' %
                                            greek2ps[greek_letter])
            legend = legend.replace('*', '')

        legend = legend.replace('\\', '')
        return legend

    def _get_linespecs(self, item):
        """
        Return the line marker, line color, line style, and
        line width of the item.
        """
        marker = self._markers[item.getp('linemarker')]
        color = self._colors[item.getp('linecolor')]
        style = self._line_styles[item.getp('linetype')]
        width = item.getp('linewidth')

        if PlotProperties._local_prop['default_lines'] == 'with_markers' \
           and color and marker == None and style == None \
           and item.getp('zdata') is None:
            # Add marker (if not too many points) so that curves in
            # png/eps can be distinguised in black-and-white
            #if len(item.getp('xdata')) <= 61:  # fixed in _add_line

            if item.getp('linecolor'):
                marker = self._markers[PlotProperties._colors2markers[
                    item.getp('linecolor')]]
            else:
                marker = None
            style = 'lines'
            width = 1  # only PNG needs thicker lines and that is set in hardcopy (savefig)

        return marker, color, style, width

    def _get_withstring(self, marker, color, style, width):
        if not width:
            width = 1
        else:
            width = int(width)

        withstring = ''
        if color is not None:
            if style is None:
                if marker:
                    # use thicker lines for larger markers
                    marker_lw = 1 if width <= 2 else width/2

                    withstring = "points lt %d pt %d ps %d lw %s" \
                                 % (color, marker, width, marker_lw)
                else:
                    withstring = "lines lt %d lw %d" % (color, width)
            elif style == 'lines':
                if marker is None:  # marker is not set
                    withstring = "lines lt %d lw %d" % (color, width)
                else:
                    withstring = "linespoints lt %d lw %d pt %d" % \
                                 (color, width, marker)
        else:  # no color
            if style is None:
                if marker:
                    withstring = "points pt %d ps %d " % (marker, width)
                else:
                    withstring = "lines"  # no color, no style, no marker
            elif style == 'lines':
                if marker is None:  # marker is not set
                    withstring = "lines"
                else:
                    withstring = "linespoints pt %d" % marker
        return withstring

    def _add_line(self, item):
        """Add a 2D or 3D curve to the scene."""
        if DEBUG:
            print "Adding a line"
        # get data:
        x = squeeze(item.getp('xdata'))
        y = squeeze(item.getp('ydata'))
        z = item.getp('zdata')
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        withstring = self._get_withstring(marker, color, style, width)
        if z is not None:
            # zdata is given, add a 3D curve:
            kwargs = {'title': self._fix_latex(item.getp('legend')),
                      'with': withstring,
                      'using': '1:2:($3)'}
            data = Gnuplot.Data(x, y, squeeze(z), **kwargs)
            self._g('set parametric')
        else:
            # no zdata, add a 2D curve:
            if withstring.startswith('linespoints') and \
               marker == self._markers[PlotProperties._colors2markers[
                item.getp('linecolor')]]:
                # assume that user has empty format spec and that
                # _get_linespecs has set marker and solid line, then
                # limit to 15 markers for visibility
                every = int(len(x)/15.)
                withstring += ' pi ' + str(every)

            kwargs = {'title': self._fix_latex(item.getp('legend')),
                      'with': withstring,
                      'using': '1:($2)'}

            data = Gnuplot.Data(x, y, **kwargs)
        return data


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

        facecolor = item.getp('facecolor')
        if not facecolor:
            facecolor = color
        else:
            facecolor = self._colors.get(facecolor, 'r')
        edgecolor = item.getp('edgecolor')
        if not edgecolor:
            edgecolor = -1  # use black for now
            # FIXME: Should use ax.getp('fgcolor') as default edgecolor
        else:
            edgecolor = self._colors.get(edgecolor, -1)

        withstring = self._get_withstring(marker, edgecolor, style, width)

        if z is not None:
            # zdata is given, add a 3D curve:
            kwargs = {'title': self._fix_latex(item.getp('legend')),
                      'with': 'filledcurve',
                      'using': '1:2:($3)'}
            data = [Gnuplot.Data(x, y, z, **kwargs)]
            self._g('set parametric')
        else:
            # no zdata, add a 2D curve:
            kwargs1 = {'title': self._fix_latex(item.getp('legend')),
                       'with': 'filledcurve %s' % facecolor,
                       'using': '1:($2)'}
            kwargs2 = {'with': withstring, 'using': '1:($2)'}
            data = [Gnuplot.Data(x, y, **kwargs1),
                    Gnuplot.Data(x, y, **kwargs2),
                    Gnuplot.Data([x[0],x[-1]], [y[0],y[-1]], **kwargs2)]
        return data

    def _add_bar_graph(self, item, shading='faceted'):
        if DEBUG:
            print "Adding a bar graph"
        # get data:
        x = item.getp('xdata')
        y = item.getp('ydata')
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        if y.ndim == 1:
            y = reshape(y,(len(y),1))
        nx, ny = shape(y)

        barticks = item.getp('barticks')
        if barticks is None:
            barticks = range(nx)
        xtics = ', '.join(['"%s" %d' % (m,i) \
                           for i,m in enumerate(barticks)])
        if item.getp('rotated_barticks'):
            self._g("set xtics rotate (%s)" % xtics)
        else:
            self._g("set xtics (%s)" % xtics)

        barwidth = item.getp('barwidth')/10
        self._g('set boxwidth %s' % barwidth)
        edgecolor = item.getp('edgecolor')
        if not edgecolor:
            edgecolor = -1  # use black for now
            # FIXME: edgecolor should be same as ax.getp('fgcolor') by default
        else:
            edgecolor = self._colors.get(edgecolor, 'r')
        if shading == 'faceted':
            self._g('set style fill solid 1.00 border %s' % edgecolor)
        else:
            self._g('set style fill solid 1.00')

        facecolor = item.getp('facecolor')
        if not facecolor:
            facecolor = color
        else:
            facecolor = self._colors.get(facecolor, 3)  # use blue as default

        step = item.getp('barstepsize')/10

        center = floor(ny/2)
        start = -step*center
        stop = step*center
        if not ny%2:
            start += step/2
            stop -= step/2
        a = linspace(start,stop,ny)

        data = []
        for j in range(ny):
            y_ = y[:,j]
            x_ = array(range(nx)) + a[j]
            if not item.getp('linecolor') and not item.getp('facecolor'):
                c = j+1
            else:
                c = facecolor
            kwargs = {'with': 'boxes linecolor %s' % c}
            legend = self._fix_latex(item.getp('legend'))
            if legend:
                legend = eval(self._fix_latex(item.getp('legend')))[j]
            kwargs['title'] = legend
            #print "|%s|" % self._fix_latex(item.getp('legend'))
            # does not work:
            #kwargs = {'with': 'boxes %s' % c,
            #          'title': self._fix_latex(item.getp('legend')),}
            data.append(Gnuplot.Data(x_, y_, **kwargs))
        return data

    def _add_surface(self, item, shading='faceted'):
        if DEBUG:
            print "Adding a surface"
        x = item.getp('xdata')  # grid component in x-direction
        y = item.getp('ydata')  # grid component in y-direction
        z = item.getp('zdata')  # scalar field
        c = item.getp('cdata')  # pseudocolor data (can be None)
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)
        if not width:
            width = 1.0
        width = width - width/2
        edgecolor = item.getp('edgecolor')
        #facecolor = item.getp('facecolor')
        #if facecolor and facecolor in self._colors:
        #    facecolor = self._colors[facecolor]

        withstring = ''
        self._g('set surface')
        if item.getp('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            self._g('unset pm3d')
            if edgecolor == '':
                withstring = 'l palette'
            else:
                edgecolor = self._colors.get(edgecolor, -1)
                withstring += 'lines lt %s lw %s' % (edgecolor,width)
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            if shading == 'flat':
                self._g('set pm3d at s solid')
            elif shading == 'faceted':
                self._g('set pm3d at s solid hidden3d 100')
                if edgecolor == '':
                    edgecolor = -1  # use black for now
                else:
                    edgecolor = self._colors.get(edgecolor, -1)
                self._g('set style line 100 lt %s lw %s' % (edgecolor,width))
            elif shading == 'interp':
                # Interpolated shading requires Gnuplot >= 4.2
                self._g('set pm3d implicit at s')
                self._g('set pm3d scansautomatic')
                self._g('set pm3d interpolate 10,10')
                self._g('set pm3d flush begin ftriangles nohidden3d')
            withstring += 'l palette'

        if item.getp('indexing') == 'xy':
            if x.ndim == 2 and y.ndim == 2:
                x = x[0,:];  y = y[:,0]
            z = transpose(z, [1,0])
        else:
            if x.ndim == 2 and y.ndim == 2:
                x = x[:,0];  y = y[0,:]
        kwargs = {'title': self._fix_latex(item.getp('legend')),
                  'with': withstring,
                  'binary': 0}
        data = Gnuplot.GridData(z, x, y, **kwargs)
        return data

    def _add_contours(self, item, placement=None):
        # The placement keyword can be either None or 'bottom'. The
        # latter specifies that the contours should be placed at the
        # bottom (as in meshc or surfc).
        if DEBUG:
            print "Adding contours"
        x = item.getp('xdata')  # grid component in x-direction
        y = item.getp('ydata')  # grid component in y-direction
        z = item.getp('zdata')  # scalar field

        filled = item.getp('filled')  # draw filled contour plot if True

        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            self._g('set cntrparam levels auto %d' % clevels)
        else:
            cvector = ','.join(['%s' % i for i in cvector])
            self._g('set cntrparam levels discrete %s' % cvector)

        location = item.getp('clocation')
        if location == 'surface':
            # place the contours at the corresponding z level (contour3)
            self._g('set contour surface')
            self._g('unset surface')
            self._g('unset pm3d')
        elif location == 'base':
            if placement == 'bottom':
                # place the contours at the bottom (as in meshc or surfc)
                self._g('set contour base')
            elif filled:
                self._g('set contour base')
                self._g('set style fill solid')
                self._g('set pm3d at s solid')
                self._g('set palette maxcolors %d' % item.getp('clevels'))
            else:
                # standard contour plot
                self._g('set contour base')
                self._g('unset surface')
                self._g('unset pm3d')

        if item.getp('clabels'):
            # add labels on the contour curves
            self._g('set clabel')
        else:
            self._g('unset clabel')

        if item.getp('indexing') == 'xy':
            z = transpose(z, [1,0])
            if x.ndim == 2 and y.ndim == 2:
                x = x[0,:];  y = y[:,0]
        else:
            if x.ndim == 2 and y.ndim == 2:
                x = x[:,0];  y = y[0,:]
        kwargs = {'title': self._fix_latex(item.getp('legend')),
                  'binary': 0,
                  'with': 'l palette'}
        data = Gnuplot.GridData(z, x, y, **kwargs)
        return data

    def _add_vectors(self, item):
        if DEBUG:
            print "Adding vectors"
        # uncomment the following command if there is no support for
        # automatic scaling of vectors in the current plotting package:
        item.scale_vectors()

        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        # vector components:
        u, v, w = item.getp('udata'), item.getp('vdata'), item.getp('wdata')
        # get line specifiactions (marker='.' means no marker):
        marker, color, style, width = self._get_linespecs(item)

        withstring = 'vectors'
        if color:
            withstring += ' lt %d' % color
        if width:
            withstring += ' lw %d' % int(width)

        # scale the vectors according to this variable (scale=0 should
        # turn off automatic scaling):
        scale = item.getp('arrowscale')

        filled = item.getp('filledarrows') # draw filled arrows if True

        if z is not None and w is not None:
            # draw velocity vectors as arrows with components (u,v,w) at
            # points (x,y,z):
            data = None  # no support for vectors in 3D space in Gnuplot
            msg = "3D vector fields not implemented in %s backend" % backend
            raise NotImplementedError(msg)
        else:
            # draw velocity vectors as arrows with components (u,v) at
            # points (x,y):
            if shape(x) != shape(u):
                if x.ndim == 2:
                    x = x*ones(shape(u))
                else:
                    if item.getp('indexing') == 'xy':
                        x = x[newaxis,:]*ones(shape(u))
                    else:
                        x = x[:,newaxis]*ones(shape(u))
            if shape(y) != shape(u):
                if y.ndim == 2:
                    y = y*ones(shape(u))
                else:
                    if item.getp('indexing') == 'xy':
                        y = y[:,newaxis]*ones(shape(u))
                    else:
                        y = y[newaxis,:]*ones(shape(u))
            kwargs = {'title': self._fix_latex(item.getp('legend')),
                      'with': withstring}
            data = Gnuplot.Data(ravel(x), ravel(y),
                                ravel(u), ravel(v),
                                **kwargs)
        return data

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

        msg = "Currently no support for '%s' in the Gnuplot backend." % \
              item.getp('function')
        raise NotImplementedError(msg)

    def _add_isosurface(self, item):
        if DEBUG:
            print "Adding a isosurface"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume
        c = item.getp('cdata')  # pseudocolor data
        isovalue = item.getp('isovalue')

        msg = "Currently no support for '%s' in the Gnuplot backend." % \
              item.getp('function')
        raise NotImplementedError(msg)

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

        msg = "Currently no support for '%s' in the Gnuplot backend." % \
              item.getp('function')
        raise NotImplementedError(msg)

    def _add_contourslices(self, item):
        if DEBUG:
            print "Adding contours in slice planes"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume

        sx, sy, sz = item.getp('slices')
        if sz.ndim == 2:
            # sx, sy, and sz define a surface
            pass
        else:
            # sx, sy, and sz are either numbers or vectors with numbers
            pass

        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels per plane
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            pass

        msg = "Currently no support for '%s' in the Gnuplot backend." % \
              item.getp('function')
        raise NotImplementedError(msg)

    def _set_figure_size(self, fig):
        if DEBUG:
            print "Setting figure size"
        width, height = fig.getp('size')
        if width and height:
            # set figure width and height
            self._g('set size %s,%s' % (width,height))
        else:
            # use the default width and height in plotting package
            pass

    def figure(self, *args, **kwargs):
        # Extension of BaseClass.figure:
        # add a plotting package figure instance as fig._g and create a
        # link to it as self._g
        fig = BaseClass.figure(self, *args, **kwargs)
        try:
            fig._g
        except:
            # create plotting package figure and save figure instance
            # as fig._g
            if DEBUG:
                name = 'Fig ' + str(fig.getp('number'))
                print "creating figure %s in backend" % name
            # Do not force persist. Instead let the user decide whether to
            # persist a plot through Gnuplot.GnuplotOpts.prefer_persist or
            # the prefer_persist option in the gnuplot section of
            # scitools.cfg.
            #fig._g = Gnuplot.Gnuplot(persist=1)
            fig._g = Gnuplot.Gnuplot()

        self._g = fig._g  # link for faster access
        self._texts = {}  # storage of text calls (dict for set)
        return fig

    def _replot(self):
        """Replot all axes and all plotitems in the backend."""
        # NOTE: only the current figure (gcf) is redrawn.
        if DEBUG:
            print "Doing replot in backend"

        fig = self.gcf()
        # reset the plotting package instance in fig._g now if needed
        self._g.reset()
        #self._g('set size 1.0, 1.0')
        #self._g('set origin 0.0, 0.0')
        self._g('unset multiplot')
        self._g('set datafile missing "nan"')

        self._set_figure_size(fig)

        if len(list(fig.getp('axes').items())) > 1:
            # multiple axes (subplot)
            self._g('set multiplot')
        nrows, ncolumns = fig.getp('axshape')
        for axnr, ax in list(fig.getp('axes').items()):
            gdata = []
            self._use_splot = False
            if nrows != 1 or ncolumns != 1:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,axnr)
                viewport = ax.getp('viewport')
                if not viewport:
                    viewport = (0,0,1,1)
                origin = viewport[:2]
                size = 1/ncolumns, 1/nrows
                self._g('set origin %s,%s' % (origin[0], origin[1]))
                self._g('set size %s,%s' % (size[0], size[1]))
            loc = self._loc_syntax(ax)
            self._g('set key ' + loc)
            plotitems = ax.getp('plotitems')
            plotitems.sort(self._cmpPlotProperties)
            for item in plotitems:
                func = item.getp('function') # function that produced this item
                if isinstance(item, Line):
                    if func[:4] == 'fill':  # fill and fill3
                        gdata.extend(self._add_filled_line(item))
                    else:
                        gdata.append(self._add_line(item))
                    if func in ['plot3', 'fill3']:
                        self._use_splot = True
                elif isinstance(item, Bars):
                    shading = ax.getp('shading')
                    gdata.extend(self._add_bar_graph(item,shading=shading))
                elif isinstance(item, Surface):
                    gdata.append(self._add_surface(item,
                                                   shading=ax.getp('shading')))
                    contours = item.getp('contours')
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
                legend = self._fix_latex(item.getp('legend'))
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

            # Gnuplot may give thread error for many plot items,
            # let it wait a bit when there are many curves in a plot
            if len(plotitems) > 6:
                time.sleep(0.3)

        if sys.platform == 'win32':
            # Since os.mkfifo is not available on the Windows platform, we
            # store a reference to the gnuplot data so that the temporary
            # files won't get deleted too early. This should fix the problem
            # with 0 byte images created with hardcopy on Windows. Use the
            # cleanup method to remove the references and free up the memory.
            try:
                self._gdata
            except AttributeError:
                self._gdata = []
            self._gdata.append(gdata)

        # Display texts (adds texts to latest axes, implying that this
        # does not work well with subplots):
        for args in self._texts:
            self.text(*args)

        if self.getp('show'):
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            pass

    def _loc_syntax(self, ax):
        """
        Change from (Matplotlib-inspired) syntax of loc
        specification of legends to Gnuplot "key" syntax.
        """
        try:
            loc = ax.getp('legend_loc')
        except KeyError:
            loc = 'best'

        mpl2gp = {
            'upper right': 'right top',
            'upper left': 'left top',
            'lower left': 'left bottom',
            'lower right': 'right bottom',
            'center left': 'left center',
            'center right': 'right center',
            'lower center': 'center bottom',
            'upper center': 'center top',
            'best': 'right top', # default
            'right': 'right top',
            'center': 'center center'}
        loc = mpl2gp[loc]

        try:
            fancybox = ax.getp('legend_fancybox')
        except KeyError:
            fancybox = False

        if fancybox:
            loc = loc + ' box'
        return loc


    def cleanup(self):
        """Clean up data."""
        try:
            del self._gdata
        except AttributeError:
            pass

    def text(self, x, y, text,
             fontname=Axis._local_prop['fontname'],
             fontsize=Axis._local_prop['fontsize']):
        """Write text at position (x,y) in a curveplot."""
        s = 'set label "%s" at %f,%f font "%s,%d"' % \
            (text, x, y, fontname, fontsize)
        self._g(s)
        self._g.refresh()
        self._texts[(x, y, text, fontname, fontsize)] = None

    def hardcopy(self, filename, **kwargs):
        """
        Currently supported extensions in Gnuplot backend:
        .ps,  .eps,  .png,  .pdf, and  .svg.
        The PDF file is generated from EPS (for better quality).
        If `filename` contains just the file extension, say ``.png``,
        it is saved to ``tmp.png``.

        Optional arguments for PostScript output:

        ===========    =====================================================
        Argument       Description
        ===========    =====================================================
        color          If True, create a plot with colors. If False
                       (default),  create a plot in black and white.
        enhanced       If True (default), enable enhanced text mode features
                       like subscripts, superscripts, and mixed fonts.
        orientation    Set orientation to 'portrait' or 'landscape'. Default
                       is to leave this unchanged. This option has no effect
                       on EPS or PDF output.
        solid          If True, force lines to become solid (i.e., not
                       dashed). Default is False.
        fontname       Set the font to be used for titles, labels, etc.
                       Must be a valid PostScript font or an oblique version
                       of the Symbol font (called "Symbol-Oblique") which is
                       useful for mathematics. Default font is "Helvetica".
        fontsize       Set the size of the font in points. Default is 20 for
                       for PostScript output and 8 for PDF output.
        ===========    =====================================================
        """
        if filename.startswith('.'):
            filename = 'tmp' + filename

        if DEBUG:
            print "Hardcopy to %s" % filename

        ext2term = {'.ps': 'postscript',
                    '.eps': 'postscript',
                    '.png': 'png',
                    #'.pdf': 'pdfcairo', does not work well
                    '.pdf': 'postscript',
                    '.svg': 'svg',
                    }

        # check if we have a PDF terminal
        if _check_terminal('pdfcairo'):
            # teach Gnuplot.py about the pdfcairo terminal
            # FIXME: This might need some tweaking. Or is this even needed?
            # Seems so, because Gnuplot does not define pdfcairo
            Gnuplot.termdefs.terminal_opts['pdfcairo'] = [
                Gnuplot.termdefs.KeywordOrBooleanArg(
                    options=['landscape', 'portrait', 'eps', 'default'],
                    argname='mode',
                    ),
                Gnuplot.termdefs.KeywordOrBooleanArg(options=['color', 'monochrome']),
                Gnuplot.termdefs.KeywordOrBooleanArg(options=['solid', 'dashed']),
                Gnuplot.termdefs.KeywordOrBooleanArg(
                    options=['defaultplex', 'simplex', 'duplex'],
                    argname='duplexing',
                    ),
                Gnuplot.termdefs.StringArg(argname='fontname'),
                Gnuplot.termdefs.BareStringArg(argname='fontsize'),
                ]
        #elif _check_terminal('pdf'):
        #    ext2term['.pdf'] = 'pdf'

        basename, ext = os.path.splitext(filename)
        if not ext:
            # no extension given, assume .ps:
            ext = '.ps'
            filename += ext
        elif ext not in ext2term:
            raise ValueError("hardcopy: extension must be %s, not '%s'" % \
                             (list(ext2term.keys()), ext))
        terminal = ext2term.get(ext, 'postscript')

        self.setp(**kwargs)
        color = self.getp('color')
        enhanced = kwargs.get('enhanced', True)
        orientation = kwargs.get('orientation', None)
        solid = kwargs.get('solid', False)
        fontname = kwargs.get('fontname', 'Helvetica')
        keyw = {'filename': filename, 'terminal': terminal}

        # Create a new Gnuplot instance only for now
        self._g = Gnuplot.Gnuplot()
        setterm = ['set', 'terminal', terminal]
        if terminal == 'postscript':
            fontsize = kwargs.get('fontsize', 20)
            keyw.update({'color': color, 'enhanced': enhanced, 'solid': solid,
                         'fontname': fontname, 'fontsize': fontsize})
            if ext == '.eps' or ext == '.pdf':
                keyw['mode'] = 'eps'
                setterm.append('eps')
            else:
                if orientation in ['landscape', 'portrait']:
                    keyw['mode'] = orientation
                    setterm.append(orientation)
            setterm.append(enhanced and 'enhanced' or 'noenhanced')
            setterm.append(color and 'color' or 'monochrome')
            setterm.append(solid and 'solid' or 'dashed')
            setterm.append(' dashlength 5 linewidth 3')  # looks best
            #setterm.append(' dashlength 5 linewidth 4')
            setterm.append('"%s"' % fontname)
            setterm.append('%s' % fontsize)
            self._doing_PS = True
        elif terminal == 'pdf' or terminal == 'pdfcairo':
            # Setting fontsizes etc is not successful with Gnuplot.hardcopy
            # Instead: use ps2pdf to convert to pdf
            fontsize = kwargs.get('fontsize', 20)
            fontname = kwargs.get('fontname', 'Helvetica')
            setterm.append(color and 'color' or 'monochrome')
            setterm.append(enhanced and 'enhanced' or 'noenhanced')
            setterm.append('font "%s,%s"' % (fontname, fontsize))
            #setterm.append(' dashlength 3 linewidth 3')  # looks best
            setterm.append(' dashlength 3 linewidth 1')  # looks best
            #setterm.append('linewidth 4'); setterm.append('dl 3')  # old
            setterm.append(solid and 'solid' or 'dashed')
            # FIXME: Should self._doing_PS be True or False in this case?
            self._doing_PS = True
            keyw.update({'color': color, 'solid': solid})
        elif terminal == 'png':
            # Options are ' background "#ffffff" fontscale 1.0 size 640, 480 '
            fontsize = kwargs.get('fontsize', 14)
            fontscale = fontsize/14.0
            # no support: setterm.append('linewidth 5')
            setterm.append('fontscale %s' % fontscale)
            keyw.update({'color': color})
        elif terminal == 'svg':
            fontsize = kwargs.get('fontsize', 12)
            fontname = kwargs.get('fontname', 'Arial')
            setterm.append("fname '%s' fsize %s" % (fontname, fontsize))
        self._g(' '.join(setterm))
        self._g('set output "%s"' % filename)
        self._replot()
        if len(self.gcf().getp('axes')) == 1:
            # Need to call hardcopy in Gnuplot.py to avoid ending up with
            # a PostScript file with multiple pages:
            self._g.hardcopy(**keyw)
        self._g('quit')
        self._g = self.gcf()._g  # set self._g to the correct instance again
        self._doing_PS = False

        if self.getp('interactive') and self.getp('show'):
            self._replot()

        if terminal == 'postscript' and ext == '.pdf':
            # Wanted PDF, used postscript, need to convert with ps2pdf
            scratchfile = '.tmp.pdf'
            if os.path.isfile(filename):
                os.rename(filename, scratchfile)
                # Can also use the epstopdf script
                # see http://phaseportrait.blogspot.no/2007/06/bounding-boxes-and-eps-to-pdf.html#epstopdf
                failure = os.system('ps2pdf -dEPSCrop %s %s' %
                                    (scratchfile, filename))
                if failure:
                    print 'Tried to make PDF format from PostScript, but the\nps2pdf program would not run successfully.'
                os.remove(scratchfile)
            else:
                print 'Could not make', filename

    def hardcopy_old(self, filename, **kwargs):
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
            raise ValueError("hardcopy: extension must be %s, not '%s'" % \
                             (list(ext2term.keys()), ext))
        terminal = ext2term.get(ext, 'postscript')

        self.setp(**kwargs)
        fontname = kwargs.get('fontname', 'Helvetica')
        fontsize = kwargs.get('fontsize', 16)
        orientation = kwargs.get('orientation', 'landscape')
        color = self.getp('color')

        self._g('unset multiplot') # is this necessary?

        if self.getp('show'): # OK to display to screen
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
                            (orientation, colortype))
                    kwargs['mode'] = orientation
            elif terminal == 'png':
                self._g('set term png')
            self._g('set output "%s"' % filename)
            self._replot()
            self._g.hardcopy(**kwargs)
            self._g('quit')
            self._g = self.gcf()._g # set _g to the correct instance again

    # reimplement methods like clf, closefig, closefigs
    def clf(self):
        """Clear current figure."""
        BaseClass.clf(self)
        self._g.reset() # reset gnuplot instance

    def closefig(self, num=None):
        """Close figure window."""
        if not num:
            pass
        elif num in self._figs:
            pass
        else:
            pass
        pass

    def closefigs(self):
        """Close figure windows and stop gnuplot."""
        for key in self._figs:
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


plt = GnuplotBackend()  # create backend instance
use(plt, globals())     # export public namespace of plt to globals()
backend = os.path.splitext(os.path.basename(__file__))[0][:-1]
