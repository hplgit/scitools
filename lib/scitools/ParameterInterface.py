#!/usr/bin/env python
"""
Utilities for holding and displaying data about input parameters.
"""
import sys, re
from cmldict import cmldict
import modulecheck
import scitools.misc

try:
    import Pmw, Tkinter
    import Scientific.Physics.PhysicalQuantities as PQ
except:
    pass
    # tests on which modules that are missing are done
    # in the constructor of the classes


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
                raise ValueError, \
                'unit=%s is an illegal physical unit' % str(self.unit)
            if self.str2type is float or self.str2type is int:
                pass  # must have float or int when units are present
            else:
                raise ValueError, \
                'str2type must be float or int, not %s' % str(self.str2type)

        self.set(default)  # set parameter value
        modulecheck.exception('InputPrm constructor', 'Scientific')

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
                    raise ValueError, '%s should be %s; illegal syntax' % \
                          (v, self.str2type.__name__)
                if not self.pq.isCompatible(self.unit):
                    raise ValueError, \
                    'illegal unit (%s); %s is registered with unit %s' % \
                    (v, self.name, self.unit)
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
                    raise ValueError, \
                    'parameter %s given with dimension: %s, but '\
                    'dimension is not registered' % (self.name,v)
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
            raise AttributeError, 'parameter %s has no registered unit' % \
                  self.name

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
    from cmldict import cmldict
    p = cmldict(sys.argv[1:], cmlargs=None, validity=0)
    # p[key] holds all command-line args, we are only interested
    # in those keys corresponding to parameters.keys()
    for key in p.keys():
        if key in parameters.keys():
            parameters[key].set(p[key])



class InputPrmGUI(InputPrm):
    """Represent an input parameter by a widget."""

    GUI_toolkit = 'Tkinter/Pmw'

    def __init__(self, name=None, default=0.0, str2type=None, 
                 widget_type='entry', values=None, parent=None,
                 help=None, unit=None, cmlarg=None):
        """
        default           default value
        str2type          function from string to type
        name              name of parameter
        widget_type       entry, slider, option, checkbutton
        values            (min,max) interval or options
        parent            parent widget
        help              description of parameter
        unit              physical unit (dimension)
        cmlarg            command-line argument for sending
                          this prm to an external program
        """
        if str2type is None: 
            str2type = scitools.misc.str2obj

        # bind self._v to an object with get and set methods
        # for assigning and extracting the parameter value
        # in the associated widget:
        if InputPrmGUI.GUI_toolkit.startswith('Tk'):
            # use Tkinter variables
            self.make_GUI_variable_Tk(str2type, unit)
        else:
            raise ValueError, \
                  'The desired GUI toolkit %s is not supported' % \
                  InputPrmGUI.GUI_toolkit
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

    def make_GUI_variable_Tk(self, str2type, unit):
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
            elif str2type == int or str2type == str2bool:
                self._v = Tkinter.IntVar()
                self._validate = {'validator' : 'int'}
            elif str2type == complex:
                self._v = Tkinter.StringVar()
            else:
                raise ValueError, \
                'str2type %s for parameter %s is not supported' % \
                (str2type, name)

    def make_widget(self):
        if InputPrmGUI.GUI_toolkit.startswith('Tk'):
            self.make_widget_Tk()
        else:
            raise ValueError, \
                  'The desired GUI toolkit %s is not supported' % \
                  InputPrmGUI.GUI_toolkit

    def make_widget_Tk(self):
        """Make Tk widget according to self._widget_type."""
        if self.name is None:
            raise TypeError, "name attribute must be set before "\
                  "widget can be created"
        if self.parent is None:
            raise TypeError, "parent attribute must be set before "\
                  "widget can be created"
        # consistency/type check of values, if it is supplied:
        if self._values is not None:
            if type(self._values) != type([]) and \
               type(self._values) != type(()):
                raise TypeError, "values attribute must be list or tuple"

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
                raise TypeError, \
                      "values attribute must be set for slider '%s'" % \
                      self.name

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
                raise TypeError, \
                      "values attribute must be set for option menu '%s'" % \
                      self.name

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
            
        return self.str2type(self._scan(gui))
        
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
            raise TypeError, "name attribute must be set before "\
                  "widget can be created"

        value = str(self.get())
        
        s = ""  # HTML code to be returned is stored in s
        if self._widget_type == 'entry' or self._widget_type == 'slider':
            s += """<INPUT TYPE="text" NAME="%s" SIZE=15 VALUE="%s">""" % \
                 (self.name, value)
        elif self._widget_type == 'option':
            # we require values, which now contains the option values
            if self._values is None:
                raise TypeError, \
                      "values attribute must be set for option menu '%s'" % \
                      self.name

            s += """<SELECT NAME="%s" SIZE=1 VALUE="%s">\n""" % \
                 (self.name, value)
            for v in self._values:
                s += """<OPTION VALUE="%s">%s </OPTION>\n""" % \
                     (v,v)
            s += """</SELECT><BR>\n"""
            
        elif self._widget_type == 'checkbutton':
            s += """<INPUT TYPE="checkbox" NAME="%s" VALUE="%s">"""\
                 """&nbsp; <BR>\n""" % \
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
        raise ValueError, "interface '%s' not supported" % interface
    
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
        interface         'plain', 'CGI', or 'GUI'
        form              cgi.FieldStorage() object
        prm_dict          dictionary with (name,value) pairs
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
                    raise ValueError, 'unknown widget_type "%s"' \
                          % p.widget_type
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
        return self.dict.keys()
    
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
        p = cmldict(argv, cmlargs=None, validity=0)
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
            raise TypeError, "widget_type attribute "\
                  "must be set for InputPrmGUI '%s'" % obj.name
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
        import modulecheck
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
        parent            parent (master) widget
        no_of_plotframes  no of graph areas
        placement         placement of the plot area
                          ('right' or 'bottom')

        Example:
        Create three plot areas to the right in the window.
        self.plot1, self.plot2, self.plot3 = \
            self.someGUI.make_curveplotGUI(parent, 3, 'right')
        self.plot1 etc. holds Pmw.Blt.Graph widgets.

        Create a single plot area:
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
                raise TypeError, \
                'graph argument is a list of length %d>1, should be scalar' %\
                len(graph)
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
                                      map(float, lines[i].split())
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
<HTML><BODY BGCOLOR="white">
"""
        if imagefile is not None:
            s += """<IMG SRC="%s" ALIGN="right"><P>""" % imagefile
        s += """
<FORM ACTION="%s" METHOD="POST">
<TABLE>
""" % CGI_script
        # should we have a help and/or dimension column?
        help = 0; unit = 0
        for p in self.p.parameters_sequence:
            if p.unit is not None: unit = 1
            if p.help is not None: help = 1
        for p in self.p.parameters_sequence:
            s += '<TR>\n<TD>%s</TD><TD>%s</TD>' % \
                 (p.name, p.make_form_entry())
            if unit:
                if p.unit is not None:
                    s += '<TD>%s</TD>' % p.unit
                else:
                    s += '<TD></TD>'  # empty
            if help:
                if p.help is not None:
                    s += '<TD>(%s)</TD>' % p.help
                else:
                    s += '<TD></TD>'  # empty
                
            s += '\n</TR>\n'
        s += """
</TABLE><BR>
<INPUT TYPE="submit" VALUE="simulate and visualize" NAME="sim">
</FORM>
"""
        # perform simulation and visualization as next step
        #return s
        print s

    def footer(self):
        """Write out HTML footer instructions."""
        s = """\n</BODY></HTML>\n"""
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
