"""
This is a backend for the VisIt visualization tool available for free at
www.llnl.gov. The backend can either be specified on the command line,
like

  python somefile.py --SCITOOLS_easyviz_backend visit

or in the SciTools configuration file scitools.cfg under the [easyviz]
section

  [easyviz]
  backend = visit

and then

  from scitools.std import *

or if just easyviz is needed

  from scitools.easyviz import *

REQUIREMENTS:

VisIt 1.6.1

NOTES:

- VisIt supports a maximum of 16 figures.

"""

from __future__ import division

from common import *
from scitools.globaldata import DEBUG, VERBOSE
from scitools.misc import check_if_module_exists

import os
import tempfile

VISIT_ARGS = os.environ.get('VISIT_ARGS', ["-nosplash"])
if isinstance(VISIT_ARGS, str):
    VISIT_ARGS = VISIT_ARGS.split()

check_if_module_exists('visit', msg='You need to install the VisIt package. Also make sure the visit Python module is in the PYTHONPATH environment variable.', abort=False)
import visit
for arg in VISIT_ARGS:
    visit.AddArgument(arg)
visit.Launch()


class VisitBackend(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self._init()

    def _init(self, *args, **kwargs):
        """Perform initialization that is special for this backend."""

        self.figure(self.getp('curfig'))
        self._g.IconifyAllWindows()

        # conversion tables for format strings:
        self._markers = {
            '': None,   # no marker
            '.': None,  # dot
            'o': None,  # circle
            'x': None,  # cross
            '+': None,  # plus sign
            '*': None,  # asterisk
            's': None,  # square
            'd': None,  # diamond
            '^': None,  # triangle (up)
            'v': None,  # triangle (down)
            '<': None,  # triangle (left)
            '>': None,  # triangle (right)
            'p': None,  # pentagram
            'h': None,  # hexagram
            }

        self._colors = {
            '': None,            # no color --> blue
            'r': (255,0,0),      # red
            'g': (0,255,0),      # green
            'b': (0,0,255),      # blue
            'c': (0,255,255),    # cyan
            'm': (255,0,255),    # magenta
            'y': (255,255,0),    # yellow
            'k': (0,0,0),        # black
            'w': (255,255,255),  # white
            }

        self._line_styles = {
            '': None, # no line
            '-': 0,   # solid line
            ':': 2,   # dotted line
            '-.': 3,  # dash-dot line
            '--': 1,  # dashed line
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
        scale = ax.getp('scale')
        if scale == 'loglog':
            # use logarithmic scale on both x- and y-axis
            pass
        elif scale == 'logx':
            # use logarithmic scale on x-axis and linear scale on y-axis
            pass
        elif scale == 'logy':
            # use linear scale on x-axis and logarithmic scale on y-axis
            pass
        elif scale == 'linear':
            # use linear scale on both x- and y-axis
            pass

    def _set_labels(self, ax):
        """Add text labels for x-, y-, and z-axis."""
        if DEBUG:
            print "Setting labels"
        xlabel = ax.getp('xlabel')
        ylabel = ax.getp('ylabel')
        zlabel = ax.getp('zlabel')
        aa = self._aa
        # add a text label on x-axis
        aa.SetXAxisUserTitleFlag(True)
        aa.SetXAxisUserTitle(xlabel)
        aa.SetXAxisUserTitleFlag2D(True)
        aa.SetXAxisUserTitle2D(xlabel)
        # add a text label on y-axis
        aa.SetYAxisUserTitleFlag(True)
        aa.SetYAxisUserTitle(ylabel)
        aa.SetYAxisUserTitleFlag2D(True)
        aa.SetYAxisUserTitle2D(ylabel)
        # add a text label on z-axis
        aa.SetZAxisUserTitleFlag(True)
        aa.SetZAxisUserTitle(zlabel)

    def _set_title(self, ax):
        """Add a title at the top of the axis."""
        if DEBUG:
            print "Setting title"
        title = ax.getp('title')
        t = self._g.CreateAnnotationObject("Text2D")
        t.SetText(title)
        t.SetPosition(0.3,0.9)  # (0,0) is lower left corner
        t.SetFontFamily(0)      # 0: Arial, 1: Courier, 2: Times
        t.SetWidth(0.25)        # 25%
        #t.SetTextColor((0,0,0)) # FIXME: Use ax.getp('fgcolor')
        #t.SetUseForegroundForTextColor(False)
        if title:
            t.SetVisible(True)  # set title
        else:
            t.SetVisible(False)
        # FIXME: This is a problem:
        # surf(peaks(21),title='Simple plot')
        # contour(peaks(21))  # title is still present

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
            pass
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.getp('xmin')
            xmax = ax.getp('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits
                pass
            else:
                # let plotting package set x-axis limits or use
                #xmin, xmax = ax.getp('xlim')
                pass

            ymin = ax.getp('ymin')
            ymax = ax.getp('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                pass
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
            pass
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
            pass
        else:
            # daspectmode is 'auto'. Plotting package handles data
            # aspect ratio automatically.
            pass

    def _set_axis_method(self, ax):
        method = ax.getp('method')
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
        state = ax.getp('box')
        self._aa.SetBboxFlag(state)

    def _set_grid(self, ax):
        """Turn grid lines on or off."""
        if DEBUG:
            print "Setting grid"
        state = ax.getp('grid')
        self._aa.SetXGridLines2D(state)
        self._aa.SetYGridLines2D(state)
        self._aa.SetXGridLines(state)
        self._aa.SetYGridLines(state)
        self._aa.SetZGridLines(state)

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
        cbar = ax.getp('colorbar')
        if cbar.getp('visible'):
            # turn on colorbar
            cbar_title = cbar.getp('cbtitle')
            cbar_location = self._colorbar_locations[cbar.getp('cblocation')]
            # ...
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
            pass
        else:
            # use autoranging for color axis scale
            pass

    def _set_colormap(self, ax):
        """Set the colormap."""
        if DEBUG:
            print "Setting colormap"
        cmap = ax.getp('colormap')
        # cmap is plotting package dependent

    def _set_view(self, ax):
        """Set viewpoint specification."""
        if DEBUG:
            print "Setting view"
        cam = ax.getp('camera')
        view = cam.getp('view')
        self._g.ResetView()
        v2D = self._g.GetView2D()
        v3D = self._g.GetView3D()
        v3D.SetPerspective(False)
        if view == 2:
            # setup a default 2D view
            v3D.SetViewUp(0,1,0)
            v3D.SetViewNormal(0,0,1)
            v3D.SetImageZoom(1.2)
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
            v3D.SetViewUp(0,0,1)
            v3D.SetViewNormal(-0.5,-0.8,0.4)
            v3D.SetImageZoom(1.0)

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
                if projection == 'perspective':
                    v3D.SetPerspective(True)
                else:
                    v3D.SetPerspective(False)
        self._g.SetView2D(v2D)
        self._g.SetView3D(v3D)

    def _set_axis_props(self, ax):
        if DEBUG:
            print "Setting axis properties"
        self._aa = self._g.AnnotationAttributes()
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
        aa = self._aa
        if ax.getp('visible'):
            self._set_labels(ax)
            self._set_box(ax)
            self._set_grid(ax)
        else:
            # turn off all axis labeling, tickmarks, and background
            aa.SetAxesFlag2D(False)
            aa.SetAxesFlag(False)
            aa.SetBboxFlag(False)
            aa.SetXGridLines2D(False)
            aa.SetYGridLines2D(False)
            aa.SetXGridLines(False)
            aa.SetYGridLines(False)
            aa.SetZGridLines(False)
            aa.SetXAxisUserTitleFlag2D(False)
            aa.SetYAxisUserTitleFlag2D(False)
            aa.SetXAxisUserTitleFlag(False)
            aa.SetYAxisUserTitleFlag(False)
            aa.SetZAxisUserTitleFlag(False)
        aa.SetAxesType(2)  # outside edges
        aa.SetDatabaseInfoFlag(False)
        aa.SetUserInfoFlag(False)
        if DEBUG:
            print "\nAnnotationAttributes:\n", self._aa
        self._g.SetAnnotationAttributes(self._aa)

    def _generate_2D_database(self, x, y, z, c, indexing='xy'):
        x = squeeze(x)
        y = squeeze(y)
        z = asarray(z)
        c = asarray(c)
        nx, ny = shape(z)
        if shape(x) != (nx,ny) and shape(y) != (nx,ny):
            x, y = meshgrid(x, y, sparse=False, indexing=indexing)
        dx, dy, dz = self._ax.getp('daspect')
        x = x/dx
        y = y/dy
        z = z/dz

        tmpfname = tempfile.mktemp(suffix='.vtk')
        self.gcf()._tmpfiles.append(tmpfname)  # clean up later
        f = open(tmpfname, 'w')
        f.write(
"""# vtk DataFile Version 2.0
vtk file written by scitools.easyviz
ASCII

DATASET STRUCTURED_GRID
DIMENSIONS %d %d 1
POINTS %d float
""" % (nx,ny,nx*ny))
        for j in range(ny):
            for i in range(nx):
                f.write("%s %s %s\n" % (x[i,j],y[i,j],z[i,j]))

        f.write("""
POINT_DATA %d
SCALARS scalars float
LOOKUP_TABLE default
""" % (nx*ny))
        for i in range(nx):
            for j in range(ny):
                f.write("%s\n" % c[i,j])
        f.close()
        return tmpfname

    def _generate_3D_database(self, x, y, z, v, c, indexing='xy'):
        x = squeeze(x)
        y = squeeze(y)
        z = squeeze(z)
        v = asarray(v)
        c = asarray(c)
        nx, ny, nz = shape(v)
        if shape(x) != (nx,ny,nz) and shape(y) != (nx,ny,nz) and \
               shape(z) != (nx,ny,nz):
            x, y, z = meshgrid(x, y, z, sparse=False, indexing=indexing)
        dx, dy, dz = self._ax.getp('daspect')
        x = x/dx
        y = y/dy
        z = z/dz

        tmpfname = tempfile.mktemp(suffix='.vtk')
        self.gcf()._tmpfiles.append(tmpfname)  # clean up later
        f = open(tmpfname, 'w')
        f.write("""# vtk DataFile Version 2.0
vtk file written by scitools.easyviz
ASCII

DATASET STRUCTURED_GRID
DIMENSIONS %d %d %d
POINTS %d float
""" % (nx,ny,nz,nx*ny*nz))
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    f.write("%s %s %s\n" % (x[i,j,k],y[i,j,k],z[i,j,k]))

        f.write("""
POINT_DATA %d
SCALARS scalars float
LOOKUP_TABLE default
""" % (nx*ny*nz))
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    f.write("%s\n" % v[i,j,k])
        f.close()
        return tmpfname

    def _get_linespecs(self, item):
        """
        Return the line marker, line color, line style, and
        line width of the item.
        """

        marker = self._markers[item.getp('linemarker')]
        color = self._colors[item.getp('linecolor')]
        style = self._line_styles[item.getp('linetype')]
        width = item.getp('linewidth')
        return marker, color, style, width

    def _add_line(self, item):
        """Add a 2D or 3D curve to the scene."""
        if DEBUG:
            print "Adding a line"
        # get data:
        x = item.getp('xdata')
        y = item.getp('ydata')
        z = item.getp('zdata')
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        if z is not None:
            # zdata is given, add a 3D curve:
            pass
        else:
            # no zdata, add a 2D curve:
            pass

    def _add_surface(self, item, shading='faceted'):
        if DEBUG:
            print "Adding a surface"
        x = item.getp('xdata')  # grid component in x-direction
        y = item.getp('ydata')  # grid component in y-direction
        z = item.getp('zdata')  # scalar field
        c = item.getp('cdata')  # pseudocolor data (can be None)
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        if c is None:
            c = asarray(z).copy()
        function = item.getp('function')
        if function == 'pcolor':
            z = 0.0*z
        db = self._generate_2D_database(x,y,z,c,indexing=item.getp('indexing'))
        self._g.OpenDatabase(db)

        contours = item.getp('contours')
        if contours:
            # the current item is produced by meshc or surfc and we
            # should therefore add contours at the bottom:
            self._add_contours(contours, placement='bottom')

        if item.getp('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            self._g.AddPlot("Mesh", "scalars")
            ma = self._g.MeshAttributes()
            if style is not None:
                ma.SetLineStyle(style)
            if color is not None:
                ma.SetMeshColor(color)
                #ma.SetBackgroundFlag(False)
                #ma.SetForegroundFlag(False)
            if width:
                ma.SetLineWidth(int(width))
            if DEBUG:
                print "\nMeshAattributes:\n", ma
            self._g.SetPlotOptions(ma)
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            if shading == 'faceted':
                self._g.AddPlot("Mesh", "scalars")
                ma = self._g.MeshAttributes()
                if DEBUG:
                    print "\nMeshAttributes:\n", ma
                # FIXME: do modifications on ma
                self._g.SetPlotOptions(ma)
            self._g.AddPlot("Pseudocolor", "scalars")
            pa = self._g.PseudocolorAttributes()
            if DEBUG:
                print "\nPseudocolorAttributes:\n", pa
            # FIXME: do modifications on pa
            self._g.SetPlotOptions(pa)

    def _add_contours(self, item, placement=None):
        # The placement keyword can be either None or 'bottom'. The
        # latter specifies that the contours should be placed at the
        # bottom (as in meshc or surfc).
        if DEBUG:
            print "Adding contours"
        x = item.getp('xdata')  # grid component in x-direction
        y = item.getp('ydata')  # grid component in y-direction
        z = item.getp('zdata')  # scalar field
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        c = asarray(z).copy()
        if item.getp('function') == 'contour':
            z = 0.0*z
        db = self._generate_2D_database(x,y,z,c)
        self._g.OpenDatabase(db)

        filled = item.getp('filled')  # draw filled contour plot if True

        self._g.AddPlot("Contour", "scalars")
        ca = self._g.ContourAttributes()

        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            ca.SetContourMethod(0)  # Level
            ca.SetContourNLevels(clevels)
        else:
            ca.SetContourMethod(1)  # Values
            ca.SetContourValue(tuple(cvector))
        location = item.getp('clocation')
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
        if DEBUG:
            print "\nContourAttributes:\n", ca
        # FIXME: more modifications on ca
        self._g.SetPlotOptions(ca)

        if item.getp('clabels'):
            # add labels on the contour curves
            pass

    def _add_vectors(self, item):
        if DEBUG:
            print "Adding vectors"
        # uncomment the following command if there is no support for
        # automatic scaling of vectors in the current plotting package:
        #item.scale_vectors()

        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        # vector components:
        u, v, w = item.getp('udata'), item.getp('vdata'), item.getp('wdata')
        # get line specifiactions (marker='.' means no marker):
        marker, color, style, width = self._get_linespecs(item)

        # scale the vectors according to this variable (scale=0 should
        # turn off automatic scaling):
        scale = item.getp('arrowscale')

        filled = item.getp('filledarrows') # draw filled arrows if True

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

    def _add_isosurface(self, item, shading='faceted'):
        if DEBUG:
            print "Adding a isosurface"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume
        c = item.getp('cdata')  # pseudocolor data
        isovalue = float(item.getp('isovalue'))

        if c is None:
            c = asarray(z).copy()
        db = self._generate_3D_database(x,y,z,v,c,
                                        indexing=item.getp('indexing'))
        self._g.OpenDatabase(db)

        self._g.AddPlot("Contour", "scalars")
        ca = self._g.ContourAttributes()
        if DEBUG:
            print "\nContourAttributes:\n", ca
        ca.SetContourMethod(1)  # Values
        ca.SetContourValue(isovalue)
        self._g.SetPlotOptions(ca)

    def _add_slices(self, item):
        if DEBUG:
            print "Adding slices in a volume"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume

        sx, sy, sz = item.getp('slices')
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
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume

        sx, sy, sz = item.getp('slices')
        if rank(sz) == 2:
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
            pass
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

            fig._g = visit
            fig._tmpfiles = []  # store all tmp files here

        self._g = fig._g  # link for faster access
        return fig

    def _replot(self):
        """Replot all axes and all plotitems in the backend."""
        # NOTE: only the current figure (gcf) is redrawn.
        if DEBUG:
            print "Doing replot in backend"

        fig = self.gcf()
        ok = self._g.SetActiveWindow(self.getp('curfig'))
        if not ok:
            self._g.AddWindow()
        # reset the plotting package instance in fig._g now if needed
        self._g.DeleteAllPlots()
        # Close databases and remove any temporary generated files:
        for tmpfname in fig._tmpfiles:
            self._g.CloseDatabase(tmpfname)
            os.remove(tmpfname)
        fig._tmpfiles = []

        self._set_figure_size(fig)

        # Prevent the active visualization window from being redrawn until
        # all plots and operators are added:
        self._g.DisableRedraw()

        nrows, ncolumns = fig.getp('axshape')
        for axnr, ax in fig.getp('axes').items():
            self._ax = ax
            if nrows != 1 or ncolumns != 1:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,axnr)
                pass
            plotitems = ax.getp('plotitems')
            plotitems.sort(self._cmpPlotProperties)
            for item in plotitems:
                func = item.getp('function') # function that produced this item
                if isinstance(item, Line):
                    self._add_line(item)
                elif isinstance(item, Surface):
                    self._add_surface(item, shading=ax.getp('shading'))
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
                legend = item.getp('legend')
                if legend:
                    # add legend to plot
                    pass

            self._set_axis_props(ax)

        self._g.RedrawWindow()
        self._g.DrawPlots()
        if self.getp('show'):
            # display plot on the screen
            if DEBUG > 1:
                print "\nDumping plot data to screen\n"
                debug(self)
            self._g.DeIconifyAllWindows()

    def hardcopy(self, filename, **kwargs):
        """
        Supported extensions:

          '.ps'    (PostScript)
          '.jpeg'  (Joint Photographic Experts Group)
          '.png'   (Portable Network Graphics)
          '.ppm'   (Portable Pixmap)
          '.tif'   (Tagged Image File Format)
          '.bmp'   (Bitmap Image)
          '.rgb'   (SGI RGB image format)
          '.obj'   (Alias Wavefront Obj file format)
          '.curve' (CURVE file format)
          '.pov'   (POV-Ray file format)
          '.stl'   (STL file format)
          '.ultra' (ULTRA file format) FIXME: Is this the correct extension?
          '.vtk'   (VTK file format)

        The first seven formats are image file formats, while the last six
        are geometry file formats.
        If `filename` contains just the file extension, say ``.png``,
        it is saved to ``tmp.png``.

        Optional arguments:

          maintain_aspect -- Set whether to maintain the aspect ratio for the
                         image at 1:1. If True (default), the image's width
                         and height will be forced to be the same.
          size        -- Set the image size. This option must be given as a
                         tuple (width,height). Default is (1024,1024).
          orientation -- Use either 'portrait' (default) or 'landscape'
                         orientation. Only available for PostScript output.
          screen_capture -- If True, the image is grabbed directly from the
                         screen, yielding an image that has exactly the same
                         size as the image on the screen. This option has no
                         effect on the geometry file formats. Default is
                         False.
          save_tiled  -- FIXME
          quality     -- Set the quality level. Must be an integer between 0
                         and 100, where 100 gives the best quality but also
                         the lowest compression. The default quality level
                         is 80. This option only affects JPEG images.
          progressive -- Set whether to use progressive JPEG images. Default
                         is False, which results in non-progressive JPEG
                         images.
          binary      -- Save VTK and STL geometry files in either binary
                         format (True) or ASCII format (False). ASCII is
                         used by default.
          stereo      -- If True, a separat image for the left and right eye
                         will be saved, resulting in files like
                         left_<filename> and right_<filename>. When displayed
                         together at high rates, they appear to have more
                         depth. This option has only effect on the image file
                         formats. Default is False.
          compression -- Set the compression method to use on TIFF images.
                         The following methods are available:

                           * None       - No compression
                           * 'packbits' - Fast lossless method (default)
                           * 'jpeg'     - Lossy compression
                           * 'deflate'  - Lossless compression (zip)

          force_merge -- FIXME

        Example on how to use the backend directly to save a hardcopy of
        the current figure:

        >>> g = get_backend()
        >>> swa = g.GetSaveWindowAttributes()
        >>> # Now set attributes in swa. Here we specify a PostScript file:
        >>> swa.SetFileName('myimage.ps')
        >>> swa.SetFormat(5)  # 5 is PostScript format
        >>> g.SetSaveWindowAttributes(swa)
        >>> g.SaveWindow()
        """
        if filename.startswith('.'):
            filename = 'tmp' + filename

        self.setp(**kwargs)
        color = self.getp('color')
        replot = kwargs.get('replot', True)
        if replot:
            self._replot()

        if DEBUG:
            print "Hardcopy to %s" % filename

        swa = self._g.GetSaveWindowAttributes()
        swa.SetFileName(filename)
        swa.SetFamily(False)

        ext2format = {'.bmp': 0, '.curve': 1, '.jpeg': 2, '.obj': 3, '.png': 4,
                      '.ps': 5, '.pov': 6, '.ppm': 7, '.rgb': 8, '.stl': 9,
                      '.tif': 10, '.ultra': 11, '.vtk': 12}
        basename, ext = os.path.splitext(filename)
        format = ext2format.get(ext, 5)  # PostScript is default format
        swa.SetFormat(format)

        maintain_aspect = kwargs.get('maintain_aspect', True)
        swa.SetMaintainAspect(maintain_aspect)

        size = kwargs.get('size', None)
        if isinstance(size, (tuple,list)) and len(size) == 2:
            width, height = size
            swa.SetWidth(int(width))
            swa.SetHeight(int(height))

        screen_capture = kwargs.get('screen_capture', False)
        swa.SetScreenCapture(screen_capture)

        save_tiled = kwargs.get('save_tiled', False)
        swa.SetSaveTiled(save_tiled)

        quality = kwargs.get('quality', 80)
        swa.SetQuality(quality)

        progressive = kwargs.get('progressive', False)
        swa.SetProgressive(progressive)

        binary = kwargs.get('binary', False)
        swa.SetBinary(binary)

        stereo = kwargs.get('stereo', False)
        swa.SetStereo(stereo)

        compression = kwargs.get('compression', 'packbits')
        compressions = {None: 0, 'packbits': 1, 'jpeg': 2, 'deflate': 3}
        try:
            compression = compressions[str(compression).lower()]
            swa.SetCompression(compression)
        except KeyError:
            pass

        force_merge = kwargs.get('force_merge', False)
        swa.SetForceMerge(force_merge)

        if DEBUG:
            print "\nSaveWindowAttributes:\n", swa
        self._g.SetSaveWindowAttributes(swa)
        self._g.SaveWindow()

    # reimplement color maps and other methods (if necessary) like clf,
    # closefig, and closefigs here.
    def clf(self):
        BaseClass.clf(self)
        self._g.ClearWindow()


    # Colormap methods:
    def hsv(self, m=64):
        return 'rainbow'

    def jet(self, m=64):
        return 'hot'

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


plt = VisitBackend()  # create backend instance
use(plt, globals())   # export public namespace of plt to globals()
backend = os.path.splitext(os.path.basename(__file__))[0][:-1]
