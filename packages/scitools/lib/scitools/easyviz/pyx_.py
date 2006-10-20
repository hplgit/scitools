from common import *
import pyx 

class pyxBackend(BaseClass):
    """
    Check pyx reference for furter tweaking:
    http://pyx.sourceforge.net/manual/index.html
    """
    def __init__(self):
        BaseClass.init(self)
        self.init()
        
    def init(self):
        self._line_types = {
            '-': pyx.style.linestyle.solid,
            '--': pyx.style.linestyle.dashed,
            '-.': pyx.style.linestyle.dashdotted,
            ':': pyx.style.linestyle.dotted
            }
        
        self._line_markers = {
            # '.': #???,
            'v': pyx.graph.style.symbol.diamond,
            '+': pyx.graph.style.symbol.plus,
            's': pyx.graph.style.symbol.square,
            'x': pyx.graph.style.symbol.cross,
            '^': pyx.graph.style.symbol.triangle,
            'o': pyx.graph.style.symbol.circle
            }
        
        self._line_colors = {
            'k': pyx.graph.style.color.cmyk.Black,
            'r': pyx.graph.style.color.cmyk.Red,
            'g': pyx.graph.style.color.cmyk.Green,
            'b': pyx.graph.style.color.cmyk.Blue,
            'y': pyx.graph.style.color.cmyk.Yellow, 
            'm': pyx.graph.style.color.cmyk.Magenta,
            'c': pyx.graph.style.color.cmyk.Cyan,
            #'w': Nobody wants white
            }
    
    def _replot(self, *args, **kwargs):
        fig = self._figs[self._attrs['curfig']]
        scale = fig.get('scale')
        
        #If axis lock
        if fig.get('movie') in ['on']:
            xmin = fig.get('xmin')
            xmax = fig.get('xmax')
            ymin = fig.get('ymin')
            ymax = fig.get('ymax')
            
            #Use defined axis range
            if scale in ['linear']:
                _x = pyx.graph.axis.lin(min=xmin, max=xmax,
                                      title=fig.get('xlabel'))
                _y = pyx.graph.axis.lin(min=ymin, max=ymax,
                                      title=fig.get('ylabel'))

            elif scale in ['logx']:
                _x = pyx.graph.axis.log(min=xmin, max=xmax,
                                      title=fig.get('xlabel'))
                _y = pyx.graph.axis.lin(min=ymin, max=ymax,
                                      title=fig.get('ylabel'))
                
            elif scale in ['logy']:
                _x = pyx.graph.axis.lin(min=xmin, max=xmax,
                                      title=fig.get('xlabel'))
                _y = pyx.graph.axis.log(min=ymin, max=ymax,
                                      title=fig.get('ylabel'))
                
            elif scale in ['logx']:
                _x = pyx.graph.axis.log(min=xmin, max=xmax,
                                      title=fig.get('xlabel'))
                _y = pyx.graph.axis.log(min=ymin, max=ymax,
                                      title=fig.get('ylabel'))
            else:
                raise Exception, "scale is wrong."
                                    
        else:
            if scale in ['linear']:
                _x = pyx.graph.axis.lin(title=fig.get('xlabel'))
                _y = pyx.graph.axis.lin(title=fig.get('ylabel'))
                
            elif scale in ['logx']:
                _x = pyx.graph.axis.log(title=fig.get('xlabel'))
                _y = pyx.graph.axis.lin(title=fig.get('ylabel'))
                
            elif scale in ['logy']:
                _x = pyx.graph.axis.lin(title=fig.get('xlabel'))
                _y = pyx.graph.axis.log(title=fig.get('ylabel'))
                
            elif scale in ['logx']:
                _x = pyx.graph.axis.log(title=fig.get('xlabel'))
                _y = pyx.graph.axis.log(title=fig.get('ylabel'))
            else:
                raise Exception, "scale is wrong"                          
            

        h = 5; w = 10 # width must be passed
        #fig._g=pyx.graph.graphxy(width=w,x=_x,y=_y) # No legend
        
        fig._g = pyx.graph.graphxy(width=w, x=_x, y=_y,
                                   key=pyx.graph.key.key(pos="tr"))
        self._g = fig._g
        _g = fig._g  # The global pointer
        d = [] # Store x and y data on a format pyx understands
        self.style = []
        
        for line in fig.lines:
            # Since it is possible to have different lines together with
            # markers at datapoints...
            style = []
            try:
                pyxsymbol = pyx.graph.style.symbol(
                    self._line_markers[line.get('marker')],
                    self._line_colors[line.get('color')]
                    )
                style.append(pyxsymbol)
            except:
                pass
            try:
                pyxline = pyx.graph.style.line(lineattrs=[
                    self._line_types[line.get('line_type')],
                    self._line_colors[line.get('color')]
                    ])
                style.append(pyxline)
            except:
                pass

            # The above styles are broken in pyx when data.list is used
            # (the error won't show up until hardcopy is issued).
            # Therefore use one of the following styles instead
            """                         
[pyx.graph.style.symbol(pyx.graph.style.symbol.circle,
                        symbolattrs=[pyx.deco.filled])] 

pyx.graph.style.symbol(pyx.graph.style.symbol.circle,
                       symbolattrs=[pyx.deco.stroked([pyx.color.rgb.red]),
                                    pyx.deco.filled([color.rgb.green])] )

# Test of thin dashed lines with circles at data points
[pyx.graph.style.line(lineattrs=[pyx.style.linewidth.Thin,
                                 pyx.style.linestyle.dashed]),
 pyx.graph.style.symbol(pyx.graph.style.symbol.circle,
                        symbolattrs=[pyx.deco.filled])
 ]

[pyx.graph.style.line()]

pyx.graph.style.line([pyx.color.palette.Rainbow])

pyx.graph.style.line(lineattrs=[pyx.style.linewidth.Thick]))

pyx.graph.style.line(lineattrs=pyx.canvas.style.linestyle.solid))#['black']))

[pyx.graph.style.rect(pyx.color.palette.Rainbow)]
"""
            style = [pyx.graph.style.line(
                lineattrs=[pyx.style.linewidth.Thin,
                           pyx.style.linestyle.dashed
                           ]),
                     pyx.graph.style.symbol(pyx.graph.style.symbol.circle,
                                            symbolattrs=[pyx.deco.filled]),
                     ]

            # How does tranpose of a list work???
            x = line.get('x')
            y = line.get('y')
            b = []
            for i in range(len(x)):
                b.append([x[i],y[i]])
                #[[1, 3], [2, 4], [3, 3], [4, 4]]
            d.append(b)
                
            title = line.get('legend')
            if len(title) == 0:
                self._g.plot(pyx.graph.data.list(d[-1], x=1, y=2), style)
            else:
                self._g.plot(pyx.graph.data.list(d[-1], x=1, y=2, title=title),
                             style)
            self.style.append(style)
            
        # Place title centered at top
        # "normalsize", "large", "Large", "LARGE", "huge", "Huge"
        # pyx.text.halign.: right , left, center
        textstyle = [pyx.text.size.large, pyx.text.halign.center]
        pos = self._g.vpos(0.5,1.05) # convert to graph coords from unit range
        self._g.text(pos[0],pos[1], fig.get('title'), textstyle)


        #self.d = d # For debugging
        #self._g.writeEPSfile("temp_rolvpyx")
                
    def hardcopy(self, filename="pyxoutput"):
        self._replot()
        self._g.writeEPSfile(filename)
        
plt = pyxBackend()
use(plt,globals()) # Export public namespace of plt to globals()

def get_backend():
    return plt._g
