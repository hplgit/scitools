"""
With this backend one can create Matlab scripts (M-files) with Matlab
commands from scripts with Easyviz commands. The interactive and show
attributes are by default turned off in this backend and one should
therefore call either show or hardcopy (both calling _replot) before
saving the Matlab script with a call to save_m. To use this backend, one
can run a script somefile.py like

  python somefile.py --SCITOOLS_easyviz_backend matlab2

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = matlab2

and then

  from scitools.std import *

or if just easyviz is needed

  from scitools.easyviz import *

REQUIREMENTS:

No requirements

EXAMPLES:

We start with a simple example using the plot command:

>>> from scitools.std import *
>>> x = linspace(-2,2,5)
>>> plot(x,x**2,'b-s',title='Simple plot')
[<scitools.easyviz.common.Line object at 0xb7de244c>]
>>> print get_script()

>>>

As we can see, the result is no output. This is because the _replot method
has not been called yet. However, we don't need to call this method
explicitly. Instead we should call either show or hardcopy (both of which
calls _replot). Here we use show:

>>> show()
>>> print get_script()
figure(1)
clf('reset')
ax1 = gca;
x = [-2.0, -1.0, 0.0, 1.0, 2.0];
y = [4.0, 1.0, 0.0, 1.0, 4.0];
plot(x,y,'Color','b','LineStyle','-','Marker','s')
title('Simple plot'),...
set(gca, 'XScale', 'lin', 'YScale', 'lin'),...
axis normal,...
axis auto,...
axis xy,...
hidden on,...
caxis auto,...
view(2),...
xlabel(''),ylabel(''),zlabel(''),...
box on,...
grid off,...
axis on,...

>>>

We can now store these commands in a Matlab script by calling the save_m
function:

>>> save_m('mytest.m')

In this case, the file mytest.m will be placed in the current working
directory and we can then run the file in Matlab, e.g., with the following
statement:

>>> os.system("matlab -nojvm -nosplash -r mytest")

Note that we skip the extension of the file name (.m). To get back to the
Python prompt, we must first exit Matlab.

Now we create a contour plot in combination with a quiver plot:

>>> reset()  # remove the previous Matlab commands
>>> xx, yy = ndgrid(linspace(-3,3,31), linspace(-3,3,31), sparse=False)
>>> zz = peaks(xx, yy)
>>> contour(xx,yy,zz,12,hold='on')
>>> uu, vv = gradient(zz)
>>> quiver(xx,yy,uu,vv,hold='off')
>>> hardcopy('tmp0.ps',color=True)
>>> save_m('mytest2.m')

Here, we begin by calling reset(). This ensures that the string with the
Matlab commands is empty before we start calling different plotting
commands. After calling contour and quiver, we use the hardcopy command to
store the plot to a PostScript file. As mentioned above, hardcopy calls
_replot so there is no need to call show in this case. At the end we call
save_m to store the Matlab commands in the file mytest2.m. We can then run
the script as we did above:

>>> os.system("matlab -nojvm -nosplash -r 'mytest2;quit'")

In this case, we will be brought back to the Python prompt once Matlab
has stored the plot in the file tmp0.ps.

NOTES:

- 3D arrays are currently not supported.
"""

from __future__ import division

from .common import *
from scitools.globaldata import DEBUG, VERBOSE
from scitools.misc import findprograms

import os
import tempfile


MATLAB_CMD_STR = os.environ.get('MATLAB_CMD_STR', "matlab -nosplash -nojvm")
has_matlab = findprograms('matlab')


class Matlab2Backend(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self._init()

    def _init(self, *args, **kwargs):
        """Perform initialization that is special for this backend."""

        self.figure(self.getp('curfig'))
        # set show and interactive to False as deafult:
        self.setp(show=False, interactive=False)
        self._script = ""

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
        self._script += "set(gca, 'XScale', '%s', 'YScale', '%s'),...\n" % \
                        (xscale,yscale)

    def _set_labels(self, ax):
        """Add text labels for x-, y-, and z-axis."""
        if DEBUG:
            print "Setting labels"
        xlabel = ax.getp('xlabel')
        ylabel = ax.getp('ylabel')
        zlabel = ax.getp('zlabel')
        self._script += "xlabel('%s'),ylabel('%s'),zlabel('%s'),...\n" % \
                        (xlabel,ylabel,zlabel)

    def _set_title(self, ax):
        """Add a title at the top of the axis."""
        if DEBUG:
            print "Setting title"
        title = self._fix_latex(ax.getp('title'))
        self._script += "title('%s'),...\n" % title

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
            self._script += "axis auto,...\n"
        elif mode == 'manual':
            # (some) axis limits are frozen
            xmin = ax.getp('xmin')
            xmax = ax.getp('xmax')
            if xmin is not None and xmax is not None:
                # set x-axis limits
                self._script += "xlim([%s,%s]),...\n" % (xmin,xmax)
            else:
                # let plotting package set x-axis limits or use
                #xmin, xmax = ax.getp('xlim')
                #self._script += "xlim auto,...\n" % (xmin,xmax)
                pass

            ymin = ax.getp('ymin')
            ymax = ax.getp('ymax')
            if ymin is not None and ymax is not None:
                # set y-axis limits
                self._script += "ylim([%s,%s]),...\n" % (ymin,ymax)
            else:
                # let plotting package set y-axis limits or use
                #ymin, ymax = ax.getp('ylim')
                #self._script += "ylim auto,...\n"
                pass

            zmin = ax.getp('zmin')
            zmax = ax.getp('zmax')
            if zmin is not None and zmax is not None:
                # set z-axis limits
                self._script += "zlim([%s,%s]),...\n" % (zmin,zmax)
            else:
                # let plotting package set z-axis limits or use
                #zmin, zmax = ax.getp('zlim')
                #self._script += "zlim auto,..."
                pass
        elif mode == 'tight':
            # set the limits on the axis to the range of the data. If
            # this is not automated in the plotting package, one can
            # use the following limits:
            #xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            self._script += "axis tight,...\n"
        elif mode == 'fill':
            # not sure about this
            self._script += "axis fill,...\n"

    def _set_position(self, ax):
        """Set axes position."""
        rect = ax.getp('viewport')
        if rect and ax.getp('pth') is None:
            # axes position is defined. In Matlab rect is defined as
            # [left,bottom,width,height], where the four parameters are
            # location values between 0 and 1 ((0,0) is the lower-left
            # corner and (1,1) is the upper-right corner).
            # NOTE: This can be different in the plotting package.
            pass  # position of arbitrary axes are done in _replot

    def _set_daspect(self, ax):
        """Set data aspect ratio."""
        if ax.getp('daspectmode') == 'manual':
            dar = ax.getp('daspect')  # dar is a list (len(dar) is 3).
            self._script += "daspect([%s,%s,%s]),...\n" % tuple(dar)
        else:
            #self._script += "daspect auto,...\n"
            pass

    def _set_axis_method(self, ax):
        method = ax.getp('method')
        if method == 'equal':
            # tick mark increments on the x-, y-, and z-axis should
            # be equal in size.
            self._script += "axis equal,...\n"
        elif method == 'image':
            # same effect as axis('equal') and axis('tight')
            self._script += "axis image,...\n"
        elif method == 'square':
            # make the axis box square in size
            self._script += "axis square,...\n"
        elif method == 'normal':
            # full size axis box
            self._script += "axis normal,...\n"
        elif method == 'vis3d':
            # freeze data aspect ratio when rotating 3D objects
            self._script += "axis vis3d,...\n"

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
            self._script += "axis ij,...\n"
        elif direction == 'xy':
            # use the default Cartesian axes form. The origin is at the
            # lower-left corner. The x-axis is vertical and numbered
            # from left to right, while the y-axis is vertical and
            # numbered from bottom to top.
            self._script += "axis xy,...\n"

    def _set_box(self, ax):
        """Turn box around axes boundary on or off."""
        if DEBUG:
            print "Setting box"
        if ax.getp('box'):
            # display box
            self._script += "box on,...\n"
        else:
            # do not display box
            self._script += "box off,...\n"

    def _set_grid(self, ax):
        """Turn grid lines on or off."""
        if DEBUG:
            print "Setting grid"
        if ax.getp('grid'):
            # turn grid lines on
            self._script += "grid on,...\n"
        else:
            # turn grid lines off
            self._script += "grid off,...\n"

    def _set_hidden_line_removal(self, ax):
        """Turn on/off hidden line removal for meshes."""
        if DEBUG:
            print "Setting hidden line removal"
        if ax.getp('hidden'):
            # turn hidden line removal on
            self._script += "hidden on,...\n"
        else:
            # turn hidden line removal off
            self._script += "hidden off,...\n"

    def _set_colorbar(self, ax):
        """Add a colorbar to the axis."""
        if DEBUG:
            print "Setting colorbar"
        cbar = ax.getp('colorbar')
        if cbar.getp('visible'):
            # turn on colorbar
            cbar_title = cbar.getp('cbtitle')
            cbar_location = cbar.getp('cblocation')
            self._script += "colorbar('%s'),..." % cbar_location
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
                self._script += "caxis manual,...\n"
            else:
                # set color axis scaling according to cmin and cmax
                self._script += "caxis([%s,%s]),...\n" % (cmin, cmax)
        else:
            # use autoranging for color axis scale
            self._script += "caxis auto,...\n"

    def _set_colormap(self, ax):
        """Set the colormap."""
        if DEBUG:
            print "Setting colormap"
        cmap = ax.getp('colormap')
        # cmap is plotting package dependent
        if cmap is not None:
            self._script += "colormap %s,...\n" % cmap
        else:
            pass  #self._script += "colormap default,...\n"

    def _set_view(self, ax):
        """Set viewpoint specification."""
        if DEBUG:
            print "Setting view"
        cam = ax.getp('camera')
        view = cam.getp('view')
        if view == 2:
            # setup a default 2D view
            self._script += "view(2),...\n"
        elif view == 3:
            az = cam.getp('azimuth')
            el = cam.getp('elevation')
            if az is None or el is None:
                # azimuth or elevation is not given. Set up a default
                # 3D view (az=-37.5 and el=30 is the default 3D view in
                # Matlab).
                self._script += "view(3),...\n"
            else:
                # set a 3D view according to az and el
                self._script += "view([%s,%s]),...\n" % (az,el)

            if cam.getp('cammode') == 'manual':
                # for advanced camera handling:
                roll = cam.getp('camroll')
                #if roll is not None:
                #    self._g.camroll(roll, nout=0)
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
            self._script += "axis on,...\n"
        else:
            # turn off all axis labeling, tickmarks, and background
            self._script += "axis off,...\n"

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

        cmd = ""
        cmd += "x = %s;\n" % list(x)
        cmd += "y = %s;\n" % list(y)
        if z is not None:
            # zdata is given, add a 3D curve:
            cmd += "z = %s;\n" % list(z)
            cmd += "plot3(x,y,z"
        else:
            # no zdata, add a 2D curve:
            cmd += "plot(x,y"

        if color:
            cmd += ",'Color','%s'" % color
        if style:
            cmd += ",'LineStyle','%s'" % style
        if marker:
            cmd += ",'Marker','%s'" % marker
            if not style:
                cmd += ",'LineStyle','none'"
        if width:
            cmd += ",'LineWidth',%g" % float(width)

        cmd += ")\n"
        self._script += cmd

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
            # FIXME: edgecolor should be ax.getp('fgcolor') as default
        facecolor = item.getp('facecolor')
        if not facecolor:
            facecolor = color

        cmd = ""
        cmd += "x = %s;\n" % list(x)
        if rank(y) == 2:
            cmd += "y = %s;\n" % str(y.tolist()).replace('],', '];')
        else:
            cmd += "y = %s;\n" % list(y)
        cmd += "bar(x,y"

        barwidth = item.getp('barwidth')
        if barwidth is not None:
            cmd += ",%s" % barwidth
        cmd += ",'grouped'"
        if facecolor:
            cmd += ",'FaceColor', '%s'" % facecolor
            # FIXME: Color can also be a three-tuple [r,g,b]
        if shading != 'faceted':
            cmd += ",'EdgeColor', 'none'"
        elif edgecolor:
            cmd += ",'EdgeColor', '%s'" % edgecolor
        cmd += ")\n"
        self._script += cmd

        barticks = item.getp('barticks')
        if barticks is not None:
            barticks = '; '.join(["'%s'" % s for s in barticks])
            self._script += "set(gca, 'XTickLabel', [%s])\n" % barticks
            if item.getp('rotated_barticks'):
                pass

    def _add_surface(self, item, shading='faceted'):
        if DEBUG:
            print "Adding a surface"
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = asarray(item.getp('zdata'))  # scalar field
        c = item.getp('cdata')           # pseudocolor data (can be None)

        cmd = ""
        if item.getp('indexing') == 'ij' and \
               (shape(x) != shape(z) and shape(y) != shape(z)):
            x,y = ndgrid(x,y,sparse=False)
        if shape(x) != shape(z) and shape(y) != shape(z):
            cmd += "x = %s;\n" % list(x)
            cmd += "y = %s;\n" % list(y)
            if item.getp('indexing') == 'ij':
                cmd += "[X,Y] = ndgrid(x,y);\n"
            else:
                cmd += "[X,Y] = meshgrid(x,y);\n"
        else:
            cmd += "X = %s;\n" % str(x.tolist()).replace('],', '];')
            cmd += "Y = %s;\n" % str(y.tolist()).replace('],', '];')
        cmd += "Z = %s;\n" % str(z.tolist()).replace('],', '];')
        if c is not None:
            c = asarray(c)
            cmd += "C = %s;\n" % str(c.tolist()).replace('],', '];')

        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)
        edgecolor = item.getp('edgecolor')
        facecolor = item.getp('facecolor')
        args = ""
        if edgecolor:
            args += ",'EdgeColor','%s'" % edgecolor
            # FIXME: Color can also be a three-tuple [r,g,b]
        if facecolor:
            args += ",'FaceColor','%s'" % facecolor
        if style:
            args += ",'LineStyle','%s'" % style
        if marker:
            args += ",'Marker','%s'" % marker
        if width:
            args += ",'LineWidth',%s" % float(width)

        if shading != 'faceted' and not color:
            args += ",'EdgeColor','none','FaceColor','%s'" % shading

        contours = item.getp('contours')
        if contours:
            # the current item is produced by meshc or surfc and we
            # should therefore add contours at the bottom:
            #self._add_contours(contours, placement='bottom')
            pass

        if item.getp('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            if contours:
                func = 'meshc'
            else:
                func = 'mesh'
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            if contours:
                func = 'surfc'
            else:
                if item.getp('function') == 'pcolor':
                    func = 'pcolor'
                else:
                    func = 'surf'

        if func in ['pcolor','meshc']:
            # pcolor needs special treatment since it has no support for
            # parameter/value pairs.
            cmd += "h = %s(X,Y,Z);\n" % func
            if c is not None:
                args += ",'CData', 'C'"
            if args:
                cmd += "set(h%s),...\n" % args
        else:
            if c is not None:
                args = ",C" + args
            cmd += "%s(X,Y,Z%s),...\n" % (func,args)

        self._script += cmd

    def _add_contours(self, item, placement=None):
        # The placement keyword can be either None or 'bottom'. The
        # latter specifies that the contours should be placed at the
        # bottom (as in meshc or surfc).
        if DEBUG:
            print "Adding contours"
        x = squeeze(item.getp('xdata'))  # grid component in x-direction
        y = squeeze(item.getp('ydata'))  # grid component in y-direction
        z = asarray(item.getp('zdata'))  # scalar field

        cmd = ""
        if item.getp('indexing') == 'ij' and \
               (shape(x) != shape(z) and shape(y) != shape(z)):
            x,y = ndgrid(x,y,sparse=False)
        if shape(x) != shape(z) and shape(y) != shape(z):
            cmd += "x = %s;\n" % list(x)
            cmd += "y = %s;\n" % list(y)
            if item.getp('indexing') == 'ij':
                cmd += "[X,Y] = ndgrid(x,y);\n"
            else:
                cmd += "[X,Y] = meshgrid(x,y);\n"
        else:
            cmd += "X = %s;\n" % str(x.tolist()).replace('],', '];')
            cmd += "Y = %s;\n" % str(y.tolist()).replace('],', '];')
        cmd += "Z = %s;\n" % str(z.tolist()).replace('],', '];')

        filled = item.getp('filled')  # draw filled contour plot if True

        args = ""
        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            #cvector =
            args += ",%s" % clevels
        else:
            args += ",%s" % list(cvector)

        location = item.getp('clocation')
        if location == 'surface':
            # place the contours at the corresponding z level (contour3)
            func = "contour3"
        elif location == 'base':
            # standard contour plot
            if filled:
                func = "contourf"
            else:
                func = "contour"

        # get line specifiactions:
        marker, color, style, width = self._get_linespecs(item)
        extra_args = ""
        if style:
            extra_args += ",'LineStyle', '%s'" % style
        if width:
            extra_args += ",'LineWidth', %s" % float(width)

        if item.getp('function') == 'contour3':
            # contour3 does not allow property-value pairs
            cmd += "[cs,h] = %s(X,Y,Z%s);\n" % (func,args)
            if color:
                extra_args += ",'EdgeColor', '%s'" % color
                # FIXME: What if color is a three-tuple [r,g,b]?
            if marker:
                extra_args += ",'Marker', '%s'" % marker
            if extra_args:
                cmd += "set(h%s),...\n" % extra_args
        else:
            if color:
                extra_args += ",'Color', '%s'" % color
                # FIXME: What if color is a three-tuple [r,g,b]?
            args += extra_args
            cmd += "[cs,h] = %s(X,Y,Z%s);\n" % (func,args)

        if item.getp('clabels'):
            # add labels on the contour curves
            cmd += "clabel(cs, h),...\n"

        self._script += cmd

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
        u = asarray(item.getp('udata'))
        v = asarray(item.getp('vdata'))
        w = item.getp('wdata')
        # get line specifiactions (marker='.' means no marker):
        marker, color, style, width = self._get_linespecs(item)

        # scale the vectors according to this variable (scale=0 should
        # turn off automatic scaling):
        scale = item.getp('arrowscale')

        filled = item.getp('filledarrows') # draw filled arrows if True

        cmd = ""
        if z is not None and w is not None:
            z = squeeze(z)
            w = asarray(w)
            # draw velocity vectors as arrows with components (u,v,w) at
            # points (x,y,z):
            if item.getp('indexing') == 'ij' and \
                   (shape(x) != shape(u) and shape(y) != shape(u) and \
                    shape(z) != shape(u)):
                x,y,z = ndgrid(x,y,z,sparse=False)
            if shape(x) != shape(u) and shape(y) != shape(u) and \
               shape(z) != shape(u):
                cmd += "x = %s;\n" % list(x)
                cmd += "y = %s;\n" % list(y)
                cmd += "z = %s;\n" % list(z)
                if item.getp('indexing') == 'ij':
                    cmd += "[X,Y,Z] = ndgrid(x,y,z);\n"
                else:
                    cmd += "[X,Y,Z] = meshgrid(x,y,z);\n"
            else:
                cmd += "X = %s;\n" % str(x.tolist()).replace('],', '];')
                cmd += "Y = %s;\n" % str(y.tolist()).replace('],', '];')
                cmd += "Z = %s;\n" % str(z.tolist()).replace('],', '];')
            cmd += "U = %s;\n" % str(u.tolist()).replace('],', '];')
            cmd += "V = %s;\n" % str(v.tolist()).replace('],', '];')
            cmd += "W = %s;\n" % str(w.tolist()).replace('],', '];')
            args = "X,Y,Z,U,V,W"
            func = "quiver3"
        else:
            # draw velocity vectors as arrows with components (u,v) at
            # points (x,y):
            if item.getp('indexing') == 'ij' and \
                   (shape(x) != shape(u) and shape(y) != shape(u)):
                x,y = ndgrid(x,y,sparse=False)
            if shape(x) != shape(u) and shape(y) != shape(u):
                cmd += "x = %s;\n" % list(x)
                cmd += "y = %s;\n" % list(y)
                if item.getp('indexing') == 'ij':
                    cmd += "[X,Y] = ndgrid(x,y);\n"
                else:
                    cmd += "[X,Y] = meshgrid(x,y);\n"
            else:
                cmd += "X = %s;\n" % str(x.tolist()).replace('],', '];')
                cmd += "Y = %s;\n" % str(y.tolist()).replace('],', '];')
            cmd += "U = %s;\n" % str(u.tolist()).replace('],', '];')
            cmd += "V = %s;\n" % str(v.tolist()).replace('],', '];')
            args = "X,Y,U,V"
            func = "quiver"
        args += ",%s" % float(scale)
        if filled:
            args += ",'filled'"
        if color:
            args += ",'Color','%s'" % color
            # FIXME: What if color is a three-tuple [r,g,b]?
        if style:
            args += ",'LineStyle','%s'" % style
        if marker:
            args += ",'Marker','%s','ShowArrowHead','off'" % marker
        if width:
            args += ",'LineWidth', %s" % float(width)
        cmd += "%s(%s),...\n" % (func,args)
        self._script += cmd

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
            #func = self._g.streamtube
        elif item.getp('ribbons'):
            # draw stream ribbons from vector data (u,v,w) at points (x,y,z)
            width = item.getp('ribbonwidth')
            args.append(width)
            #func = self._g.streamribbon
        else:
            if z is not None and w is not None:
                # draw stream lines from vector data (u,v,w) at points (x,y,z)
                pass
            else:
                # draw stream lines from vector data (u,v) at points (x,y)
                args = [x,y,u,v,sx,sy]
            #func = self._g.streamline
        kwargs = {'nout': 0}
        #func(*args, **kwargs)

    def _add_isosurface(self, item):
        if DEBUG:
            print "Adding a isosurface"
        # grid components:
        x = squeeze(item.getp('xdata'))
        y = squeeze(item.getp('ydata'))
        z = squeeze(item.getp('zdata'))
        v = asarray(item.getp('vdata'))  # volume
        c = item.getp('cdata')  # pseudocolor data
        isovalue = item.getp('isovalue')

        cmd = ""
        if item.getp('indexing') == 'ij' and \
               (shape(x) != shape(v) and shape(y) != shape(v) and \
                shape(z) != shape(v)):
            x,y,z = ndgrid(x,y,z,sparse=False)
        if shape(x) != shape(v) and shape(y) != shape(v) and \
               shape(z) != shape(v):
            cmd += "x = %s;\n" % list(x)
            cmd += "y = %s;\n" % list(y)
            cmd += "z = %s;\n" % list(z)
            if item.getp('indexing') == 'ij':
                cmd += "[X,Y,Z] = ndgrid(x,y,z);\n"
            else:
                cmd += "[X,Y,Z] = meshgrid(x,y,z);\n"
        else:
            cmd += "X = %s;\n" % str(x.tolist()).replace('],', '];')
            cmd += "X = reshape(X,%d,%d,%d);\n" % shape(v)
            cmd += "Y = %s;\n" % str(y.tolist()).replace('],', '];')
            cmd += "Y = reshape(Y,%d,%d,%d);\n" % shape(v)
            cmd += "Z = %s;\n" % str(z.tolist()).replace('],', '];')
            cmd += "Z = reshape(Z,%d,%d,%d);\n" % shape(v)
        cmd += "V = %s;\n" % str(v.tolist()).replace('],', '];')
        cmd += "V = reshape(V,%d,%d,%d);\n" % shape(v)
        args = "X,Y,Z,V"
        if c is not None:
            c = asarray(c)
            cmd += "C = %s;\n" % str(c.tolist()).replace('],', '];')
            cmd += "C = reshape(C,%d,%d,%d);\n" % shape(v)
            args += ",C"
        args += ",%s" % float(isovalue)
        cmd += "isosurface(%s),...\n" % args
        self._script += cmd

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
        #self._g.slice_(x,y,z,v,sx,sy,sz,nout=0)

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
        #self._g.contourslice(*args, **kwargs)

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

            fig._g = ""
        self._g = fig._g  # link for faster access
        return fig

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
        self._script += "figure(%s)\n" % self.getp('curfig')
        # reset the plotting package instance in fig._g now if needed
        self._script += "clf('reset')\n"

        self._set_figure_size(fig)

        nrows, ncolumns = fig.getp('axshape')
        for axnr, ax in list(fig.getp('axes').items()):
            if nrows != 1 or ncolumns != 1:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,axnr)
                self._script += "ax%d = subplot(%d,%d,%d);\n" % \
                                (axnr,nrows,ncolumns,axnr)
            else:
                rect = ax.getp('viewport')
                if rect and ax.getp('pth') is None:
                    self._script += "ax%d = axes('position', %s);\n" % \
                                    (axnr,rect)
                else:
                    self._script += "ax%d = gca;\n" % axnr
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
                        self._add_bar_graph(item, shading=ax.getp('shading'))
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
                        self._script += "hold on\n"
                        hold_state = True

                if legends:
                    legends = ','.join("'%s'" % l for l in legends)
                    self._script += "legend(%s),...\n" % legends

                if hold_state:
                    self._script += "hold off,...\n"

                self._set_axis_props(ax)
            else:
                self._script += "set(%d, 'Visible', 'off')\n" % axnr

        if False and self.getp('show') and has_matlab:
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            fname = "easyviz_tmp_mfile.m"
            self.save_m(fname)
            basename, ext = os.path.splitext(fname)
            os.system('xterm -e "%s -r %s"' % (MATLAB_CMD_STR,basename))
            #os.remove(fname)

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

        renderer = kwargs.get('renderer', '')
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

        if renderer:
            renderer = "-%s" % renderer
        self._script += "print %s %s %s\n" % (device,filename,renderer)

        if False and has_matlab:
            fname = tempfile.mktemp(suffix='.m')
            self.save_m(fname)
            path, fname = os.path.split(fname)
            basename, ext = os.path.splitext(fname)
            statement = '"%s;quit"' % basename
            os.system("xterm -e '%s -sd %s -r %s'" % \
                      (MATLAB_CMD_STR,path,statement))

    def reset(self):
        """
        Reset the class variable _script where the current Matlab commands
        are stored.
        """
        self._script = ""

    def save_m(self, filename):
        """
        Save the Matlab commands for the current figure(s) in a M-file
        script.
        """
        f = open(filename, 'w')
        f.write(self._script)
        f.close()

    def get_script(self):
        """Return a string with the currently stored Matlab commands."""
        return self._script

    # reimplement color maps and other methods (if necessary) like clf,
    # closefig, and closefigs here.

    def clf(self):
        self._g = ""
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
        self._script += "close(%s)\n" % num
        #del self._figs[num]._g
        #del self._figs[num]

    def closefigs(self):
        for key in self._figs:
            self.closefig(key)
        #del self._g
        BaseClass.closefigs(self)

    # Colormap methods:
    def hsv(self, m=64):
        return "hsv(%s)" % m

    def hot(self, m=64):
        return "hot(%s)" % m

    def gray(self, m=64):
        return "gray(%s)" % m

    def bone(self, m=64):
        return "bone(%s)" % m

    def copper(self, m=64):
        return "copper(%s)" % m

    def pink(self, m=64):
        return "pink(%s)" % m

    def white(self, m=64):
        return "white(%s)" % m

    def flag(self, m=64):
        return "flag(%s)" % m

    def lines(self, m=64):
        return "lines(%s)" % m

    def colorcube(self, m=64):
        return "colorcube(%s)" % m

    def vga(self, m=64):
        return "vga(%s)" % m

    def jet(self, m=64):
        return "jet(%s)" % m

    def prism(self, m=64):
        return "prism(%s)" % m

    def cool(self, m=64):
        return "cool(%s)" % m

    def autumn(self, m=64):
        return "autumn(%s)" % m

    def spring(self, m=64):
        return "spring(%s)" % m

    def winter(self, m=64):
        return "winter(%s)" % m

    def summer(self, m=64):
        return "summer(%s)" % m


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


plt = Matlab2Backend()  # create backend instance
use(plt, globals())     # export public namespace of plt to globals()
backend = os.path.splitext(os.path.basename(__file__))[0][:-1]
