"""
This is a template file for writing new backends. It is a fully functional
backend, but no output is produced. One can specify this backend by

  python somefile.py --SCITOOLS_easyviz_backend template

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = template

and then

  from scitools.std import *

or if just easyviz is needed

  from scitools.easyviz import *

When writing a new backend, one can copy this file to xxx_.py (note the
underscore), where 'xxx' is the name of the new backend. Then replace all
instances of 'template' with 'xxx' and start implementing the class
methods below. The most important methods are figure, _replot, and hardcopy.

REQUIREMENTS:

VTK >= 4.2
Python bindings for VTK.

Notes:

- filled contours (contourf) doesn't look good in VTK 5.0.

"""

from __future__ import division

from common import *
from scitools.globaldata import DEBUG, VERBOSE, OPTIMIZATION
from scitools.misc import check_if_module_exists
from scitools.numpyutils import allclose
from misc import _update_from_config_file

check_if_module_exists('vtk', msg='You need to install the vtk package.', abort=False)
import vtk
import os

check_if_module_exists('Tkinter', msg='You need to install the Tkinter package.')
import Tkinter
# use old behavior in Tkinter module to get around issue with Tcl
# (more info: http://www.python.org/doc/2.3/whatsnew/node18.html)
Tkinter.wantobjects = 0

try:
    import vtkTkRenderWidget
except:
    from vtk.tk import vtkTkRenderWidget

_vtk_options = {'mesa': 0,
                'vtk_inc_dir': ['/usr/include/vtk-5.0'],
                'vtk_lib_dir': ['/usr/lib',
                                '/usr/lib/python-support/python-vtk/python2.5/vtk']}
_update_from_config_file(_vtk_options, section='vtk')

if _vtk_options['mesa']:
    _graphics_fact = vtk.vtkGraphicsFactory()
    _graphics_fact.SetOffScreenOnlyMode(1)
    _graphics_fact.SetUseMesaClasses(1)
    _imaging_fact = vtk.vtkImagingFactory()
    _imaging_fact.SetUseMesaClasses(1)
    del _graphics_fact
    del _imaging_fact

# change these to suit your needs.
inc_dirs=['/usr/include/vtk-5.0']
lib_dirs=['/usr/lib', '/usr/lib/python-support/python-vtk/python2.5/vtk']

if OPTIMIZATION == 'weave':
    try:
        from scipy import weave
    except ImportError:
        try:
            import weave
        except ImportError:
            print "Weave not available. Optimization turned off."


class _VTKFigure(object):
    def __init__(self, plt, width=800, height=600, title=''):
        # create the GUI:
        self.plt = plt
        self.width = width
        self.height = height
        self.master = plt._master
        self.root = Tkinter.Toplevel(self.master)
        self.root.title(title)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<KeyPress-q>", self.close)
        self.root.minsize(200, 200)
        self.root.geometry('%sx%s' % (width,height))
        self.root.withdraw()
        self.frame = Tkinter.Frame(self.root, relief='sunken', bd=2)
        self.frame.pack(side='top', fill='both', expand=1)
        self.tkw = vtkTkRenderWidget.vtkTkRenderWidget(self.frame,
                                                       width=width,
                                                       height=height)
        self.tkw.pack(expand='true', fill='both')
        self.renwin = self.tkw.GetRenderWindow()
        self.renwin.SetSize(width, height)

    def reset(self):
        # remove all renderers:
        renderers = self.renwin.GetRenderers()
        ren = renderers.GetFirstRenderer()
        while ren is not None:
            self.renwin.RemoveRenderer(ren)
            ren = renderers.GetNextItem()

    def close(self, event=None):
        self.plt.clf()
        self.root.withdraw()

    def display(self, show=True):
        if show:
            self.root.deiconify()  # raise window
        self.root.update()         # update window
        self.render()

    def render(self):
        # First we render each of the axis renderers:
        renderers = self.renwin.GetRenderers()
        ren = renderers.GetFirstRenderer()
        while ren is not None:
            ren.Render()
            ren = renderers.GetNextItem()
        # Then we render the complete scene:
        self.renwin.Render()

    def exit(self):
        self.root.destroy()

    def set_size(self, width, height):
        self.root.geometry('%sx%s' % (width,height))
        self.root.update()


class VTKBackend(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self._init()

    def _init(self, *args, **kwargs):
        """Perform initialization that is special for this backend."""

        self._master = Tkinter.Tk()
        self._master.withdraw()
        self.figure(self.getp('curfig'))

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

        self._arrow_types = {
            # tuple: (type,rotation)
            '':  (9,0),   # arrow
            '.': (0,0),   # no marker
            'o': (7,0),   # circle
            '+': (3,0),   # plus
            'x': (3,45),  # x-mark
            '*': (3,0),   # star --> plus
            's': (6,0),   # square
            'd': (8,0),   # diamond
            'v': (5,180), # triangle (down)
            '^': (5,0),   # triangle (up)
            '<': (5,90),  # triangle (left)
            '>': (5,270), # triangle (right)
            'p': (6,0),   # pentagram --> square
            'h': (6,0),   # hexagram --> square
            }

        self._colors = {
            '': None,   # no color --> blue
            'r': (1,0,0),  # red
            'g': (0,1,0),  # green
            'b': (0,0,1),  # blue
            'c': (0,1,1),  # cyan
            'm': (1,0,1),  # magenta
            'y': (1,1,0),  # yellow
            'k': (0,0,0),  # black
            'w': (1,1,1),  # white
            }

        self._line_styles = {
            '': None,    # no line
            '-': None,   # solid line
            ':': None,   # dotted line
            '-.': None,  # dash-dot line
            '--': None,  # dashed line
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

    def _get_color(self, color, default=None):
        if not (isinstance(color, (tuple,list)) and len(color) == 3):
            color = self._colors.get(color, default)
            if color is None:
                color = default
        return color

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
        if xlabel:
            # add a text label on x-axis
            pass
        if ylabel:
            # add a text label on y-axis
            pass
        if zlabel:
            # add a text label on z-axis
            pass

    def _set_title(self, ax):
        """Add a title at the top of the axis."""
        if DEBUG:
            print "Setting title"
        title = self._fix_latex(ax.getp('title'))
        if title:
            tprop = vtk.vtkTextProperty()
            tprop.BoldOff()
            tprop.SetFontSize(ax.getp('fontsize'))
            tprop.SetColor(ax.getp('fgcolor'))
            tprop.SetFontFamilyToArial()
            tprop.SetVerticalJustificationToTop()
            tprop.SetJustificationToCentered()
            tmapper = vtk.vtkTextMapper()
            tmapper.SetInput(title)
            tmapper.SetTextProperty(tprop)
            tactor = vtk.vtkActor2D()
            tactor.SetMapper(tmapper)
            tactor.GetPositionCoordinate().SetCoordinateSystemToView()
            tactor.GetPositionCoordinate().SetValue(0.0, 0.95)
            ax._renderer.AddActor(tactor)

    def _set_limits(self, ax):
        """Set axis limits in x, y, and z direction."""
        if DEBUG:
            print "Setting axis limits"
        mode = ax.getp('mode')
        if mode == 'auto':
            # let plotting package set 'nice' axis limits in the x, y,
            # and z direction. If this is not automated in the plotting
            # package, one can use the following limits:
            xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.getp('xmin')
            xmax = ax.getp('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits
                pass
            else:
                # let plotting package set x-axis limits or use
                xmin, xmax = ax.getp('xlim')

            ymin = ax.getp('ymin')
            ymax = ax.getp('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                pass
            else:
                # let plotting package set y-axis limits or use
                ymin, ymax = ax.getp('ylim')

            zmin = ax.getp('zmin')
            zmax = ax.getp('zmax')
            if zmin is not None and zmax is not None:
                # set z-axis limits
                pass
            else:
                # let plotting package set z-axis limits or use
                zmin, zmax = ax.getp('zlim')
        elif mode == 'tight':
            # set the limits on the axis to the range of the data. If
            # this is not automated in the plotting package, one can
            # use the following limits:
            xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
        elif mode == 'fill':
            # not sure about this
            xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()

        limits = [xmin, xmax, ymin, ymax, zmin, zmax]
        ax._limits = (xmin, xmax, ymin, ymax, zmin, zmax)

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
        dar = ax.getp('daspect')  # dar is a list (len(dar) is 3).
        # the axis limits are stored as ax._limits
        l = list(ax._limits)
        l[0] /= dar[0];  l[1] /= dar[0]
        l[2] /= dar[1];  l[3] /= dar[1]
        l[4] /= dar[2];  l[5] /= dar[2]
        ax._scaled_limits = tuple(l)

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
        if ax.getp('box'):
            # display box
            pass
        else:
            # do not display box
            pass

    def _set_grid(self, ax):
        """Turn grid lines on or off."""
        if DEBUG:
            print "Setting grid"
        if ax.getp('grid'):
            # turn grid lines on
            pass
        else:
            # turn grid lines off
            pass

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
            ax._caxis = (cmin, cmax)
        else:
            # use autoranging for color axis scale
            ax._caxis = None

    def _set_colormap(self, ax):
        """Set the colormap."""
        if DEBUG:
            print "Setting colormap"
        cmap = ax.getp('colormap')
        # cmap is plotting package dependent
        if not isinstance(cmap, vtk.vtkLookupTable):
            cmap = self.jet()  # use default colormap
        ax._colormap = cmap

    def _set_view(self, ax):
        """Set viewpoint specification."""
        if DEBUG:
            print "Setting view"
        cam = ax.getp('camera')

        view = cam.getp('view')

        fp = cam.getp('camtarget')
        camera = vtk.vtkCamera()
        camera.SetFocalPoint(cam.getp('camtarget'))
        camera.SetViewUp(cam.getp('camup'))
        camera.ParallelProjectionOn()
        if view == 2:
            # setup a default 2D view
            camera.SetPosition(fp[0], fp[1], 1)
        elif view == 3:
            camera.SetPosition(fp[0],fp[1]-1,fp[2])
            az = cam.getp('azimuth')
            el = cam.getp('elevation')
            if az is None or el is None:
                # azimuth or elevation is not given. Set up a default
                # 3D view (az=-37.5 and el=30 is the default 3D view in
                # Matlab).
                az = -37.5
                el = 30
            # set a 3D view according to az and el
            camera.Azimuth(az)
            camera.Elevation(el)

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
                    camera.ParallelProjectionOff()
                else:
                    camera.ParallelProjectionOn()


        self._ax._renderer.SetActiveCamera(camera)
        self._ax._camera = camera

        # make sure all actors are inside the current view:
        ren = self._ax._renderer
        ren.ResetCamera()
        #if self._ax.getp('camera').getp('view') == 2:
        #    ren.GetActiveCamera().Zoom(1.5)
        camera.Zoom(cam.getp('camzoom'))

        # set the camera in the vtkCubeAxesActor2D object:
        #self._ax._vtk_axes.SetCamera(camera)


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
            self._set_labels(ax)
            self._set_box(ax)
            self._set_grid(ax)
        else:
            # turn off all axis labeling, tickmarks, and background
            pass

    def _is_inside_limits(self, data):
        """Return True if data limits is inside axis limits."""
        slim = self._ax._scaled_limits
        dlim = data.GetBounds()
        for i in range(0, len(slim), 2):
            if dlim[i] < slim[i] and not allclose(dlim[i], slim[i]):
                return False
        for i in range(1, len(slim), 2):
            if dlim[i] > slim[i] and not allclose(dlim[i], slim[i]):
                return False
        return True

    def _cut_data(self, data):
        """Return cutted data if limits is outside (scaled) axis limits."""
        if self._is_inside_limits(data.GetOutput()):
            return data
        box = vtk.vtkBox()
        box.SetBounds(self._ax._scaled_limits)
        clipper = vtk.vtkClipPolyData()
        clipper.SetInput(data.GetOutput())
        clipper.SetClipFunction(box)
        #clipper.GenerateClipScalarsOn()
        #clipper.GenerateClippedOutputOn()
        clipper.SetValue(0.0)
        clipper.InsideOutOn()
        clipper.Update()
        return clipper

    def _set_shading(self, item, source, actor):
        shading = self._ax.getp('shading')
        if shading == 'interp':
            actor.GetProperty().SetInterpolationToGouraud()
        elif shading == 'flat':
            actor.GetProperty().SetInterpolationToFlat()
        else:
            # use 'faceted' as the default shading
            actor.GetProperty().SetInterpolationToFlat()
            edges = vtk.vtkExtractEdges()
            edges.SetInput(source.GetOutput())
            edges.Update()
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(edges.GetOutput())
            mapper.ScalarVisibilityOff()
            mapper.SetResolveCoincidentTopologyToPolygonOffset()
            mesh = vtk.vtkActor()
            mesh.SetMapper(mapper)
            edgecolor = self._colors.get(item.getp('edgecolor'), None)
            if edgecolor is None:
                # try items linecolor property:
                edgecolor = self._colors.get(item.getp('linecolor'), None)
                if edgecolor is None:
                    edgecolor = (0,0,0)  # use black as default edge color
            mesh.GetProperty().SetColor(edgecolor)
            self._ax._renderer.AddActor(mesh)

    def _set_actor_properties(self, item, actor):
        # set line properties:
        color = self._get_color(item.getp('linecolor'), (0,0,1))
        actor.GetProperty().SetColor(color)
        if item.getp('linetype') == '--':
            actor.GetProperty().SetLineStipplePattern(65280)
        elif item.getp('linetype') == ':':
            actor.GetProperty().SetLineStipplePattern(0x1111)
            actor.GetProperty().SetLineStippleRepeatFactor(1)
        #actor.GetProperty().SetPointSize(item.getp('pointsize'))
        linewidth = item.getp('linewidth')
        if linewidth:
            actor.GetProperty().SetLineWidth(float(linewidth))

    def _set_actor_material_properties(self, item, actor):
        # set material properties:
        ax = self._ax
        mat = item.getp('material')
        if mat.getp('opacity') is not None:
            actor.GetProperty().SetOpacity(mat.getp('opacity'))
        if mat.getp('ambient') is not None:
            actor.GetProperty().SetAmbient(mat.getp('ambient'))
        if ax.getp('ambientcolor') is not None:
            actor.GetProperty().SetAmbientColor(ax.getp('ambientcolor'))
        if mat.getp('diffuse') is not None:
            actor.GetProperty().SetDiffuse(mat.getp('diffuse'))
        if ax.getp('diffusecolor') is not None:
            actor.GetProperty().SetDiffuseColor(ax.getp('diffusecolor'))
        if mat.getp('specular') is not None:
            actor.GetProperty().SetSpecular(mat.getp('specular'))
        if mat.getp('specularpower') is not None:
            actor.GetProperty().SetSpecularPower(mat.getp('specularpower'))

    def _create_2D_scalar_data(self, item):
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = asarray(item.getp('zdata'))  # scalar field
        try:
            c = item.getp('cdata')       # pseudocolor data
        except KeyError:
            c = z.copy()
        if c is None:
            c = z.copy()
        else:
            c = asarray(c)
        assert shape(c) == shape(z)

        if shape(x) != shape(z) and shape(y) != shape(z):
            assert rank(x) == 1 and rank(y) == 1
            x, y = meshgrid(x,y,sparse=False,indexing=item.getp('indexing'))
            # FIXME: use ndgrid instead of meshgrid
        assert shape(x) == shape(z) and shape(y) == shape(z)

        # scale x, y, and z according to data aspect ratio:
        dx, dy, dz = self._ax.getp('daspect')
        x = x/dx;  y = y/dy;  z = z/dz

        function = item.getp('function')
        if function in ['contour', 'contourf', 'pcolor']:
            z *= 0
        if function in ['meshc', 'surfc'] and isinstance(item, Contours):
            # this item is the Contours object beneath the surface in
            # a meshc or surfc plot.
            z *= 0
            z += self._ax._scaled_limits[4]

        points = vtk.vtkPoints()
        points.SetNumberOfPoints(item.getp('numberofpoints'))
        scalars = vtk.vtkFloatArray()
        scalars.SetNumberOfTuples(item.getp('numberofpoints'))
        scalars.SetNumberOfComponents(1)
        nx, ny = shape(z)
        if OPTIMIZATION == 'weave':
            code = """
int ind=0;
for (int j=0; j<ny; j++) {
    for (int i=0; i<nx; i++) {
        points->SetPoint(ind, x(i,j), y(i,j), z(i,j));
        scalars->SetValue(ind, c(i,j));
        ind += 1;
    }
}
"""
            args = ['nx', 'ny', 'x', 'y', 'z', 'c', 'points', 'scalars']
            weave.inline(code, args,
                         include_dirs=inc_dirs, library_dirs=lib_dirs,
                         type_converters=weave.converters.blitz)
        else:
            ind = 0
            for j in range(ny):
                for i in range(nx):
                    points.SetPoint(ind, x[i,j], y[i,j], z[i,j])
                    scalars.SetValue(ind, c[i,j])
                    ind += 1
        points.Modified()
        sgrid = vtk.vtkStructuredGrid()
        sgrid.SetDimensions(item.getp('dims'))
        sgrid.SetPoints(points)
        sgrid.GetPointData().SetScalars(scalars)
        sgrid.Update()
        return sgrid

    def _create_2D_vector_data(self, item):
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = item.getp('zdata')           # scalar field
        # vector components:
        u = asarray(item.getp('udata'))
        v = asarray(item.getp('vdata'))
        w = item.getp('wdata')

        if z is None:
            z = zeros(shape(u))
        else:
            z = squeeze(z)
        if w is None:
            w = zeros(shape(u))
        else:
            w = asarray(w)

        # scale x, y, and z according to data aspect ratio:
        dx, dy, dz = self._ax.getp('daspect')
        x = x/dx;  y = y/dy;  z = z/dz

        if shape(x) != shape(u) and shape(y) != shape(u):
            assert rank(x) == 1 and rank(y) == 1
            x, y = meshgrid(x,y,sparse=False,indexing=item.getp('indexing'))
            # FIXME: use ndgrid instead of meshgrid
        assert shape(x) == shape(u) and shape(y) == shape(u) and \
               shape(z) == shape(u) and shape(v) == shape(u) and \
               shape(w) == shape(u)

        n = item.getp('numberofpoints')
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(n)
        vectors = vtk.vtkFloatArray()
        vectors.SetNumberOfTuples(n)
        vectors.SetNumberOfComponents(3)
        vectors.SetNumberOfValues(3*n)
        nx, ny = shape(u)
        if OPTIMIZATION == 'weave':
            code = """
int ind=0;
for (int j=0; j<ny; j++) {
    for (int i=0; i<nx; i++) {
        points->SetPoint(ind, x(i,j), y(i,j), z(i,j));
        vectors->SetTuple3(ind, u(i,j), v(i,j), w(i,j));
        ind += 1;
    }
}
"""
            args = ['nx', 'ny', 'x', 'y', 'z',
                    'u', 'v', 'w', 'points', 'vectors']
            weave.inline(code, args,
                         include_dirs=inc_dirs, library_dirs=lib_dirs,
                         type_converters=weave.converters.blitz)
        else:
            ind = 0
            for j in range(ny):
                for i in range(nx):
                    points.SetPoint(ind, x[i,j], y[i,j], z[i,j])
                    vectors.SetTuple3(ind, u[i,j], v[i,j], w[i,j])
                    ind += 1
        points.Modified()
        sgrid = vtk.vtkStructuredGrid()
        sgrid.SetDimensions(item.getp('dims'))
        sgrid.SetPoints(points)
        sgrid.GetPointData().SetVectors(vectors)
        sgrid.Update()
        return sgrid

    def _create_3D_scalar_data(self, item):
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = squeeze(item.getp('zdata'))  # grid component in z-direction
        v = asarray(item.getp('vdata'))  # scalar data
        c = item.getp('cdata')           # pseudocolor data
        # FIXME: What about pseudocolor data?

        if shape(x) != shape(v) and shape(y) != shape(v) \
               and shape(z) != shape(v):
            assert rank(x) == 1 and rank(y) == 1 and rank(z) == 1
            x,y,z = meshgrid(x,y,z,sparse=False,indexing=item.getp('indexing'))
            # FIXME: use ndgrid instead of meshgrid
        assert shape(x) == shape(v) and shape(y) == shape(v) \
               and shape(z) == shape(v)

        # scale x, y, and z according to data aspect ratio:
        dx, dy, dz = self._ax.getp('daspect')
        x = x/dx;  y = y/dy;  z = z/dz

        points = vtk.vtkPoints()
        points.SetNumberOfPoints(item.getp('numberofpoints'))
        scalars = vtk.vtkFloatArray()
        scalars.SetNumberOfTuples(item.getp('numberofpoints'))
        scalars.SetNumberOfComponents(1)
        nx, ny, nz = shape(v)
        if OPTIMIZATION == 'weave':
            code = """
int ind=0;
for (int k=0; k<nz; k++) {
    for (int j=0; j<ny; j++) {
        for (int i=0; i<nx; i++) {
            points->SetPoint(ind, x(i,j,k), y(i,j,k), z(i,j,k));
            scalars->SetValue(ind, v(i,j,k));
            ind += 1;
        }
    }
}
"""
            args = ['nx', 'ny', 'nz', 'x', 'y', 'z', 'v', 'points', 'scalars']
            weave.inline(code, args,
                         include_dirs=inc_dirs, library_dirs=lib_dirs,
                         type_converters=weave.converters.blitz)
        else:
            ind = 0
            for k in range(nz):
                for j in range(ny):
                    for i in range(nx):
                        points.SetPoint(ind, x[i,j,k], y[i,j,k], z[i,j,k])
                        scalars.SetValue(ind, v[i,j,k])
                        ind += 1
        points.Modified()
        sgrid = vtk.vtkStructuredGrid()
        sgrid.SetDimensions(item.getp('dims'))
        sgrid.SetPoints(points)
        sgrid.GetPointData().SetScalars(scalars)
        sgrid.Update()
        return sgrid

    def _create_3D_vector_data(self, item):
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = squeeze(item.getp('zdata'))  # grid component in z-direction
        # vector components:
        u = asarray(item.getp('udata'))
        v = asarray(item.getp('vdata'))
        w = asarray(item.getp('wdata'))

        # scale x, y, and z according to data aspect ratio:
        dx, dy, dz = self._ax.getp('daspect')
        x = x/dx;  y = y/dy;  z = z/dz

        if shape(x) != shape(u) and shape(y) != shape(u) \
               and shape(z) != shape(u):
            assert rank(x) == 1 and rank(y) == 1 and rank(z) == 1
            x,y,z = meshgrid(x,y,z,sparse=False,indexing=item.getp('indexing'))
            # FIXME: use ndgrid instead of meshgrid
        assert shape(x) == shape(u) and shape(y) == shape(u) and \
               shape(z) == shape(u) and shape(v) == shape(u) and \
               shape(w) == shape(u)

        n = item.getp('numberofpoints')
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(n)
        vectors = vtk.vtkFloatArray()
        vectors.SetNumberOfTuples(n)
        vectors.SetNumberOfComponents(3)
        vectors.SetNumberOfValues(3*n)
        nx, ny, nz = shape(u)
        if OPTIMIZATION == 'weave':
            code = """
int ind=0;
for (int k=0; k<nz; k++) {
    for (int j=0; j<ny; j++) {
        for (int i=0; i<nx; i++) {
            points->SetPoint(ind, x(i,j,k), y(i,j,k), z(i,j,k));
            vectors->SetTuple3(ind, u(i,j,k), v(i,j,k), w(i,j,k));
            ind += 1;
        }
    }
}
"""
            args = ['nx', 'ny', 'nz', 'x', 'y', 'z',
                    'u', 'v', 'w', 'points', 'vectors']
            weave.inline(code, args,
                         include_dirs=inc_dirs, library_dirs=lib_dirs,
                         type_converters=weave.converters.blitz)
        else:
            ind = 0
            for k in range(nz):
                for j in range(ny):
                    for i in range(nx):
                        points.SetPoint(ind, x[i,j,k], y[i,j,k], z[i,j,k])
                        vectors.SetTuple3(ind, u[i,j,k], v[i,j,k], w[i,j,k])
                        ind += 1
        points.Modified()
        sgrid = vtk.vtkStructuredGrid()
        sgrid.SetDimensions(item.getp('dims'))
        sgrid.SetPoints(points)
        sgrid.GetPointData().SetVectors(vectors)
        sgrid.Update()
        return sgrid

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

        sgrid = self._create_2D_scalar_data(item)

        contours = item.getp('contours')
        if contours:
            # the current item is produced by meshc or surfc and we
            # should therefore add contours at the bottom:
            self._add_contours(contours, placement='bottom')

        if item.getp('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            pass
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            pass
        plane = vtk.vtkStructuredGridGeometryFilter()
        plane.SetInput(sgrid)
        plane.Update()
        data = self._cut_data(plane)
        normals = vtk.vtkPolyDataNormals()
        normals.SetInput(data.GetOutput())
        normals.SetFeatureAngle(45)
        normals.Update()
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInput(normals.GetOutput())
        mapper.SetLookupTable(self._ax._colormap)
        cax = self._ax._caxis
        if cax is None:
            cax = data.GetOutput().GetScalarRange()
        mapper.SetScalarRange(cax)
        mapper.Update()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        if item.getp('wireframe'):
            actor.GetProperty().SetRepresentationToWireframe()
        else:
            self._set_shading(item, data, actor)
        self._set_actor_properties(item, actor)
        #self._add_legend(item, normals.GetOutput())
        self._ax._renderer.AddActor(actor)
        self._ax._apd.AddInput(normals.GetOutput())

    def _add_contours(self, item, placement=None):
        # The placement keyword can be either None or 'bottom'. The
        # latter specifies that the contours should be placed at the
        # bottom (as in meshc or surfc).
        if DEBUG:
            print "Adding contours"

        sgrid = self._create_2D_scalar_data(item)
        plane = vtk.vtkStructuredGridGeometryFilter()
        plane.SetInput(sgrid)
        plane.Update()
        data = self._cut_data(plane)

        filled = item.getp('filled')  # draw filled contour plot if True
        if filled:
            iso = vtk.vtkBandedPolyDataContourFilter()
            iso.SetScalarModeToValue()
            #iso.SetScalarModeToIndex()
            iso.GenerateContourEdgesOn()
        else:
            iso = vtk.vtkContourFilter()
        iso.SetInput(data.GetOutput())

        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            zmin, zmax = data.GetOutput().GetScalarRange()
            iso.SetNumberOfContours(clevels)
            iso.GenerateValues(clevels, zmin, zmax)
        else:
            for i in range(clevels):
                iso.SetValue(i, cvector[i])
        iso.Update()

        isoMapper = vtk.vtkPolyDataMapper()
        isoMapper.SetInput(iso.GetOutput())
        cmap = self._ax._colormap
        #if filled:
        #    cmap.SetNumberOfColors(clevels)
        #    cmap.Build()
        isoMapper.SetLookupTable(cmap)
        cax = self._ax._caxis
        if cax is None:
            cax = data.GetOutput().GetScalarRange()
        isoMapper.SetScalarRange(cax)
        if item.getp('linecolor'):  # linecolor is defined
            isoMapper.ScalarVisibilityOff()
        isoMapper.Update()
        isoActor = vtk.vtkActor()
        isoActor.SetMapper(isoMapper)
        self._set_actor_properties(item, isoActor)
        #self._add_legend(item, iso.GetOutput())
        self._ax._renderer.AddActor(isoActor)
        self._ax._apd.AddInput(data.GetOutput())

        if filled:
            # create contour edges:
            edgeMapper = vtk.vtkPolyDataMapper()
            edgeMapper.SetInput(iso.GetContourEdgesOutput())
            edgeMapper.SetResolveCoincidentTopologyToPolygonOffset()
            edgeActor = vtk.vtkActor()
            edgeActor.SetMapper(edgeMapper)
            fgcolor = self._get_color(self._ax.getp('fgcolor'), (0,0,0))
            edgecolor = self._get_color(item.getp('edgecolor'), fgcolor)
            edgeActor.GetProperty().SetColor(edgecolor)
            # FIXME: use edgecolor property above (or black as default)
            self._ax._renderer.AddActor(edgeActor)

        if item.getp('clabels'):
            # add labels on the contour curves
            # subsample the points and label them:
            mask = vtk.vtkMaskPoints()
            mask.SetInput(iso.GetOutput())
            mask.SetOnRatio(int(data.GetOutput().GetNumberOfPoints()/50))
            mask.SetMaximumNumberOfPoints(50)
            mask.RandomModeOn()

            # Create labels for points - only show visible points
            visPts = vtk.vtkSelectVisiblePoints()
            visPts.SetInput(mask.GetOutput())
            visPts.SetRenderer(self._ax._renderer)
            ldm = vtk.vtkLabeledDataMapper()
            ldm.SetInput(mask.GetOutput())
            ldm.SetLabelFormat("%.1g")
            ldm.SetLabelModeToLabelScalars()
            tprop = ldm.GetLabelTextProperty()
            tprop.SetFontFamilyToArial()
            tprop.SetFontSize(10)
            tprop.SetColor(0,0,0)
            tprop.ShadowOff()
            tprop.BoldOff()
            contourLabels = vtk.vtkActor2D()
            contourLabels.SetMapper(ldm)
            self._ax._renderer.AddActor(contourLabels)

    def _add_vectors(self, item):
        if DEBUG:
            print "Adding vectors"
        # uncomment the following command if there is no support for
        # automatic scaling of vectors in the current plotting package:
        item.scale_vectors()

        if rank(item.getp('udata')) == 3:
            sgrid = self._create_3D_vector_data(item)
        else:
            sgrid = self._create_2D_vector_data(item)

        # get line specifiactions (marker='.' means no marker):
        marker, color, style, width = self._get_linespecs(item)

        # scale the vectors according to this variable (scale=0 should
        # turn off automatic scaling):
        scale = item.getp('arrowscale')

        filled = item.getp('filledarrows') # draw filled arrows if True

        marker, rotation = self._arrow_types[item.getp('linemarker')]
        arrow = vtk.vtkGlyphSource2D()
        arrow.SetGlyphType(marker)
        arrow.SetFilled(item.getp('filledarrows'))
        arrow.SetRotationAngle(rotation)
        if arrow.GetGlyphType() != 9: # not an arrow
            arrow.DashOn()
            arrow.SetCenter(.75,0,0)
        else:
            arrow.SetCenter(.5,0,0)
        arrow.SetColor(self._get_color(item.getp('linecolor'), (1,0,0)))

        plane = vtk.vtkStructuredGridGeometryFilter()
        plane.SetInput(sgrid)
        plane.Update()
        data = self._cut_data(plane)
        glyph = vtk.vtkGlyph3D()
        glyph.SetInput(data.GetOutput())
        glyph.SetSource(arrow.GetOutput())
        glyph.SetColorModeToColorByVector()
        glyph.SetRange(data.GetOutput().GetScalarRange())
        glyph.ScalingOn()
        glyph.SetScaleModeToScaleByVector()
        glyph.OrientOn()
        glyph.SetVectorModeToUseVector()
        glyph.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(glyph.GetOutput())
        #vr = data.GetOutput().GetPointData().GetVectors().GetRange()
        #mapper.SetScalarRange(vr)
        mapper.ScalarVisibilityOff()
        mapper.Update()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self._set_actor_properties(item, actor)
        #self._add_legend(item, arrow.GetOutput())
        self._ax._renderer.AddActor(actor)
        self._ax._apd.AddInput(glyph.GetOutput())

    def _add_streams(self, item):
        if DEBUG:
            print "Adding streams"

        if rank(item.getp('udata')) == 3:
            sgrid = self._create_3D_vector_data(item)
        else:
            sgrid = self._create_2D_vector_data(item)

        length = sgrid.GetLength()
        max_velocity = sgrid.GetPointData().GetVectors().GetMaxNorm()
        max_time = 35.0*length/max_velocity

        dx, dy, dz = self._ax.getp('daspect')
        sx = ravel(item.getp('startx'))/dx
        sy = ravel(item.getp('starty'))/dy
        sz = ravel(item.getp('startz'))/dz
        for i in range(item.getp('numberofstreams')):
            integ = vtk.vtkRungeKutta2()
            #integ = vtk.vtkRungeKutta4()
            stream = vtk.vtkStreamLine()
            stream.SetInput(sgrid)
            stream.SetStepLength(item.getp('stepsize'))
            #stream.SetIntegrationStepLength(item.getp('stepsize'))
            #stream.SetIntegrationDirectionToIntegrateBothDirections()
            stream.SetIntegrationDirectionToForward()
            #stream.SetMaximumPropagationTime(max_time)
            #stream.SetMaximumPropagationTime(200)
            stream.SpeedScalarsOn()
            #stream.VorticityOn()
            stream.SetStartPosition(sx[i], sy[i], sz[i])
            stream.SetIntegrator(integ)
            stream.Update()
            data = self._cut_data(stream)

            if item.getp('tubes'):
                # draw stream tubes:
                ncirc = item.getp('n')
                scale = item.getp('tubescale')
                streamtube = vtk.vtkTubeFilter()
                streamtube.SetInput(data.GetOutput())
                streamtube.SetRadius(1)
                streamtube.SetNumberOfSides(ncirc)
                streamtube.SetVaryRadiusToVaryRadiusByVector()
                streamtube.Update()
                output = streamtube.GetOutput()
            elif item.getp('ribbons'):
                # draw stream ribbons:
                width = item.getp('ribbonwidth')
                streamribbon = vtk.vtkRibbonFilter()
                streamribbon.SetInput(data.GetOutput())
                streamribbon.VaryWidthOn()
                streamribbon.SetWidthFactor(width)
                #streamribbon.SetAngle(90)
                streamribbon.SetDefaultNormal([0,1,0])
                streamribbon.UseDefaultNormalOn()
                streamribbon.Update()
                output = streamribbon.GetOutput()
            else:
                # draw stream lines:
                output = data.GetOutput()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(output)
            mapper.SetLookupTable(self._ax._colormap)
            cax = self._ax._caxis
            if cax is None:
                cax = output.GetBounds()[4:]
                #cax = sgrid.GetScalarRange()
            mapper.SetScalarRange(cax)
            mapper.Update()
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            #self._set_shading(item, stream, actor)
            self._set_actor_properties(item, actor)
            #self._add_legend(item, output)
            self._ax._renderer.AddActor(actor)
            self._ax._apd.AddInput(output)

    def _add_isosurface(self, item):
        if DEBUG:
            print "Adding a isosurface"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume
        c = item.getp('cdata')  # pseudocolor data
        isovalue = item.getp('isovalue')

        sgrid = self._create_3D_scalar_data(item)
        iso = vtk.vtkContourFilter()
        iso.SetInput(sgrid)
        iso.SetValue(0, isovalue)
        iso.Update()
        data = self._cut_data(iso)
        normals = vtk.vtkPolyDataNormals()
        normals.SetInput(data.GetOutput())
        normals.SetFeatureAngle(45)
        normals.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(normals.GetOutput())
        mapper.SetLookupTable(self._ax._colormap)
        cax = self._ax._caxis
        if cax is None:
            cax = sgrid.GetScalarRange()
        mapper.SetScalarRange(cax)
        mapper.Update()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self._set_shading(item, data, actor)
        self._set_actor_properties(item, actor)
        self._ax._renderer.AddActor(actor)
        self._ax._apd.AddInput(normals.GetOutput())

    def _add_slices(self, item, contours=False):
        if DEBUG:
            print "Adding slices in a volume"

        sgrid = self._create_3D_scalar_data(item)

        sx, sy, sz = item.getp('slices')
        if rank(sz) == 2:
            # sx, sy, and sz defines a surface
            h = Surface(sx,sy,sz)
            sgrid2 = self._create_2D_scalar_data(h)
            plane = vtk.vtkStructuredGridGeometryFilter()
            plane.SetInput(sgrid2)
            plane.Update()
            data = self._cut_data(plane)
            implds = vtk.vtkImplicitDataSet()
            implds.SetDataSet(data.GetOutput())
            implds.Modified()
            cut = vtk.vtkCutter()
            cut.SetInput(sgrid)
            cut.SetCutFunction(implds)
            cut.GenerateValues(10, -2,2)
            cut.GenerateCutScalarsOn()
            cut.Update()
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(cut.GetOutput())
            mapper.SetLookupTable(self._ax._colormap)
            cax = self._ax._caxis
            if cax is None:
                cax = data.GetOutput().GetScalarRange()
            mapper.SetScalarRange(cax)
            mapper.Update()
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            self._set_shading(item, data, actor)
            self._set_actor_properties(item, actor)
            self._ax._renderer.AddActor(actor)
            self._ax._apd.AddInput(cut.GetOutput())
            self._ax._apd.AddInput(data.GetOutput())
        else:
            # sx, sy, and sz is either numbers or vectors with numbers
            origins = []
            normals = []
            center = sgrid.GetCenter()
            dx, dy, dz = self._ax.getp('daspect')
            sx = ravel(sx)/dx
            sy = ravel(sy)/dy
            sz = ravel(sz)/dz
            for i in range(len(sx)):
                normals.append([1,0,0])
                origins.append([sx[i], center[1], center[2]])
            for i in range(len(sy)):
                normals.append([0,1,0])
                origins.append([center[0], sy[i], center[2]])
            for i in range(len(sz)):
                normals.append([0,0,1])
                origins.append([center[0], center[1], sz[i]])
            for i in range(len(normals)):
                plane = vtk.vtkPlane()
                plane.SetOrigin(origins[i])
                plane.SetNormal(normals[i])
                cut = vtk.vtkCutter()
                cut.SetInput(sgrid)
                cut.SetCutFunction(plane)
                cut.Update()
                data = self._cut_data(cut)
                mapper = vtk.vtkPolyDataMapper()
                if contours:
                    iso = vtk.vtkContourFilter()
                    iso.SetInput(data.GetOutput())
                    cvector = item.getp('cvector')
                    if cvector is not None:
                        for i in range(len(cvector)):
                            iso.SetValue(i, cvector[i])
                    else:
                        zmin, zmax = data.GetOutput().GetScalarRange()
                        iso.GenerateValues(item.getp('clevels'), zmin, zmax)
                    iso.Update()
                    mapper.SetInput(iso.GetOutput())
                else:
                    mapper.SetInput(data.GetOutput())
                mapper.SetLookupTable(self._ax._colormap)
                cax = self._ax._caxis
                if cax is None:
                    cax = sgrid.GetScalarRange()
                mapper.SetScalarRange(cax)
                mapper.Update()
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                if not contours:
                    self._set_shading(item, data, actor)
                self._set_actor_properties(item, actor)
                self._ax._renderer.AddActor(actor)
                self._ax._apd.AddInput(cut.GetOutput())

    def _add_contourslices(self, item):
        if DEBUG:
            print "Adding contours in slice planes"

        self._add_slices(item, contours=True)

    def _set_figure_size(self, fig):
        if DEBUG:
            print "Setting figure size"
        width, height = fig.getp('size')
        if width and height:
            # set figure width and height
            self._g.set_size(width, height)
        else:
            # use the default width and height in plotting package
            self._g.set_size(800, 600)
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
            name = 'Figure ' + str(fig.getp('number'))
            if DEBUG:
                print "creating figure %s in backend" % name

            fig._g = _VTKFigure(self, title=name)

        self._g = fig._g  # link for faster access
        return fig

    def _setup_axis(self, ax):
        self._set_limits(ax)
        self._set_daspect(ax)
        self._set_colormap(ax)
        self._set_caxis(ax)

        # Create a renderer for this axis and add it to the current
        # figures renderer window:
        ax._renderer = vtk.vtkRenderer()
        self._g.renwin.AddRenderer(ax._renderer)

        # Set the renderers background color:
        bgcolor = self._colors.get(ax.getp('bgcolor'), (1,1,1))
        ax._renderer.SetBackground(bgcolor)

        rect = ax.getp('viewport')
        if not rect:
            rect = (0,0,1,1)
        ax._renderer.SetViewport(rect)

        ax._renderer.RemoveAllViewProps()  # clear current scene
        #axshape = self.gcf().getp('axshape')
        #ax._renderer.SetPixelAspect(axshape[1], axshape[0])

        ax._apd = vtk.vtkAppendPolyData()

    def _fix_latex(self, legend):
        """Remove latex syntax a la $, \, {, } etc."""
        legend = legend.strip()
        # General fix of latex syntax (more readable)
        legend = legend.replace('**', '^')
        #legend = legend.replace('*', '')
        legend = legend.replace('$', '')
        legend = legend.replace('{', '')
        legend = legend.replace('}', '')
        legend = legend.replace('\\', '')
        return legend

    def _replot(self):
        """Replot all axes and all plotitems in the backend."""
        # NOTE: only the current figure (gcf) is redrawn.
        if DEBUG:
            print "Doing replot in backend"

        fig = self.gcf()
        # reset the plotting package instance in fig._g now if needed
        self._g.reset()

        self._set_figure_size(fig)

        nrows, ncolumns = fig.getp('axshape')
        for axnr, ax in fig.getp('axes').items():
            if ax.getp('numberofitems') == 0:
                continue
            self._ax = ax  # link for faster access
            if nrows != 1 or ncolumns != 1:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,axnr)
                pass
            self._setup_axis(ax)
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
                legend = self._fix_latex(item.getp('legend'))
                if legend:
                    # add legend to plot
                    pass

            self._set_axis_props(ax)

        if self.getp('show'):
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            pass
        self._g.display(show=self.getp('show'))

    def hardcopy(self, filename, **kwargs):
        """
        Supported extensions in VTK backend:

          * '.ps'  (PostScript)
          * '.eps' (Encapsualted PostScript)
          * '.pdf' (Portable Document Format)
          * '.jpg' (Joint Photographic Experts Group)
          * '.png' (Portable Network Graphics)
          * '.pnm' (Portable Any Map)
          * '.tif' (Tagged Image File Format)
          * '.bmp' (Bitmap Image)

        Optional arguments for JPEG output:

          quality     -- Set the quality of the resulting JPEG image. The
                         argument must be given as an integer between 0 and
                         100, where 100 gives the best quality (but also
                         the largest file). Default quality is 100.

          progressive -- Set whether to use progressive JPEG generation or
                         not. Default is False.

        Optional arguments for PostScript and PDF output:

          vector_file -- If True (default), the figure will be stored as a
                         vector file, i.e., using vtkGL2PSExporter instead
                         of vtkPostScriptWriter (requires VTK to be built
                         with GL2PS support). GL2PS gives much better
                         results, but at a cost of longer generation times
                         and larger files.

          orientation -- Set the orientation to either 'portrait' (default)
                         or 'landscape'. This option only has effect when
                         vector_file is True.

          raster3d    -- If True, this will write 3D props as raster images
                         while 2D props are rendered using vector graphic
                         primitives. Default is False. This option only has
                         effect when vector_file is True.

          compression -- If True, compression will be used when generating
                         PostScript or PDF output. Default is False (no
                         compression). This option only has effect when
                         vector_file is True.
        """
        if filename.startswith('.'):
            filename = 'tmp' + filename

        self.setp(**kwargs)
        color = self.getp('color')
        replot = kwargs.get('replot', True)

        if not self.getp('show'):  # don't render to screen
            self._g.renwin.OffScreenRenderingOn()

        if replot:
            self._replot()

        if DEBUG:
            print "Hardcopy to %s" % filename

        basename, ext = os.path.splitext(filename)
        if not ext:
            # no extension given, assume .ps:
            ext = '.ps'
            filename += ext

        jpeg_quality = int(kwargs.get('quality', 100))
        progressive = bool(kwargs.get('progressive', False))
        vector_file = bool(kwargs.get('vector_file', True))
        orientation = kwargs.get('orientation', 'portrait')
        raster3d = bool(kwargs.get('raster3d', False))
        compression = bool(kwargs.get('compression', False))

        landscape = False
        if orientation.lower() == 'landscape':
            landscape = True

        vector_file_formats = {'.ps': 0, '.eps': 1, '.pdf': 2, '.tex': 3}
        if vector_file and ext.lower() in vector_file_formats:
            exp = vtk.vtkGL2PSExporter()
            exp.SetRenderWindow(self._g.renwin)
            exp.SetFilePrefix(basename)
            exp.SetFileFormat(vector_file_formats[ext.lower()])
            exp.SetCompress(compression)
            exp.SetLandscape(landscape)
            exp.SetSortToBSP()
            #exp.SetSortToSimple()  # less expensive sort algorithm
            exp.DrawBackgroundOn()
            exp.SetWrite3DPropsAsRasterImage(raster3d)
            exp.Write()
        else:
            vtk_image_writers = {
                '.tif': vtk.vtkTIFFWriter(),
                '.tiff': vtk.vtkTIFFWriter(),
                '.bmp': vtk.vtkBMPWriter(),
                '.pnm': vtk.vtkPNMWriter(),
                '.png': vtk.vtkPNGWriter(),
                '.jpg': vtk.vtkJPEGWriter(),
                '.jpeg': vtk.vtkJPEGWriter(),
                '.ps': vtk.vtkPostScriptWriter(),
                '.eps': vtk.vtkPostScriptWriter(),  # gives a normal PS file
                }
            w2if = vtk.vtkWindowToImageFilter()
            w2if.SetInput(self._g.renwin)
            try:
                writer = vtk_image_writers[ext.lower()]
            except KeyError:
                raise TypeError(
                    "hardcopy: Extension '%s' is currently not supported." \
                    % ext)
            if ext.lower() in ('.jpg', '.jpeg'):
                writer.SetQuality(jpeg_quality)
                writer.SetProgressive(progressive)
            if ext.lower() in ('.tif', '.tiff'):
                # FIXME: allow to set compression mode for TIFF output
                # see http://www.vtk.org/doc/release/5.0/html/a02108.html
                pass
            writer.SetFileName(filename)
            writer.SetInputConnection(w2if.GetOutputPort())
            writer.Write()
        self._g.renwin.OffScreenRenderingOff()


    # reimplement color maps and other methods (if necessary) like clf,
    # closefig, and closefigs here.

    def hsv(self, m=64):
        lut = vtk.vtkLookupTable()
        lut.SetHueRange(0.0, 1.0)
        lut.SetSaturationRange(1.0, 1.0)
        lut.SetValueRange(1.0, 1.0)
        lut.SetNumberOfColors(m)
        lut.Build()
        return lut

    def gray(self, m=64):
        lut = vtk.vtkLookupTable()
        lut.SetHueRange(0.0, 0.0)
        lut.SetSaturationRange(0.0, 0.0)
        lut.SetValueRange(0.0, 1.0)
        lut.SetNumberOfColors(m)
        lut.Build()
        return lut

    def hot(self, m=64):
        lut = vtk.vtkLookupTable()
        inc = 0.01175
        lut.SetNumberOfColors(256)
        i = 0
        r = 0.0; g = 0.0; b = 0.0
        while r <= 1.:
            lut.SetTableValue(i, r, g, b, 1)
            r += inc;  i += 1
        r = 1.
        while g <= 1.:
            lut.SetTableValue(i, r, g, b, 1)
            g += inc;  i += 1
        g = 1.
        while b <= 1:
            if i == 256: break
            lut.SetTableValue(i, r, g, b, 1)
            b += inc;  i += 1
        lut.Build()
        return lut

    def flag(self, m=64):
        assert m%4==0, "flag: the number of colors must be a multiple of 4."
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfColors(m)
        # the last parameter alpha is set to 1 by default
        # in method declaration
        for i in range(0,m,4):
            lut.SetTableValue(i,1,0,0,1)   # red
            lut.SetTableValue(1+i,1,1,1,1) # white
            lut.SetTableValue(2+i,0,0,1,1) # blue
            lut.SetTableValue(3+i,0,0,0,1) # black
        lut.Build()
        return lut

    def jet(self, m=64):
        # blue, cyan, green, yellow, red, black
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfColors(m)
        lut.SetHueRange(0.667,0.0)
        lut.Build()
        return lut

    def spring(self, m=64):
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfColors(m)
        lut.SetHueRange(0.0, 0.17)
        lut.SetSaturationRange(0.5, 1.0)
        lut.SetValueRange(1.0, 1.0)
        lut.Build()
        return lut

    def summer(self, m=64):
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfColors(m)
        lut.SetHueRange(0.47, 0.17)
        lut.SetSaturationRange(1.0, 0.6)
        lut.SetValueRange(0.5, 1.0)
        lut.Build()
        return lut

    def winter(self, m=64):
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfColors(m)
        lut.SetHueRange(0.8, 0.42)
        lut.SetSaturationRange(1.0, 1.0)
        lut.SetValueRange(0.6, 1.0)
        lut.Build()
        return lut

    def autumn(self, m=64):
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfColors(m)
        lut.SetHueRange(0.0, 0.15)
        lut.SetSaturationRange(1.0, 1.0)
        lut.SetValueRange(1.0, 1.0)
        lut.Build()
        return lut

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


plt = VTKBackend()   # create backend instance
use(plt, globals())  # export public namespace of plt to globals()
backend = os.path.splitext(os.path.basename(__file__))[0][:-1]
