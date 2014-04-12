"""
This backend uses the Matlab package for plotting and mlabwrap (available at
http://sourceforge.net/projects/mlabwrap) for the connection between Python
and Matlab. To use this backend, one can run a script somefile.py like

  python somefile.py --SCITOOLS_easyviz_backend matlab

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = matlab

and then

  from scitools.std import *

or if just easyviz is needed

  from scitools.easyviz import *

REQUIREMENTS:

Matlab
mlabwrap (http://www.scipy.org/MlabWrap)

Tip:

- To run this backend in batch mode, set the -nodisplay option in the
environment variable MLABRAW_CMD_STR. This might give unexpected results
when using the hardcopy command (or the print command directly in Matlab).
However, this seems to be fixed by closing the figure window between each
call to hardcopy. A short example follows next (see also
http://www.mathworks.com/support/solutions/data/1-1A62W.html).

  from scitools.std import *
  x = linspace(0,5,31)
  for i in range(10):
      plot(x,cos(-0.1*i+x),ymin=-1.1,ymax=1.1)
      hardcopy('/tmp/img_%02d.eps' % i)
      close()
  movie('/tmp/img_%02d.eps')

"""

from __future__ import division

from .common import *
from scitools.globaldata import DEBUG, VERBOSE
from scitools.misc import check_if_module_exists

try:
    from scikits.mlabwrap import mlab
except ImportError:
    try:
        from mlabwrap import mlab
    except ImportError:
        # mlabwrap is not available
        check_if_module_exists('mlabwrap', msg='You need to install the mlabwrap package.', abort=False)


class MatlabBackend(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self._init()

    def _init(self, *args, **kwargs):
        """Perform initialization that is special for this backend."""

        #self.figure(self.getp('curfig'))
        pass

    def _set_scale(self, ax):
        """Set linear or logarithmic (base 10) axis scale."""
        if DEBUG:
            print "Setting scales"
        scale = ax.getp('scale')
        if scale == 'loglog':
            # use logarithmic scale on both x- and y-axis
            xscale = 'log'
            yscale = 'log'
        elif scale == 'logx':
            # use logarithmic scale on x-axis and linear scale on y-axis
            xscale = 'log'
            yscale = 'lin'
        elif scale == 'logy':
            # use linear scale on x-axis and logarithmic scale on y-axis
            xscale = 'lin'
            yscale = 'log'
        else:
            # use linear scale on both x- and y-axis
            xscale = 'lin'
            yscale = 'lin'
        self._axargs.extend(['XScale', xscale, 'YScale', yscale])

    def _set_labels(self, ax):
        """Add text labels for x-, y-, and z-axis."""
        if DEBUG:
            print "Setting labels"
        xlabel = ax.getp('xlabel')
        ylabel = ax.getp('ylabel')
        zlabel = ax.getp('zlabel')
        if xlabel:
            self._g.xlabel(xlabel)
        if ylabel:
            self._g.ylabel(ylabel)
        if zlabel:
            self._g.zlabel(zlabel)

    def _set_title(self, ax):
        """Add a title at the top of the axis."""
        if DEBUG:
            print "Setting title"
        title = self._fix_latex(ax.getp('title'))
        if title:
            self._g.title(title)

    def _set_limits(self, ax):
        """Set axis limits in x, y, and z direction."""
        if DEBUG:
            print "Setting axis limits"
        mode = ax.getp('mode')
        h = self._g.gca()
        if mode == 'auto':
            # let plotting package set 'nice' axis limits in the x, y,
            # and z direction. If this is not automated in the plotting
            # package, one can use the following limits:
            #xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            pass  #self._g.axis('auto', nout=0)
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.getp('xmin')
            xmax = ax.getp('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits
                #self._g.set_(h, 'XLim', [xmin,xmax], nout=0)
                self._axargs.extend(['XLim', [xmin,xmax]])
            else:
                # let plotting package set x-axis limits or use
                #xmin, xmax = ax.getp('xlim')
                pass

            ymin = ax.getp('ymin')
            ymax = ax.getp('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                #self._g.set_(h, 'YLim', [ymin,ymax], nout=0)
                self._axargs.extend(['YLim', [ymin,ymax]])
            else:
                # let plotting package set y-axis limits or use
                #ymin, ymax = ax.getp('ylim')
                pass

            zmin = ax.getp('zmin')
            zmax = ax.getp('zmax')
            if zmin is not None and zmax is not None:
                # set z-axis limits
                #self._g.set_(h, 'ZLim', [zmin,zmax], nout=0)
                self._axargs.extend(['ZLim', [zmin,zmax]])
            else:
                # let plotting package set z-axis limits or use
                #zmin, zmax = ax.getp('zlim')
                pass
            #self._g.axis('manual', nout=0)
        elif mode == 'tight':
            # set the limits on the axis to the range of the data. If
            # this is not automated in the plotting package, one can
            # use the following limits:
            #xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            self._g.axis('tight', nout=0)
        elif mode == 'fill':
            # not sure about this
            self._g.axis('fill', nout=0)

    def _set_position(self, ax):
        """Set axes position."""
        rect = ax.getp('viewport')
        if rect and ax.getp('pth') is None:
            # axes position is defined. In Matlab rect is defined as
            # [left,bottom,width,height], where the four parameters are
            # location values between 0 and 1 ((0,0) is the lower-left
            # corner and (1,1) is the upper-right corner).
            # NOTE: This can be different in the plotting package.
            #h = self._g.gca()
            #self._g.set_(h, 'Position', rect, nout=0)
            pass  # position of arbitrary axes are done in _replot

    def _set_daspect(self, ax):
        """Set data aspect ratio."""
        if ax.getp('daspectmode') == 'manual':
            dar = ax.getp('daspect')  # dar is a list (len(dar) is 3).
            self._axargs.extend(['DataAspectRatio', dar])
        else:
            #self._axargs.extend(['DataAspectRatioMode', 'auto'])
            pass

    def _set_axis_method(self, ax):
        method = ax.getp('method')
        if method == 'equal':
            # tick mark increments on the x-, y-, and z-axis should
            # be equal in size.
            self._g.axis('equal', nout=0)
        elif method == 'image':
            # same effect as axis('equal') and axis('tight')
            self._g.axis('image', nout=0)
        elif method == 'square':
            # make the axis box square in size
            self._axargs.extend(['DataAspectRatioMode', 'auto',
                                 'PlotBoxAspectRatio', [1,1,1]])
        elif method == 'normal':
            # full size axis box
            self._axargs.extend(['DataAspectRatioMode', 'auto',
                                 'PlotBoxAspectRatioMode', 'auto',
                                 'CameraViewAngleMode', 'auto'])
        elif method == 'vis3d':
            # freeze data aspect ratio when rotating 3D objects
            #self._g.axis('vis3d', nout=0)
            ax = self._g.gca()
            camva = self._g.get(ax, 'CameraViewAngle')
            dar = self._g.get(ax, 'DataAspectRatio')
            pbar = self._g.get(ax, 'PlotBoxAspectRatio')
            self._axargs.extend(['DataAspectRatio', dar,
                                 'PlotBoxAspectRatio', pbar,
                                 'CameraViewAngle', camva])

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
            self._axargs.extend(['YDir', 'reverse'])
        elif direction == 'xy':
            # use the default Cartesian axes form. The origin is at the
            # lower-left corner. The x-axis is vertical and numbered
            # from left to right, while the y-axis is vertical and
            # numbered from bottom to top.
            self._axargs.extend(['YDir', 'normal'])

    def _set_box(self, ax):
        """Turn box around axes boundary on or off."""
        if DEBUG:
            print "Setting box"
        if ax.getp('box'):
            # display box
            self._axargs.extend(['Box', 'on'])
        else:
            # do not display box
            self._axargs.extend(['Box', 'off'])

    def _set_grid(self, ax):
        """Turn grid lines on or off."""
        if DEBUG:
            print "Setting grid"
        state = None
        if ax.getp('grid'):
            # turn grid lines on
            state = 'on'
        else:
            # turn grid lines off
            state = 'off'
        self._axargs.extend(['XGrid', state, 'YGrid', state, 'ZGrid', state])

    def _set_hidden_line_removal(self, ax):
        """Turn on/off hidden line removal for meshes."""
        if DEBUG:
            print "Setting hidden line removal"
        if ax.getp('hidden'):
            # turn hidden line removal on
            pass  #self._g.hidden('on', nout=0)
        else:
            # turn hidden line removal off
            self._g.hidden('off', nout=0)

    def _set_colorbar(self, ax):
        """Add a colorbar to the axis."""
        if DEBUG:
            print "Setting colorbar"
        cbar = ax.getp('colorbar')
        if cbar.getp('visible'):
            # turn on colorbar
            cbar_title = cbar.getp('cbtitle')
            cbar_location = cbar.getp('cblocation')
            self._g.colorbar(cbar_location)
            # FIXME: what about the title?
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
                #cmin, cmax = [0,1]
                self._axargs.extend(['CLimMode', 'manual'])
            else:
                # set color axis scaling according to cmin and cmax
                self._axargs.extend(['CLim', [cmin, cmax]])
        else:
            # use autoranging for color axis scale
            self._axargs.extend(['CLimMode', 'auto'])

    def _set_colormap(self, ax):
        """Set the colormap."""
        if DEBUG:
            print "Setting colormap"
        cmap = ax.getp('colormap')
        # cmap is plotting package dependent
        if cmap is not None:
            self._g.colormap(cmap, nout=0)
        else:
            pass  #self._g.colormap('default', nout=0)

    def _set_view(self, ax):
        """Set viewpoint specification."""
        if DEBUG:
            print "Setting view"
        cam = ax.getp('camera')
        view = cam.getp('view')
        matlab_view = list(ravel(self._g.get(self._g.gca(), 'View')))
        if view == 2:
            # setup a default 2D view
            self._axargs.extend(['View', [0,90]])
        elif view == 3:
            az = cam.getp('azimuth')
            el = cam.getp('elevation')
            if az is None or el is None:
                # azimuth or elevation is not given. Set up a default
                # 3D view (az=-37.5 and el=30 is the default 3D view in
                # Matlab).
                self._axargs.extend(['View', [-37.5,30]])
            else:
                # set a 3D view according to az and el
                self._axargs.extend(['View', [az,el]])

            if cam.getp('cammode') == 'manual':
                # for advanced camera handling:
                roll = cam.getp('camroll')
                if roll is not None:
                    self._g.camroll(roll, nout=0)
                zoom = cam.getp('camzoom')
                #if zoom != 1:  # FIXME: Is this the right way?
                #    self._g.camzoom(zoom, nout=0)
                dolly = cam.getp('camdolly')
                #if dolly != (0,0,0):
                #    self._g.camdolly(list(dolly), nout=0)
                target = cam.getp('camtarget')
                position = cam.getp('campos')
                up_vector = cam.getp('camup')
                view_angle = cam.getp('camva')
                projection = cam.getp('camproj')
                #self._axargs.extend(['CameraTarget', target,
                #                     'CameraPosition', position,
                #                     'CameraPosition', position,
                #                     'CamearUpVector', up_vector,
                #                     'CameraViewAngle', view_angle,
                #                     'Projection', projection])

    def _set_axis_props(self, ax):
        if DEBUG:
            print "Setting axis properties"
        h = self._g.gca()
        self._axargs = [h]
        self._set_title(ax)
        self._set_scale(ax)
        self._set_axis_method(ax)  # should be called before _set_limits.
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
            self._axargs.extend(['Visible', 'on'])
        else:
            # turn off all axis labeling, tickmarks, and background
            self._axargs.extend(['Visible', 'off'])
        kwargs = {'nout': 0}
        self._g.set_(*self._axargs, **kwargs)

    def _get_linespecs(self, item):
        """
        Return the line marker, line color, line style, and
        line width of the item.
        """
        marker = item.getp('linemarker')
        color = item.getp('linecolor')
        style = item.getp('linetype')
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
            args = [x,y,z]
            func = self._g.plot3
        else:
            # no zdata, add a 2D curve:
            args = [x,y]
            func = self._g.plot

        if color:
            args.extend(['Color', color])
        if style:
            args.extend(['LineStyle', style])
        if marker:
            args.extend(['Marker', marker])
            if not style:
                args.extend(['LineStyle', 'none'])
        if width:
            args.extend(['LineWidth', float(width)])

        kwargs = {'nout': 0}
        func(*args, **kwargs)

    def _add_bar_graph(self, item, shading='faceted'):
        if DEBUG:
            print "Adding a bar graph"
        # get data:
        x = item.getp('xdata')
        y = item.getp('ydata')
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)

        edgecolor = item.getp('edgecolor')
        if not edgecolor:
            edgecolor = 'k'
            # FIXME: should use ax.getp('fgcolor') as the default edgecolor
        facecolor = item.getp('facecolor')
        if not facecolor:
            facecolor = color
        args = [x,y]

        barwidth = item.getp('barwidth')
        if barwidth is not None:
            args.append(barwidth)
        args.append('grouped')
        if facecolor:
            args.extend(['FaceColor', facecolor])
        if shading != 'faceted':
            args.extend(['EdgeColor', 'none'])
        elif edgecolor:
            args.extend(['EdgeColor', '%s' % edgecolor])
            # FIXME: a three-tuple [r,g,b] should also be supported

        kwargs = {'nout': 0}
        self._g.bar(*args, **kwargs)

        barticks = item.getp('barticks')
        if barticks is not None:
            #self._g.set_(self._g.gca(), 'XTickLabel', barticks, nout=0)
            if item.getp('rotated_barticks'):
                pass

    def _add_surface(self, item, shading='faceted'):
        if DEBUG:
            print "Adding a surface"
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = item.getp('zdata')           # scalar field
        c = item.getp('cdata')           # pseudocolor data (can be None)

        if item.getp('indexing') == 'ij' and \
               (shape(x) != shape(z) and shape(y) != shape(z)):
            x,y = ndgrid(x, y, sparse=False)
        args = [x,y,z]
        if c is not None:
            args.append(c)

        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)
        edgecolor = item.getp('edgecolor')
        facecolor = item.getp('facecolor')
        if edgecolor:
            args.extend(['EdgeColor', edgecolor])
        if facecolor:
            args.extend(['FaceColor', facecolor])
        if style:
            args.extend(['LineStyle', style])
        if marker:
            args.extend(['Marker', marker])
        if width:
            args.extend(['LineWidth', float(width)])

        if not shading == 'faceted' and not color:
            args.extend(['EdgeColor', 'none', 'FaceColor', shading])

        contours = item.getp('contours')
        if contours:
            # the current item is produced by meshc or surfc and we
            # should therefore add contours at the bottom:
            #self._add_contours(contours, placement='bottom')
            pass

        if item.getp('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            if contours:
                func = self._g.meshc
            else:
                func = self._g.mesh
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            if contours:
                func = self._g.surfc
            else:
                if item.getp('function') == 'pcolor':
                    func = self._g.pcolor
                else:
                    func = self._g.surf

        kwargs = {'nout': 0}
        if item.getp('function') in ['pcolor','meshc']:
            # pcolor needs special treatment since it has no support for
            # parameter/value pairs.
            if c is not None:
                extra_args = ['CData', c] + args[4:]
            else:
                extra_args = args[3:]
            h = func(x,y,z,nout=1)
            if extra_args:
                extra_args = [h] + extra_args
                self._g.set_(*extra_args, **kwargs)
        else:
            func(*args, **kwargs)

    def _add_contours(self, item, placement=None):
        # The placement keyword can be either None or 'bottom'. The
        # latter specifies that the contours should be placed at the
        # bottom (as in meshc or surfc).
        if DEBUG:
            print "Adding contours"
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = item.getp('zdata')           # scalar field

        if item.getp('indexing') == 'ij' and \
               (shape(x) != shape(z) and shape(y) != shape(z)):
            x,y = ndgrid(x, y, sparse=False)
        args = [x,y,z]

        filled = item.getp('filled')  # draw filled contour plot if True

        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            args.append(clevels)
        else:
            args.append(cvector)

        location = item.getp('clocation')
        if location == 'surface':
            # place the contours at the corresponding z level (contour3)
            func = self._g.contour3
        elif location == 'base':
            # standard contour plot
            if filled:
                func = self._g.contourf
            else:
                func = self._g.contour

        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)
        extra_args = []
        if style:
            extra_args.extend(['LineStyle', style])
        if width:
            extra_args.extend(['LineWidth', float(width)])

        kwargs = {'nout': 2}
        if item.getp('function') == 'contour3':
            # contour3 does not allow property-value pairs
            cs, h = func(*args, **kwargs)
            if color:
                extra_args.extend(['EdgeColor', color])
            if marker:
                extra_args.extend(['Marker', marker])
            args = [h] + extra_args
            kwargs = {'nout': 0}
            if len(args) > 1:
                self._g.set_(*args, **kwargs)
        else:
            if color:
                extra_args.extend(['Color', color])
            args.extend(extra_args)
            cs, h = func(*args, **kwargs)

        if item.getp('clabels'):
            # add labels on the contour curves
            self._g.clabel(cs, h, nout=0)

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
        u = item.getp('udata')
        v = item.getp('vdata')
        w = item.getp('wdata')
        # get line specifiactions (marker='.' means no marker):
        marker, color, style, width = self._get_linespecs(item)

        # scale the vectors according to this variable (scale=0 should
        # turn off automatic scaling):
        scale = item.getp('arrowscale')

        filled = item.getp('filledarrows') # draw filled arrows if True

        if z is not None and w is not None:
            # draw velocity vectors as arrows with components (u,v,w) at
            # points (x,y,z):
            z = squeeze(z)
            if item.getp('indexing') == 'ij' and \
                   (shape(x) != shape(u) and shape(y) != shape(u) and \
                    shape(z) != shape(u)):
                x,y,z = ndgrid(x, y, z, sparse=False)
            args = [x,y,z,u,v,w]
            func = self._g.quiver3
        else:
            # draw velocity vectors as arrows with components (u,v) at
            # points (x,y):
            if item.getp('indexing') == 'ij' and \
                   (shape(x) != shape(u) and shape(y) != shape(u)):
                x,y = ndgrid(x, y, sparse=False)
            args = [x,y,u,v]
            func = self._g.quiver
        args.append(scale)
        if filled:
            args.append('filled')
        if color:
            args.extend(['Color', color])
        if style:
            args.extend(['LineStyle', style])
        if marker:
            args.extend(['Marker', marker, 'ShowArrowHead', 'off'])
        if width:
            args.extend(['LineWidth', float(width)])
        kwargs = {'nout': 0}
        func(*args, **kwargs)

    def _add_streams(self, item):
        if DEBUG:
            print "Adding streams"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        # vector components:
        u, v, w = item.getp('udata'), item.getp('vdata'), item.getp('wdata')
        # starting positions for streams:
        sx = item.getp('startx')
        sy = item.getp('starty')
        sz = item.getp('startz')
        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)
        # TODO: implement linepecs

        args = [x,y,z,u,v,w,sx,sy,sz]
        if item.getp('tubes'):
            # draw stream tubes from vector data (u,v,w) at points (x,y,z)
            n = item.getp('n') # no points along the circumference of the tube
            scale = item.getp('tubescale')
            args.append([scale, n])
            func = self._g.streamtube
        elif item.getp('ribbons'):
            # draw stream ribbons from vector data (u,v,w) at points (x,y,z)
            width = item.getp('ribbonwidth')
            args.append(width)
            func = self._g.streamribbon
        else:
            if z is not None and w is not None:
                # draw stream lines from vector data (u,v,w) at points (x,y,z)
                pass
            else:
                # draw stream lines from vector data (u,v) at points (x,y)
                args = [x,y,u,v,sx,sy]
            func = self._g.streamline
        kwargs = {'nout': 0}
        func(*args, **kwargs)

    def _add_isosurface(self, item):
        if DEBUG:
            print "Adding a isosurface"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume
        c = item.getp('cdata')  # pseudocolor data
        isovalue = item.getp('isovalue')

        if item.getp('indexing') == 'ij' and \
               (shape(x) != shape(v) and shape(y) != shape(v) and \
                shape(z) != shape(v)):
            x,y,z = ndgrid(x,y,z,sparse=False)
        args = [x,y,z,v]
        if c is not None:
            args.append(c)
        args.append(isovalue)
        kwargs = {'nout': 0}
        self._g.isosurface(*args, **kwargs)

    def _add_slices(self, item):
        if DEBUG:
            print "Adding slices in a volume"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume

        if item.getp('indexing') == 'ij' and \
               (shape(x) != shape(v) and shape(y) != shape(v) and \
                shape(z) != shape(v)):
            x,y,z = ndgrid(x,y,z,sparse=False)
        sx, sy, sz = item.getp('slices')
        if rank(sz) == 2:
            # sx, sy, and sz defines a surface
            pass
        else:
            # sx, sy, and sz is either numbers or vectors with numbers
            pass
        self._g.slice_(x,y,z,v,sx,sy,sz,nout=0)

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

        if item.getp('indexing') == 'ij' and \
               (shape(x) != shape(v) and shape(y) != shape(v) and \
                shape(z) != shape(v)):
            x,y,z = ndgrid(x,y,z,sparse=False)
        args = [x,y,z,v,sx,sy,sz]

        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels per plane
        if cvector is None:
            # the contour levels are chosen automatically
            args.append(clevels)
        else:
            args.append(cvector)
        kwargs = {'nout': 0}
        self._g.contourslice(*args, **kwargs)

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

            fig._g = mlab
        self._g = fig._g # link for faster access

        #h = self._g.figure(self.getp('curfig'), nout=1)
        # hide figure until calling _replot:
        #self._g.set_(h, 'Visible', 'off', nout=0)
        return fig

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
        try:
            fig._g
        except:
            self.figure(self.getp('curfig'))
        h = self._g.figure(self.getp('curfig'), nout=1)
        # reset the plotting package instance in fig._g now if needed
        self._g.clf('reset')

        self._set_figure_size(fig)

        nrows, ncolumns = fig.getp('axshape')
        for axnr, ax in fig.getp('axes').items():
            if nrows != 1 or ncolumns != 1:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,axnr)
                axhandle = self._g.subplot(nrows,ncolumns,axnr,nout=1)
            else:
                rect = ax.getp('viewport')
                if rect and ax.getp('pth') is None:
                    axhandle = self._g.axes('position', rect, nout=1)
                else:
                    axhandle = self._g.gca()
            if ax.getp('numberofitems') > 0:
                hold_state = False
                legends = []
                plotitems = ax.getp('plotitems')
                plotitems.sort(self._cmpPlotProperties)
                for item in plotitems:
                    func = item.getp('function')
                    if isinstance(item, Line):
                        self._add_line(item)
                    elif isinstance(item, Bars):
                        self._add_bar_graph(item,shading=ax.getp('shading'))
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
                        legends.append(legend)
                    if ax.getp('numberofitems') > 1 and not hold_state:
                        self._g.hold(axhandle, 'on', nout=0)
                        hold_state = True

                if legends:
                    self._g.legend(*legends)

                if hold_state:
                    self._g.hold(axhandle, 'off', nout=0)

                self._set_axis_props(ax)
            else:
                self._g.set_(axhandle, 'Visible', 'off', nout=0)

        if self.getp('show'):
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            #h = self._g.gcf()
            #self._g.set_(h, 'Visible', 'on', nout=0)

    def hardcopy(self, filename, **kwargs):
        """
        Supported extensions:

          '.ps'  (PostScript)
          '.eps' (Encapsualted PostScript)
          '.jpg' (Joint Photographic Experts Group)
          '.png' (Portable Network Graphics)
          '.pdf' (Portable Document Format)
          '.pbm' (Portable Bitmap)
          '.pgm' (Portable Graymap)
          '.ppm' (Portable Pixmap)
          '.tif' (Tagged Image File Format)
          '.hgl' (Hewlett-Packard Graphics Language)
          '.ai'  (Adobe Illustrator file)
          '.pcx' (Paintbrush 24-bit file)
          '.bmp' (Bitmap Image)

        If `filename` contains just the file extension, say ``.png``,
        it is saved to ``tmp.png``.

        Optional arguments:

          renderer    -- Specify which renderer to use. Available renderers
                         are 'painters', 'zbuffer', and 'opengl'. If not
                         specified, the default renderer in Matlab is chosen.
                         (This option is not available when running Matlab
                         with the -nodisplay argument.)
          color       -- If True, create a plot with colors. If False
                         (default), create a plot in black and white. This
                         option is only available for PostScript output.
          pslevel     -- Set the PostScript level to be used. By default,
                         level 1 PostScript is used, while pslevel=2 will use
                         PostScript level 2 instead.
          raw         -- If True, this will use raw format on PBM, PGM,
                         and PPM files. If False (default), a plain text
                         format is used.
          quality     -- Set the quality level of a JPEG image. Must be an
                         integer between 0 and 100, where 100 gives the best
                         quality but also the lowest compression. The default
                         quality level is 75.
          tiffcompression -- Set whether to use compression or no compression
                         (default) on a TIFF file.

        Example on how to use the backend directly to save a hardcopy of
        the current figure:

        >>> g = get_backend()
        >>> g.print_(g.gcf(), '-deps', 'foo.eps')
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

        renderer = kwargs.get('renderer', None)
        pscolor = color and 'c' or ''
        quality = kwargs.get('quality', 75)
        pslevel = kwargs.get('pslevel', '')
        tiffcompression = kwargs.get('tiffcompression', False)
        tiffcompression = tiffcompression and '' or 'nocompression'
        raw = kwargs.get('raw', False)
        raw = raw and 'raw' or ''

        # convert table (extension --> device):
        ext2dev = {
            '': '-dps%s%s' % (pscolor,pslevel),
            '.ps': '-dps%s%s' % (pscolor,pslevel),
            '.eps': '-deps%s%s' % (pscolor,pslevel),
            '.jpg': '-djpeg%d' % int(quality),
            '.jpeg': '-djpeg%d' % int(quality),
            '.jpe': '-djpeg%d' % int(quality),
            '.png': '-dpng',
            '.hgl': '-dhpgl',
            '.ai': '-dill',
            '.tif': '-dtiff%s' % tiffcompression,
            '.tiff': '-dtiff%s' % tiffcompression,
            '.pbm': '-dpbm%s' % raw,
            '.ppm': '-dpgm%s' % raw,
            '.ppm': '-dppm%s' % raw,
            '.pdf': '-dpdf',
            '.pcx': '-dpcx24b',
            '.bmp': '-dbmp',
            '.dib': '-dbmp',
            }
        basename, ext = os.path.splitext(filename)
        device = ext2dev[ext]

        h = self._g.gcf()
        args = [h,device,filename]
        if renderer is not None:
            args.append('-%s' % renderer)
        kwargs = {'nout': 0}
        self._g.print_(*args, **kwargs)

    # reimplement color maps and other methods (if necessary) like clf,
    # closefig, and closefigs here.

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
        #del self._g
        BaseClass.closefigs(self)

    # Colormap methods:
    def hsv(self, m=64):
        return mlab.hsv(m)

    def hot(self, m=64):
        return mlab.hot(m)

    def gray(self, m=64):
        return mlab.gray(m)

    def bone(self, m=64):
        return mlab.bone(m)

    def copper(self, m=64):
        return mlab.copper(m)

    def pink(self, m=64):
        return mlab.pink(m)

    def white(self, m=64):
        return mlab.white(m)

    def flag(self, m=64):
        return mlab.flag(m)

    def lines(self, m=64):
        return mlab.lines(m)

    def colorcube(self, m=64):
        return mlab.colorcube(m)

    def vga(self, m=64):
        return mlab.vga(m)

    def jet(self, m=64):
        return mlab.jet(m)

    def prism(self, m=64):
        return mlab.prism(m)

    def cool(self, m=64):
        return mlab.cool(m)

    def autumn(self, m=64):
        return mlab.autumn(m)

    def spring(self, m=64):
        return mlab.spring(m)

    def winter(self, m=64):
        return mlab.winter(m)

    def summer(self, m=64):
        return mlab.summer(m)


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


plt = MatlabBackend()  # create backend instance
use(plt, globals())      # export public namespace of plt to globals()
backend = os.path.splitext(os.path.basename(__file__))[0][:-1]
