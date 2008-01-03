"""
Module containing class FuncDependenceViz for visualizing how
the shape of a function depends continuously on its parameters.

"""

try:
    import Pmw, Tkinter, Gnuplot
    from numpy import *
except:
    pass

class FuncDependenceViz:
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
        import modulecheck
        modulecheck.exception("FuncDependenceViz module:",
                              'Pmw', 'Tkinter', 'Gnuplot', 'Numeric')
        
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
            self.g = Gnuplot.Gnuplot(persist=1)

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
                raise IndexError, "x has wrong length"
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
                plots.append(Gnuplot.Data(
                    self.x, self.y[funcname],
                    with="line %d" % line_counter))
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



def _test():
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

    root=Tkinter.Tk()
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

if __name__ == '__main__':
    _test()
