"""
This backend is based on OpenDX (www.opendx.org) which is the open source
version of IBM's Visualization Data Explorer and is a powerfull, full-
featured software package for visualization of scientific, engineering
and analytical data. The connection with Python is handled by py2dx which
is available for download at http://www.psc.edu/~eschenbe/. This backend
can be used by

  python somefile.py --SCITOOLS_easyviz_backend dx

or one can specify the backend in the SciTools configuration file
scitools.cfg under the [easyviz] section

  [easyviz]
  backend = dx

and then

  from scitools.std import *

or if just easyviz is needed

  from scitools.easyviz import *

REQUIREMENTS:

OpenDX
py2dx

Tips:

* The following is an example on how one can send commands directly to DX:

  g = get_backend()
  g('<your DX command here>')

* The complete DX script can be saved to disk for running at a later stage.
  See save_script and its doc string for further details.

TODO:

* Set axis limits. Use the ClipBox module. Problems with AutoAxes.

* Add support for vector fields in two and three dimensions. In 3D we can
  create the vector field by

  f = open('vector3D.dat', 'w')
  nx, ny = shape(z)
  for i in iseq(nx-1):
      for j in iseq(ny-1):
          f.write('%5.3lf\t%5.3lf\t%5.3lf\t%5.3lf\t%5.3lf\t%5.3lf\n' % \
                  (x[i,j],y[i,j],z[i,j],u[i,j],v[i,j],w[i,j]))
  f.close()

  and then use a general header file like this

    file = vector3D.dat
    points = 25
    format = ascii
    interleaving = field
    field = locations, field0
    structure = 3-vector, 3-vector
    type = float, float
    end

  Then use the AutoGlyph/Glyph module in DX to create arrows or use
  Streamline alone or together with Ribbon/Tube.
  (Similar applies to 2D vector fields)

* Fix problems with camera.

* Look more into scaling of data fields.

* Implement different colormaps.

* Is it possible to implement the coneplot command?

* Add support for the isocaps command:

  isocaps = CappedIsosurfaceMacro(data,isovalue,capDir=0);

  Problem: Not only isocaps but also complete isosurface.

* How can we treat NaNs?
  (see http://www.opendx.org/cgi-bin/forum/YaBB.pl?num=1155198504)

* Let _DXFigure be based on DXServer rather than just DX.

* In addition look at curve plotting (Plot module), caxis, colorbar,
  meshc/surfc, ...

"""


from __future__ import division

from .common import *
from scitools.globaldata import DEBUG, VERBOSE
from scitools.misc import check_if_module_exists

check_if_module_exists('DX', msg='You need to install the py2dx package.', abort=False)
import DX
import Tkinter
import tempfile


DXMACROS = '/usr/share/dx/samples/macros'
DXMACROS = os.environ.get('DXMACROS', DXMACROS)


class _DXFigure(object):
    def __init__(self, plt, width=640, height=480, depth=24, title='',
                 hw_render_mode='opengl'):
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
        #button = Tkinter.Button(self.root, text="Quit", command=self.close)
        #button.pack()

        # start DX:
        cmd = DX.DXEXEC + ' -execonly -hwrender opengl'
        self.conn = DX.DXLStartDX(cmd, None)

        #DX.DXLLoadMacroDirectory(self.conn, DXMACROS)
        # hack for loading necessary macro files:
        DX.exDXLLoadScript(self.conn,
                           os.path.join(DXMACROS, "ArrangeMemberMacro.net"))
        DX.exDXLLoadScript(self.conn,
                           os.path.join(DXMACROS, "CappedIsoMacro.net"))

        self.script = ''

    def __call__(self, cmd):
        self.send(cmd)

    def send(self, cmd):
        if not isinstance(cmd, str):
            raise ValueError('DX command must be string, not %s' \
                             % type(cmd))
        self.script += cmd + '\n'
        if not cmd.startswith('//'):  # don't send comments to DX
            DX.DXLSend(self.conn, cmd)

    def reset(self):
        self.script = ''
        DX.DXLEndExecuteOnChange(self.conn)
        DX.DXLSync(self.conn)

    def close(self, event=None):
        self.plt.clf()
        self.root.withdraw()

    def display(self, show=True):
        if show:
            self.root.deiconify()
        self.root.update()
        DX.DXLExecuteOnChange(self.conn)
        DX.WaitForDXIdle(self.conn)
        #DX.DXLExecuteOnce(self.conn)
        #DX.uiDXLOpenVPE(self.conn)

    def exit(self):
        self.root.destroy()
        DX.WaitForDXIdle(self.conn)
        DX.DXLExitDX(self.conn)


class DXBackend(BaseClass):
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
            '': None,       # no color --> blue
            'r': "red",     # red
            'g': "green",   # green
            'b': "blue",    # blue
            'c': "cyan",    # cyan
            'm': "magenta", # magenta
            'y': "yellow",  # yellow
            'k': "black",   # black
            'w': "white",   # white
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
        self._g('labels = {"%s","%s","%s"};' % (xlabel,ylabel,zlabel))

    def _set_title(self, ax):
        """Add a title at the top of the axis."""
        if DEBUG:
            print "Setting title"
        title = self._fix_latex(ax.getp('title'))
        self._g('title = "%s";' % title)
        self._g('caption = Caption(title,[0.5,0.98],font="fixed");')
        self._g('collected = Append(collected,caption);')

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

        # scale limits according to data aspect ratio:
        dar = ax.getp('daspect')
        xmin /= dar[0];  xmax /= dar[0]
        ymin /= dar[1];  ymax /= dar[1]
        zmin /= dar[2];  zmax /= dar[2]
        # create vector to be used in AutoAxes later:
        self._g('axislimits = {[%s,%s,%s],[%s,%s,%s]};' % \
                (xmin,ymin,zmin,xmax,ymax,zmax))
        #self._g('clipped = ClipBox(collected,axislimits);')
        #self._g('collected = Collect(clipped);')

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
            self._g('daspect = [%s %s %s];' % (dar[0],dar[1],dar[2]))
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
        if ax.getp('box'):
            # display box
            self._g('show_box = 1;')
        else:
            # do not display box
            self._g('show_box = 0;')

    def _set_grid(self, ax):
        """Turn grid lines on or off."""
        if DEBUG:
            print "Setting grid"
        if ax.getp('grid'):
            # turn grid lines on
            self._g('show_grid = 1;')
        else:
            # turn grid lines off
            self._g('show_grid = 0;')

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
            #xpos, ypos, length, width, horiz = cbar_location
            #self._g('cbar = ColorBar(collected);')
            #self._g('collected = Append(collected,cbar);')
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

        width = self._g.width
        height = self._g.height
        self._g('resolution = %s;' % width)
        self._g('aspect = %f;' % ((height)/width))

        if view == 2:
            # setup a default 2D view
            #self._g('camtarget = collected;')
            #self._g('campos = Direction(0, 90, 10);')
            #self._g('camup = [0,1,0];')
            #self._g('camva = 30;')
            #self._g('camproj = 0;')
            self._g('camera = AutoCamera(collected);')
        elif view == 3:
            az = cam.getp('azimuth')
            el = cam.getp('elevation')
            if az is None or el is None:
                # azimuth or elevation is not given. Set up a default
                # 3D view (az=-37.5 and el=30 is the default 3D view in
                # Matlab).
                self._g('campos = Direction(-37.5, 30, 10);')
            else:
                # set a 3D view according to az and el
                self._g('campos = Direction(%s, %s, 10);' % (az,el))

            if cam.getp('cammode') == 'manual':
                # for advanced camera handling:
                roll = cam.getp('camroll')
                zoom = cam.getp('camzoom')
                dolly = cam.getp('camdolly')
                target = cam.getp('camtarget')
                position = cam.getp('campos')
                assert target != position, \
                       'camera target and position cannot be equal'
                up_vector = cam.getp('camup')
                view_angle = cam.getp('camva')
                projection = cam.getp('camproj')
                self._g('camtarget = [%s,%s,%s];' % target)
                self._g('campos = [%s,%s,%s];' % position)
                self._g('camup = [%s,%s,%s];' % up_vector)
                if view_angle is None:
                    view_angle = 30;
                self._g('camva = %s;' % view_angle)
                if projection == 'perspective':
                    self._g('camproj = 1;')
                else:
                    self._g('camproj = 0;')
            else:
                # set up some default values:
                self._g('camtarget = collected;')
                self._g('camproj = 0;')
                self._g('camup = [0,0,1];')
                self._g('camva = 30;')

            #self._g('camera = Camera(to=camtarget, from=campos, ' +
            #        'resolution=resolution, aspect=aspect, up=camup, ' +
            #        'angle=camva, ' +
            #        'perspective=camproj, background="black");')

            # use AutoCamera instead:
            self._g('camera = AutoCamera(camtarget, "off-bottom");')

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

        self._g('iact_mode = CollectNamed(2, "mode");')  # 2 = ROTATE
        hw_render_mode = 'opengl'
        hw_render_approx = 'none'
        if hw_render_mode == "none":
            options = '"rendering mode", "software"'
        else:
            options = '"rendering mode", "hardware", ' + \
                      ('"rendering approximation", "%s"' % hw_render_approx)
        options = options + ', "interaction mode", iact_mode'
        self._g('collected = Options(collected, %s);' % options)

        self._set_view(ax)

        if ax.getp('visible'):
            self._set_labels(ax)
            self._set_box(ax)
            self._set_grid(ax)
            self._g('objectwithaxes = AutoAxes(collected, camera, labels, ' +
                    'frame=show_box, corners=collected, grid=show_grid, ' +
                    'colors={"red","yellow","yellow"}, ' +
                    'annotation={"grid","labels","ticks"});')
            #self._g('objectwithaxes = Scale(objectwithaxes, daspect);')
            self._g('camera = UpdateCamera(camera,objectwithaxes);')
            self._g('renderable = objectwithaxes;')
        else:
            # turn off all axis labeling, tickmarks, and background
            self._g('renderable = collected;')

    def _create_2D_vector_field(x, y, u, v):
        pass

    def _create_3D_vector_field(x, y, z, u, v, w):
        dataf = "x y z u v w"
        """file = /tmp/vector3D.dat
points = 25
format = ascii
interleaving = field
field = locations, field0
structure = 3-vector, 3-vector
type = float, float

end
"""
        pass

    def _create_2D_scalar_data_file(self, x, y, z,
                                    regular_grid=False, indexing='ij'):
        tmp = tempfile.mktemp()
        # first create data file:
        data_file = open(tmp+'.dat', 'w')
        nx, ny = shape(z)
        if regular_grid:
            for i in range(nx):
                for j in range(ny):
                    data_file.write("%5.3lf\t" % z[i,j])
                data_file.write("\n")
        else:
            if shape(x) != (nx,ny) and shape(y) != (nx,ny):
                x, y = ndgrid(x,y,sparse=False)
            for i in range(nx):
                for j in range(ny):
                    data_file.write("%5.3lf\t%5.3lf\t%5.3lf\n" % \
                                    (x[i,j],y[i,j],z[i,j]))
        data_file.write("\n")
        data_file.close()
        # then create general header file:
        header_file = open(tmp+'.general', 'w')
        if regular_grid:
            x0 = x[0,0]
            y0 = y[0,0]
            if indexing == 'ij':
                dx = x[1,0] - x[0,0]
                dy = y[0,1] - y[0,0]
            else:
                dx = x[0,1] - x[0,0]
                dy = y[1,0] - y[0,0]
            header_file.write("""file = %s
grid = %d x %d
format = ascii
interleaving = record
majority = row
field = field0
structure = scalar
type = float
dependency = positions
positions = regular, regular, %s, %s, %s, %s

end
""" % (data_file.name,nx,ny,x0,dx,y0,dy))
        else:
            header_file.write("""file = %s
grid = %d x %d
format = ascii
interleaving = field
majority = row
field = locations, field0
structure = 2-vector, scalar
type = float, float

end
""" % (data_file.name,nx,ny))
        header_file.close()
        return header_file.name

    def _create_3D_scalar_data_file(self, x, y, z, v,
                                    regular_grid=False, indexing='ij'):
        tmp = tempfile.mktemp()
        # create data file:
        data_file = open(tmp+'.dat', 'w')
        nx, ny, nz = shape(v)
        if regular_grid:
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        data_file.write("%5.3lf\t" % v[i,j,k])
                    data_file.write("\n")
        else:
            if shape(x) != (nx,ny,nz) and shape(y) != (nx,ny,nz) \
                   and shape(z) != (nx,ny,nz):
                x, y, z = ndgrid(x,y,z,sparse=False)
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        data_file.write("%5.3lf\t%5.3lf\t%5.3lf\t%5.3lf\n" % \
                                        (x[i,j,k],y[i,j,k],z[i,j,k],v[i,j,k]))
        data_file.write("\n")
        data_file.close()
        # create general header file:
        header_file = open(tmp+'.general', 'w')
        if regular_grid:
            x0 = x[0,0,0]
            y0 = y[0,0,0]
            z0 = z[0,0,0]
            if indexing == 'ij':
                dx = x[1,0,0] - x[0,0,0]
                dy = y[0,1,0] - y[0,0,0]
                dz = z[0,0,1] - z[0,0,0]
            else:
                dx = x[0,1,0] - x[0,0,0]
                dy = y[1,0,0] - y[0,0,0]
                dz = z[0,0,1] - z[0,0,0]
            header_file.write("""file = %s
grid = %d x %d x %d
format = ascii
interleaving = record
majority = row
field = field0
structure = scalar
type = float
dependency = positions
positions = regular, regular, regular, %s, %s, %s, %s, %s, %s

end
""" % (data_file.name,nx,ny,nz,x0,dx,y0,dy,z0,dz))
        else:
            header_file.write("""file = %s
grid = %d x %d x %d
format = ascii
interleaving = field
majority = row
field = locations, field0
structure = 3-vector, scalar
type = float, float

end
""" % (data_file.name,nx,ny,nz))
        header_file.close()
        return header_file.name

    def _create_2D_scalar_field(self, x, y, z, id,
                                regular_grid=False,
                                indexing='ij'):
        nx, ny = shape(z)
        if shape(x) != (nx,ny) and shape(y) != (nx,ny):
            x, y = ndgrid(x,y,sparse=False,indexing=indexing)

        # the scalar field should be a string on the form
        # 'z0 z1 z2 ... zn' where n=nx*ny*nz:
        z = ravel(z).tolist()
        scalar_field = ' '.join([str(i) for i in z])

        data = 'data%s' % id
        if regular_grid:
            x0 = x[0,0]
            y0 = y[0,0]
            if indexing == 'ij':
                dx = x[1,0] - x0
                dy = y[0,1] - y0
            else:
                dx = x[0,1] - x0
                dy = y[1,0] - y0

            self._g('%s = Construct([%s %s],[%s %s],[%s %s],{%s});' % \
                    (data,x0,y0,dx,dy,nx,ny,scalar_field))
        else:
            x = ravel(x).tolist()
            y = ravel(y).tolist()
            # create a string with grid positions on the form
            # '[x0 y0][x1 y0] ... [xn y0][x0 y1] ... [xn yn]':
            positions = ''.join(['[%s %s]' % (xp,yp) for xp, yp in zip(x,y)])

            self._g('%s = Construct({%s},NULL,[%d %d],{%s});' % \
                    (data,positions,nx,ny,scalar_field))
        return data

    def _create_3D_scalar_field(self, x, y, z, v, id,
                                regular_grid=False,
                                indexing='ij'):
        nx, ny, nz = shape(v)
        if shape(x) != (nx,ny,nz) and shape(y) != (nx,ny,nz) \
               and shape(z) != (nx,ny,nz):
            x, y, z = ndgrid(x,y,z,sparse=False,indexing=indexing)

        # the scalar field should be a string on the form
        # 'z0 z1 z2 ... zn' where n=nx*ny*nz:
        v = ravel(v).tolist()
        scalar_field = ' '.join([str(i) for i in v])

        data = 'data%s' % id
        if regular_grid:
            x0 = x[0,0,0]
            y0 = y[0,0,0]
            z0 = z[0,0,0]
            if indexing == 'ij':
                dx = x[1,0,0] - x0
                dy = y[0,1,0] - y0
                dz = z[0,0,1] - z0
            else:
                dx = x[0,1,0] - x0
                dy = y[1,0,0] - y0
                dz = z[0,0,1] - z0
            self._g('%s = Construct([%s %s %s],[%s %s %s],[%s %s %s],{%s});' \
                    % (data,x0,y0,z0,dx,dy,dz,nx,ny,nz,scalar_field))
        else:
            x = ravel(x).tolist()
            y = ravel(y).tolist()
            z = ravel(z).tolist()
            # create a string with grid positions on the form
            # '[x0 y0 z0][x1 y0 z0] ... [xn y0 z0][x0 y1 z0] ... [xn yn zn]'
            positions = ''.join(['[%s %s %s]' % (xp,yp,zp) \
                                 for xp, yp, zp in zip(x,y,z)])

            self._g('%s = Construct({%s},NULL,[%d %d %d],{%s});' % \
                    (data,positions,nx,ny,nz,scalar_field))
        return data

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

    def _add_surface(self, item, id, shading='faceted'):
        if DEBUG:
            print "Adding a surface"
        x = item.getp('xdata')  # grid component in x-direction
        y = item.getp('ydata')  # grid component in y-direction
        z = item.getp('zdata')  # scalar field
        c = item.getp('cdata')  # pseudocolor data (can be None)
        indexing = item.getp('indexing')

        #general_file = self._create_2D_scalar_data_file(x, y, z,
        #                                                regular_grid=False,
        #                                                indexing=indexing)
        #self._g('imported%s = Import("%s",format="general");' \
        #        % (id,general_file))
        #data_field = 'imported%s' % id
        data_field = self._create_2D_scalar_field(x, y, z, id,
                                                  regular_grid=False,
                                                  indexing=indexing)
        self._g('colored%s = AutoColor(%s);' % (id,data_field))
        self._g('rubbersheet%s = RubberSheet(colored%s,scale=1);' % (id,id))
        dar = self._ax.getp('daspect')
        self._g('rubbersheet%s = Scale(rubbersheet%s,[%s %s %s]);' % \
                (id,id,dar[0],dar[1],dar[2]))

        contours = item.getp('contours')
        if contours:
            # the current item is produced by meshc or surfc and we
            # should therefore add contours at the bottom:
            self._add_contours(contours, id, placement='bottom')

        if item.getp('wireframe'):
            # wireframe mesh (as produced by mesh or meshc)
            self._g('obj%s = ShowConnections(rubbersheet%s);' % (id,id))
        else:
            # colored surface (as produced by surf, surfc, or pcolor)
            # use keyword argument shading to set the color shading mode
            pcolor = item.getp('function') == 'pcolor'
            if pcolor:
                self._g('rubbersheet%s = colored%s;' % (id,id))
            if shading == 'flat':
                self._g('obj%s = FaceNormals(rubbersheet%s);' % (id,id))
            elif shading == 'interp':
                self._g('obj%s = Normals(rubbersheet%s);' % (id,id))
                #self._g('obj%s = rubbersheet%s;' % (id,id))
            else:
                self._g('colored_mesh%s = Color(%s,"black");' % \
                        (id,data_field)) # FIXME: add sup. for other colors
                self._g(('mesh_rubbersheet%s = RubberSheet(colored_mesh%s, ' +\
                        'scale=1);') % (id,id))
                self._g(('mesh_rubbersheet%s = Scale(mesh_rubbersheet%s, ' + \
                         '[%s %s %s]);') % (id,id,dar[0],dar[1],dar[2]))
                if pcolor:
                    self._g('mesh_rubbersheet%s = colored_mesh%s;' % \
                            (id,id))
                self._g('faceted%s = ShowConnections(mesh_rubbersheet%s);' % \
                        (id,id))
                self._g('collected = Append(collected,faceted%s);' % id)
                self._g('obj%s = FaceNormals(rubbersheet%s);' % (id,id))

        self._g('collected = Append(collected, obj%s);' % id)

    def _add_contours(self, item, id, placement=None):
        # The placement keyword can be either None or 'bottom'. The
        # latter specifies that the contours should be placed at the
        # bottom (as in meshc or surfc).
        if DEBUG:
            print "Adding contours"
        x = item.getp('xdata')  # grid component in x-direction
        y = item.getp('ydata')  # grid component in y-direction
        z = item.getp('zdata')  # scalar field
        indexing = item.getp('indexing')
        dar = self._ax.getp('daspect')

        #general_file = self._create_2D_scalar_data_file(x, y, z)
        #self._g('imported%s = Import("%s",format="general");' \
        #        % (id,general_file))
        data_field = self._create_2D_scalar_field(x, y, z, id,
                                                  indexing=indexing)
        self._g('colored%s = AutoColor(%s);' % (id,data_field))

        filled = item.getp('filled')  # draw filled contour plot if True

        cvector = item.getp('cvector')
        clevels = item.getp('clevels')  # number of contour levels
        if cvector is None:
            # the contour levels are chosen automatically
            self._g('cvector = NULL;')
        else:
            cvector = '{' + ','.join([str(c) for c in cvector]) + '}'
            self._g('cvector = %s;' % cvector)
        self._g('clevels = %s;' % clevels)

        location = item.getp('clocation')
        if location == 'surface':
            # place the contours at the corresponding z level (contour3)
            self._g('rubbersheet%s = RubberSheet(colored%s,scale=1);' % \
                    (id,id))
            self._g('rubbersheet%s = Scale(rubbersheet%s, [%s %s %s]);' % \
                    (id,id,dar[0],dar[1],dar[2]))
            self._g(('obj%s = Isosurface(rubbersheet%s, value=cvector, ' + \
                     'number=clevels);') % (id,id))
        elif location == 'base':
            if placement == 'bottom':
                # place the contours at the bottom (as in meshc or surfc)
                pass
            else:
                # standard contour plot
                pass
            self._g(('obj%s = Isosurface(colored%s, value=cvector, ' + \
                     'number=clevels);') % (id,id))
            self._g('obj%s = Scale(obj%s, [%s %s %s]);' % \
                    (id,id,dar[0],dar[1],dar[2]))

        if item.getp('clabels'):
            # add labels on the contour curves
            pass

        linewidth = item.getp('linewidth')
        if linewidth:
            self._g('obj%s = Options(obj%s, "line width", %s);' % \
                    (id,id,linewidth))
        self._g('collected = Append(collected, obj%s);' % id)

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

    def _add_isosurface(self, item, id):
        if DEBUG:
            print "Adding a isosurface"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume
        c = item.getp('cdata')  # pseudocolor data
        isovalue = item.getp('isovalue')
        indexing = item.getp('indexing')
        dar = self._ax.getp('daspect')

        #general_file = self._create_3D_scalar_data_file(x, y, z, v)
        #self._g('data%s = Import("%s",format="general");' \
        #        % (id,general_file))
        data_field = self._create_3D_scalar_field(x, y, z, v, id,
                                                  regular_grid=False,
                                                  indexing=indexing)
        self._g('colored%s = AutoColor(%s);' % (id,data_field))
        self._g('obj%s = Isosurface(colored%s, value=%s);' % \
                (id,id,isovalue))
        self._g('obj%s = Scale(obj%s,[%s %s %s]);' % \
                (id,id,dar[0],dar[1],dar[2]))

        self._g('collected = Append(collected, obj%s);' % id)

    def _add_slices(self, item, id, shading='faceted'):
        if DEBUG:
            print "Adding slices in a volume"
        # grid components:
        x, y, z = item.getp('xdata'), item.getp('ydata'), item.getp('zdata')
        v = item.getp('vdata')  # volume
        indexing = item.getp('indexing')
        dar = self._ax.getp('daspect')
        xmin, xmax, ymin, ymax, zmin, zmax = item.get_limits()
        center = [(xmax+xmin)/2, (ymax+ymin)/2, (zmax+zmin)/2]

        data_field = self._create_3D_scalar_field(x, y, z, v, id,
                                                  regular_grid=False,
                                                  indexing=indexing)
        self._g('colored%s = AutoColor(%s);' % (id,data_field))

        self._g('slices%s = Collect();' % id)

        sx, sy, sz = item.getp('slices')
        if rank(sz) == 2:
            # sx, sy, and sz defines a surface
            pass
        else:
            # sx, sy, and sz is either numbers or vectors with numbers
            points = []
            normals = []
            sx = ravel(sx)#/dar[0]
            sy = ravel(sy)#/dar[1]
            sz = ravel(sz)#/dar[2]
            for i in range(len(sx)):
                normals.append([1,0,0])
                points.append([sx[i], center[1], center[2]])
            for i in range(len(sy)):
                normals.append([0,1,0])
                points.append([center[0], sy[i], center[2]])
            for i in range(len(sz)):
                normals.append([0,0,1])
                points.append([center[0], center[1], sz[i]])
            for i in range(len(normals)):
                normal = normals[i]
                point = points[i]
                self._g('normal = [%s %s %s];' % \
                        (normal[0],normal[1],normal[2]))
                self._g('point = [%s %s %s];' % (point[0],point[1],point[2]))
                self._g('slice = MapToPlane(colored%s, point, normal);' % id)
                if shading == 'interp':
                    self._g('slice = Normals(slice);')
                elif shading == 'flat':
                    self._g('slice = FaceNormals(slice);')
                else:
                    self._g('mesh_slice%s = Color(slice,"black");' % id)
                    self._g('mesh_slice%s = ShowConnections(mesh_slice%s);' % \
                            (id,id))
                    self._g('slices%s = Append(slices%s, mesh_slice%s);' % \
                            (id,id,id))
                #self._g(
                self._g('slices%s = Append(slices%s, slice);' % (id,id))

        self._g('collected = Append(collected, slices%s);' % id)

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
            self._g.root.geometry('%sx%s' % (width,height))
            self._g.root.update()
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
            name = 'Figure ' + str(fig.getp('number'))
            if DEBUG:
                print "creating figure %s in backend" % name

            fig._g = _DXFigure(self, title=name)

        self._g = fig._g  # link for faster access
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
        # reset the plotting package instance in fig._g now if needed
        fig._g.reset()

        # include some useful macros:
        # (look at DXLLoadMacroFile)
        fig._g('//include "AutoScaleMacro.net"')
        fig._g('//include "ArrangeMemberMacro.net"')
        fig._g('//include "CappedIsoMacro.net"')

        self._set_figure_size(fig)

        #DX.exDXLBeginMacroDefinition(self._g.conn, 'macro main()')

        width = self._g.width
        height = self._g.height
        parent = self._g.frame.winfo_id()
        depth = self._g.frame.winfo_depth()
        self._g(('where, size, events = SuperviseWindow("Easyviz", ' +
                 'display=NULL, size=[%d,%d], offset=NULL, ' +
                 'parent=%s, depth=%d);') % (width, height, parent, depth))

        nrows, ncolumns = fig.getp('axshape')
        for axnr, ax in list(fig.getp('axes').items()):
            self._ax = ax          # create link for easier access later
            self._axnr = axnr - 1  # same
            pth = ax.getp('pth')
            if pth:
                # create axes in tiled position
                # this is subplot(nrows,ncolumns,axnr)
                pass
            i = 0
            self._g('collected = Collect();')
            plotitems = ax.getp('plotitems')
            plotitems.sort(self._cmpPlotProperties)
            for item in plotitems:
                item_id = str(i)
                func = item.getp('function') # function that produced this item
                if isinstance(item, Line):
                    self._add_line(item)
                elif isinstance(item, Surface):
                    self._add_surface(item, item_id, shading=ax.getp('shading'))
                elif isinstance(item, Contours):
                    self._add_contours(item, item_id)
                elif isinstance(item, VelocityVectors):
                    self._add_vectors(item)
                elif isinstance(item, Streams):
                    self._add_streams(item)
                elif isinstance(item, Volume):
                    if func == 'isosurface':
                        self._add_isosurface(item, item_id)
                    elif func == 'slice_':
                        self._add_slices(item, item_id,
                                         shading=ax.getp('shading'))
                    elif func == 'contourslice':
                        self._add_contourslices(item)
                legend = self._fix_latex(item.getp('legend'))
                if legend:
                    # add legend to plot
                    pass
                i += 1

            self._rendermode = "hardware"  # hardware or software rendering
            self._interactionmode = 0      # 0:rotate, 1:pan, 2:zoom

            self._set_axis_props(ax)

            nr = self._axnr
            self._g(('object%s, cam%s, where%s = ArrangeMember(renderable, ' +
                     'renderMode="%s", defaultCamera=camera, ' +
                     'interactionMode=%d, parentSize=size, parent=where, ' +
                     'title="image", totalSubimages={%d}, ' +
                     'nHorizontal={%d}, which={%d});') % \
                    (nr,nr,nr,self._rendermode,self._interactionmode,
                     nrows*ncolumns,ncolumns,nr))
            #self._g('Display(renderable, camera, where=where);')

        #DX.exDXLEndMacroDefinition(self._g.conn)

        if self.getp('show'):
            # display plot on the screen
            if DEBUG:
                print "\nDumping plot data to screen\n"
                debug(self)
            pass
        self._g.display(show=self.getp('show'))

    def hardcopy(self, filename, **kwargs):
        """
        Supported extensions:

          '.ps'   (PostScript)
          '.epsf' (Encapsualted PostScript)
          '.gif'  (Graphics Interchange Format)
          '.tiff' (Tag Image File Format)
          '.miff' (Magick Image File Format)
          FIXME: Add more formats like rgb, r+g+b, yuv, ...

        If `filename` contains just the file extension, say ``.png``,
        it is saved to ``tmp.png``.

        Optional arguments:

          color       -- True (colors) or False (black and white).
          size        -- A tuple (width,height) to set the size in inches of
                         the image. The default is (8.5,11).
          dpi         -- Set the number of dots (pixels) per inch in the
                         hardcopy image. Use this only if you want to
                         explicitly set the number of dots per inch.
          orientation -- 'auto' (default), 'portrait', or 'landscape'. Only
                         available for PostScript output.
          margin      -- Sets the desired margin around the image. The
                         default is 0.5 inch.
          width       -- FIXME ...
          height      -- FIXME ...
          gamma       -- Sets the gamma correction factor for the output
                         image. The default is 2.0. Avaliable for all output
                         formats.
          delayed     -- If True this creates an image-with-colormap. Only
                         available for PostScript, TIFF, and MIFF formats.
                         The default is False.
          frame       -- FIXME ...

        """
        if filename.startswith('.'):
            filename = 'tmp' + filename

        if DEBUG:
            print "Hardcopy to %s" % filename

        self.setp(**kwargs)
        color = self.getp('color')
        replot = kwargs.get('replot', True)
        if replot:
            self._replot()

        if color:
            color = 'color'
        else:
            color = 'gray'
        size = kwargs.get('size', (8.5,11))
        dpi = kwargs.get('dpi', None)
        orientation = kwargs.get('orientation', 'auto')
        margin = kwargs.get('margin', 0.5)
        width = kwargs.get('width', None)
        height = kwargs.get('height', None)
        gamma = kwargs.get('gamma', 2.0)
        delayed = kwargs.get('delayed', False)

        basename, ext = os.path.splitext(filename)
        if not ext:
            ext = '.ps'
            filename += ext

        format = ext[1:]
        options = ''
        if ext in ['.ps', '.epsf']:
            options += '%s page=%sx%s margin=%s orient=%s' % \
                       (color,size[0],size[1],margin,orientation)
            if dpi is not None:
                options += ' dpi=%s' % dpi
            if width is not None:
                options += ' width=%s' % width
            if height is not None:
                options += ' height=%s' % height
        if ext in ['.ps', '.epsf', '.tiff', '.miff']:
            if delayed:
                options += ' delayed=1'
        options += ' gamma=%s' % gamma

        format_str = '%s %s' % (format,options)
        # render image(s):
        nrows, ncolumns = self.gcf().getp('axshape')
        self._g('images = Collect();')
        for i in range(nrows*ncolumns):
            self._g('image%d = Render(object%d, cam%d);' % (i,i,i))
            self._g('images = Append(images, image%d);' % i)
        self._g('arranged = Arrange(images, %d);' % ncolumns)
        # write to file:
        self._g('WriteImage(arranged,"%s","%s");' % (basename,format_str))

    # reimplement methods like clf, closefig, closefigs
    def clf(self):
        self._g.reset()
        self._g.root.withdraw()
        BaseClass.clf(self)

    def save_script(self, filename):
        """
        Save the DX commands used for the plot in the current figure in a
        script file that can be run by the command dx -script <filename>.
        Note that some aspects of the script has to be modified in order
        for it to work as intended (like uncommenting the necessary macros
        and removing the parent option in the SuperviseWindow.
        """
        f = open(filename, 'w')
        f.write(self._g.script)
        f.close()

    # implement colormap functions here
    #def jet(self, m=None):
    #    """Variant of hsv."""
    #    pass


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


plt = DXBackend()    # create backend instance
use(plt, globals())  # export public namespace of plt to globals()
backend = os.path.splitext(os.path.basename(__file__))[0][:-1]
