#!/usr/bin/env python
"""
Notebook for selecting functions.
"""

import Pmw, Tkinter, os, types
from scitools.numpyutils import seq, wrap2callable, ndarray, pi
from DrawFunction import DrawFunction
from StringFunction import StringFunction
from ParameterInterface import Parameters, parametersGUI

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

        representation          class Drawing, UserFunction, or
                                StringFormula
        name                    name of function
        parameters=None         parameters in the function, either
                                dict or Parameters instance
        independent_variables=[] list/tuple of strings with the
                                names of the indep. variables.
        formula=None            textual doc of function formula
        image=None              filename of GIF image (LaTeX)
        function_object=None    callable object for evaluating the
                                function
        vector=0                0: scalar function
                               >0: no of vector comp.
        description=None        more verbose description than formula
        xcoor=None              array of coordinates for drawing
        scrolled_frame=False    scrollbars in the notebook page, False
                                or dict: {'width': 300, 'height':200}

        Examples:
        see test_FunctionSelector in FunctionSelector.py.
        """
        self.name = name
        self.representation = representation
        if not self.name:
            raise ValueError, \
                  'name keyword must be set when creating a '\
                  'FuncSpec object'
        
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
                raise TypeError, \
                  'parameters must be a dictionary or Parameters object, '\
                  'not a %s' % type(self.parameters)

        if 'independent_variables' in kwargs:
            self.independent_variables = kwargs['independent_variables']
        if 'formula' in kwargs:
            self.formula = kwargs['formula']
        if 'image' in kwargs:
            self.image = kwargs['image']
        if 'function_object' in kwargs:
            self.function_object = kwargs['function_object']
            if type(self.function_object) == types.ClassType:
                raise TypeError, \
                'class type, not instance, provided as '\
                'function_object for %s' % self.name
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
            raise TypeError, \
                  'independent_variables must be list or tuple, not %s' % \
                  type(self.independent_variables)

        if self.formula is not None:
            if not isinstance(self.formula, basestring):
                raise TypeError, \
                      'formula must be string, not %s' % type(self.formula)

        if self.image is not None:
            if not isinstance(self.image, basestring):
                raise TypeError, \
                      'image must be string (filename), not %s' % \
                      type(self.image)
            if not os.path.isfile(self.image):
                raise ValueError, 'file %s not found' % self.image

        if not isinstance(self.vector, int):
            raise TypeError, \
                  'vector must be int (0=scalar, >=1: no of vector comp.), '\
                  'not %s' % type(self.vector)

        if self.description is not None:
            if not isinstance(self.description, basestring):
                raise TypeError, \
                      'description must be string, not %s' % \
                      type(self.description)

        if self.xcoor is not None:
            if not isinstance(self.xcoor, ndarray):
                raise TypeError, \
                      'xcoor must be a NumPy array, not %s' % type(self.xcoor)

        if self.scrolled_frame != False:
            if not isinstance(self.scrolled_frame, dict):
                raise TypeError, 'scrolled_frame must be True or dict, '\
                      'not %s' % type(self.scrolled_frame)
            

    def get_independent_variables(self):
        if not self.independent_variables:
            raise ValueError, \
                  'FuncSpec for "%s" has no list of independent '\
                  'variables' % self.name
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
                    raise AttributeError, \
                          'FuncSpec "%s" used in UserFunction has '\
                          'no function_object set' % self.fspec.name
                if hasattr(f, name):
                    setattr(f, name, d[name])
                else:
                    raise NameError, 'expected parameter name %s '\
                          'as attribute in function object '\
                          '\n(dir(function object)=%s)' % (name,dir(f))
        return wrap2callable(self.fspec.function_object)


class Drawing(UserFunction):
    def __init__(self, parent, func_spec):
        UserFunction.__init__(self, parent, func_spec)
        if self.fspec.xcoor is None:
            raise ValueError, \
                  'want DrawFunction widget, but no xcoor info'\
                  ' in the FuncSpec object'
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
        

def test_FunctionChoices(root):
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


def test_FunctionSelector(root):
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


if __name__ == '__main__':
    root = Tkinter.Tk()
    Pmw.initialise(root)
    import scitools.misc
    scitools.misc.fontscheme6(root)
    root.title('FunctionSelector notebook demo')
    test_FunctionSelector(root)
