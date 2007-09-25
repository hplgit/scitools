"""
This is a template file for writing new backends. It is a fully functional
backend, but no output is produced. One can specify this backend by

  python somefile.py --SCITOOLS_easyviz_backend template

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = template

and then

  from scitools.all import *

or if just easyviz is needed

  from scitools.easyviz import *

When writing a new backend, one can copy this file to xxx_.py (note the
underscore), where 'xxx' is the name of the new backend. Then replace all
instances of 'template' with 'xxx' and start implementing the class
methods below. The most important methods are figure, _replot, and hardcopy.

REQUIREMENTS:

<fill in requirements for backend>

"""

from __future__ import division

from common import *
from scitools.globaldata import DEBUG, VERBOSE
from scitools.misc import test_if_module_exists as check
from scitools.numpyutils import allclose

check('vtk', msg='You need to install the VTK package.')
import vtk
import os

check('Tkinter', msg='You need to install the Tkinter package.')
import Tkinter
try:
    import vtkTkRenderWidget
except:
    from vtk.tk import vtkTkRenderWidget


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
        title = ax.getp('title')
        if title:
            pass  # set title
    
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
        color = self._colors.get(item.getp('linecolor'), (0,0,1))
        if color is None:
            color = (0,0,1)
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

    def _create_2D_scalar_grid(self, item):
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = asarray(item.getp('zdata'))  # scalar field
        c = item.getp('cdata')           # pseudocolor data
        if c is None:
            c = z.copy()
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
        if function in ['contour', 'pcolor']:
            z *= 0
        if function in ['meshc', 'surfc'] and isinstance(item, Contours):
            # this item is the Contours object beneath the surface in
            # a meshc or surfc plot.
            z *= 0
            z += self._scaled_limits[4]
        
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(item.getp('numberofpoints'))
        scalars = vtk.vtkFloatArray()
        scalars.SetNumberOfTuples(item.getp('numberofpoints'))
        scalars.SetNumberOfComponents(1)
        ind = 0
        nx, ny = shape(z)
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

        sgrid = self._create_2D_scalar_grid(item)
        
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
        x = item.getp('xdata')  # grid component in x-direction
        y = item.getp('ydata')  # grid component in y-direction
        z = item.getp('zdata')  # scalar field

        filled = item.getp('filled')  # draw filled contour plot if True

        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            pass

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
            self._g.set_size(width, height)
        else:
            # use the default width and height in plotting package
            self._g.set_size(800, 600)
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
            name = 'Figure ' + str(self.getp('curfig'))
            if DEBUG:
                print "creating figure %s in backend" % name

            fig._g = _VTKFigure(self, title=name)
            
        self._g = fig._g # link for faster access

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
                legend = item.getp('legend')
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
        Supported extensions: <fill in extensions for this backend>
        """
        self.setp(**kwargs)
        color = self.getp('color')
        replot = kwargs.get('replot', True)
        if replot:
            self._replot()

        if DEBUG:
            print "Hardcopy to %s" % filename

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
