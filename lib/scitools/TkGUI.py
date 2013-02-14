"""
Module with functions and classes used in the GUI chapters of
the book "Python Scripting for Computational Science".
"""
# NOTE: This file merges the previous modules
# CanvasCoords, FunctionSelector, DrawFunction, FuncDependenceViz,
# ParameterInterface
#

import Tkinter, os
from scitools.misc import import_module
Pmw = import_module('Pmw')

class DrawFunction:
    """
    Interactive drawing of y=f(x) functions.
    The drawing takes place in a Pmw.Blt.Graph widget.
    """
    def __init__(self, xcoor, parent,
                 ymin=0.0, ymax=1.0,
                 width=500, height=200,
                 curvename=' ', ylabel='', xlabel='',
                 curvecolor='green', curvewidth=4,
                 yrange_widgets=True):
        """
        Interactive drawing of a function.

        xcoor           grid points (on the x axsis) for interpolation
        parent          parent widget
        ymin, ymax      initial extent of the y axis
        width, height   size of widget
        curvename       name of function to be drawn
        xlabel, ylabel  labels on the axis
        curvecolor      color of the drawn curve
        curvewidth      line thickness of the drawn curve
        yrange_widgets  True: add text entries for range of y axis

        These parameters, except for parent and yrange_widgets,
        can also be set as keyword arguments in the configure method.
        """
        self.master = parent
        self.top = Tkinter.Frame(self.master)
        # packed in self.pack(); the user can then place this
        # DrawFunction wherever it is desired in a big GUI

        frame1 = Tkinter.Frame(self.top);  frame1.pack(side='top')
        if yrange_widgets:
            column1 = Tkinter.Frame(frame1)
            column1.pack(side='left')
            if ylabel:  yl = ylabel
            else:       yl = 'y'
            self.ymin_widget = Pmw.EntryField(column1,
                labelpos='n', label_text=yl+' min',
                entry_width=6, command=self.__ymin)
            self.ymin_widget.pack(side='top',padx=2,pady=2)

            self.ymax_widget = Pmw.EntryField(column1,
                labelpos='n', label_text=yl+' max',
                entry_width=6, command=self.__ymax)
            self.ymax_widget.pack(side='top',padx=2,pady=2)
            Pmw.alignlabels([self.ymin_widget,self.ymax_widget])

        self.g = Pmw.Blt.Graph(frame1,
                               width=width, height=height)
        self.g.pack(side='left', expand=1, fill='both')

        if yrange_widgets:
            self.set_yaxis(ymin, ymax)

        self.configure(xcoor=xcoor, width=width, height=height,
                       curvename=curvename, curvecolor=curvecolor,
                       curvewidth=curvewidth,
                       xlabel=xlabel, ylabel=ylabel)

        self.g.grid_on()
        self.g.bind('<ButtonPress>',   self.mouse_down)
        self.g.bind('<ButtonRelease>', self.mouse_up)

        row1 = Tkinter.Frame(self.top)
        row1.pack(side='top')
        Tkinter.Button(row1, text='Interpolate to grid',
            width=20, command=self.interpolate).pack(side='left',padx=2)
        Tkinter.Button(row1, text='Erase drawing',
            width=20, command=self.erase).pack(side='left',padx=2)

        self.erase() # some init

    def pack(self, **kwargs):
        self.top.pack(kwargs, expand=1, fill='both')

    def configure(self, **kwargs):
        """
        Legal parameters (kwargs):

        xcoor           grid points (on the x axsis) for interpolation
        width, height   size of widget
        curvename       name of function to be drawn
        xlabel, ylabel  labels on the axis
        curvecolor      color of the drawn curve
        curvewidth      line thickness of the drawn curve

        ymin and ymax are set in set_yaxis method.
        """
        for name in kwargs:
            if name == 'xcoor':
                xcoor = kwargs['xcoor']
                self.xcoor = xcoor
                self.xmin = min(xcoor); self.xmax = max(xcoor)
                self.g.xaxis_configure(min=self.xmin, max=self.xmax)
            elif name == 'width':
                self.g.configure(width=kwargs['width'])
            elif name == 'height':
                self.g.configure(width=kwargs['height'])
            elif name == 'curvename':
                self.curvename = kwargs['curvename']
            elif name == 'curvecolor':
                self.curvecolor = kwargs['curvecolor']
            elif name == 'curvewidth':
                self.curvewidth = kwargs['curvewidth']
            elif name == 'xlabel':
                self.g.xaxis_configure(title=kwargs['xlabel'])
            elif name == 'ylabel':
                self.g.xaxis_configure(title=kwargs['ylabel'])

        if self.curvename == ' ':
            self.legend = ''
        else:
            self.legend = self.curvename

    def set_yaxis(self, ymin, ymax):
        try:
            self.ymax_widget.setvalue(ymax)
            self.ymin_widget.setvalue(ymin)
        except:
            # no widgets for ymin, ymax
            pass
        self.g.yaxis_configure(min=ymin, max=ymax)

    def __ymin(self):
        self.g.yaxis_configure(min=float(self.ymin_widget.get()))

    def __ymax(self):
        self.g.yaxis_configure(max=float(self.ymax_widget.get()))

    def erase(self):
        """delete all curves and make new empty self.x and self.y"""
        for curvename in self.g.element_show():
            self.g.element_delete(curvename)

        self.x = Pmw.Blt.Vector()
        self.y = Pmw.Blt.Vector()
        self.g.configure(title='0 drawn points')

    def mouse_drag(self, event):
        # transform screen coordinates of the mouse position,
        # (event.x,event.y) to physical coordinates (x,y):
        x = self.g.xaxis_invtransform(event.x)
        y = self.g.yaxis_invtransform(event.y)
        self.x.append(x); self.y.append(y)

        # plot the curve as soon as we have two points, BLT vectors
        # will automatically update the graph when they get new
        # elements...
        if len(self.x) == 2:
            if self.g.element_exists(self.curvename):
                self.g.element_delete(self.curvename)

            self.g.line_create(self.curvename,
                               label=self.legend,
                               xdata=self.x,
                               ydata=self.y,
                               color=self.curvecolor,
                               linewidth=self.curvewidth,
                               outlinewidth=0, fill='')

        self.g.configure(title='%d points drawn' % len(self.x))

    def mouse_down(self, event):
        self.g.bind('<Motion>', self.mouse_drag)

    def mouse_up(self, event):
        self.g.unbind('<Motion>')

    def interpolate(self):
        # first build a new list with the approved (x,y) pairs:
        # if the drawn curve is too short, stretch the end points:
        if self.x[0] > self.xmin:   self.x[0] = self.xmin
        if self.x[-1] < self.xmax:  self.x[-1] = self.xmax

        x = [];  y = []; current_xmax = -9.9E+20
        for i in range(len(self.x)):
            # skip points outside [xmin,xmax]:
            if self.x[i] >= self.xmin and self.x[i] <= self.xmax:
                if self.x[i] > current_xmax:
                    x.append(self.x[i]); y.append(self.y[i])
                    current_xmax = self.x[i]
        # ensure that the end points are included:
        if x[0]  > self.xmin:
            x.insert(0,self.xmin); y.insert(0,y[0])
        if x[-1] < self.xmax:
            x.append(self.xmax); y.append(y[-1])

        self.f = points2grid(x, y, self.xcoor)
        # the interpolated curve is now (self.xcoor,self.f)
        # both are NumPy arrays

        if self.g.element_exists(self.curvename + '_i'):
            self.g.element_delete(self.curvename + '_i')
        if len(self.xcoor) > 30:
            # many points, remove drawn curve, replace by interpolated data:
            self.g.element_delete(self.curvename)
            circles = 0
        else:
            # keep drawn curve, add circles at interpolation points:
            circles = 1
        self.g.line_create(self.curvename + '_i',
                           label=self.legend,
                           xdata=tuple(self.xcoor),
                           ydata=tuple(self.f),
                           color='blue',
                           linewidth=1,
                           outlinewidth=circles, fill='')

    def get(self):
        """
        return points (x,y), interpolated to the grid, where
        x and y are NumPy arrays of coordinates
        """
        try:
            return self.xcoor, self.f
        except:
            raise AttributeError('No drawing! Draw the curve first!')


def points2grid(x, y, xcoor):
    "Transform points (x,y) to a uniform grid with coordinates xcoor."
    L = 0; R = 0
    n = len(xcoor)
    m = len(x)
    from numpy import zeros
    f = zeros(n)
    for i in range(n):
        xi = xcoor[i]
        # find j such that xi is between x[j-1] and x[j]
        j = L  # we know that xcoor[i-1]>L so x[i]>L
        while j < m-1 and x[j] <= xi:
            j += 1
        if j < m:
            L = j-1; R = j
            #print "i=%d xi=%g; in between x[%d]=%g and x[%d]=%g" % (i,xi,L,x[L],R,x[R])
            # linear interpolation:
            f[i] = y[L] + (y[R]-y[L])/(x[R]-x[L])*(xi-x[L])
        else:
            raise ValueError("bug")
    return f


class DrawFunctionDialog:
    def __init__(self, xcoor, parent=None):
        """Dialog box with DrawFunction widget"""
        self.d = Pmw.Dialog(parent,
                            title='Programmer-Defined Dialog',
                            buttons=('Approved', 'Cancel'),
                            command=self.action)

        self.d_gui = DrawFunction(xcoor, self.d.interior())
        self.d_gui.pack(padx=10,pady=10)

    def action(self, result):
        if result == 'Approved':
            self.x, self.f = self.d_gui.get()
        self.d.destroy()

    def get(self):
        return self.x, self.f


def _test_DrawFunction():
    root = Tkinter.Tk()
    Pmw.initialise(root)
    import scitools.misc; scitools.misc.fontscheme6(root)
    root.title('DrawFunction demo')
    from numpy import linspace
    x = linspace(0, 1, 21)
    df = DrawFunction(x, root)
    df.pack()
#    Tkinter.Button(root, text='Print coordinates (interpolated to grid)',
#           command=lambda o=df: sys.stdout.write(str(o.get()[1]))).pack(pady=2)
    root.mainloop()


def roundInt(a): return int(a+0.5)

class CanvasCoords:
    """
    Utilities for transforming between canvas coordinates and
    physical (real) coordinates.
    """
    def __init__(self):
        # 400x400 pixels is default:
        self.canvas_x = self.canvas_y = 400
        # origin: lower left corner:
        self.x_origin = 0; self.y_origin = self.canvas_y
        # x and y measured in pixels:
        self.x_range = self.canvas_x
        self.xy_scale = self.canvas_x/self.x_range

    def set_coordinate_system(self, canvas_width, canvas_height,
                              x_origin, y_origin, x_range = 1.0):
        """
        Define parameters in the physical coordinate system
        (origin, width) expressed in canvas coordinates.
        x_range is the width of canvas window in physical coordinates.
        """
        self.canvas_x = canvas_width   # width  of canvas window
        self.canvas_y = canvas_height  # height of canvas window

        # the origin in canvas coordinates:
        self.x_origin = x_origin
        self.y_origin = y_origin

        # x range (canvas_x in physical coords):
        self.x_range = x_range
        self.xy_scale = self.canvas_x/self.x_range

    def print_coordinate_system(self):
        print "canvas = (%d,%d)" % (self.canvas_x, self.canvas_y)
        print "canvas origin = (%d,%d)" % (self.x_origin, self.y_origin)
        print "range of physical x coordinate =", self.x_range
        print "xy_scale (from physical to canvas): ", self.xy_scale

    # --- transformations between physical and canvas coordinates: ---

    def physical2canvas(self, x, y):
        """Transform physical (x,y) to canvas 2-tuple."""
        return (roundInt(self.x_origin + x*self.xy_scale),
                roundInt(self.y_origin - y*self.xy_scale))

    def cx(self,x):
        """Transform physical x to canvas x."""
        return roundInt(self.x_origin + x*self.xy_scale)

    def cy(self,y):
        """Transform physical y to canvas y."""
        return roundInt(self.y_origin - y*self.xy_scale)

    def physical2canvas4(self, coords):
        """
        Transform physical 4-tuple (x1,x2,y1,y2) to
        canvas 4-tuple.
        """
        return (roundInt(self.x_origin + coords[0]*self.xy_scale),
                roundInt(self.y_origin - coords[1]*self.xy_scale),
                roundInt(self.x_origin + coords[2]*self.xy_scale),
                roundInt(self.y_origin - coords[3]*self.xy_scale))

    def canvas2physical(self, x, y):
        """Inverse of physical2canvas."""
        return (float((x - self.x_origin)/self.xy_scale),
                float((self.y_origin - y)/self.xy_scale))

    def canvas2physical4(self, coords):
        """Inverse of physical2canvas4."""
        return (float((coords[0] - self.x_origin)/self.xy_scale),
                float((self.y_origin - coords[1])/self.xy_scale),
                float((coords[2] - self.x_origin)/self.xy_scale),
                float((self.y_origin - coords[3])/self.xy_scale))

    def scale(self, dx):
        """
        Transform a length in canvas coordinates
        to a length in physical coordinates.
        """
        return self.xy_scale*dx

    # short forms:
    c2p  = canvas2physical
    c2p4 = canvas2physical4
    p2c  = physical2canvas
    p2c4 = physical2canvas4

def _CanvasCoords_test():
    root = Tkinter.Tk()
    c = Tkinter.Canvas(root,width=400, height=400)
    c.pack()
    # let physical (x,y) be at (200,200) and let the x range be 2:
    C.set_coordinate_system(400,400, 200,200, 2.0)
    cc = C.p2c4((0.2, 0.2, 0.6, 0.6))
    c.create_oval(cc[0],cc[1],cc[2],cc[3],fill='red',outline='blue')
    c1, c2 = C.physical2canvas(0.2,0.2)
    c.create_text(c1, c2, text='(0.2,0.2)')
    c1, c2 = C.physical2canvas(0.6,0.6)
    c.create_text(c1, c2, text='(0.6,0.6)')
    c.create_line(C.cx(0.2), C.cy(0.2),
                  C.cx(0.6), C.cy(0.2),
                  C.cx(0.6), C.cy(0.6),
                  C.cx(0.2), C.cy(0.6),
                  C.cx(0.2), C.cy(0.2))



"""
Utilities for holding and displaying data about input parameters.
"""
import re
import scitools.modulecheck
import scitools.misc
try:
    PQ = import_module('Scientific.Physics.PhysicalQuantities')
except ImportError:
    pass

from scitools.misc import str2bool, str2obj

class InputPrm:
    """Class for holding data about a parameter."""
    def __init__(self, name=None, default=0.0, str2type=None,
                 help=None, unit=None, cmlarg=None, prmclass=None):
        """
        default           default value
        str2type          string to type conversion
                          (float, int, str, str2bool)
        name              parameter name
        help              description of parameter
        unit              physical unit (dimension)
        cmlarg            command-line argument for sending
                          this prm to an external program
        prmclass          classification of this parameter, e.g.,
                          'numerics', 'physics', 'material', etc.

        Note: value with unit only works if str is float or int

        >>> p=InputPrm('q', 1, float, unit='m')
        >>> p.set(6)
        >>> p.get()
        6.0
        >>> p.set('6 cm')
        >>> p.get()
        0.059999999999999998
        >>> p=InputPrm('q', '1 m', float, unit='m')
        >>> p.set('1 km')
        >>> p.get()
        1000.0
        >>> p.get_wunit()
        '1000.0 m'
        >>> p.unit
        'm'
        """
        self.str2type = str2type
        self.name = name
        self.help = help
        self.unit = unit
        self.cmlarg = cmlarg
        self.prmclass = prmclass
        if str2type is None:
            self.str2type = scitools.misc.str2obj

        # check that unit is a valid physical dimension:
        if self.unit is not None:
            try:
                q = PQ.PhysicalQuantity('1.0 ' + str(self.unit))
            except:
                raise ValueError(
                    'unit=%s is an illegal physical unit' % str(self.unit))
            if self.str2type is float or self.str2type is int:
                pass  # must have float or int when units are present
            else:
                raise ValueError(
                    'str2type must be float or int, not %s' % \
                    str(self.str2type))

        self.set(default)  # set parameter value
        scitools.modulecheck.exception('InputPrm constructor', 'Scientific')

    def get(self):
        """Return the value of the parameter."""
        return self._v

    def set(self, value):
        """Set the value of the parameter."""
        self._v = self.str2type(self._scan(value))

    v = property(fget=get, fset=set, doc='value of parameter')

    def get_wunit(self):
        """
        Return value with unit (dimension) as string, if it has.
        Otherwise, return value (with the right type).
        """
        if self.unit is not None:
            return str(self.get()) + ' ' + self.unit
        else:
            return self.get()

    def __repr__(self):
        """Application of eval to this output creates the instance."""
        return "InputPrm(name='%s', default=%s, str2type=%s, "\
               "help=%s, unit=%s, cmlarg=%s)" % \
               (self.name, self.__str__(), self.str2type.__name__,
                self.help, self.unit, self.cmlarg)

    def __str__(self):
        """
        Compact output; just the value as a formatted string.
        Note that __str__ is used by __repr__ so strings must
        be enclosed in quotes.
        """
        return repr(self._v) # ensure quotes in strings

    def _handle_unit(self, v):
        """
        Check if v is of the form 'value unit', extract value, after
        conversion to correct unit (if necessary).
        """
        if isinstance(v, PQ.PhysicalQuantity):
            v = str(v)  # convert to 'value unit' string
        if isinstance(v, str) and isinstance(self.unit, str) and \
           (self.str2type is float or self.str2type is int):
            if ' ' in v: # 'value unit' string?
                try:
                    self.pq = PQ.PhysicalQuantity(v)
                except:
                    raise ValueError('%s should be %s; illegal syntax' % \
                                     (v, self.str2type.__name__))
                if not self.pq.isCompatible(self.unit):
                    raise ValueError(
                        'illegal unit (%s); %s is registered with unit %s' % \
                        (v, self.name, self.unit))
                self.pq.convertToUnit(self.unit)
                v = self.str2type(str(self.pq).split()[0])
                return v
            else:
                # string value without unit given:
                return self.str2type(v)
        else:  # no unit handling
            if isinstance(v, str):
                # check if a unit was given:
                try:
                    PQ.PhysicalQuantity(v)
                    raise ValueError(
                        'parameter %s given with dimension: %s, but '\
                        'dimension is not registered' % (self.name,v))
                except:
                    pass
            return self.str2type(v)

    def getPhysicalQuantity(self):
        if self.unit is not None:
            try:
                return self.pq  # may be computed in _handle_unit
            except:
                return PQ.PhysicalQuantity(self.get_wunit())
        else:
            raise AttributeError('parameter %s has no registered unit' % \
                                 self.name)

    def _scan(self, s):
        """Interpret string s. Return number (for self._v)."""
        # multiple loops?
        v = self._handle_unit(s)
        return self.str2type(v)


def commandline2dict(argv, parameters):
    """
    Load data from the command line into a dictionary of
    parameter values. The argv argument is typically sys.argv[1:].
    Each option --opt in argv is extracted and the
    proceeding value v is assigned to parameters:
       parameters[opt].set(v)
    Hence, parameters must hold objects that have a set
    function. Normally, parameters is a dictionary of
    InputPrm objects.
    """
    p = scitools.misc.cmldict(sys.argv[1:], cmlargs=None, validity=0)
    # p[key] holds all command-line args, we are only interested
    # in those keys corresponding to parameters.keys()
    for key in p.keys():
        if key in list(parameters.keys()):
            parameters[key].set(p[key])



class InputPrmGUI(InputPrm):
    """Represent an input parameter by a widget."""

    GUI_toolkit = 'Tkinter/Pmw'

    def __init__(self, name=None, default=0.0, str2type=None,
                 widget_type='entry', values=None, parent=None,
                 help=None, unit=None, cmlarg=None):
        """
        @param default:           default value
        @param str2type:          function from string to type
        @param name:              name of parameter
        @param widget_type:       entry, slider, option, checkbutton
        @param values:            (min,max) interval or options
        @param parent:            parent widget
        @param help:              description of parameter
        @param unit:              physical unit (dimension)
        @param cmlarg:            command-line argument for sending
                                  this prm to an external program
        """
        if str2type is None:
            str2type = scitools.misc.str2obj

        # bind self._v to an object with get and set methods
        # for assigning and extracting the parameter value
        # in the associated widget:
        if InputPrmGUI.GUI_toolkit.startswith('Tk'):
            # use Tkinter variables
            self.make_GUI_variable_Tk(str2type, unit, name)
        else:
            raise ValueError(
                'The desired GUI toolkit %s is not supported' % \
                InputPrmGUI.GUI_toolkit)
        # How to implement support for other toolkits:
        # self._v must point to an object with a get and set method
        # for extracting and setting the value of the parameter in
        # the associated widget. In Tkinter self._v is a Tkinter
        # variable (DoubleVar, StringVar, IntVar). In another toolkit
        # one can just create a corresponding class:
        # class GUIVariable:
        #     def __init__(self): pass
        #     def attach(self, widget):
        #         self.widget = widget # can be done in make_widget_*
        #     def get(self):
        #         self.widget.get()  # for example
        #     def set(self, value):
        #         self.widget.set(value) # for example

        InputPrm.__init__(self, name, default,
                          str2type, help, unit, cmlarg)
        self._widget_type = widget_type
        self.parent = parent
        self._values = values  # (from, to) interval for parameter

        self.widget = None     # no widget created (yet)
        self._validate = None  # no validation of answers by default

        if str2type == str2bool and self._widget_type != 'checkbutton':
            self._widget_type = 'checkbutton'
            # no warning because minimal input, just name and a
            # bool value, leads us here - which is okay - all other
            # widgets become entries

    def get_widget_type(self):  return self._widget_type
    widget_type = property(fget=get_widget_type) # read-only

    def make_GUI_variable_Tk(self, str2type, unit, name):
        """
        Bind self._v to a variable with set and get methods for
        setting and getting the value in/from a GUI.
        """
        if unit is not None:
            self._v = Tkinter.StringVar()  # value with unit
        else:
            if str2type == float:
                self._v = Tkinter.DoubleVar()
                self._validate = {'validator' : 'real'}
            elif str2type == str:
                self._v = Tkinter.StringVar()
            elif str2type == int:
                self._v = Tkinter.IntVar()
                self._validate = {'validator' : 'int'}
            elif str2type == str2bool:
                self._v = Tkinter.StringVar()
            elif str2type == complex:
                self._v = Tkinter.StringVar()
            elif str2type == str2obj:
                self._v = Tkinter.StringVar()
            else:
                raise ValueError(
                    'str2type %s for parameter %s is not supported' % \
                    (str2type, name))

    def make_widget(self):
        if InputPrmGUI.GUI_toolkit.startswith('Tk'):
            self.make_widget_Tk()
        else:
            raise ValueError(
                'The desired GUI toolkit %s is not supported' % \
                InputPrmGUI.GUI_toolkit)

    def make_widget_Tk(self):
        """Make Tk widget according to self._widget_type."""
        if self.name is None:
            raise TypeError("name attribute must be set before "\
                            "widget can be created")
        if self.parent is None:
            raise TypeError("parent attribute must be set before "\
                            "widget can be created")
        # consistency/type check of values, if it is supplied:
        if self._values is not None:
            if type(self._values) != type([]) and \
               type(self._values) != type(()):
                raise TypeError("values attribute must be list or tuple")

        if self.unit is None:
            label = self.name
        else:
            label = '%s (%s)' % (self.name, self.unit)

        if self._widget_type == 'entry':
            if self._validate is not None and self._values is not None:
                self._validate['min'] = self._values[0]
                self._validate['max'] = self._values[1]
            self.widget = Pmw.EntryField(self.parent,
                            labelpos='w',
                            label_text=label,
                            validate=self._validate,
                            entry_width=15,
                            entry_textvariable=self._v)
        elif self._widget_type == 'slider':
            # we require values:
            if self._values is None:
                raise TypeError(
                    "values attribute must be set for slider '%s'" % \
                    self.name)

            min = float(self._values[0]); max = float(self._values[1])
            try:
                step = float(self._values[2])  # try if present
            except:
                step = (max - min)/100.0       # default
            self.widget = Tkinter.Scale(self.parent,
                     orient='horizontal',
                     from_=min, to=max,
                     tickinterval=(max - min)/5.0,
                     resolution=step,
                     label=label,
                     #font="helvetica 12 italic",
                     length=300,
                     variable=self._v)
        elif self._widget_type == 'option':
            # we require values, which now contains the option values
            if self._values is None:
                raise TypeError(
                    "values attribute must be set for option menu '%s'" % \
                    self.name)

            self.widget = Pmw.OptionMenu(self.parent,
               labelpos='w',  # n, nw, ne, e and so on
               label_text=label,
               items=self._values,
               menubutton_textvariable=self._v
               )
        elif self._widget_type == 'checkbutton':
            self.widget = Tkinter.Checkbutton(self.parent,
                                              text=label,
                                              variable=self._v)
        # no packing of widgets
        return self.widget  # if desired (it's stored in the class too)

    def get(self):
        """
        Get GUI text/number, handle special input like numbers
        with units, if necessary.
        """
        # self.str2type(self._scan(gui)) is sufficient here
        # but we check if we have a unit and then if the unit
        # is registered:
        try:
            gui = self._v.get()  # fails if value has unit
        except ValueError, msg:
            if self.unit is None:
                print msg, '\nvalue with unit, but no registered unit!'
                sys.exit(1)
            # else: ok, go on with self._scan and interpret

        r = self._scan(gui)
        return r

    def set(self, value):
        self._v.set(self.str2type(self._scan(value)))

    def __repr__(self):
        """Application of eval to this output creates the object."""
        return "InputPrmGUI(name='%s', default=%s, str2type=%s, "\
               "widget_type='%s', parent=None, values=%s, "\
               "help=%s, unit=%s, cmlarg=%s)" % \
               (self.name, self.__str__(), self.str2type.__name__,
                self._widget_type, str(self._values),
                self.help, self.unit, self.cmlarg)


class InputPrmCGI(InputPrm):
    """Represent a parameter by a form variable in HTML."""
    def __init__(self, name=None, default=0.0, str2type=None,
                 widget_type='entry', values=None, form=None,
                 help=None, unit=None, cmlarg=None):
        """
        default            default value
        str2type           function from string to type
        name               name of parameter
        widget_type        entry, slider, option, checkbutton
        values             option values
        form               cgi.FieldStorage object
        help               description of parameter
        unit               physical unit (dimension)
        cmlarg             command-line argument for sending
                           this prm to an external program
        """

        InputPrm.__init__(self, name, default, str2type,
                          help, unit, cmlarg)
        self._widget_type = widget_type
        self._form = form
        self._values = values

    def make_form_entry(self):
        """Write the form's input field, according to widget_type."""
        if self.name is None:
            raise TypeError("name attribute must be set before "\
                            "widget can be created")

        value = str(self.get())

        s = ""  # HTML code to be returned is stored in s
        if self._widget_type == 'entry' or self._widget_type == 'slider':
            s += """<input type="text" name="%s" size=15 value="%s">""" % \
                 (self.name, value)
        elif self._widget_type == 'option':
            # we require values, which now contains the option values
            if self._values is None:
                raise TypeError(
                    "values attribute must be set for option menu '%s'" % \
                    self.name)

            s += """<select name="%s" size=1 value="%s">\n""" % \
                 (self.name, value)
            for v in self._values:
                s += """<option value="%s">%s </option>\n""" % \
                     (v,v)
            s += """</select><br>\n"""

        elif self._widget_type == 'checkbutton':
            s += """<input type="checkbox" name="%s" value="%s">"""\
                 """&nbsp; <br>\n""" % \
                 (self.name, value)

        return s

    def get(self):
        if self._form is not None:
            InputPrm.set(self,\
                self._form.getvalue(self.name, str(self._v)))
            # InputPrm.set handles units

        return self._v

    # just inherit def set(self, value):


    def __repr__(self):
        """Application of eval to this output creates the object."""
        return "InputPrmCGI(name='%s', default=%s, str2type=%s, "\
               "widget_type='%s', form=None, values=%s, "\
               "help=%s, unit=%s, cmlarg=%s)" % \
               (self.name, self.__str__(), self.str2type.__name__,
                self._widget_type, str(self._values),
                self.help, self.unit, self.cmlarg)


def createInputPrm(interface, name, default, str2type=None,
                   widget_type='entry', values=None,
                   parent=None, form=None,
                   help=None, unit=None, cmlarg=None):
    """Unified interface to parameter classes InputPrm/GUI/CGI."""
    if interface == '' or interface == 'plain':
        p = InputPrm(name=name, default=default,
                     str2type=str2type,
                     help=help, unit=unit, cmlarg=cmlarg)
    elif interface == 'GUI':
        p = InputPrmGUI(name=name, default=default,
                        str2type=str2type,
                        widget_type=widget_type,
                        values=values, parent=parent,
                        help=help, unit=unit, cmlarg=cmlarg)
    elif interface == 'CGI':
        p = InputPrmCGI(name=name, default=default,
                        str2type=str2type,
                        widget_type=widget_type,
                        values=values, form=form,
                        help=help, unit=unit, cmlarg=cmlarg)
    else:
        raise ValueError("interface '%s' not supported" % interface)

    return p

class Parameters:
    """
    Class for holding a set of InputPrm-type parameters.
    See src/py/examples/simviz/simviz1cp.py for examples
    on usage.

    Some attributes may be useful in application code:

    self.dict is a dictionary of InputPrm-type objects.

    self.parameters_sequence (and self._seq) is a list of
    InputPrm-type objects in the sequence they were registered.

    self.sliders_sequence is a list of InputPrm-type objects,
    with slider widget representation in a GUI, in the sequence
    they were registered.
    self.entries_sequence, self.checkbt_sequence,
    self.options_sequence are similar for text entries, checkbuttons,
    and option menus.

    The self.*_sequence lists can be used to build GUIs or CGI scripts.
    Normally, this is automated in classes like AutoSimVizGUI and
    AutoSimVizCGI.
    """
    def __init__(self, interface='plain', form=None, prm_dict={}):
        """
        @param interface: 'plain', 'CGI', or 'GUI'
        @param form: cgi.FieldStorage() object
        @param prm_dict: dictionary with (name,value) pairs
        (will be added using the add method)
        """

        self.dict = {}  # holds InputPrm/GUI/CGI objects
        self._seq = []  # holds self.dict items in sequence
        self._interface = interface
        self._form = form  # used for CGI
        for prm in prm_dict:
            self.add(prm, prm_dict[prm])

    def add(self, name, default, str2type=None,
            widget_type='entry', values=None,
            help=None, unit=None, cmlarg=None):
        """Add a new parameter."""
        self.dict[name] = createInputPrm(self._interface, name,
            default, str2type, widget_type=widget_type,
            values=values, help=help, unit=unit, cmlarg=cmlarg)
        self._seq.append(self.dict[name])

    def endadd(self):
        """Process parameters, make internal data structures."""
        self.parameters_sequence = self._seq
        if self._interface == 'GUI':
            self.sliders_sequence = []
            self.entries_sequence = []
            self.options_sequence = []
            self.checkbt_sequence = []
            for p in self._seq:
                if p.widget_type == 'slider':
                    self.sliders_sequence.append(p)  # add instance ref.
                elif p.widget_type == 'entry':
                    self.entries_sequence.append(p)
                elif p.widget_type == 'option':
                    self.options_sequence.append(p)
                elif p.widget_type == 'checkbutton':
                    self.checkbt_sequence.append(p)
                else:
                    raise ValueError('unknown widget_type "%s"' \
                                     % p.widget_type)
        elif self._interface == 'CGI':
            for p in self._seq:
                p.form = self._form

    def __setitem__(self, name, value):
        self.dict[name].set(value)
        if name in self.__dict__:  # is item attribute too (name2attr)?
            # self.__dict__[name] = value # will not handle string w/unit
            self.__dict__[name] = self.dict[name].get()

    def __getitem__(self, name):
        return self.dict[name].get()

    def keys(self):
        """
        Return parameter names. With this method Parameter objects p
        can be used in dictionary update functions: somedict.update(p).
        """
        return list(self.dict.keys())

    def __iter__(self):
        """Iterate over keys in self.dict."""
        # short cut using generator function
        for name in self.dict:
            yield name

    def get(self):
        """Return dictionary with (name,value) pairs."""
        d = {}
        for name in self:
            d[name] = self[name]  # same as self.dict[name].get()
        return d

    def name2attr(self):
        """
        Turn all item keys into attributes.
        Warning: values are copied! __setitem__ and
        __setattr__ (or properties) must
        take care of parallel updates.
        """
        for name in self.dict:
            self.__dict__[name] = self.dict[name].get()

    def __setattr__(self, name, value):
        """
        If name2attr is called, self.m = 2.3 (using this
        function) is safe, because this also implies update of
        the corresponding InputPrm-type object in self.dict.
        """
        self.__dict__[name] = value
        if name in self.dict:
            self.dict[name].set(value)
        #if str(a) in self.dict:
        #    self.dict[str(a)].set(value)

    def parse_options(self, argv):
        """
        Examine the command line and for each -opt val pair,
        set the value of parameter opt to val, if opt is a
        registered parameter.
        argv is typically sys.argv[1:]
        Note that the name of a parameter may contain blanks.
        A blank is replaced by two underscores in the command-line
        options.
        """
        p = scitools.misc.cmldict(argv, cmlargs=None, validity=0)
        # p[key] holds all command-line args, we are only interested
        # in those keys corresponding to self.dict.keys()
        for key in p.keys():
            if key.find('__') != -1:
                key_blanks = key.replace('__', ' ')
            else:
                key_blanks = key
            if key_blanks in self.dict:
                self.dict[key_blanks].set(p[key])

    def usage(self):
        """Print legal command-line options."""
        s = '' # returned message
        for p in self.dict:
            if p.find(' ') != -1:
                opt = p.replace(' ', '__')
            else:
                opt = p
            if self.dict[p].help is not None:
                s += '--' + '%-30s' % opt + ' ' + self.dict[p].help + '\n'
            else:
                s += '--' + opt + ' value '

        return s

    def dump(self):
        s = ''
        for p in self.dict:
            s += repr(self.dict[p]) + '\n'
        return s

    def __str__(self):
        return str(self.get())

    def __repr__(self):
        s = 'Parameters: interface="%s"\n' % self._interface
        for name in self.dict:
            s += repr(self.dict[name]) + '\n'
        return s



def parametersGUI(p, parent, pack_side='top',
                  scrolled={'height': 400, 'width': 350}):
    """
    Load all parameters in a Parameters object p into a GUI.

    parent          parent widget
    pack_side       packing is donw with
                    widget.pack(side=pack_side, expand=1, fill='both')
    scrolled        False: use standard Tk Frame
                    non-empty dict: use Pmw.ScrolledFrame with the
                    prescribed height and width
    """
    p.endadd()  # for safety
    if scrolled:
        frame = Pmw.ScrolledFrame(parent,
          usehullsize=1, hull_width=scrolled['width'],
                         hull_height=scrolled['height'])
        frame.pack(side=pack_side, fill='both', expand=1)
        frame = frame.interior()
    else:
        frame = Tkinter.Frame(parent, borderwidth=2)
        frame.pack(side=pack_side, fill='both', expand=1)

    widgets = []  # for alignment
    for obj in p.parameters_sequence:
        # must be set on beforehand: obj.widget_type = 'entry'
        if obj.widget_type is None:
            raise TypeError("widget_type attribute "\
                            "must be set for InputPrmGUI '%s'" % obj.name)
        obj.parent = frame
        obj.make_widget()
        #obj.widget.pack(side='top', padx=5, pady=5, fill='x', expand=1)
        obj.widget.pack(side='top', padx=5, pady=3, anchor='w')
        if obj.widget_type == 'entry' or \
               obj.widget_type == 'option':
            widgets.append(obj.widget)
    Pmw.alignlabels(widgets)  # nice alignment


class AutoSimVizGUI:
    """
    Organize a set of widgets for input data together with
    buttons for running a simulator and performing visualizations.
    The input data are represented by a Parameters object
    from the ParameterInterface module.
    The individual parameters in this object are represented as
    InputPrmGUI instances.
    The application code creates Parameters object
    (recall to call addend() after all parameters are registered).

    The method make_prmGUI takes the Parameters objects,
    makes the associated widgets and packs them in an appropriate
    GUI. All widgets may appear in one column, in the order the
    parameters were registered in the Parameters object, if
    sort_widgets is false. Otherwise, two column of widgets are
    made: one with sliders and one with the rest (checkbuttons,
    entries, options). The sequence of widgets in the latter case
    is determined by the sequence of registration in the Parameters,
    e.g., all sliders are grouped in their original sequence,
    all option menus are grouped in their original sequence, and so on.

    The method make_buttonGUI creates buttons for simulation and
    visualization, plus an optional logo and a help button.
    If more buttons are wanted, one can add these to the
    button_frame Tkinter.Frame attribute.

    There is an optional column of widgets with BLT graphs for
    curve plotting, enabled by the make_curveplotGUI method.

    The great advantage of this class is that the application code
    can concentrate on defining input parameters to a problem,
    the simulation and visualization functions, and leave it to
    this class to put everything together. It is then an easy task
    to change the layout of the whole GUI in one common place.
    """

    def __init__(self):
        from . import modulecheck
        modulecheck.exception("Class AutoSimVizGUI", 'Pmw', 'Tkinter')
        return

    def make_prmGUI(self,
                    parent,
                    parameters,
                    sort_widgets=0,
                    height=None,
                    pane=0
                    ):
        """
        The height parameter controls the height (in pixels) of
        the GUI.

        The columns are realized by Pmw.ScrolledFrame widgets.
        """

        self.p = parameters  # scitools.ParameterInterface.Parameters instance
        self.p.endadd()

        if sort_widgets:
            self.sliders_sequence = self.p.sliders_sequence
        else:
            self.sliders_sequence = None
        if sort_widgets:
            self.entries_sequence = self.p.entries_sequence
        else:
            self.entries_sequence = None
        if sort_widgets:
            self.options_sequence = self.p.options_sequence
        else:
            self.options_sequence = None
        if sort_widgets:
            self.checkbuttons_sequence = self.p.checkbt_sequence
        else:
            self.checkbuttons_sequence = None
        if not sort_widgets:
            self.parameters_sequence = self.p.parameters_sequence
        else:
            self.parameters_sequence = None


        self.master = parent
        self.top = Tkinter.Frame(self.master)
        self.top.pack(expand=1, fill='both')  # could be moved to pack method...
        self.top_columns = Tkinter.Frame(self.top)
        self.top_columns.pack(expand=1, fill='both')

        self.pane = pane
        if self.pane:
            self.top_pane = Pmw.PanedWidget(self.top_columns,
                                            orient='horizontal')
###                            hull_width=900, hull_height=600)
            self.top_pane.pack(expand=1, fill='both')

        if self.sliders_sequence is not None:
            # create a scrolled frame with a set of slider widgets
            # below each other:
            if self.pane:
                self.top_pane.add('sliders', min=340)
                parent = self.top_pane.pane('sliders')
            else:
                parent = self.top_columns
            self.sliders_frame = Pmw.ScrolledFrame(parent,
                usehullsize=1, hull_width=320, hull_height=height)
            self.sliders_frame.pack(side='left', fill='both', expand=1)
            self.sliders_frame = self.sliders_frame.interior()

            for obj in self.sliders_sequence:
                if obj.widget_type is None:
                    obj.widget_type = 'slider'
                obj.parent = self.sliders_frame
                obj.make_widget()
                obj.widget.pack(side='top', padx=5, pady=3,
                                fill='x', expand=1)

        if self.entries_sequence is not None or \
           self.options_sequence is not None or \
           self.checkbuttons_sequence is not None:
            if self.pane:
                self.top_pane.add('entries', min=175)
                parent = self.top_pane.pane('entries')
            else:
                parent = self.top_columns
            self.entries_frame = Pmw.ScrolledFrame(parent,
                usehullsize=1, hull_width=240, hull_height=height)
            self.entries_frame.pack(side='left', fill='both', expand=1)
            self.entries_frame = self.entries_frame.interior()

        widgets = []
        if self.entries_sequence is not None:
            for obj in self.entries_sequence:
                if obj.widget_type is None:
                    obj.widget_type = 'entry'
                obj.parent = self.entries_frame
                obj.make_widget()
                obj.widget.pack(side='top', padx=5, pady=3,
                                fill='x', expand=1, anchor='w')
                widgets.append(obj.widget)

        # add option menus under the entries in the second column:
        if self.options_sequence is not None:
            for obj in self.options_sequence:
                if obj.widget_type is None:
                    obj.widget_type = 'option'
                obj.parent = self.entries_frame
                obj.make_widget()
                obj.widget.pack(side='top', padx=5, pady=3, anchor='w')
                widgets.append(obj.widget)
        Pmw.alignlabels(widgets)  # nice alignment

        # add checkbuttons under the options/entries in the second column:
        if self.checkbuttons_sequence is not None:
            for obj in self.checkbuttons_sequence:
                if obj.widget_type is None:
                    obj.widget_type = 'checkbutton'
                obj.parent = self.entries_frame
                obj.make_widget()
                obj.widget.pack(side='top', padx=5, pady=3, anchor='w')

        if self.parameters_sequence is not None:
            if self.pane:
                self.top_pane.add('parameters', min=350)
                parent = self.top_pane.pane('parameters')
            else:
                parent = self.top_columns

            if height is None:
                height = min(len(self.parameters_sequence)*80, 700)

            parametersGUI(self.p, parent,
                         pack_side='left',
                         scrolled={'height':height, 'width':350})

        # note: if we use Pmw.ScrolledCanvas, call canvas.resizescrollregion()

    def make_buttonGUI(self, parent, buttons=[], logo=None, help=None):
        if self.pane:
            #self.top_pane.add('buttons', min=300)
            self.top_pane.add('buttons')
            parent = self.top_pane.pane('buttons')
        else:
            parent = self.top_columns
        self.button_frame = Tkinter.Frame(parent)
        self.button_frame.pack(side='left')

        # put a help button first:
        if type(help) is type(""):  # description given?
            self.description = help
            Tkinter.Button(self.button_frame, text="Help", width=10,
               command=self._helpwindow).\
               pack(side='top', padx=5, pady=3, anchor="n")


        if logo is not None:
            self.logo = Tkinter.PhotoImage(file=logo)
            Tkinter.Label(self.button_frame, image=self.logo).\
                         pack(side='top', pady=20)

        if buttons:
            for button_name, func in buttons:
                width = max(len(button_name), 10)
                Tkinter.Button(self.button_frame, text=button_name,
                           width=width, command=func).\
                           pack(side='top', padx=5, pady=3)

        self.master.bind('<q>', self._quit)
        if self.pane:
            self.top_pane.setnaturalsize()

    def make_curveplotGUI(self,
                          parent,
                          no_of_plotframes=1,
                          placement='right',
                          ):
        """
        @param parent: parent (master) widget
        @param no_of_plotframes: no of graph areas
        @param placement: placement of the plot area ('right' or 'bottom')

        Example on creating
        three plot areas to the right in the window::

          self.plot1, self.plot2, self.plot3 = \
              self.someGUI.make_curveplotGUI(parent, 3, 'right')
          self.plot1 etc. holds Pmw.Blt.Graph widgets.

        Create a single plot area::
          self.plot1 = self.someGUI.make_curveplotGUI(parent,
                                                      1, 'bottom')
        """
        if placement == 'right':
            if self.pane:
                self.top_pane.add('plot', size=300)
                parent = self.top_pane.pane('plot')
            else:
                parent = self.top_columns
            self.plotframe = Tkinter.Frame(parent)
            self.plotframe.pack(side='left', expand=1, fill='both')
            # size of plot canvas:
            width=400; total_height=500
        elif placement == 'bottom':
            self.plotframe = Tkinter.Frame(self.top)
            self.plotframe.pack(side='bottom', expand=1, fill='both')
            # size of plot canvas:
            width=None; total_height=no_of_plotframes*200

        height=int(total_height/float(no_of_plotframes))
        self.g = []
        for i in range(no_of_plotframes):
            try:
                self.g.append(Pmw.Blt.Graph(self.plotframe,
                                            width=width,height=height))
            except:
                print "Python is not linked with Blt"; sys.exit(1)
            # place the plot areas below each other:
            self.g[i].pack(side='top',expand=1, fill='both')

        # some dictionaries with self.g[i] as keys:
        self.data = {}  # holds (x,y) Blt vectors in a graph
        self.identifier = {} # holds curve identifiers (numbers) for each graph
        for graph in self.g:
            self.identifier[graph] = 0
        # when a new curve is drawn, the self.nsavecurves old ones
        # are still present
        self.nsavecurves = 2
        self.curvecolors = ('red', 'blue', 'green', 'yellow', 'black')

        if self.pane:
            self.top_pane.setnaturalsize()

        return self.g

    def load_curveplot(self, filename, graph, curvename=''):
        """
        Load data from a two-column file into x and y Blt vectors.
        graph is a Pmw.Blt.Graph widget, normally returned from
        make_curveplotGUI.

        x, y = self.someGUI.load_curveplot('my.dat', self.plot2,
                                        curvename='measured data')

        One can convert x and y, which are plain Python lists, to
        NumPy arrays for further processing if desired.
        """
        if isinstance(graph, (list,tuple)):
            if len(graph) != 1:
                raise TypeError(
                    'graph argument is a list of length %d>1, should be scalar' %\
                    len(graph))
            else:
                graph = graph[0]

        f = open(filename, 'r')

        self.identifier[graph] += 1  # identifiers are integers
        id = self.identifier[graph]
        # current storage index in an array [0,..,self.nsavecurves+1]
        counter = id % (self.nsavecurves+1)

        # The Blt vectors cannot be local variables, because the plot
        # disappears when the vectors go out of scope.
        # Letting the user handle these objects results in more user
        # code. On the other hand, we do not know how many vectors
        # we need. Remedy: use a dict. with graph as key and
        # one (x,y) pair of Blt vectors
        if graph not in self.data:
            self.data[graph] = {}
        self.data[graph][counter] = {}
        self.data[graph][counter]['x'] = Pmw.Blt.Vector()
        self.data[graph][counter]['y'] = Pmw.Blt.Vector()
        for line in f:
            numbers = line.split()
            self.data[graph][counter]['x'].append(float(numbers[0]))
            self.data[graph][counter]['y'].append(float(numbers[1]))
        f.close()

        # remove an old curve (save the last self.nsavecurves curves):
        id_old = id - self.nsavecurves - 1
        if graph.element_exists(str(id_old)):
            graph.element_delete(str(id_old))  # remove old curve
        # dash the old remaining curves:
        for i in range(max(id_old+1,1),id):
            graph.element_configure(str(i), linewidth=1)
        color = self.curvecolors[counter]

        graph.line_create(str(id),
                          label='',
                          xdata=self.data[graph][counter]['x'],
                          ydata=self.data[graph][counter]['y'],
                          linewidth=2, dashes='', symbol='',
                          color=color)
        # drop label, use title instead
        graph.configure(title=curvename)
        self.master.update()
        return self.data[graph][counter]['x'],\
               self.data[graph][counter]['y']

    def update_curveplot(self, filename, graph):
        """Update Blt vectors with data from a two-column file."""

        id = self.identifier[graph]
        counter = id % (self.nsavecurves+1)

        f = open(filename, 'r')
        lines = f.readlines()
        if len(lines) != len(self.data[graph][counter]['x']):
            print "Blt vector has length=%d, but %s has %d lines" % \
                  (len(self.data[graph][counter]['x']),len(lines))
        for i in range(len(self.data[graph][counter]['x'])):
            self.data[graph][counter]['x'][i], \
            self.data[graph][counter]['y'][i] = \
                                      list(map(float, lines[i].split()))
        f.close()

    def _quit(self, event=None):
        self.master.destroy()

    def _helpwindow(self):
        """
        Launch a separate toplevel window with a scrolled text widget
        containing self.description.
        """
        # read file into a text widget in a _separate_ window:
        self.filewindow = Tkinter.Toplevel(self.master) # new window

        lines = self.description.split('\n')
        nlines = min(len(lines),30)
        width = min(max([len(i) for i in lines]), 70) # max line width
        self.filetext = Pmw.ScrolledText(self.filewindow,
             borderframe=5, # a bit space around the text
             vscrollmode='dynamic', hscrollmode='dynamic',
             labelpos='n', label_text="Description",
             text_width=width, text_height=nlines,
             text_wrap='none')
        self.filetext.pack()

        self.filetext.insert('end', self.description)

        # add a quit button:
        Tkinter.Button(self.filewindow, text="Quit",
               command=self.filewindow.destroy).pack(pady=10)


class AutoSimVizCGI:
    """
    Organize a set of form variables for input data.
    """

    def __init__(self):
        return

    def make(self,
             form,
             parameters,
             CGI_script,
             imagefile=None,
             ):
        """
        Create an HTML page consisting of an optional
        image (specified by imagefile), a table of form variables
        (specified by parameters (scitools.ParameterInterface.Parameters)),
        and a "simulate and visualize" button.
        The resulting visualization part must be created after
        calling this function. Finally, the HTML page needs
        a footer (see the footer function).
        """

        self.p = parameters
        self.p.endadd()

        s = """
<html><body bgcolor="white">
"""
        if imagefile is not None:
            s += """<img src="%s" align="right"><p>""" % imagefile
        s += """
<form action="%s" method="post">
<table>
""" % CGI_script
        # should we have a help and/or dimension column?
        help = 0; unit = 0
        for p in self.p.parameters_sequence:
            if p.unit is not None: unit = 1
            if p.help is not None: help = 1
        for p in self.p.parameters_sequence:
            s += '<tr>\n<td>%s</td><td>%s</td>' % \
                 (p.name, p.make_form_entry())
            if unit:
                if p.unit is not None:
                    s += '<td>%s</td>' % p.unit
                else:
                    s += '<td></td>'  # empty
            if help:
                if p.help is not None:
                    s += '<td>(%s)</td>' % p.help
                else:
                    s += '<td></td>'  # empty

            s += '\n</tr>\n'
        s += """
</table><br>
<input type="submit" value="simulate and visualize" name="sim">
</form>
"""
        # perform simulation and visualization as next step
        #return s
        print s

    def footer(self):
        """Write out HTML footer instructions."""
        s = """\n</body></html>\n"""
        #return s
        print s

def _test1_Parameters():
    d = {'A': 1.0, 'w': 0.2, 'func': 'siny', 'y0': 0.0}
    p = Parameters(interface='GUI', prm_dict=d)
    p['w'] = 0.1
    p.add('tstop', 2.0, widget_type='slider', values=(0,10))
    p.add('plot', False)
    d = p.get()
    print d
    print repr(p)
    p['plot'] = True
    for name in p:
        print 'p[%s]=%s' % (name, p[name])
    return p

def _test1_Parameters_wGUI():
    parent = Tkinter.Tk()
    Pmw.initialise(parent)
    import scitools.misc
    scitools.misc.fontscheme1(parent)
    p = _test1_Parameters()
    parametersGUI(p, parent, scrolled=False)
    def get():
        print p.get()
    Tkinter.Button(parent, text='Dump', command=get).pack(pady=10)
    Tkinter.Button(parent, text='Quit', command=parent.quit).pack(pady=10)
    parent.mainloop()

if __name__ == '__main__':
    cmd = sys.argv[1] + '(' + '  '.join(sys.argv[2:]) + ')'
    print cmd
    exec(cmd)


"""
Notebook for selecting functions.
"""
import types
from scitools.numpyutils import seq, wrap2callable, ndarray, pi
from scitools.StringFunction import StringFunction

class FuncSpec:
    """
    Specification of a function.
    Lists of such specifications can be fed to class FunctionSelector
    to form a notebook where each page is designed according to the
    contents of a FuncSpec object.
    """

    def __init__(self,
                 representation,
                 name='',
                 parameters=None,
                 independent_variables=[],
                 formula=None,
                 image=None,
                 function_object=None,
                 vector = 0,
                 description=None,
                 xcoor=None,
                 scrolled_frame=False,
                 ):
        """
        Arguments:

        @param representation:  class Drawing, UserFunction, or
                                StringFormula
        @param name:            name of function
        @param parameters:      parameters in the function, either
                                dict or Parameters instance
        @param independent_variables: list/tuple of strings with the
                                names of the indep. variables.
        @param formula:         textual doc of function formula
        @param image:           filename of GIF image (LaTeX)
        @param function_object: callable object for evaluating the function
        @param vector:          0: scalar function, >0: no of vector comp.
        @param description:     more verbose description than formula
        @param xcoor:           array of coordinates for drawing
        @param scrolled_frame:  scrollbars in the notebook page, False
                                or dict: {'width': 300, 'height':200}

        Examples: see test_FunctionSelector in TkGUI.py.
        """
        self.name = name
        self.representation = representation
        if not self.name:
            raise ValueError('name keyword must be set when creating a '\
                             'FuncSpec object')

        self.configure(
            parameters=parameters,
            independent_variables=independent_variables,
            formula=formula,
            image=image,
            function_object=function_object,
            vector=vector,
            description=description,
            xcoor=xcoor,
            scrolled_frame=scrolled_frame)

    def configure(self, **kwargs):
        if 'parameters' in kwargs:
            self.parameters = kwargs['parameters']
        if self.parameters is not None:
            if isinstance(self.parameters, dict):
                self.parameters = \
                   Parameters(interface='GUI', prm_dict=self.parameters)
            if not isinstance(self.parameters, Parameters):
                raise TypeError(
                    'parameters must be a dictionary or Parameters object, '\
                    'not a %s' % type(self.parameters))

        if 'independent_variables' in kwargs:
            self.independent_variables = kwargs['independent_variables']
        if 'formula' in kwargs:
            self.formula = kwargs['formula']
        if 'image' in kwargs:
            self.image = kwargs['image']
        if 'function_object' in kwargs:
            self.function_object = kwargs['function_object']
            if type(self.function_object) == types.ClassType:
                raise TypeError(
                    'class type, not instance, provided as '\
                    'function_object for %s' % self.name)
        if 'vector' in kwargs:
            self.vector = kwargs['vector']
        if 'description' in kwargs:
            self.description = kwargs['description']
        if 'xcoor' in kwargs:
            self.xcoor = kwargs['xcoor']
        if 'scrolled_frame' in kwargs:
            self.scrolled_frame = kwargs['scrolled_frame']

        self.ok()  # check validity of arguments

    def ok(self):
        if not isinstance(self.independent_variables, (list, tuple)):
            raise TypeError(
                'independent_variables must be list or tuple, not %s' % \
                type(self.independent_variables))

        if self.formula is not None:
            if not isinstance(self.formula, str):
                raise TypeError(
                    'formula must be string, not %s' % type(self.formula))

        if self.image is not None:
            if not isinstance(self.image, str):
                raise TypeError(
                    'image must be string (filename), not %s' % \
                    type(self.image))
            if not os.path.isfile(self.image):
                raise ValueError('file %s not found' % self.image)

        if not isinstance(self.vector, int):
            raise TypeError(
                'vector must be int (0=scalar, >=1: no of vector comp.), '\
                'not %s' % type(self.vector))

        if self.description is not None:
            if not isinstance(self.description, basestring):
                raise TypeError(
                    'description must be string, not %s' % \
                    type(self.description))

        if self.xcoor is not None:
            if not isinstance(self.xcoor, ndarray):
                raise TypeError(
                    'xcoor must be a NumPy array, not %s' % type(self.xcoor))

        if self.scrolled_frame != False:
            if not isinstance(self.scrolled_frame, dict):
                raise TypeError('scrolled_frame must be True or dict, '\
                                'not %s' % type(self.scrolled_frame))


    def get_independent_variables(self):
        if not self.independent_variables:
            raise ValueError('FuncSpec for "%s" has no list of independent '\
                             'variables' % self.name)
        text = 'independent variable'
        if len(self.independent_variables) > 1:
            text += 's'
        text += ': ' + ', '.join(self.independent_variables)
        return text

    def __repr__(self):
        args = []
        for key in self.__dict__:
            if self.__dict__[key] is not None:
                args.append('%s=%s' % (key,self.__dict__[key]))
        return 'FuncSpec(' + ', '.join(args) + ')'


class StringFormula:
    def __init__(self, parent, func_spec):
        self.fspec = func_spec
        self.master = parent
        self.top = Tkinter.Frame(parent, borderwidth=2)
        self.top.pack(side='top')

        # note that StringFunction works for scalar and vector fields!
        # just use [formula_x, formula_y]

        self.formula = Tkinter.StringVar()
        if self.fspec.formula is not None:
            self.formula.set(self.fspec.formula)

        self.widget = Pmw.EntryField(self.top,
                      labelpos='n',
                      label_text=self.fspec.get_independent_variables(),
                      entry_width=15,
                      entry_textvariable=self.formula)
        self.widget.pack(pady=5)

        if self.fspec.parameters:
            parametersGUI(self.fspec.parameters, self.top,
                          scrolled=self.fspec.scrolled_frame)

    def get(self):
        """Return function object."""
        f = StringFunction(self.formula.get(),
            independent_variables=self.fspec.independent_variables)
        if self.fspec.parameters:
            # turn parameters object into dictionary and send
            # this as keyword arguments to StringFunction.set_parameters
            f.set_parameters(**self.fspec.parameters.get())
        return wrap2callable(f)



class UserFunction:
    def __init__(self, parent, func_spec):
        self.fspec = func_spec
        self.master = parent
        self.top = Tkinter.Frame(parent, borderwidth=2)
        self.top.pack(side='top')
        Tkinter.Label(self.top,
        text=self.fspec.get_independent_variables()).pack()
        if self.fspec.formula:
            width = min(len(self.fspec.formula)+5, 30)
            Tkinter.Label(self.top, text=self.fspec.formula,
                          width=width).pack()
        else:
            print 'Warning: UserFunction, name=%s, has no formula!' % \
                  self.fspec.name
            Tkinter.Label(self.top, text='no function expression known').pack()
        if self.fspec.parameters:
            print self.fspec.parameters, type(self.fspec.parameters)
            Tkinter.Label(self.top, text='parameters: ' +
                          ', '.join(self.fspec.parameters.keys())).pack()

        if self.fspec.image is not None:
            self.image = Tkinter.PhotoImage(file=self.fspec.image)
            Tkinter.Label(self.top, image=self.image).pack()

        # widgets for setting parameters:
        if self.fspec.parameters:
            parametersGUI(self.fspec.parameters, self.top,
                          pack_side='top',scrolled=self.fspec.scrolled_frame)

    def get(self):
        """Return function object."""
        # extract parameter values from the GUI?
        if self.fspec.parameters:
            d = self.fspec.parameters.get()  # dict of (name,value) pairs
            for name in d:
                try:
                    f = self.fspec.function_object
                except:
                    raise AttributeError(
                        'FuncSpec "%s" used in UserFunction has '\
                        'no function_object set' % self.fspec.name)
                if hasattr(f, name):
                    setattr(f, name, d[name])
                else:
                    raise NameError('expected parameter name %s '\
                                    'as attribute in function object '\
                                    '\n(dir(function object)=%s)' % \
                                    (name,dir(f)))
        return wrap2callable(self.fspec.function_object)


class Drawing(UserFunction):
    def __init__(self, parent, func_spec):
        UserFunction.__init__(self, parent, func_spec)
        if self.fspec.xcoor is None:
            raise ValueError('want DrawFunction widget, but no xcoor info'\
                             ' in the FuncSpec object')
        self.drawing = DrawFunction(self.fspec.xcoor, self.top)
        self.drawing.pack(padx=10, pady=10)

    def get(self):
        """Return function object."""
        x, y = self.drawing.get()
        d = wrap2callable((x,y))
        # The drawing function d may be combined with another
        # expression, forming a new function object. This functionality
        # is in a method 'embed' in self.func_spec.function_object.
        try:
            f = UserFunction.get(self)
            f.attach_func(d)
            d = f
        except:
            pass # no combination with other functions registered
        return d


class FunctionChoices:
    """
    Notebook for various representations of a function.
    The representations appear as pages. Each page is
    realized as a UserFunction, StringFormula, or Drawing
    instance.
    """
    def __init__(self, parent, func_spec_list):
        self.master = parent
        self.top = Tkinter.Frame(self.master, borderwidth=2)
        self.top.pack(expand=True, fill='both')
        self.nb = Pmw.NoteBook(self.top)
        self.func_spec_list = func_spec_list # list of FuncSpec objects
        # hold UserFunction, Drawing, or StringFormula objects,
        # one for each page (key is page name):
        self.page = {}

        for f in self.func_spec_list:
            # define a page:
            new_page = self.nb.add(f.name, tab_text=f.name)
            # group is a kind of frame widget with a solid border:
            group = Pmw.Group(new_page, tag_text=f.name)
            group.pack(fill='both', expand=1, padx=10, pady=10)
            # build contents in current page:
            self.page[f.name] = \
                          f.representation(group.interior(), f)

        self.nb.pack(padx=5, pady=5, fill='both', expand=1)
        self.nb.setnaturalsize()

    def get(self):
        """
        Return initialized function object corresponding to
        the currently selected notebook page.
        """
        # get user-chosen page name:
        current = self.nb.getcurselection()
        # get corresponding function object (self.page[current]
        # is a UserFunction, Drawing, or StringFunction instance):
        f = self.page[current].get()
        #from scitools.misc import dump
        #dump(f, hide_nonpublic=False)
        return f, current

class FunctionSelector:
    """
    Notebook with a collection of functions to be specified.
    Each function is represented by a FunctionChoices page.
    This page is again a notebook with pages corresponding to
    different ways of specifying a function:
    drawing, string formulas, ready-made formulas with
    free parameters, hardcoded Python functions etc.
    """
    def __init__(self, parent):
        self.master = parent
        self.top = Tkinter.Frame(self.master, borderwidth=2)
        self.top.pack(expand=True, fill='both')
        self.nb = Pmw.NoteBook(self.top)
        self.page = {}  # FunctionChoices widgets

    def add(self, name, func_spec_list):
        new_page = self.nb.add(name, tab_text=name)
        group = Tkinter.Frame(new_page, borderwidth=2)
        group.pack(expand=True, fill='both')
        w = FunctionChoices(group, func_spec_list)
        self.page[name] = w

    def pack(self, **kwargs):
        # pack notebook:
        self.nb.pack(padx=5, pady=5, fill='both', expand=1, **kwargs)
        self.nb.setnaturalsize()

    def select(self, name, page):
        """Select page under the name tab."""
        self.page[name].nb.selectpage(page)

    def get(self, name):
        """
        Return initialized function object corresponding to
        the page with the given name.
        """
        return self.page[name].get()
        #from scitools.misc import dump
        #dump(f, hide_nonpublic=False)


def _test_FunctionChoices(root):
    class MyFunc:
        def __init__(self, a, b):
            self.a = a;  self.b = b
        def __call__(self, q, t):
            return self.a*q + self.b*t

    F = FuncSpec
    nb = [F(Drawing, name='k coeff', xcoor=seq(0,1,0.01)),
          F(StringFormula, name='velocity',
            parameters={'A': 1, 'B': 1, 'p': 1, 'q': 1},
            formula='[-B*cos(q*y), A*sin(p*x)]',  # vector field
            independent_variables=('x', 'y'),
            vector=2),
          F(UserFunction, name='bc',
            parameters=('a', 'b'),
            formula='a*q + b*t',
            independent_variables=('q', 't'),
            function_object=MyFunc(0,0)),
          ]
    print nb
    gui = FunctionChoices(root, nb)
    Tkinter.Button(root, text='get',
                   # note that gui is local so obj=gui is needed to
                   # remember the gui object...
                   command=gui.get).pack(pady=5)
    root.mainloop()


def _test_FunctionSelector(root):
    """Two-level notebook. Top level: f, I, bc."""
    s = FunctionSelector(root)

    class MovingSource1:
        """Function object: A*exp(-(x - x0 - sin(w*t))**2)."""
        def __init__(self, A, w, x0):
            self.A = A; self.w = w; self.x0 = x0
        def __call__(self, x, t):
            return self.A*exp(-(x - self.x0 - sin(self.w*t))**2)
        def __str__(self):
            return 'A*exp(-(x - x0 - sin(w*t))**2)'
        def parameters(self):
            return {'A': self.A, 'w': self.w, 'x0': self.x0}


    def growing_source(x, t):
        A = 1; w  = 0.1; x0 = 5
        return A*(sin(w*t))**2*exp(-(x-x0)**2)

    class MovingSource2:
        """
        As MovingSource1, but let the user specify
        (through a drawing, for instance) the spatial shape f:
        f(x - x0 - sin(w*t)).
        """
        def __init__(self, w, x0):
            self.w = w; self.x0 = x0
            self.spatial_shape = lambda x: exp(-x*x)
        def attach_func(self, spatial_shape):
            self.spatial_shape = spatial_shape
        def __call__(self, x, t):
            return self.spatial_shape(x - self.x0 - sin(self.w*t))
        def __str__(self):
            return 'f(x - x0 - sin(w*t))'
        def parameters(self):
            return {'w': self.w, 'x0': self.x0}

    ms1 = MovingSource1(1, 1, 5)
    ms2 = MovingSource2(1, 5)

    F = FuncSpec  # short form
    f = [F(UserFunction, name='moving source 1',
           independent_variables=('x', 't'),
           formula=str(ms1),
           function_object=ms1,
           parameters=ms1.parameters()),
         F(UserFunction, name='growing source 1',
           independent_variables=('x', 't'),
           formula='A*(sin(w*t))**2*exp(-(x-x0)**2); A=1, w=0.1',
           function_object=growing_source),
         F(Drawing, name='moving source 2',
           independent_variables=('x', 't'),
           description='spatial shape f(x) can be drawn',
           function_object=ms2,
           parameters=ms2.parameters(),
           formula=str(ms2),
           xcoor=seq(0,10,0.1),),
         F(StringFormula, name='growing source 2',
           parameters={'A': 1.0, 'w': 1.0, 'x0': 0},
           formula='A*(sin(w*t))**2*exp(-(x-x0)**2)',
           independent_variables=('x', 't')),
         F(UserFunction, name='no source',
           independent_variables=('x', 't'),
           formula='f(x,t)=0',
           function_object=lambda x,t: 0),
         ]
    s.add('f', f)

    class GaussianBell:
        """Gaussian Bell at x0 with st.dev. sigma."""
        def __init__(self, x0, sigma):
            self.x0 = x0; self.sigma = sigma
        def __call__(self, x):
            return exp(-0.5*((x-self.x0)/self.sigma)**2)
        def __str__(self):
            return 'exp(-0.5*((x-x0)/sigma)**2)'
        def parameters(self):
            return {'x0': self.x0, 'sigma': self.sigma}

    gb = GaussianBell(5,1)
    I = [F(UserFunction, name='localized disturbance',
           function_object=gb,
           independent_variables=['x'],
           parameters=gb.parameters()),
         F(Drawing, name='draw initial shape',
           independent_variables=['x'],
           xcoor=seq(0,10,0.1),)
         ]
    s.add('initial condition', I)

    class OscHalfPeriod:
        """Oscillate sin(w*t) half a period, then hold zero."""
        def __init__(self, w):
            self.w = w
        def __call__(self, t):
            T = pi/self.w
            if t <= T:
                return sin(self.w*t)
            else:
                return 0.0
        def __str__(self):
            return 'sin(w*t) for t<pi/w, otherwise 0'
        def parameters(self):
            return {'w': self.w}

    half_period = OscHalfPeriod(pi/2)
    bc = [F(UserFunction, name='1 period oscillation',
            independent_variables=('t',),
            function_object=half_period,
            formula=str(half_period),
            parameters=half_period.parameters()),
          F(UserFunction, name='fixed ends',
            independent_variables=('t',),
            function_object=lambda x: 0,
            formula='u=0 at the ends',),
          ]
    s.add('boundary conditions', bc)
    s.pack()

    def get():
        f_func, page = s.get('f')
        I_func, page = s.get('initial condition')
        bc_func, page = s.get('boundary conditions')
        from scitools.misc import dump
        print 'f_func:'
        dump(f_func, hide_nonpublic=False)
        print 'I_func:'
        dump(I_func, hide_nonpublic=False)
        print 'bc_func:'
        dump(bc_func, hide_nonpublic=False)

    Tkinter.Button(root, text='get',
                   command=get).pack(pady=5)
    root.mainloop()


def _FunctionSelector_test():
    root = Tkinter.Tk()
    Pmw.initialise(root)
    import scitools.misc
    scitools.misc.fontscheme6(root)
    root.title('FunctionSelector notebook demo')
    _test_FunctionSelector(root)



class FuncDependenceViz:
    """
    Visualization of the shape of a function depends
    continuously on its parameters, and this class
    makes a graphical illustration of this dependence.

    """
    def __init__(self, master,
                 parameter_intervals={}, # interval for each prm
                 functions={},           # functions to be plotted
                 xmin=0.0, xmax=1.0,     # x axis range
                 resolution=101,         # no of x evaluations
                 width=500, height=400,  # size of plot window
                 viztool = 'Pmw.Blt.Graph', # or 'gnuplot'
                 plot_update = 'after'   # how slider movements
                                         # update the plots
                 ):
        """
        Define a set of functions depending on a set of parameters.
        This class creates a GUI where the parameters can be adjusted,
        and the effect on the function graphs can be seen immediately.
        """
        import scitools.modulecheck as sm
        sm("TkGUI module:", 'Pmw', 'Tkinter', 'Gnuplot', 'numpy')

        Gnuplot = import_module('Gnuplot')
        self.Gnuplot = Gnuplot
        self.master = master
        self.top = Tkinter.Frame(master, borderwidth=2)
        self.top.pack()  # could leave this pack for a pack class function

        self.p_intervals = parameter_intervals
        self.funcs = functions  # f_i(x; p_1,...p_n)

        self.p = {}           # values of the parameters
        self.slider_var = {}  # Tkinter vars for slide.p
        for pname in self.p_intervals:
            # set parameter value to midpoint in interval:
            self.p[pname] = (self.p_intervals[pname][0] + \
                             self.p_intervals[pname][1])/2.0
            self.slider_var[pname] = Tkinter.DoubleVar()
            self.slider_var[pname].set(self.p[pname])

        # define the sliders:
        for pname in self.p_intervals:
            pmin = self.p_intervals[pname][0]
            pmax = self.p_intervals[pname][1]
            slider = Tkinter.Scale(self.top,
                           orient='horizontal',
                           from_=pmin,
                           to=pmax,
                           tickinterval=(pmax-pmin)/10.0,
                           resolution=(pmax-pmin)/100.0,
                           label=pname,
                           font="helvetica 10 bold",
                           length=width-100,
                           variable=self.slider_var[pname])
            slider.pack(side='top', pady=4)

            # we can update the plot according to slider
            # movements in two ways: during movement
            # (command= option) or after movement (event binding)
            if plot_update == 'after':
                slider.bind('<ButtonRelease-1>', self.visualize)
            else:
                slider.configure(command=self.visualize)
            # does not work: slider.bind('<B1-Motion>', self.visualize)

        # define a widget row where xmin/xmax and n can be adjusted:
        self.xmin = Tkinter.DoubleVar(); self.xmin.set(xmin)
        self.xmax = Tkinter.DoubleVar(); self.xmax.set(xmax)
        self.n = Tkinter.IntVar(); self.n.set(resolution)

        row = Tkinter.Frame(self.top, borderwidth=2)
        row.pack()
        Tkinter.Label(row, text="x min:").pack(side='left')
        Tkinter.Entry(row, textvariable=self.xmin, width=5,
                      justify='right').pack(side='left')
        Tkinter.Label(row, text="  x max:").pack(side='left')
        Tkinter.Entry(row, textvariable=self.xmax, width=5,
                      justify='right').pack(side='left')
        Tkinter.Label(row, text="  no of points:").pack(side='left')
        Tkinter.Entry(row, textvariable=self.n, width=3,
                      justify='right').pack(side='left')

        # make graph widget or use a plotting program?
        try:
            # see if we can create a BLT graph successfully:
            self.g = Pmw.Blt.Graph(self.top,
                                   width=width, height=height)
            have_blt = 1
        except:
            have_blt = 0

        self.viztool = viztool  # user-specified plotting tool

        print have_blt, viztool
        if have_blt and viztool == "Pmw.Blt.Graph":
            self.g.pack(expand=1, fill='both')
        else:
            # we do not have BLT or the user has not requested BLT:
            self.g = self.Gnuplot.Gnuplot(persist=1)

        self.dx = 0  # new vectors must be made if the x incr. changes
        self.make_vectors()  # vectors for x and y values in plot

        # PostScript plot:
        Tkinter.Button(row, text="Postscript plot",
                       command=self.psdump).pack(side='left',padx=5)
        # bind 'p' to dumping the plot in PostScript:
        # (must bind to master, not self.top)
        self.master.bind('<p>', self.psdump)
        self.master.bind('<q>', self.quit)  # convenient

    def psdump(self, event=None):
        import tkFileDialog
        fname = tkFileDialog.SaveAs(
                filetypes=[('psfiles','*.ps')],
                initialfile="tmp.ps",
                title="Save plot in PostScript format").show()
        if fname:
            if self.viztool == "gnuplot":
                self.g.hardcopy(filename=fname, enhanced=1,
                                mode='eps', color=0,
                                fontname='Times-Roman', fontsize=28)
            elif self.viztool == "Pmw.Blt.Graph":
                self.g.postscript_output(fileName=fname,
                                         decorations='no')

    def quit(self, event=None):
        "kill plot window"
        self.master.destroy()

    def make_vectors(self):
        "make x vector and a dictionary of y vectors"
        # self.x : vector of x coordinates
        # self.y[funcname] : vector of function values

        dx = (self.xmax.get() - self.xmin.get())/\
             float(self.n.get() - 1)
        if dx != self.dx:
            self.dx = dx
            # x increment has changed, make new vectors:

            # add dx/2 to upper limit to ensure self.n entries:
            x = arange(self.xmin.get(), self.xmax.get()+dx/2, dx, float)
            if x.shape[0] != self.n.get():
                raise IndexError("x has wrong length")
            self.x = x

            self.y = {}
            for funcname in self.funcs:
                self.y[funcname] = zeros(x.shape[0],float)

            if self.viztool == "Pmw.Blt.Graph":
                self.bind_vectors2BLTgraph()

            # fill the vectors with appropriate data for testing:
            self.fill_vectors()


    def bind_vectors2BLTgraph(self):
        "bind vectors to the curves in the BLT graph"
        # each curve has its own color:
        colors = ['red','blue','green','black','grey',
                  'black','yellow','orange']
        if len(self.funcs) > len(colors):
            print "Cannot handle more than %d functions"\
                  % len(self.funcs); sys.exit(1)
        color_counter = 0
        for curvename in self.funcs:
            if self.g.element_exists(curvename):
                self.g.element_delete(curvename)
            self.g.line_create(
                curvename,           # used as identifier
                xdata=tuple(self.x),            # x coords
                ydata=tuple(self.y[curvename]), # y coords
                color=colors[color_counter],
                linewidth=1,
                dashes='',           # number: dash, "": solid
                label=curvename,     # legend
                symbol='',           # no symbols at data points
                )
            color_counter += 1

    def visualize(self, var):
        for pname in self.p:
            self.p[pname] = self.slider_var[pname].get()
        self.make_vectors()
        self.fill_vectors()

        title = ""
        for pname in self.p:
            title  += "%s=%g " % (pname,self.p[pname])

        if self.viztool == "gnuplot":
            self.g.clear()
            self.g("set xrange [%g:%g]" % (self.xmin.get(),
                                           self.xmax.get()))
            self.g.title(title)
            # we do not launch the plot here
            plots = []; line_counter=1
            for funcname in self.funcs:
                plots.append(self.Gnuplot.Data(
                    self.x, self.y[funcname],
                    with_="line %d" % line_counter))
                line_counter += 1
            self.g.plot(*tuple(plots))
        elif self.viztool == "Pmw.Blt.Graph":
            # BLT graph commands:
            self.g.xaxis_configure(min=self.xmin.get(),
                                   max=self.xmax.get())
            for curvename in self.funcs:
                self.g.element_configure(
                    curvename, ydata=tuple(self.y[curvename]))
            self.g.update()
            self.g.configure(title=title)

    def fill_vectors(self):
        for funcname in self.funcs:
            # slow loop over NumPy array...
            for i in range(self.n.get()):
                x = self.x[i]
                self.y[funcname][i] = \
                     self.funcs[funcname](x, self.p)



def _test_FuncDependenceViz():
    import math
    p_intervals = {'mu': (0,8), 'sigma': (0,1), 'alpha': (0,1)}

    # recall that lambda is a reserved keyword in Python,
    # use lambda_ instead:
    def lognormal(x, lambda_, zeta):
        if x < 1.0E-9:
            f = 0.0
        else:
            f = 1/(zeta*math.sqrt(2*math.pi)*x)*math.exp(
                -0.5*((math.log(x)-lambda_)/zeta)**2)
        return f

    def U(x, p):
        mu = p['mu']; sigma = p['sigma']
        zeta = math.sqrt(math.log(1 + (sigma/mu)**2))
        lambda_ = math.log(mu) - 0.5*0.5*zeta**2
        return lognormal(x, lambda_, zeta)

    def F(x, p):
        mu = p['mu']; sigma = p['mu']; alpha = p['alpha']
        zeta = math.sqrt(math.log(1 + (sigma/mu)**2))
        lambda_ = math.log(mu) - 0.5*0.5*zeta**2
        # response modification:
        lambda_ = math.log(alpha) + 2*lambda_
        zeta = 2*zeta
        return lognormal(x, lambda_, zeta)

    f = { 'U': U, 'F': F }   # function names and objects

    root = Tkinter.Tk()
    Pmw.initialise(root)
    try:
        viztool = sys.argv[1]
    except:
        viztool = 'gnuplot'  # alternative: Pmw.Blt.Graph
    try:
        update = sys.argv[2]
    except:
        update = 'after'  # alternative: arbitrary (cont. update)
    gui = FuncDependenceViz(root, p_intervals, f,
                            xmin=0, xmax=8,
                            resolution=40,
                            viztool=viztool,
                            plot_update=update)
    root.mainloop()


def _test():
    print 'Testing DrawFunction:'
    _test_DrawFunction()
    print 'Testing CanvasCoords:'
    _CanvasCoords_test()
    print 'Testing FunctionSelector:'
    _FunctionSelector_test()
    print 'Testing ParameterInterface:'
    _test1_Parameters()
    _test1_Parameters_wGUI()
    print 'Testing FuncDependenceViz:'
    _test_FuncDependenceViz()

if __name__ == '__main__':
    _test()
