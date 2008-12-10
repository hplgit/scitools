#!/usr/bin/env python
"""
Interactive drawing of y=f(x) functions.
The drawing takes place in a Pmw.Blt.Graph widget.
"""
import Pmw, Tkinter, os

class DrawFunction:
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
            raise AttributeError, 'No drawing! Draw the curve first!'
    

def points2grid(x, y, xcoor):
    "transform points (x,y) to a uniform grid with coordinates xcoor"
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
            raise ValueError, "bug"
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
            

if __name__ == '__main__':
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
