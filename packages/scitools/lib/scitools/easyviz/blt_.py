from common import *
import Pmw

class BltBackend(BaseClass):
    """
    Backend using Blt through Pmw (Python Mega Widgets)

    The Pmw.Blt tutorial is located at
    http://folk.uio.no/hpl/Pmw.Blt/doc/

    The documentation of the module is located here
    http://folk.uio.no/hpl/Pmw.Blt/doc/reference.html
    """
    
    def __init__(self, master=None):
        BaseClass.__init__(self)
        self.init(master)
        
    def init(self, master):
        self._symboldict = {'s':"square",
                            'o': "circle",
                            'v': "triangle",
                            '+':"plus",
                            'x': "cross",
                            '^':"triangle",
                            'd':"diamond",
                            # Some extra styles must be casted
                            '.':"splus",    # dot --> small cross
                            '*':"scross",   # star --> Large cross
                            'v':"triangle", # triangle (down) --> triangle
                            '<':"triangle", # triangle (left) --> triangle
                            '>':"triangle", # triangle (right)--> triangle
                            'p':"diamond",  # pentagram --> diamond
                            'h':"diamond"}  # hexagram  --> diamond
                
        self._colordict={'y':'yellow',
                         'm':'magenta',
                         'c':'cyan',
                         'r':'red',
                         'g':'green',
                         'b':'blue',
                         'w':'white',
                         'k':'black'}
         
        if master == None:
            #master = Tkinter.Tk()
            master = Pmw.initialise()
            #master = Pmw.MegaToplevel()
        self._master = master

        #self._master.withdraw()  #Hide window
        
        notebook = Pmw.NoteBook(self._master)
        notebook.pack(fill='both', expand=1, padx=10, pady=10)
        page = notebook.add('Fig 1')
        notebook.tab('Fig 1').focus_set()
        self._notebook = notebook
        self._g = Pmw.Blt.Graph(page)
        self._g.pack(expand=1, fill='both')
        self.set(interactive=True)
        
    def figure(self, *args):
        BaseClass.figure(self, *args)
        _fig = self._figs[self._attrs['curfig']]
        name = 'Fig '+str(self._attrs['curfig'])
        
        try:
            self._g = _fig._g
        except:
            try: self._notebook.delete(name)
            except: pass
            newpage = self._notebook.add(name)
            _fig._g = Pmw.Blt.Graph(newpage)
            self._g = _fig._g
            self._g.pack(expand = 1,fill = 'both')
            
        self._notebook.tab(name).focus_set()
        
    def _replot(self):
        # create graph with label, x-data, and y-data
        _fig = self._figs[self._attrs['curfig']]
        i = 1
        for line in _fig.lines:
            legend = line.get('legend')
            if legend == '':
                legend = 'line '+str(i)
            line.set(x=tuple(line.get('x')))
            line.set(y=tuple(line.get('y')))
            name = str(i)  #Identifying name
            #Force new linking each time
            if self._g.element_exists(name):
                self._g.element_delete(name)

            # Dictionary for backends plot command 
            plotkwargs = {'xdata':line.get('x'),
                          'ydata':line.get('y'),
                          #'color':color,
                          'label':line.get('legend'),
                          #'dashes':dashes,
                          #'symbol':symbol,
                          #'linewidth':linewidth,
                          #'pixels':pixels
                          }


            if line.get('marker'):
                symbol = self._symboldict[line.get('marker')]
                plotkwargs['symbol'] = symbol
                if line.get('pointsize'):
                    plotkwargs['pixels'] = pointsize
            elif line.get('line_type'): # No marker if line_type is set
                plotkwargs['symbol'] = ""
            
            #Set linewidth
            linewidth = line.get('linewidth')
            if not linewidth:
                linewidth = 2 # Change this if size is specified
                linewidth = 1

            """Doc on how dashed is implemented:
            Sets the dash style of element line.
            Dashes is a tuple of up to 11 numbers that alternately represent
            the lengths of the dashes and gaps on the element line.
            Each number must be between 1 and 255. If dashes is "", the lines
            will be solid.
            """
            # Set linetype if specified 
            linetype = line.get('line_type')
            if linetype in(None, ""):
                dashes = ""
                if line.get('marker'): # marker only
                    linewidth = 0
            else:
                if linetype == '-':   
                    dashes = ""
                elif linetype == ':':   # Dotted
                    dashes = linewidth*1, linewidth*5
                elif linetype == '-.':  # Dashdotted
                    dashes = linewidth*1, linewidth*5, \
                             linewidth *5, linewidth*5
                elif linetype == '--':  # Dashed
                    dashes = linewidth *5, linewidth*5
                
                plotkwargs['dashes'] = dashes
            plotkwargs['linewidth'] = linewidth
                
                    
            # Set color
            colordict = {'y':'yellow', 'm':'magenta', 'c':'cyan', 'r':'red',\
                       'g':'green', 'b':'blue', 'w':'white', 'k':'black'}
            try:
                color = self._colordict[line.get('color')]
                plotkwargs['color']=color
            except:
                pass
            
            self._g.line_create(
                name,
                **plotkwargs
                #xdata=line.get('x'),
                #ydata=line.get('y'),
                #color=color,
                #label=line.get('legend'),
                #dashes=dashes,
                #symbol=symbol,
                #linewidth=linewidth,
                #pixels=pixels
                )
            i = i+1
        del(i)
            
        # Set axis range
        fail = False
        for item in ['xmin', 'xmax']:
            if isinstance(_fig.get(item), (float, int)) and _fig.get(item):
                pass
            else:
                fail = True
        
        if not fail:
            self._g.axis_configure('x',
                                   min=_fig.get('xmin'),  
                                   max=_fig.get('xmax')  
                                   )
        fail = False
        for item in ['ymin', 'ymax']:
            if isinstance(_fig.get(item), (float, int)) and _fig.get(item):
                pass
            else:
                fail = True
        
        if not fail:       
            self._g.axis_configure('y',
                                   min=_fig.get('ymin'), 
                                   max=_fig.get('ymax')
                                   )
            
        
        # Set titles
        self._g.axis_configure('x', title=_fig.get('xlabel'))
        self._g.axis_configure('y', title=_fig.get('ylabel'))
        self._g.configure(title=_fig.get('title'))

        # Set correct logscale
        scale = _fig.get('scale')
        if scale == 'linear':
            self._g.axis_configure('x', logscale=0)
            self._g.axis_configure('y', logscale=0)
        elif scale == 'logy':
            self._g.axis_configure('x', logscale=0)
            self._g.axis_configure('y', logscale=1)
        elif scale == 'logx':
            self._g.axis_configure('x', logscale=1)
            self._g.axis_configure('y', logscale=0)
        elif scale == 'loglog':
            self._g.axis_configure('x', logscale=1)
            self._g.axis_configure('y', logscale=1)
        else:
            raise Exception, "Illegal scale"
        
        self._g.update  #Check if any of the data have changed
        #self.show()

    def hardcopy(self, filename="tmp.ps", *args, **kwargs):
        self._replot()

        if 'color' in kwargs:
            self.set(color=kwargs['color'])
        
        if self.get('color'):
            colormode="color"
        else:
            colormode="gray"
            
        self._g.postscript_configure(
            center=0,                    
            colormode=colormode,              
            decorations=0)                 
        # ps = g.postscript_output()        # get the ps-code
        self._g.postscript_output(filename)    
        
    def show(self):
        # Useful for noninteractive python sessions
        self._master.mainloop()

plt = BltBackend()
use(plt,globals()) # Export public namespace of plt to globals()

def get_backend():
    return plt._g
