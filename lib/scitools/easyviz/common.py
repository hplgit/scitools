import pickle, os, operator, pprint

from scitools.numpyutils import seq, iseq, asarray, ones, zeros, sqrt, shape, \
     ravel, meshgrid, rank, squeeze, reshape, ndgrid, size, ndarray
from scitools.globaldata import backend

from .misc import _check_xyz, _check_xyuv, _check_xyzuvw, _check_xyzv, \
     _check_size, _check_type, _toggle_state, _update_from_config_file

from warnings import warn


def docadd(comment, *lists, **kwargs):
    """
    Format a string, intended to be appended to or inserted in a doc
    string, containing a comment and a nicely formatted sequence of
    lists. Typically used for adding lists of options to a doc string,
    where the lists of options are available as static list data in
    a class.

    Example on usage:
    # add to the class doc string:
    __doc__ += docadd('Keywords for the setp method', list(_local_attrs.keys()))

    # add to a method (get) doc string:
    get.__doc__ += docadd('Keywords for the setp method',
                          list(BaseClass._local_attrs.keys()),
                          list(SomeSubClass._local_attrs.keys()))
    """
    lst = []
    for l in lists:
        lst.extend(l)
    lst.sort()
    s = '\n' + comment + ':\n'
    s += ' ' + pprint.pformat(lst)[1:-1]  # strip off leading [ and trailing ]
    # add indent:
    indent = kwargs.get('indent', 4)
    indent = ' '*indent
    lines = s.split('\n')
    for i in range(2,len(lines)):  # skip first 2 lines (heading)
        if lines[i].strip() != '':
            lines[i] = indent + '- ' + lines[i]  # add - for list syntax in some markup languages
    s = '\n'.join(lines)
    return s


class MaterialProperties(object):
    """
    Storage of various properties for a material on a PlotProperties object.
    """
    _local_prop = {
        'opacity': None,
        'ambient': None,
        'diffuse': None,
        'specular': None,
        'specularpower': None,
        }
    _update_from_config_file(_local_prop)  # get defaults from scitools.cfg
    __doc__ += docadd('Keywords for the setp method', list(_local_prop.keys()))

    def __init__(self, **kwargs):
        self._prop = {}
        self._prop.update(self._local_prop)
        self.setp(**kwargs)

    def __str__(self):
        return pprint.pformat(self._prop)

    def setp(self, **kwargs):
        for key in self._prop:
            if key in kwargs:
                _check_type(kwargs[key], key, (int,float))
                self._prop[key] = float(kwargs[key])

    def getp(self, name):
        try:
            return self._prop[name]
        except:
            raise KeyError('%s.getp: no parameter with name "%s"' % \
                           (self.__class__.__name__, name)        )


class PlotProperties(object):
    """
    Storage of various properties needed for plotting, such as line types,
    surface features, contour values, etc.
    Different subclasses (Line, Surface, Contours) are specialized
    for different kinds of plots.

    All properties are stored in the dictionary self._prop.

    """
    _colors  = "b r g m c y k w".split()  # colororder determines unset colors
    _markers = "o s v + ^ x d * < > p h .".split()
    _colors2markers = dict([(color, marker)
                      for color, marker in zip(_colors, _markers)])
    _linestyles = ": -. -- -".split()
    _sizes = "1 2 3 4 5 6 7 8 9".split()
    _styledoc = {'y': 'yellow',
                 'm': 'magenta',
                 'c': 'cyan',
                 'r': 'red',
                 'g': 'green',
                 'b': 'blue',
                 'w': 'white',
                 'k': 'black',

                 '.': 'point',
                 'o': 'circle',
                 'x': 'x-mark',
                 '+': 'plus',
                 '*': 'star',
                 's': 'square',
                 'd': 'diamond',
                 'v': 'triangle (down)',
                 '^': 'triangle (up)',
                 '<': 'triangle (left)',
                 '>': 'triangle (right)',
                 'p': 'pentagram',
                 'h': 'hexagram',

                 '-': 'solid',
                 ':': 'dotted',
                 '-.':'dashdot',
                 '--':'dashed',
                 }
    __doc__ += 'Valid symbols::\n      - Colors: %s\n      - Markers: %s\n      - Linestyles: %s\n      - Sizes: %s\n      - Styles:\n%s' % (_colors, _markers, _linestyles, _sizes, pprint.pformat(_styledoc)[1:-1])

    _local_prop = {
        'description': '',
        'legend': '',
        'xlim': (0,0), 'ylim': (0,0), 'zlim': (0,0),
        'dims': (0,0,0),
        'numberofpoints': 0,
        'function': '', # the function that created this item
        'linecolor': '',
        'linewidth': '',
        'linetype': '',
        'linemarker': '',
        'facecolor': '',
        'edgecolor': '',
        'pointsize': 1.0,
        'material': None,
        'memoryorder': 'yxz',  # FIXME: this is deprecated and will be removed
        'indexing': 'ij',  # 'xy' is Cartesian indexing, 'ij' matrix indexing
        'default_lines': 'with_markers'  # 'plain'
        }
    _update_from_config_file(_local_prop)  # get defaults from scitools.cfg
    __doc__ += docadd('Keywords for the setp method', list(_local_prop.keys()))

    def __init__(self, **kwargs):
        self._prop = {}
        self._prop.update(PlotProperties._local_prop)
        self._prop['material'] = MaterialProperties()

    def __str__(self):
        props = {}
        for key in self._prop:
            prop = self._prop[key]
            if isinstance(prop, (list,tuple,ndarray)) and \
                   len(ravel(prop)) > 3:
                props[key] = '%s with shape %s' % (type(prop), shape(prop))
            else:
                props[key] = self._prop[key]
        return pprint.pformat(props)

    # repr is maybe not smart since
    # >>> plot(...)
    # will then return Line, Surface,
    # etc which automatically gets printed.
    # Better to make a dump function
    # that one can call on the current figure f.ex.
    #def __repr__(self):
    #    return self.__str__()

    def dump(self):
        """Dump the parameters of this object."""
        return str(self)

    def setp(self, **kwargs):
        """
        Set plot properties.

        The method adds the argument value to the self._prop
        (if the value is legal).
        """
        if 'description' in kwargs:
            descr = kwargs['description']
            self._prop['description'] = descr
            # descr is on the form 'mesh: 3D mesh' (say)
            self._prop['function'] = descr.split(':')[0]

        if 'legend' in kwargs:
            self._prop['legend'] = str(kwargs['legend'])

        if 'linewidth' in kwargs:
            _check_type(kwargs['linewidth'], 'linewidth', (float,int))
            self._prop['linewidth'] = float(kwargs['linewidth'])

        if 'linecolor' in kwargs:
            color = kwargs['linecolor']
            if isinstance(color, str) and color in self._colors:
                self._prop['linecolor'] = color
            elif isinstance(color, (list,tuple)) and len(color) == 3:
                self._prop['linecolor'] = color
            else:
                raise ValueError("linecolor must be '%s', not '%s'" % \
                                 (self._colors, kwargs['linecolor']))

        if 'linetype' in kwargs:
            if kwargs['linetype'] in self._linestyles:
                self._prop['linetype'] = kwargs['linetype']
            else:
                raise ValueError("linetype must be '%s', not '%s'" % \
                                 (self._linestyles, kwargs['linetype']))

        if 'linemarker' in kwargs:
            if kwargs['linemarker'] in self._markers:
                self._prop['linemarker'] = kwargs['linemarker']
            else:
                raise ValueError("linemarker must be '%s', not '%s'" % \
                                 (self._markers, kwargs['linemarker']))

        if 'facecolor' in kwargs:
            self._prop['facecolor'] = kwargs['facecolor']

        if 'edgecolor' in kwargs:
            self._prop['edgecolor'] = kwargs['edgecolor']

        if 'memoryorder' in kwargs:
            msg = "Keyword argument 'memoryorder' is deprecated and will be " \
                  "removed in the future. Please use the 'indexing' keyword " \
                  "argument instead."
            warn(msg, DeprecationWarning)
            if kwargs['memoryorder'] == 'xyz':
                self._prop['indexing'] = 'ij'
                self._prop['memoryorder'] = 'xyz'
            elif kwargs['memoryorder'] == 'yxz':
                self._prop['indexing'] = 'xy'
                self._prop['memoryorder'] = 'yxz'
            else:
                raise ValueError("memoryorder must be 'xyz' or 'yxz', not %s"\
                                 % kwargs['memoryorder'])

        if 'indexing' in kwargs:
            if kwargs['indexing'] in ['xy', 'ij']:
                self._prop['indexing'] = kwargs['indexing']
            else:
                raise ValueError("indexing must be 'xy' or 'ij', not '%s'" \
                                 % kwargs['indexing'])

        # set material properties:
        self._prop['material'].setp(**kwargs)

    def getp(self, prm_name=None):
        """
        Return the value of the parameter with name prm_name.
        If the name is None, the dictionary with all parameters
        is returned.
        """
        if prm_name == 'memoryorder':
            msg = "Keyword argument 'memoryorder' is deprecated and will be " \
                  "removed in the future. Please use the 'indexing' keyword " \
                  "argument instead."
            warn(msg, DeprecationWarning)

        if prm_name is None:
            return self._prop
        else:
            try:
                return self._prop[prm_name]
            except:
                #raise KeyError('%s.getp: no parameter with name "%s"' % \
                #               (self.__class__.__name__, prm_name))
                return None

    def setformat(self, format):
        """
        Extract the right values for color, linetype, marker, etc. given
        a Matlab-like format string for a curve (e.g., 'r-').
        The extracted values are stored in self._prop (with keys like
        'linecolor', 'linetype', etc.).

        Erroneous chars will be ignored.
        When there are multiple format characters for a property, the last
        one will count.
        """
        if isinstance(format,str) and len(format) > 0:
            color = ""
            linetype = ""
            marker = ""
            linewidth = ""
            pointsize = ""
            # Notice that '--' and '-.' are before '-' in the _linestyles
            # alphabet.

            for item in self._linestyles:
                if item in format:
                    linetype = item
                    break

            for item in format:
                if item in self._colors:
                    color = item
                elif item in self._markers:
                    if item == '.':
                        if ('.' in linetype) and (format.count('.') == 1):
                            pass
                        else:
                            marker = item # same as '.'
                    else:
                        marker = item
                elif item in self._sizes:
                    # this int describes pointsize or linewidth
                    self._prop['pointsize'] = item
                    self._prop['linewidth'] = item

            if color in self._colors or color == "":
                self._prop['linecolor'] = color
            else:
                print "Illegal line color choice, %s is not known" % color
            if linetype != "" or marker != "":
                if linetype in self._linestyles:
                    self._prop['linetype'] = linetype
                elif linetype == "":
                    self._prop['linetype'] = linetype # Since marker is known
                else:
                    print "Illegal line style choice, %s is not known" % \
                          linetype
                if marker in self._markers:
                    self._prop['linemarker'] = marker
                elif marker == "":
                    self._prop['linemarker'] = marker # Since linetype is known
                else:
                    print "Illegal line marker choice, %s is not known" % \
                          marker

    def get_limits(self):
        """
        Return limits on the x, y, and z axis:
        xmin, xmax, ymin, ymax, zmin, zmax.
        """
        return self._prop['xlim']+self._prop['ylim']+self._prop['zlim']

    def _set_lim(self, a, name, adj_step=0.03):
        if isinstance(a, ndarray):
            try:
                amin = a.min()
                amax = a.max()
            except ValueError:
                amin = min(ravel(a))
                amax = max(ravel(a))
        else:
            amin = min(a)
            amax = max(a)
        if (amax - amin) == 0:
            #print 'empty %s-range [%g,%g], adjusting to [%g,%g]' % \
            #      (name[0], amin, amax, amin-adj_step, amax+adj_step)
            amin -= adj_step;  amax += adj_step
        self._prop[name] = (amin,amax)


class Line(PlotProperties):
    """
    Storage of information about lines in curve plots.
    """
    _local_prop = {
        'xdata': None,
        'ydata': None,
        'zdata': None,
        }
    __doc__ += docadd('Keywords for the setp method',
                      list(PlotProperties._local_prop.keys()),
                      list(_local_prop.keys()))

    def __init__(self, *args, **kwargs):
        PlotProperties.__init__(self, **kwargs)
        self._prop.update(Line._local_prop)
        self.setp(**kwargs)

    def setp(self, **kwargs):
        """
        Set line properties. Legal keyword arguments: x, y, format.
        The x and y arguments hold the x and y points of a curve.
        The format string is just passed on to setformat, which parses the
        contents and sets the format information.
        """
        PlotProperties.setp(self, **kwargs)

        # Here x,y values can be any SequenceType
        # The proper casting should be in the backends plotroutine

        if 'z' in kwargs:
            if not operator.isSequenceType(kwargs['z']):
                raise TypeError("Can only plot sequence types, "\
                                "z is %s" % type(kwargs['z']))
            z = kwargs['z']
            if 'format' in kwargs:
                self.setformat(kwargs['format'])
            if 'y' in kwargs:  # will only set y variable if z is set
                if isinstance(kwargs['y'], basestring) \
                       and kwargs['y'] == 'auto':
                    # now y is the indicies of z
                    y = list(range(len(z)))
                else:
                    if not operator.isSequenceType(kwargs['y']):
                        raise TypeError("Can only plot sequence types, "\
                                        "y is %s" % type(kwargs['y']))
                    y = kwargs['y']
            if 'x' in kwargs:  # will only set x variable if y is set
                if isinstance(kwargs['x'], basestring) \
                       and kwargs['x'] == 'auto':
                    # now x is the indicies of y
                    x = list(range(len(y)))
                else:
                    if not operator.isSequenceType(kwargs['x']):
                        raise TypeError("Can only plot sequence types, "\
                                        "x is %s" % type(kwargs['x']))
                    x = kwargs['x']

            # Consitency check
            assert size(x) == size(y), \
                   'Line.setp: x has size %d, expected y to have size %d, ' \
                   'not %d' % (size(x),size(x),size(y))
            assert size(x) == size(z), \
                   'Line.setp: x has size %d, expected z to have size %d, ' \
                   'not %d' % (size(x),size(x),size(z))

            self._set_data(x, y, z)

        elif 'y' in kwargs:
            if not operator.isSequenceType(kwargs['y']):
                raise TypeError("Can only plot sequence types, "\
                                "y is %s" % type(kwargs['y']))
            y = kwargs['y']
            if 'format' in kwargs:
                self.setformat(kwargs['format'])
            if 'x' in kwargs:  # will only set x variable if y is set
                if isinstance(kwargs['x'], basestring) \
                       and kwargs['x'] == 'auto':
                    # now x is the indicies of y
                    x = list(range(len(y)))
                else:
                    if not operator.isSequenceType(kwargs['x']):
                        raise TypeError("Can only plot sequence types, "\
                                        "x is %s" % type(kwargs['x']))
                    x = kwargs['x']

            # Consitency check
            assert size(x) == size(y), \
                   'Line.setp: x has size %d, expected y to have size %d, ' \
                   'not %d.' % (size(x),size(x),size(y))

            self._set_data(x, y)

    def _set_data(self, x, y, z=None):
        self._set_lim(x, 'xlim')
        self._set_lim(y, 'ylim')
        self._prop['xdata'] = x
        self._prop['ydata'] = y
        self._prop['dims'] = (len(x), 1, 1)
        self._prop['numberofpoints'] = len(x)
        if z is not None:
            self._set_lim(z, 'zlim')
            self._prop['zdata'] = z
            self._prop['dims'] = (len(x), len(y), 1)


class Bars(PlotProperties):
    """
    Properties of bars in bar graphs.
    """
    _local_prop = {
        'xdata': None,
        'ydata': None,
        'barwidth': 0.8,
        'barstepsize': 1.0,
        'barticks': None,
        'rotated_barticks': False,
        }
    __doc__ += docadd('Keywords for the setp method',
                      list(PlotProperties._local_prop.keys()),
                      list(_local_prop.keys()))

    def __init__(self, *args, **kwargs):
        PlotProperties.__init__(self, **kwargs)
        self._prop.update(Bars._local_prop)
        self.setp(**kwargs)
        self._parseargs(*args)

    def setp(self, **kwargs):
        PlotProperties.setp(self, **kwargs)

        if 'barwidth' in kwargs:
            self._prop['barwidth'] = float(kwargs['barwidth'])

        if 'barstepsize' in kwargs:
            self._prop['barstepsize'] = float(kwargs['barstepsize'])

        if 'barticks' in kwargs:
            self._prop['barticks'] = kwargs['barticks']

        if 'rotated_barticks' in kwargs:
            self._prop['rotated_barticks'] = bool(kwargs['rotated_barticks'])

    def _parseargs(self, *args):
        # allow both bar(...,LineSpec,width) and bar(...,width,LineSpec):
        for i in range(2):
            arg = args[-1]
            if isinstance(arg, str) and arg in self._colors:
                self._prop['linecolor'] = arg
                args = args[:-1]
            elif isinstance(arg, (float,int)):
                self._prop['barwidth'] = float(arg)
                args = args[:-1]
        nargs = len(args)
        if nargs == 2:    # bar(x,Y)
            x = args[0]
            y = args[1]
            self._prop['barticks'] = x
        elif nargs == 1:  # bar(Y)
            y = args[0]
            if isinstance(y, dict):
                a = []
                keys = list(y.keys())
                keys.sort()
                for key in keys:
                    a.append(list(y[key].values()))
                self._prop['barticks'] = keys
                y = asarray(a)
            x = list(range(len(y)))
        else:
            raise TypeError("Bars._parseargs: wrong number of arguments")

        self._set_data(x, y)

    def _set_data(self, x, y):
        if x is None:
            pass
        self._set_lim(x, 'xlim')
        self._set_lim(y, 'ylim')
        self._prop['xdata'] = asarray(x)
        self._prop['ydata'] = asarray(y)
        n = len(x)
        self._prop['dims'] = (n, 1, 1)
        self._prop['numberofpoints'] = n


class Surface(PlotProperties):
    """
    Properties of surfaces in scalar field plots.
    """
    _local_prop = {
        'cdata': None,
        'wireframe': True,
        'contours': None,
        'xdata': None,
        'ydata': None,
        'zdata': None,
        }
    __doc__ += docadd('Keywords for the setp method',
                      list(PlotProperties._local_prop.keys()),
                      list(_local_prop.keys()))

    def __init__(self, *args, **kwargs):
        PlotProperties.__init__(self, **kwargs)
        self._prop.update(Surface._local_prop)
        self.setp(**kwargs)
        self._parseargs(*args)

        if self._prop['function'] in ['meshc', 'surfc']:
            self._prop['contours'] = Contours(self._prop['xdata'],
                                              self._prop['ydata'],
                                              self._prop['zdata'],
                                              **kwargs)

    def setp(self, **kwargs):
        PlotProperties.setp(self, **kwargs)

        if 'wireframe' in kwargs:
            self._prop['wireframe'] = _toggle_state(kwargs['wireframe'])

    def _parseargs(self, *args):
        kwargs = {'indexing': self._prop['indexing']}
        nargs = len(args)
        if nargs >= 3 and nargs <= 4: # mesh(X,Y,Z) or mesh(x,y,Z)
            x, y, z = _check_xyz(*args[:3], **kwargs)
        elif nargs >= 1 and nargs <= 2: # mesh(Z)
            x, y, z = _check_xyz(args[0], indexing=kwargs['indexing'])
        else:
            raise TypeError("Surface._parseargs: wrong number of arguments")

        if nargs == 2 or nargs == 4: # mesh(...,C)
            self._prop['cdata'] = args[-1]

        self._set_data(x, y, z)

    def _set_data(self, x, y, z):
        self._set_lim(x, 'xlim')
        self._set_lim(y, 'ylim')
        self._set_lim(z, 'zlim')
        self._prop['xdata'] = x
        self._prop['ydata'] = y
        self._prop['zdata'] = z
        nx, ny = shape(z)
        self._prop['dims'] = (nx, ny, 1)
        self._prop['numberofpoints'] = nx*ny
        if not 'mesh' in self._prop['function']:
            self._prop['wireframe'] = False


class Contours(PlotProperties):
    """
    Information about contours for plot of scalar fields.
    """
    _local_prop = {
        'cvector':   None,   # vector of contour heights
        'clevels':   8,      # default number of contour levels
        'clabels':   False,  # display contour labels
        'clocation': 'base', # location of cntr levels (surface or base)
        'filled':    False,  # fill contours
        'xdata':     None,
        'ydata':     None,
        'zdata':     None,
        }
    _update_from_config_file(_local_prop)  # get defaults from scitools.cfg
    __doc__ += docadd('Keywords for the setp method',
                      list(PlotProperties._local_prop.keys()),
                      list(_local_prop.keys()))

    def __init__(self, *args, **kwargs):
        PlotProperties.__init__(self, **kwargs)
        self._prop.update(Contours._local_prop)
        self.setp(**kwargs)
        self._parseargs(*args)

    def setp(self, **kwargs):
        PlotProperties.setp(self, **kwargs)

        if 'cvector' in kwargs:
            _check_type(kwargs['cvector'], 'cvector', (tuple,list,ndarray))
            self._prop['cvector'] = kwargs['cvector']
            self._prop['clevels'] = len(kwargs['cvector'])

        if 'clevels' in kwargs:
            clevels = kwargs['clevels']
            _check_type(clevels, 'clevels', int)
            cvector = self._prop['cvector']
            if cvector is not None and clevels > len(cvector):
                clevels = len(cvector)
            self._prop['clevels'] = clevels

        if 'clabels' in kwargs:
            self._prop['clabels'] = _toggle_state(kwargs['clabels'])

    def _parseargs(self, *args):
        if isinstance(args[-1], str): # contour(...,LineSpec)
            self.setformat(args[-1]);  args = args[:-1]
        kwargs = {'indexing': self._prop['indexing']}
        nargs = len(args)
        if nargs >= 3 and nargs <= 4:
            x, y, z = _check_xyz(*args[:3], **kwargs)
        elif nargs >= 1:
            x, y, z = _check_xyz(args[0], indexing=kwargs['indexing'])
        else:
            raise TypeError("Contours._parseargs: wrong number of arguments")

        if nargs == 2 or nargs == 4:
            tmp = args[-1]
            if operator.isSequenceType(tmp):
                self._prop['cvector'] = tmp
                self._prop['clevels'] = len(tmp)
            elif isinstance(tmp, int):
                self._prop['clevels'] = tmp
            else:
                raise TypeError(
                    "Contours._parseargs: expected array or integer for " \
                    " argument %d, not %s" % (nargs, type(tmp)))

        self._set_data(x, y, z)

    def _set_data(self, x, y, z):
        self._set_lim(x, 'xlim')
        self._set_lim(y, 'ylim')
        self._set_lim(z, 'zlim')
        self._prop['xdata'] = x
        self._prop['ydata'] = y
        self._prop['zdata'] = z
        nx, ny = shape(z)
        self._prop['dims'] = (nx, ny, 1)
        self._prop['numberofpoints'] = len(ravel(z))
        if self._prop['function'] == 'contour3':
            self._prop['clocation'] = 'surface'
        elif self._prop['function'] == 'contourf':
            self._prop['filled'] = True


class VelocityVectors(PlotProperties):
    """
    Information about velocity vectors in a vector plot.
    """
    _local_prop = {
        'arrowscale': 1.0,
        'filledarrows': False,
        'xdata': None, 'ydata': None, 'zdata': None, # grid components
        'udata': None, 'vdata': None, 'wdata': None, # vector components
        }
    __doc__ += docadd('Keywords for the setp method',
                      list(PlotProperties._local_prop.keys()),
                      list(_local_prop.keys()))

    def __init__(self, *args, **kwargs):
        PlotProperties.__init__(self, **kwargs)
        self._prop.update(VelocityVectors._local_prop)
        self.setp(**kwargs)
        self._parseargs(*args)

    def setp(self, **kwargs):
        PlotProperties.setp(self, **kwargs)

        if 'arrowscale' in kwargs:
            _check_type(kwargs['arrowscale'], 'arrowscale', (int,float))
            self._prop['arrowscale'] = float(kwargs['arrowscale'])

        if 'filledarrows' in kwargs:
            self._prop['filledarrows'] = _toggle_state(kwargs['filledarrows'])

    def _parseargs(self, *args):
        # allow both quiver(...,LineSpec,'filled') and quiver(...,'filled',LS):
        for i in range(2):
            if isinstance(args[-1], str):
                if args[-1] == 'filled':
                    self._prop['filledarrows'] = True;  args = args[:-1]
                else:
                    self.setformat(args[-1]);  args = args[:-1]

        z, w = [None]*2
        func = self._prop['function']
        kwargs = {'indexing': self._prop['indexing']}
        nargs = len(args)
        if nargs >= 6 and nargs <= 7: # quiver3(X,Y,Z,U,V,W)
            x, y, z, u, v, w = _check_xyzuvw(*args[:6], **kwargs)
        elif nargs >= 4 and nargs <= 5: # quiver(X,Y,U,V) or quiver3(Z,U,V,W)
            if func == 'quiver3':
                x, y, z, u, v, w = _check_xyzuvw(*args[:4], **kwargs)
            else:
                x, y, u, v = _check_xyuv(*args[:4], **kwargs)
        elif func == 'quiver' and nargs >= 2 and nargs <= 3: # quiver(U,V)
            x, y, u, v = _check_xyuv(*args[:2], **kwargs)
        else:
            raise TypeError(
                "VelocityVectors._parseargs: wrong number of arguments")

        if (func == 'quiver3' and nargs in (5,7)) or \
               (func == 'quiver' and nargs in (3,5)): # quiver?(...,arrowscale)
            _check_type(args[-1], 'arrowscale', (float,int))
            self._prop['arrowscale'] = float(args[-1])

        self._set_data(x, y, z, u, v, w)

    def scale_vectors(self):
        as_ = self._prop['arrowscale']
        if as_:
            u = self._prop['udata']
            v = self._prop['vdata']
            w = self._prop['wdata']
            dims = self._prop['dims']
            xmin, xmax, ymin, ymax, zmin, zmax = self.get_limits()
            dx = (xmax - xmin)/dims[1]
            dy = (ymax - ymin)/dims[0]
            d = dx**2 + dy**2
            if w is not None:
                dz = (zmax - zmin)/max(dims[0],dims[1])
                d += dx**2
            if d > 0:
                if w is not None:
                    length = sqrt((u/d)**2 + (v/d)**2 + (w/d)**2)
                else:
                    length = sqrt((u/d)**2 + (v/d)**2)
                maxlen = max(length.flat)
            else:
                maxlen = 0

            if maxlen > 0:
                as_ = as_*0.9/maxlen
            else:
                as_ = as_*0.9
            self._prop['udata'] = u*as_
            self._prop['vdata'] = v*as_
            if w is not None:
                self._prop['wdata'] = w*as_

    def _set_data(self, x, y, z, u, v, w):
        self._set_lim(x, 'xlim')
        self._set_lim(y, 'ylim')
        if z is not None:
            self._set_lim(z, 'zlim')
        self._prop['xdata'] = x
        self._prop['ydata'] = y
        self._prop['zdata'] = z
        self._prop['udata'] = u
        self._prop['vdata'] = v
        self._prop['wdata'] = w
        if rank(u) == 1:
            self._prop['dims'] = (len(u), 1, 1)
        elif rank(u) == 2:
            nx, ny = shape(u)
            self._prop['dims'] = (nx, ny, 1)
        else:
            self._prop['dims'] = u.shape
        self._prop['numberofpoints'] = len(ravel(u))


class Streams(PlotProperties):
    """
    Information about stream lines, stream tubes, and similar
    vector field visualization techniques.
    """
    _local_prop = {
        'stepsize': 0.1,
        'numberofstreams': 0,
        'tubes': False,
        'tubescale': 1.0,
        'n': 20, # number of points along the circumference of the tube
        'ribbons': False,
        'ribbonwidth': 0.5,
        'xdata': None, 'ydata': None, 'zdata': None,    # grid components
        'udata': None, 'vdata': None, 'wdata': None,    # vector components
        'startx': None, 'starty': None, 'startz': None, # starting points
        }
    __doc__ += docadd('Keywords for the setp method',
                      list(PlotProperties._local_prop.keys()),
                      list(_local_prop.keys()))

    def __init__(self, *args, **kwargs):
        PlotProperties.__init__(self, **kwargs)
        self._prop.update(Streams._local_prop)
        self.setp(**kwargs)
        self._parseargs(*args)

    def setp(self, **kwargs):
        PlotProperties.setp(self, **kwargs)

        for key in 'stepsize tubescale ribbonwidth'.split():
            if key in kwargs:
                _check_type(kwargs[key], key, (float,int))
                self._prop[key] = float(kwargs[key])

        # set whether we should use lines, tubes, or ribbons:
        func = self._prop['function']
        self._prop['tubes'] = func == 'streamtube'
        self._prop['ribbons'] = func == 'streamribbon'

    def _parseargs(self, *args):
        # TODO: do more error checking and add support for indexing='ij'.
        z, w, sz, option = [None]*4
        #kwargs = {'indexing': self._prop['indexing']}
        nargs = len(args)
        if nargs >= 9 and nargs <= 10:
            x, y, z, u, v, w, sx, sy, sz = [asarray(a) for a in args[:9]]
            #x, y, z, u, v, w = _check_xyzuvw(*args[:6])
            #x, y, z = [asarray(a) for a in args[:3]] #_check_xyz(*args[:3])
            #u, v, w = [asarray(a) for a in args[3:6]]
            #sx, sy, sz = [asarray(a) for a in args[6:9]]
        elif nargs >= 6 and nargs <= 7:
            u, v = [asarray(a) for a in args[:2]]
            if rank(u) == 3: # streamline(U,V,W,startx,starty,startz)
                nx, ny, nz = shape(u)
                x, y, z = ndgrid(seq(nx-1), seq(ny-1), seq(nz-1))
                #w = asarray(args[2])
                w, sx, sy, sz = [asarray(a) for a in args[2:6]]
            else: # streamline(X,Y,U,V,startx,starty)
                x = u;  y = v
                #u, v = [asarray(a) for a in args[2:4]]
                u, v, sx, sy = [asarray(a) for a in args[2:6]]
        elif nargs >= 4 and nargs <= 5: # streamline(U,V,startx,starty)
            u, v = [asarray(a) for a in args[:2]]
            try:
                nx, ny = shape(u)
            except:
                raise ValueError("u must be 2D, not %dD" % rank(u))
            x, y = ndgrid(seq(nx-1), seq(ny-1))
            sx, sy = [asarray(a) for a in args[2:4]]
        elif nargs >= 1 and nargs <= 2: # streamline(XYZ) or streamline(XY)
            raise NotImplementedError('Streams._parseargs: not implemented')
        else:
            raise TypeError('wrong number of arguments')

        if nargs in (5,7,10): # streamline(...,options)
            func = self._prop['function']
            options = args[-1]
            if isinstance(options, (tuple,list)) and len(options) in (1,2):
                if func == 'streamtube':
                    self._prop['tubescale'] = float(options[0])
                else:
                    self._prop['stepsize'] = float(options[0])
                if len(options) == 2:
                    if func == 'streamtube':
                        self._prop['n'] = int(options[1])
                    else:
                        maxverts = float(options[1])
            elif isinstance(options, (float,int)):
                if func == 'streamtube':
                    self._prop['tubescale'] = float(options)
                elif func == 'streamribbon':
                    self._prop['ribbonwidth'] = float(options)
                else:
                    self._prop['stepsize'] = float(options)
            else:
                msg = "options must be [stepsize[,maxverts]], not '%s'" % \
                      options
                if func == 'streamtube':
                    msg = "options must be [scale[,n]], not '%s'" % options
                elif func == 'streamribbon':
                    msg = "options must be a [width], not %s" % options
                raise ValueError(msg)

##         if len(u.shape) == 3:
##             assert shape(x) == shape(y) == shape(z) == \
##                    shape(u) == shape(v) == shape(w), \
##                    "x, y, z, u, v, and z must be 3D arrays and of same shape"
##             assert shape(sx) == shape(sy) == shape(sz), \
##                    "startx, starty, and startz must all be of same shape"
##         else:
##             assert shape(x) == shape(y) == shape(u) == shape(v), \
##                    "x, y, u, and v must be 2D arrays and of same shape"
##             assert shape(sx) == shape(sy), \
##                    "startx and starty must be of same shape"
            z = w = zeros(shape(u))
            sz = zeros(shape(sx))

        self._set_data(x, y, z, u, v, w, sx, sy, sz)

    def _set_data(self, x, y, z, u, v, w, sx, sy, sz):
        self._set_lim(x, 'xlim')
        self._set_lim(y, 'ylim')
        if z is not None:
            self._set_lim(z, 'zlim')
        self._prop['xdata'] = x
        self._prop['ydata'] = y
        self._prop['zdata'] = z
        self._prop['udata'] = u
        self._prop['vdata'] = v
        self._prop['wdata'] = w
        self._prop['startx'] = sx
        self._prop['starty'] = sy
        self._prop['startz'] = sz
        if rank(u) == 2:
            nx, ny = shape(u)
            self._prop['dims'] = (nx, ny, 1)
        else:
            self._prop['dims'] = shape(u)
        self._prop['numberofpoints'] = len(ravel(u))
        self._prop['numberofstreams'] = len(ravel(sx))


class Volume(PlotProperties):
    """
    Information about volume visualization techniques.
    """
    _local_prop = {
        'slices': None,
        'isovalue': None,
        'clevels': 5, # default number of contour lines per plane
        'cvector': None,
        'xdata': None, 'ydata': None, 'zdata': None, # grid components
        'vdata': None, # data values at grid points
        'cdata': None, # pseudocolor data
        }
    _update_from_config_file(_local_prop)  # get defaults from scitools.cfg
    __doc__ += docadd('Keywords for the setp method',
                      list(PlotProperties._local_prop.keys()),
                      list(_local_prop.keys()))

    def __init__(self, *args, **kwargs):
        PlotProperties.__init__(self, **kwargs)
        self._prop.update(Volume._local_prop)
        self.setp(**kwargs)
        self._parseargs(*args)

    def setp(self, **kwargs):
        PlotProperties.setp(self, **kwargs)

        if 'isovalue' in kwargs:
            _check_type(kwargs['isovalue'], 'isovalue', (float,int))
            self._prop['isovalue'] = float(kwargs['isovalue'])

        if 'clevels' in kwargs:
            clevels = kwargs['clevels']
            _check_type(kwargs['clevels'], 'clevels', int)
            cvector = self._prop['cvector']
            if cvector is not None and clevels > len(cvector):
                clevels = len(cvector)
            self._prop['clevels'] = clevels

        if 'cvector' in kwargs:
            _check_type(kwargs['cvector'], 'cvector', (tuple,list))
            self._prop['cvector'] = kwargs['cvector']
            self._prop['clevels'] = len(kwargs['cvector'])

    def _parseargs(self, *args):
        func = self._prop['function']
        if func in ['slice_', 'contourslice']:
            self._parseargs_slice_(*args)
        elif func == 'isosurface':
            self._parseargs_isosurface(*args)

    def _parseargs_slice_(self, *args):
        # this method also works for contourslice
        kwargs = {'indexing': self._prop['indexing']}
        nargs = len(args)
        if nargs >= 7 and nargs <= 8:
            # slice_(X,Y,Z,V,Sx,Sy,Sz) or slice_(X,Y,Z,V,XI,YI,ZI)
            x, y, z, v = _check_xyzv(*args[:4], **kwargs)
            slices = [asarray(a) for a in args[4:7]]
        elif nargs >= 4 and nargs <= 5:
            # slice_(V,Sx,Sy,Sz) or slice_(V,XI,YI,ZI)
            x, y, z, v = _check_xyzv(args[0], indexing=kwargs['indexing'])
            slices = [asarray(a) for a in args[1:4]]
        else:
            raise TypeError("Wrong number of arguments")

        if nargs == 5 or nargs == 8:
            func = self._prop['function']
            tmparg = args[-1]
            if func == 'slice_': # slice_(...,'method')
                intrp_methods = 'linear cubic nearest'.split()
                method = str(tmparg)
                if not method in interp_methods:
                    raise ValueError(
                        'interpolation method must be %s, not %s' % \
                        (interp_methods, method))
                #self._prop['interpolationmethod'] = method
            elif func == 'contourslice': # contourslice(...,
                if isinstance(tmparg, int) and tmparg >= 0:
                    self._prop['clevels'] = tmparg
                elif isinstance(tmparg, (list,tuple)):
                    self._prop['cvector'] = tmparg
                    self._prop['clevels'] = len(tmparg)

        self._set_data(x, y, z, v, slices=slices)

    def _parseargs_isosurface(self, *args):
        kwargs = {'indexing': self._prop['indexing']}
        nargs = len(args)
        if nargs >= 5 and nargs <= 6: # isosurface(X,Y,Z,V,isovalue)
            x, y, z, v = _check_xyzv(*args[:4], **kwargs)
            isovalue = float(args[4])
        elif nargs >= 2 and nargs <= 3: # isosurface(V,isovalue)
            x, y, z, v = _check_xyzv(args[0], indexing=kwargs['indexing'])
            isovalue = float(args[1])
        else:
            raise TypeError("Wrong number of arguments")

        if nargs in (3,6): # isosurface(...,COLORS)
            cdata = asarray(args[-1])
            assert v.shape == cdata.shape, \
                   "COLORS must have shape %s (as V), not %s" % \
                   (v.shape, cdata.shape)
            self._prop['cdata'] = cdata

        self._set_data(x, y, z, v, isovalue=isovalue)

    def _set_data(self, x, y, z, v, slices=None, isovalue=None):
        self._set_lim(x, 'xlim')
        self._set_lim(y, 'ylim')
        self._set_lim(z, 'zlim')
        self._prop['xdata'] = x
        self._prop['ydata'] = y
        self._prop['zdata'] = z
        self._prop['vdata'] = v
        if slices:
            self._prop['slices'] = slices
        if isovalue is not None:
            self._prop['isovalue'] = isovalue
        self._prop['dims'] = v.shape
        self._prop['numberofpoints'] = len(ravel(v))


class Colorbar(object):
    """
    Information about color bars in color plots.
    """
    _local_prop = {
        'cblocation': 'EastOutside',
        'cbtitle': '',
        'visible': False,
        }
    _update_from_config_file(_local_prop)  # get defaults from scitools.cfg
    __doc__ += docadd('Keywords for the setp method', list(_local_prop.keys()))

    _locations = 'North South East West NorthOutside SouthOutside ' \
                 'EastOutside WestOutside'.split()

    __doc__ += docadd('Legal values for color bar location',
                      _locations)

    def __init__(self, **kwargs):
        self._prop = {}
        self._prop.update(Colorbar._local_prop)
        self._defaults = self._prop.copy()
        self.setp(**kwargs)

    def __str__(self):
        return pprint.pformat(self._prop)

    def setp(self, **kwargs):
        if 'cblocation' in kwargs:
            if kwargs['cblocation'] in self._locations:
                self._prop['cblocation'] = kwargs['cblocation']
            else:
                print "colorbar location must be one of %s, not %s" % \
                      (self._locations, kwargs['cblocation'])

        if 'cbtitle' in kwargs:
            self._prop['cbtitle'] = str(kwargs['cbtitle'])

        if 'visible' in kwargs:
            self._prop['visible'] = _toggle_state(kwargs['visible'])

    def getp(self, prm_name):
        try:
            return self._prop[prm_name]
        except:
            raise KeyError("%s.getp: no parameter with name '%s'" % \
                           (self.__class__.__name__, prm_name))

    def reset(self):
        self._prop = self._defaults.copy()


class Light(object):
    """
    Information about light in a visualization.
    """
    _local_prop = {
        'lightcolor': (1,1,1),
        'lightpos': (1,0,1),
        'lighttarget': (0,0,0),
        'intensity': 1,
        'visible': True,
        }
    _update_from_config_file(_local_prop)  # get defaults from scitools.cfg
    __doc__ += docadd('Keywords for the setp method', list(_local_prop.keys()))

    def __init__(self, **kwargs):
        self._prop = {}
        self._prop.update(Light._local_prop)
        self._defaults = self._prop.copy()
        self.setp(**kwargs)

    def __str__(self):
        return pprint.pformat(self._prop)

    def setp(self, **kwargs):
        if 'lightcolor' in kwargs:
            color = kwargs['lightcolor']
            _check_type(color, 'lightcolor', (list,tuple))
            _check_size(color, 'lightcolor', 3)
            for i in range(3):
                _check_type(color[i], 'lightcolor', (float,int))
            self._prop['lightcolor'] = color

        if 'lightpos' in kwargs:
            self._prop['lightpos'] = kwargs['lightpos']

        if 'lighttarget' in kwargs:
            self._prop['lighttarget'] = kwargs['lighttarget']

        if 'itensity' in kwargs:
            self._prop['itensity'] = kwargs['itensity']

        if 'visible' in kwargs:
            self._prop['visible'] = _toggle_state(kwargs['visible'])

    def getp(self, name):
        try:
            return self._prop[name]
        except:
            raise KeyError("%s.getp: no parameter with name '%s'." % \
                           (self.__class__.__name__, name))

    def reset(self):
        self._prop = self._defaults.copy()


class Camera(object):
    """
    Information about the camera in a visualization.
    """
    _local_prop = {
        'cammode': 'auto',
        'camtarget': (0,0,0),
        'camva': None, # view angle
        'azimuth': None,
        'elevation': None,
        'view': 2,
        'camup': (0,1,0),
        'camdolly': (0,0,0),
        'camroll': None, # angle
        'camzoom': 1,
        'campos': (0,0,0),
        'camproj': 'orthographic'
        }
    _update_from_config_file(_local_prop)  # get defaults from scitools.cfg
    __doc__ += docadd('Keywords for the setp method', list(_local_prop.keys()))

    _modes = ['auto', 'manual']
    _camprojs = ['orthographic', 'perspective']

    __doc__ += docadd('Legal values for the mode keyword', _modes)
    __doc__ += docadd('Legal values for the camproj keyword', _camprojs)

    def __init__(self, axis, **kwargs):
        self._prop = {}
        self._prop.update(Camera._local_prop)
        self._ax = axis
        self._defaults = self._prop.copy()
        self.setp(**kwargs)

    def __str__(self):
        return pprint.pformat(self._prop)

    def setp(self, **kwargs):
        if 'cammode' in kwargs:
            if kwargs['cammode'] in self._modes:
                self._prop['cammode'] = kwargs['cammode']
            else:
                raise ValueError("Camera.setp: cammode must be %s, not %s" % \
                                 (self._modes, kwargs['cammode']))

        if 'view' in kwargs:
            view = kwargs['view']
            if view in (2,3):
                self._set_default_view(view)
            elif isinstance(view, (tuple,list)) and len(view) == 2:
                self._prop['azimuth'], self._prop['elevation'] = view
            else:
                raise ValueError(
                    "Camera.setp: view must be either [az,el], 2, or 3.")

        if 'camproj' in kwargs:
            if kwargs['camproj'] in self._camprojs:
                self._prop['camproj'] = kwargs['camproj']
            else:
                raise ValueError("projection must one of %s, not %s" % \
                                 (self._camprojs, kwargs['camproj']))

        for prop in 'camzoom camva camroll'.split():
            if prop in kwargs:
                _check_type(kwargs[prop], prop, (int,float))
                self._prop[prop] = float(kwargs[prop])

        if 'azimuth' in kwargs:
            _check_type(kwargs['azimuth'], 'azimuth', (int,float))
            self._prop['azimuth'] = float(kwargs['azimuth'])
            if self._prop['elevation'] is None:
                self._prop['elevation'] = 0

        if 'elevation' in kwargs:
            _check_type(kwargs['elevation'], 'elevation', (int,float))
            self._prop['elevation'] = float(kwargs['elevation'])
            if self._prop['azimuth'] is None:
                self._prop['azimuth'] = 0

        if self._prop['azimuth'] is not None: # elevation is also != None
            self._prop['view'] = 3
            self._prop['camup'] = (0,0,1)

        for prop in 'camtarget campos camup camdolly'.split():
            if prop in kwargs:
                _check_type(kwargs[prop], prop, (list,tuple))
                _check_size(kwargs[prop], prop, 3)
                self._prop[prop] = kwargs[prop]

    def getp(self, name):
        try:
            return self._prop[name]
        except:
            raise KeyError("%s.getp: no parameter with name '%s'." % \
                           (self.__class__.__name__, name))

    def reset(self):
        """Reset camera to defaults."""
        self._prop = self._defaults.copy()

    def _set_default_view(self, view):
        self.reset()
        self._prop['view'] = view
        self._prop['camtarget'] = self._ax.getp('center')
        if self._prop['view'] == 3:
            self._prop['camup'] = (0,0,1)


class Axis(object):
    """
    Information about the axis in curve, surface, and volume plots.
    """
    _local_prop = {
        'plotitems': [],
        'numberofitems': 0,
        'mode': 'auto',
        'method': 'normal',
        'direction': 'xy',
        'hold': False,
        'hidden': True,
        'box': False,
        'grid': False,
        'camera': None,
        'cameramode': 'auto',
        'lights': [],
        'colorbar': None,
        'colormap': None,
        'caxis': [None]*2,
        'caxismode': 'auto',
        'axiscolor': (0,0,0),
        'bgcolor': (1,1,1), # background color
        'fgcolor': (0,0,0), # foreground color
        'fontname': 'Helvetica',
        'fontsize': 12,
        'shading': 'faceted',
        'scale': 'linear',
        'xmin': None, 'xmax': None,
        'ymin': None, 'ymax': None,
        'zmin': None, 'zmax': None,
        'xlim': [None]*2,
        'ylim': [None]*2,
        'zlim': [None]*2,
        'title': '',
        'xlabel': '', 'ylabel': '', 'zlabel': '',
        'center': (0,0,0),
        'daspect': [None]*3,
        'daspectmode': 'auto',
        'visible':  True,
        'viewport': None, # viewport coords (list with 4 elm, backend specific)
        'ambientcolor': None,
        'diffusecolor': None,
        'speculartcolor': None,
        'pth': None, # this is the p-th axis in subplot(m,n,p)
        'colororder': 'b r g m c y k'.split(),
        'curcolor': 0,
        }
    _update_from_config_file(_local_prop)  # get defaults from scitools.cfg
    __doc__ += docadd('Keywords for the setp method', list(_local_prop.keys()))

    _directions = "ij xy".split()
    _methods = "equal image square normal vis3d".split()
    _modes = "auto manual tight fill".split()
    _ranges = "xmin xmax ymin ymax zmin zmax".split()
    _shadings = "flat interp faceted".split()
    _legend_locs = {'upper right': 1, 'upper left': 2,
                    'lower left': 3,  'lower right': 4,
                    'center left': 6, 'center right': 7,
                    'lower center': 8, 'upper center': 9,
                    'best': 0, 'right': 5, 'center': 10}

    __doc__ += docadd('Legal values for direction keyword', _directions)
    __doc__ += docadd('Legal values for method keyword', _methods)
    __doc__ += docadd('Legal values for mode keyword', _modes)
    __doc__ += docadd('Legal values for range keyword', _ranges)
    __doc__ += docadd('Legal values for shading keyword', _shadings)
    __doc__ += docadd('Legal values for legend locations',
                      list(_legend_locs.keys()))

    def __init__(self, *args, **kwargs):
        self._prop = {}
        self._prop.update(Axis._local_prop)
        self._defaults = self._prop.copy()
        # self was not available when _local_prop was defined:
        self._prop['camera'] = Camera(self)
        self._prop['colorbar'] = Colorbar()

    def __str__(self):
        return pprint.pformat(self._prop)

    def dump(self):
        """Dump the parameters of this object."""
        return str(self)

    def setp(self, **kwargs):
        if 'mode' in kwargs:
            mode = kwargs['mode']
            if mode in self._modes:
                self._prop['mode'] = mode
                if mode in ['auto', 'tight']:
                    # clear the current axis ranges:
                    for r in self._ranges:
                        self._prop[r] = None
            else:
                raise ValueError("Axis.setp: mode must be %s, not %s" % \
                                 (self._modes, mode))

        if 'method' in kwargs:
            if kwargs['method'] in self._methods:
                self._prop['method'] = kwargs['method']
            else:
                raise ValueError("Axis.setp: method must be %s, not %s" % \
                                 (self._methods, kwargs['method']))

        if 'direction' in kwargs:
            if kwargs['direction'] in self._directions:
                self._prop['direction'] = kwargs['direction']
            else:
                raise ValueError("Axis.setp: direction must be %s, not %s" % \
                                 (self._directions, kwargs['direction']))

        for key in 'hold hidden box grid'.split():
            if key in kwargs:
                self._toggle_state(key, kwargs[key])
                del kwargs[key]

        if 'colorbar' in kwargs:
            if isinstance(kwargs['colorbar'], Colorbar):
                self._prop['colorbar'] = kwargs['colorbar']
            else:
                self._prop['colorbar'].setp(visible=kwargs['colorbar'])

        if 'colormap' in kwargs:
            self._prop['colormap'] = kwargs['colormap'] # backend dependent

        if 'caxis' in kwargs:
            ca = kwargs['caxis']
            if isinstance(ca, (tuple,list)) and len(ca) == 2:
                _check_type(ca[0], 'cmin', (int,float))
                _check_type(ca[1], 'cmax', (int,float))
                self._prop['caxis'] = ca
                self._prop['caxismode'] = 'manual'
            else:
                raise ValueError("%s.setp: caxis must be a two element vector" \
                                 " [cmin,cmax], not '%s'." \
                                 % (self.__class__.__name__,ca))

        if 'caxismode' in kwargs:
            mode = kwargs['caxismode']
            if kwargs['caxismode'] in self._modes:
                self._prop['caxismode'] = mode
                if mode == 'auto':
                    self._prop['caxis'] = [None]*2
                elif mode == 'manual':
                    if None in self._prop['caxis']:
                        zmin, zmax = self._prop['zlim']
                        if zmin is None or zmax is not None:
                            self._prop['caxis'] = (zmin, zmax)
                        else:
                            self._prop['caxis'] = (0,1)
            else:
                raise ValueError("Axis.setp: caxismode must be %s, not %s" \
                                 (self._modes, mode))

        if 'shading' in kwargs:
            if kwargs['shading'] in self._shadings:
                self._prop['shading'] = kwargs['shading']
                #self._update_shading()
            else:
                raise ValueError("Axis.setp: '%s' not a valid shading mode" \
                                 % kwargs['shading'])

        if 'light' in kwargs:
            if isinstance(kwargs['light'], Light):
                self._prop['lights'].append(kwargs['light'])
            else:
                raise ValueError("Axis.setp: light must be %s, not %s" % \
                                 (type(Light), type(self._prop['light'])))

        # Set scale
        if 'log' in kwargs:
            if kwargs['log'] == 'x':
                self._prop['scale'] = 'logx'
            elif kwargs['log'] == 'y':
                self._prop['scale'] = 'logy'
            elif kwargs['log'] == 'xy':
                self._prop['scale'] = 'loglog'
            # Note: The only way to reset scale to linear after log is to
            # use plot(args,log=None)
            elif kwargs['log'] == None:
                self._prop['scale'] = 'linear'

        for key in self._ranges:
            if key in kwargs and isinstance(kwargs[key], (float,int)):
                self._prop[key] = kwargs[key]

        for key in 'xlim ylim zlim'.split():
            if key in kwargs and isinstance(kwargs[key], (tuple,list)):
                _check_size(kwargs[key], key, 2)
                self._prop[key[0]+'min'] = kwargs[key][0]
                self._prop[key[0]+'max'] = kwargs[key][1]

        if 'axis' in kwargs:
            axis = kwargs['axis']
            if isinstance(axis, (tuple,list)):
                n = len(axis)
                if n in (4,6):
                    for i in range(n):
                        _check_type(axis[i], self._ranges[i], (float,int))
                        self._prop[self._ranges[i]] = axis[i]
            elif axis in ['on', 'off']: #, None, True, False]:
                self._prop['visible'] = _toggle_state(axis)
            elif axis in self._methods:
                self._prop['method'] = axis
            elif axis in self._modes:
                self._prop['mode'] = axis
            elif axis in self._directions:
                self._prop['direction'] = axis
            else:
                raise ValueError("not a valid axis specification")

        for key in 'title xlabel ylabel zlabel'.split():
            if key in kwargs and isinstance(kwargs[key], str):
                self._prop[key] = kwargs[key]

        if 'daspect' in kwargs:
            daspect = kwargs['daspect']
            if isinstance(daspect, (int,float)):
                daspect = [daspect]*3
            _check_type(daspect, 'daspect', (tuple,list))
            _check_size(daspect, 'daspect', 3)
            self._prop['daspect'] = [float(elm) for elm in daspect]
            self._prop['daspectmode'] = 'manual'

        if 'daspectmode' in kwargs:
            self._prop['daspectmode'] = kwargs['daspectmode']

        if 'fgcolor' in kwargs:
            self._prop['fgcolor'] = kwargs['fgcolor']

        if 'bgcolor' in kwargs:
            self._prop['bgcolor'] = kwargs['bgcolor']

        if 'visible' in kwargs:
            self._toggle_state('visible', kwargs['visible'])
            del kwargs['visible']

        if 'viewport' in kwargs:
            viewport = kwargs['viewport']
            _check_type(viewport, 'viewport', (list,tuple))
            _check_size(viewport, 'viewport', 4)
            #for i in range(4):
            #    _check_type(viewport[i], 'viewport coor', (int,float))
            self._prop['viewport'] = viewport

        if 'pth' in kwargs:
            pth = kwargs['pth']
            _check_type(pth, 'pth', int)
            self._prop['pth'] = pth

        if 'legend_loc' in kwargs:
            self._prop['legend_loc'] = kwargs['legend_loc']
        if 'legend_fancybox' in kwargs:
            self._prop['legend_fancybox'] = kwargs['legend_fancybox']

        # set properties for camera and colorbar:
        self._prop['camera'].setp(**kwargs)
        self._prop['colorbar'].setp(**kwargs)

        # update the axis:
        self.update()

    def getp(self, name):
        """Return parameter with name 'name'."""
        try:
            return self._prop[name]
        except:
            raise KeyError("%s.getp: no parameter with name '%s'" % \
                           (self.__class__.__name__, name))

    def get_next_color(self):
        """Return the next color defined in the 'colororder' property."""
        colors = self._prop['colororder']
        if self._prop['curcolor'] == len(colors):
            self._prop['curcolor'] = 0
        curcolor = colors[self._prop['curcolor']]
        self._prop['curcolor'] += 1
        return curcolor

    def reset(self):
        """Reset axis attributes to default values."""
        viewport = self._prop['viewport'] # don't reset viewport coords
        pth = self._prop['pth'] # don't reset p-th axis information
        self._prop = self._defaults.copy()
        self._prop['viewport'] = viewport
        self._prop['pth'] = pth
        self._prop['plotitems'] = []
        #self._prop['camera'].reset()
        del self._prop['camera']
        self._prop['camera'] = Camera(self)
        #for l in self._prop['lights']:
        #    l.reset()
        self._prop['lights'] = []
        #self._prop['colorbar'].reset()
        self._prop['colorbar'] = Colorbar()

    def add(self, items):
        """Add all items in 'items' to this axis."""
        if not self._prop['hold']:
            self.reset()
        if not isinstance(items, (tuple,list)):
            items = (items,)
        for item in items:
            if not isinstance(item, PlotProperties):
                raise ValueError("item must be %s (or a subclass), not %s" % \
                                 (type(PlotProperties), type(item)))
            self._prop['plotitems'].append(item)
        self.update()

    def get_limits(self):
        """Return axis limits."""
        return self._prop['xlim']+self._prop['ylim']+self._prop['zlim']

    def toggle(self, name):
        """Toggle axis parameter with name 'name'."""
        if self._prop[name]:
            self._prop[name] = False
        else:
            self._prop[name] = True

    def update(self):
        """Update axis."""
        if len(self._prop['plotitems']) > self._prop['numberofitems']:
            self._prop['numberofitems'] = len(self._prop['plotitems'])
            for item in self._prop['plotitems']:
                self._update_limits(item)
        if len(self._prop['plotitems']) > 0:
            if None in self._prop['daspect'] or \
                   self._prop['daspectmode'] == 'auto':
                self._update_daspect()
            self._set_center()
        p = self._prop
        if (p['xmin'] is not None and p['xmax'] is not None) or \
           (p['ymin'] is not None and p['ymax'] is not None) or \
           (p['zmin'] is not None and p['zmax'] is not None):
            self._prop['mode'] = 'manual'
        method = self._prop['method']
        if method == 'equal':
            self._prop['daspect'] = (1.,1.,1.)
        elif method == 'image':
            self._prop['daspect'] = (1.,1.,1.)
            self._prop['mode'] = 'tight'
        elif method == 'square':
            #print "axis method 'square' not implemented yet"
            pass
        elif method == 'normal':
            if None in self._prop['daspect'] or \
                   self._prop['daspectmode'] == 'auto':
                self._update_daspect()

    def _toggle_state(self, name, state):
        self._prop[name] = _toggle_state(state)

    def _set_center(self):
        center = [None]*3
        xmin, xmax, ymin, ymax, zmin, zmax = self.get_limits()
        center[0] = (xmax + xmin) / 2.0
        center[1] = (ymax + ymin) / 2.0
        center[2] = (zmax + zmin) / 2.0
        self._prop['center'] = tuple(center)

    def _check_lim(self, l1, l2):
        """Return a tuple with the "larger" values of 'l1' and 'l2'."""
        lim = [None]*2
        if l1[0] > l2[0]:
            lim[0] = l2[0]
        else:
            lim[0] = l1[0]
        if l1[1] < l2[1]:
            lim[1] = l2[1]
        else:
            lim[1] = l1[1]
        return tuple(lim)

    def _update_limits(self, item):
        """
        Update axis limits according to the PlotProperties given in 'item'.
        """
        xlim = item.getp('xlim')
        ylim = item.getp('ylim')
        zlim = item.getp('zlim')
        if not None in self._prop['xlim']:
            xlim = self._check_lim(self._prop['xlim'], xlim)
        if not None in self._prop['ylim']:
            ylim = self._check_lim(self._prop['ylim'], ylim)
        if not None in self._prop['zlim']:
            zlim = self._check_lim(self._prop['zlim'], zlim)
        self._prop['xlim'] = xlim
        self._prop['ylim'] = ylim
        self._prop['zlim'] = zlim

    def _update_daspect(self):
        lim = list(self.get_limits())
        xmin, xmax = self._prop['xmin'], self._prop['xmax']
        ymin, ymax = self._prop['ymin'], self._prop['ymax']
        zmin, zmax = self._prop['zmin'], self._prop['zmax']
        if not None in [xmin, xmax]:
            lim[0] = xmin
            lim[1] = xmax
        if not None in [ymin, ymax]:
            lim[2] = ymin
            lim[3] = ymax
        if not None in [zmin, zmax]:
            lim[4] = zmin
            lim[5] = zmax
        if self._prop['method'] == 'normal':
            if not None in lim: # limits are set
                sx = float(lim[1] - lim[0])
                sy = float(lim[3] - lim[2])
                sz = float(lim[5] - lim[4])
                scale = max([sx,sy,sz])
                if not scale > 0:
                    scale = 1
                if sz == 0:
                    daspect = (sx/scale, sy/scale, 1.0)
                else:
                    daspect = (sx/scale, sy/scale, sz/scale)
                self._prop['daspect'] = daspect


class Figure(object):
    """Hold figure attributtes like axes, size, ...."""

    _local_prop = {
        'axes': None,     # dictionary of axis instances
        'curax': 1,       # current axis
        'axshape': (1,1), # shape of axes
        'size': [None]*2, # size of figure ([width, height])
        'number': 1,      # this figures number
        }
    _update_from_config_file(_local_prop)  # get defaults from scitools.cfg
    __doc__ += docadd('Keywords for the setp method', list(_local_prop.keys()))

    def __init__(self, **kwargs):
        self._prop = {}
        self._prop.update(Figure._local_prop)
        # store a copy of the default values for use when figure is reset:
        self._defaults = self._prop.copy()
        self._prop['axes'] = {1: Axis()}
        self.setp(**kwargs)

    def __str__(self):
        return pprint.pformat(self._prop)

    def dump(self):
        """Dump the contents of the figure (all axes)."""
        s = '\nFigure object:\n'
        if self._prop['size'] is not None:
            s += pprint.pformat(self._prop['size']) + '\n'
        for ax in self._prop['axes']:
            s += 'axis %d:\n' % ax
            #s += pprint.pformat(str(self._prop['axes'][ax]))
            s += pprint.pformat(self._prop['axes'][ax]._prop)
        return s

    def gca(self):
        """Return current axis."""
        return self._prop['axes'][self._prop['curax']]

    def reset(self):
        """Reset figure attributes and backend to defaults."""
        self._prop = self._defaults.copy()
        self._prop['axes'] = {1: Axis()}
        self._prop['axes'][1].reset()

    def setp(self, **kwargs):
        if 'axshape' in kwargs:
            shape = kwargs['axshape']
            _check_type(shape, 'axshape', (tuple,list))
            _check_size(shape, 'axshape', 2)
            _check_type(shape[0], 'm', int)
            _check_type(shape[1], 'n', int)
            self._prop['axshape'] = shape
            dx = 1./shape[1];  dy = 1./shape[0]
            last_x = 0;  last_y = 1-dy
            viewport_coords = []
            for y in seq(dy,1,dy):
                for x in seq(dx,1,dx):
                    if backend.startswith('vtk'):
                        viewport_coords.append((last_x,last_y,x,last_y+dy))
                    else:
                        viewport_coords.append((last_x,last_y,x,y))
                    last_x = x
                last_x = 0
                last_y = last_y - dy

            self._prop['axes'] = {}
            for i in iseq(1,len(viewport_coords)):
                ax = Axis()
                ax.setp(viewport=viewport_coords[i-1])
                self._prop['axes'][i] = ax
                ax.setp(pth=i)

        if 'curax' in kwargs:
            curax = kwargs['curax']
            #_check_type(curax, 'curax', int)
            self._set_current_axis(curax)

        if 'size' in kwargs:
            size = kwargs['size']
            # size should be a list/tuple with two elements [width, height]
            _check_type(size, 'size', (list,tuple))
            _check_size(size, 'size', 2)
            self._prop['size'] = size

        if 'number' in kwargs:
            number = kwargs['number']
            _check_type(number, 'number', int)
            self._prop['number'] = number

    def getp(self, prm_name):
        try:
            return self._prop[prm_name]
        except:
            raise KeyError("%s.getp: no parameter with name '%s'" % \
                           (self.__class__.__name__, prm_name))

    def _set_current_axis_old(self, ax):
        if isinstance(ax, int):
            # check if it is inside axshape
            self._prop['curax'] = ax # no good!
        elif isinstance(ax, Axis):
            self._prop['axes'] = {1:ax}
            self._prop['axshape'] = (1,1)
            self._prop['curax'] = 1

    def _set_current_axis(self, ax):
        if isinstance(ax, int) and ax in self._prop['axes']:
            self._prop['curax'] = ax
        elif isinstance(ax, Axis):
            if ax in list(self._prop['axes'].values()):
                for i in self._prop['axes']:
                    if ax == self._prop['axes'][i]:
                        self._prop['curax'] = i
                        break
            else:
                n = max(list(self._prop['axes'])) + 1
                self._prop['axes'][n] = ax
                self._prop['curax'] = n


class BaseClass(object):
    """
    Subclasses implement different backends
    (GnuplotBackend for Gnuplot, for instance).

    This base class saves info about plotting to instances of class Figure,
    Line, and PlotItem.

    List of internal helper functions (for subclasses):
    ...


    """
    _matlab_like_cmds = [
        'autumn', 'axes', 'axis', 'bone', 'box', 'brighten',
        'camdolly', 'camlight', 'camlookat', 'campos',
        'camproj', 'camroll', 'camtarget', 'camup', 'camva',
        'camzoom', 'caxis', 'cla', 'clabel', 'clf', 'close',
        'closefig', 'closefigs', 'coneplot', 'colorbar',
        'colorcube', 'colormap', 'contour', 'contour3',
        'contourf', 'contourslice', 'cool', 'copper',
        'daspect', 'dumpfig', 'figure', 'fill', 'fill3', 'flag',
        'gca', 'gcf', 'get', 'gray', 'grid', 'hardcopy', 'hidden',
        'hold', 'hot', 'hsv', 'ishold', 'isocaps',
        'isosurface', 'jet', 'legend', 'light', 'lines',
        'loglog', 'material', 'mesh', 'meshc', 'loadfig',
        'pcolor', 'pink', 'plot', 'plot3', 'prism',
        'quiver', 'quiver3', 'reducevolum', 'semilogx',
        'semilogy', 'set', 'shading', 'show', 'slice_',
        'spring', 'streamline', 'streamribbon', 'streamslice',
        'streamtube', 'savefig', 'subplot', 'subvolume',
        'summer', 'surf', 'surfc', 'surfl', 'title', 'vga', 'view',
        'white', 'winter', 'xlabel', 'ylabel', 'zlabel']
    __doc__ += docadd('List of "Matlab-like" interface functions (for ' + \
                      'the user)', _matlab_like_cmds)

    _local_attrs = {
        'curfig': 1,         # current figure
        'show': True,        # screenplot after each plot command
        #'changed': False,    # sync state
        'interactive': True, # update backend after each change
        'color': False,      # hardcopy with color?
        }
    _update_from_config_file(_local_attrs)  # get defaults from scitools.cfg
    __doc__ += docadd('Keywords for the setp method', list(_local_attrs.keys()))

    # Dictionary of functions testing legal types
    _attrs_type = {'curfig': lambda arg: isinstance(arg, (int)),
                   'show': lambda arg: isinstance(arg, (bool)),
                   'interactive': lambda arg: isinstance(arg,(bool)),
                   #'changed': lambda arg: isinstance(arg, (bool)),
                   'color': lambda arg: isinstance(arg,(bool))
                   }

    def __init__(self):
        BaseClass.init(self)

    def init(self):
        """Initialize internal data structures."""
        self._g = None  # Pointer to the backend for manual labour.
        self._figs = {1: Figure()}  # dictionary of figure instances
        self._attrs = {}
        self._attrs.update(BaseClass._local_attrs)

    def __str__(self):
        return pprint.pformat(self._attrs)

    def setp(self, *args, **kwargs):
        """
        Set object properties or attributes in this backend instance.

        Calling::

            setp([obj,] prop1=value1, prop2=value2, ...)

        will set the attributes as given in this backend instance. If the
        optional positional argument obj is a given object with a set method
        (like Figure, Axis, and PlotProperties objects), the (relevant)
        properties and values are also set in this object. This also works on
        a list with objects.
        """
        nargs = len(args)
        if nargs > 0:
            arg = args[0]
            if not isinstance(arg, (tuple,list)):
                arg = (arg,)
            for obj in arg:
                if hasattr(obj, 'setp'):
                    obj.setp(**kwargs)

        if 'savefig' in kwargs:  # synonym: hardcopy
            kwargs['hardcopy'] = kwargs['savefig']

        for key in kwargs:
            value = kwargs[key]
            if key in self._attrs:  # legal key?
                if self._attrs_type[key](value):  # legal type?
                    self._attrs[key] = value
                else:
                    raise TypeError(
                        'BaseClass.setp: keyword "%s" %s is illegal.' % \
                        (key, type(key)))

        if 'hardcopy' in kwargs:
            self.hardcopy(kwargs['hardcopy'])

        if 'material' in kwargs:
            self.material(kwargs['material'])

        # subclasses should extend the doc string like this:
        #set.__doc__ += docadd('Keywords for the setp method',
        #                      list(BaseClass._local_attrs.keys()),
        #                      list(SomeSubClass._local_attrs.keys()))

    def getp(self, *args):
        """
        Get object properties or an attribute in this backend instance.

        Calling::

            getp('name')

        returns the attribute with name 'name' in this backend instance.

        Calling::

            getp(obj, 'name')

        returns the property with name 'name' of the object given in obj. This
        object must have a get method (like Figure, Axis, or PlotProperties
        objects).

        Calling::

            getp(obj)

        displays all property names and values for the object given in obj.
        """
        nargs = len(args)
        if nargs > 0:
            if hasattr(args[0], 'getp'):
                obj = args[0]
                if nargs == 1:
                    print obj
                else:
                    return obj.getp(args[1])
            else:
                prm_name = args[0]
                try:
                    return self._attrs[prm_name]
                except:
                    raise KeyError('%s.getp: no parameter with name "%s"' % \
                                   (self.__class__.__name__, prm_name))
        else:
            raise TypeError("getp: wrong number of arguments")

    #def __getitem__(self, name):  self.getp(name)

    #def __setitem__(self, name, value):  self.setp({name:value})


    def _replot(self, *args, **kwargs):
        """
        Update backend after change in data.
        This is a key routine and must be implemented in the backend.
        """
        raise NotImplementedError('_replot not implemented in class %s' % \
                                  self.__class__.__name__)

    def _check_args(self, *args):
        """Return the current axis, the argument list args, and the number of
        arguments in args. If the first argument in args is an Axis instance,
        this will be returned instead of the current axis. The Axis instancce
        is then removed from the argument list and the number of arguments
        is decremented by one."""
        ax = self.gca()
        nargs = len(args)
        if nargs > 0 and isinstance(args[0], Axis):
            ax = args[0];  args = args[1:];  nargs -= 1
        return ax, args, nargs

    def _cmpPlotProperties(self, a, b):
        """Sort cmp function for PlotProperties."""
        plotorder = [Volume, Streams, Surface, Contours,
                     VelocityVectors, Bars, Line]
        assert isinstance(a, PlotProperties)
        assert isinstance(b, PlotProperties)
        assert len(PlotProperties.__class__.__subclasses__(PlotProperties)) ==\
               len(plotorder)  # check all subclasses is in plotorder
        return cmp(plotorder.index(a.__class__),plotorder.index(b.__class__))

    def gcf(self):
        """Return current figure."""
        return self._figs[self._attrs['curfig']]

    def gca(self):
        """Return the current axis in the current figure."""
        return self.gcf().gca()

    def axes(self, *args, **kwargs):
        """Create axes in specified positions.

        Calling::

            axes()

        returns a default Axis instance.

        Calling::

            axes(ax)

        sets the axis in the Axis instance ax as the current axis.

        Calling::

            axes(viewport=RECT)

        returns a axis at the position given in RECT. RECT is normally a list
        [left,bottom,width,height], where the four parameters (values between
        0 and 1) specifies the location and size of the axis box ((0,0) is the
        lower-left corner and (1,1) is the upper-right corner). However, this
        is backend-dependent.
        """
        nargs = len(args)
        if nargs == 0:
            a = Axis()
            if len(kwargs) > 0:
                a.setp(**kwargs)
            self.gcf().setp(curax=a)
            return a
        elif nargs == 1:
            _check_type(args[0], 'ax', Axis)
            self.gcf().setp(curax=args[0])
            #raise NotImplementedError('not yet implemented')
        elif nargs == 2:
            pass
        else:
            raise TypeError("axes: wrong number of arguments")

    def subplot(self, *args, **kwargs):
        """Create axes in tiled positions.

        Calling::

            subplot(m,n,p)

        splits the Figure window into m rows and n columns of small axes. The
        p-th axis is then selected for the current plot and the Axis object
        is returned.

        Calling::

            subplot(mnp)

        is the same as calling subplot(m,n,p) as long as m<=n<=p<10.

        Example:

        >>> x = linspace(-5,5,101)
        >>> subplot(2,1,1)
        >>> plot(x,x-cos(x**2))
        >>> x = logspace(-1,2)
        >>> subplot(2,1,2)
        >>> loglog(x,exp(x),'b-s')
        """
        fig = self.gcf()
        nargs = len(args)
        if nargs == 1:
            sp = str(args[0])
            if len(sp) != 3:
                raise TypeError("subplot: '%s' is not a valid subplot" % sp)
            args = [int(a) for a in sp]
            nargs = 3
        if nargs == 3:
            m, n, p = args
            if fig.getp('axshape') == (m,n):
                fig.setp(curax=p)
            else:
                fig.setp(axshape=(m,n), curax=p)
            self.gca().setp(**kwargs)
        else:
            raise TypeError("subplot: wrong number of arguments")
        return self.gca()

    def daspect(self, *args):
        """Change the data aspect ratio.

        Calling::

            daspect([x,y,z])

        sets the data aspect ratio for the x, y, and z axis (e.g.,
        daspect([1,2,4]) means that one unit in x direction is equal in
        length to two units in y direction and four units in z direction).
        For example, daspect([r,1,1]) makes the physical size of the
        y axis in the plot r times the x axis.

        The size of the axes must be explicitly in order for the
        daspect command to work properly.
        Note that setting the aspect ratio is not supported by all backends.

        Calling::

            daspect()

        returns the data aspect ratio for the current axis.

        Calling::

            daspect(mode)

        sets the data aspect ratio mode, where mode can be 'auto', 'equal',
        or 'manual'. By specifying the mode to 'auto' (default), the data
        aspect ratio will be automatically computed so that each axis spans
        the available space in the figure window. In the 'manual' mode
        the user sets the aspect ratio, while 'equal' means that the
        the same units are used in both axes (for example, if the x axis
        goes from 0 to 10 and the y axis from 0 to 1, and we want the
        x axis ten times as long as the y axis, the manual aspect ratio
        er 0.1, and 'equal' will automatically set the ratio to 0.1).

        Calling::

            daspect('mode')

        returns the data aspect ratio mode.

        Calling::

            daspect(r)

        sets the data aspect ratio to r. This is for backends that do not
        support setting individual aspect ratios for the x, y, and z axis
        (like the Gnuplot backend). If the backend do support individual
        aspect ratios, the aspect ratio is set to r for all three axes.

        Calling::

            daspect(ax, ...)

        uses the the Axis object ax instead of the current axis.

        >>> surf(peaks(21))
        <scitools.easyviz.common.Surface object at 0xb7d7950c>
        >>> daspect()
        (1.0, 1.0, 0.71549553759291729)
        >>> figure()
        >>> surf(peaks(21))
        <scitools.easyviz.common.Surface object at 0xb58ff70c>
        >>> daspect([1,1,1])
        >>>
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            return ax.getp('daspect')
        elif nargs == 1:
            arg = args[0]
            if isinstance(arg, str):
                if arg == 'mode':
                    return ax.getp('daspectmode')
                else:
                    ax.setp(daspcetmode=arg)
            else:
                ax.setp(daspect=arg)
        else:
            raise TypeError("daspect: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def loadfig(self, filename='figspickle.txt'):
        """
        Load figures saved in a file (with the given filename) by dumpfig.
        The format of this file is currently standard Python pickle format.
        All figures in a previous session were dumped to the file, and
        all these figures are by this method reloaded and added to the
        current set of figures.
        """
        # in savefig, self._figs was pickled as one object
        handle = open(filename, 'r')
        filefigs = pickle.load(handle)
        handle.close()

        # check that filefigs is a dict of Figure instances:
        fail = True
        if isinstance(filefigs, dict):
            fail = False
            for item in filefigs:
                if not isinstance(item, Figure):
                    fail = True
        if fail:
            raise Exception("Import error. Cannot retrieve figures from filename %s ." % filename)

        self._figs.update(filefigs)

    def dumpfig(self, filename='figspickle.txt'):
        """
        Save all current figures to a file (with the given filename).
        The file has standard Python pickle format (dict of Figure
        instances). The figures can later be reloaded by the loadfig
        method.
        """
        handle = open(filename, 'w')
        pickle.dump(self._figs, handle)
        handle.close()

    def hardcopy(self, filename, **kwargs):
        """
        Save a hardcopy of the current figure to file (with the given
        filename). The file format (image type) is determined from the
        extension of the filename. If any changes have been made by working
        directly on the backend instance, set the keyword argument replot
        to False to stop Easyviz from replotting the current figure and
        destroying those changes.
        """
        # must be implemented in subclass
        raise NotImplementedError('hardcopy not implemented in class %s' % \
                                  self.__class__.__name__)

    def hold(self, *args):
        """Change the hold state of the current axis.

        Calling::

            hold('on')

        makes every subsequent plotting commands be added to the current plot.

        Calling::

            hold('off')

        clears the previous plot before the new plot is drawn. This is the
        default behavior.

        Calling::

            hold()

        toggles the hold state in the current axis.

        Calling::

            hold(ax, ...)

        affects the Axis object ax instead of the current axis.

        Note that one can use hold(True) and hold(False) instead of
        hold('on') and hold('off'), respectively.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 1:
            ax.setp(hold=args[0])
        elif nargs == 0:
            ax.toggle('hold')
            print "hold state is %s" % ax.getp('hold')
        else:
            raise TypeError('hold: wrong number of arguments')

    def ishold(self):
        """
        Return the hold state (True if hold is on, and False if it is off).
        """
        return self.gca().getp('hold')

    def figure(self, num=None, **kwargs):
        """
        Create a new figure or switch between figures and return Figure object.
        num is the figure number of the new or existing figure.
        """
        try:
            num = int(num)
        except:
            # print str(num),' is not an integer'
            if len(self._figs) == 0: # No figures left
                num = 1
            else:
                num = max(list(self._figs.keys()))+1
                #print "Active figure is %d." % num

        if not num in self._figs:
            # Points to class Figure or other convenient function
            # In gnuplot backend this should instantiate a new pipe instead
            kwargs['number'] = num
            self._figs[num] = Figure(**kwargs)

        self._attrs['curfig'] = num
        return self._figs[num]

    def clf(self):
        """Clear the current figure."""
        #self.gcf().reset()
        del self._figs[self._attrs['curfig']]
        self.figure(self._attrs['curfig'])

    def cla(self, *args):
        """Clear the current axis.

        Calling::

            cla()

        clears the current axis.

        Calling::

            cla(ax)

        clears the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)
        ax.reset()

    def axis(self, *args, **kwargs):
        """Choose the axis limits and appearance.

        Calling::

            axis([xmin, xmax, ymin, ymax[, zmin, zmax]])

        sets the limits on the x-, y-, and z-axes in the current plot.

        Calling::

            axis(xmin, xmax, ymin, ymax[, zmin, zmax])

        gives the same result as above.

        Calling::

            axis()

        returns the limits on the x-, y-, and z-axes for the current plot.
        If the view in the current plot is a 2D view, only the limits on the
        x- and y-axis are returned.

        Calling::

            axis(mode)

        sets axis scaling to mode, where mode can be

          * 'auto'   - autoscaling is used
          * 'manual' - freeze the scaling at the current limits
          * 'tight'  - sets the axis limits to the range of the data
          * 'fill'   - has currently no affect

        Calling::

            axis(method)

        sets the appearance of the current axis as specified by method.
        %s

        Calling::

            axis(direction)

        sets the direction of the increasing values on the axes.

          * 'ij' - reverse y-axis
          * 'xy' - restore y-axis

        Calling::

            axis('off')

        turns off the visibility of the axis.

        Calling::

            axis('on')

        turns the visibility of the axis back on.

        Calling::

            axis(ax, ...)

        affects the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 0 and len(kwargs) == 0:
            xmin, xmax, ymin, ymax, zmin, zmax = ax.get_limits()
            def get_lim(amin, amax, n1, n2):
                if ax.getp(n1) is not None and ax.getp(n2) is not None:
                    return ax.getp(n1), ax.getp(n2)
                else:
                    return amin, amax
            xmin, xmax = get_lim(xmin, xmax, 'xmin', 'xmax')
            ymin, ymax = get_lim(ymin, ymax, 'ymin', 'ymax')
            zmin, zmax = get_lim(zmin, zmax, 'zmin', 'zmax')
            if ax.getp('camera').getp('view') == 2:
                return xmin, xmax, ymin, ymax
            return xmin, xmax, ymin, ymax, zmin, zmax

        limits = Axis._ranges

        # Allow both axis(xmin,xmax,ymin,ymax[,zmin,zmax]) and
        # axis([xmin,xmax,ymin,ymax[,zmin,zmax]])
        if nargs == 1:
            if isinstance(args[0], (tuple,list)):
                args = args[0];  nargs = len(args)
            elif isinstance(args[0], str):
                if args[0] in Axis._modes:
                    ax.setp(mode=args[0])
                elif args[0] in ['on', 'off']:
                    state = _toggle_state(args[0])
                    ax.setp(visible=state)
                elif args[0] in Axis._methods:
                    ax.setp(method=args[0])
                elif args[0] in Axis._directions:
                    ax.setp(direction=args[0])

        kwargs_ = {}
        # first treat positional arguments:
        if nargs in (4,6):
            for i in range(nargs):
                kwargs_[limits[i]] = args[i]
        # allow keyword arguments:
        for kw in limits:
            if kw in kwargs:
                kwargs_[kw] = kwargs[kw]
        ax.setp(**kwargs_)

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    axis.__doc__ = axis.__doc__ % docadd('Legal values for method are',
                                         Axis._methods, indent=10)

    def xlim(self, *args):
        """Set or get limits on x axis.

        Calling::

            xlim([xmin,xmax])

        sets the x limits on the current axis.

        Calling::

            xlim(xmin,xmax)

        gives the same results as above.

        Calling::

            xmin, xmax = xlim()

        returns the x limits for the current axis.

        Calling::

            xlim(ax, ...)

        affects the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            xmin = ax.getp('xmin')
            xmax = ax.getp('xmax')
            if xmin is None or xmax is None:
                xmin, xmax = ax.getp('xlim')
            if xmin is None or xmax is None:
                return [0,1]
            return xmin, xmax
        elif nargs == 1:
            arg = args[0]
            if isinstance(arg, (list,tuple,ndarray)) and len(arg) == 2:
                ax.setp(xmin=arg[0], xmax=arg[1])
            elif isinstance(arg, str):
                raise NotImplementedError()
        elif nargs == 2:
            ax.setp(xmin=args[0], xmax=args[1])
        else:
            raise TypeError('xlim: wrong number of arguments.')

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def ylim(self, *args):
        """Set or get limits on y axis.

        Calling::

            ylim([ymin,ymax])

        sets the y limits on the current axis.

        Calling::

            ylim(ymin,ymax)

        gives the same results as above.

        Calling::

            ymin, ymax = ylim()

        returns the y limits for the current axis.

        Calling::

            ylim(ax, ...)

        affects the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            ymin = ax.getp('ymin')
            ymax = ax.getp('ymax')
            if ymin is None or ymax is None:
                ymin, ymax = ax.getp('ylim')
            if ymin is None or ymax is None:
                return [0,1]
            return ymin, ymax
        elif nargs == 1:
            arg = args[0]
            if isinstance(arg, (list,tuple,ndarray)) and len(arg) == 2:
                ax.setp(ymin=arg[0], ymax=arg[1])
            elif isinstance(arg, str):
                raise NotImplementedError()
        elif nargs == 2:
            ax.setp(ymin=args[0], ymax=args[1])
        else:
            raise TypeError('ylim: wrong number of arguments.')

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def zlim(self, *args):
        """Set or get limits on z axis.

        Calling::

            zlim([zmin,zmax])

        sets the z limits on the current axis.

        Calling::

            zlim(zmin,zmax)

        gives the same results as above.

        Calling::

            zmin, zmax = zlim()

        returns the z limits for the current axis.

        Calling::

            zlim(ax, ...)

        affects the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            zmin = ax.getp('zmin')
            zmax = ax.getp('zmax')
            if zmin is None or zmax is None:
                zmin, zmax = ax.getp('zlim')
            if zmin is None or zmax is None:
                return [0,1]
            return zmin, zmax
        elif nargs == 1:
            arg = args[0]
            if isinstance(arg, (list,tuple,ndarray)) and len(arg) == 2:
                ax.setp(zmin=arg[0], zmax=arg[1])
            elif isinstance(arg, str):
                raise NotImplementedError()
        elif nargs == 2:
            ax.setp(zmin=args[0], zmax=args[1])
        else:
            raise TypeError('zlim: wrong number of arguments.')

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def close(self, *args):
        """Close figure.

        Calling::

            close()

        closes the current figure.

        Calling::

            close(num)

        closes the figure with number num.

        Calling::

            close(fig)

        closes the Figure object fig.

        Calling::

            close('all')

        closes all figures.
        """
        nargs = len(args)
        if nargs == 0:
            self.closefig(self._attrs['curfig'])
        elif nargs == 1:
            if args[0] == 'all':
                self.closefigs()
            else:
                self.closefig(args[0])
        else:
            raise TypeError("close: wrong number of arguments")

    def closefig(self, arg):
        """Close figure window."""
        raise NotImplementedError('closefig not implemented in class %s' % \
                                  self.__class__.__name__)

    def closefigs(self):
        """Close all figure windows."""
        self._figs = {}
        self._figs[1] = Figure()
        self._attrs['curfig'] = 1
        # the rest should be written in subclass

    def grid(self, *args):
        """Toggle the display of grid lines.

        Calling::

            grid('on')

        displays grid lines in the current axis.

        Calling::

            grid('off')

        removes the grid lines from the current axis.

        Calling::

            grid()

        toggles the display of grid lines in the current axis.

        Calling::

            grid(ax, ...)

        uses Axis object ax instead of the current axis.

        Note that calling grid(True) and grid(False) is the same as calling
        grid('on') and grid('off'), respectively.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            ax.toggle('grid')
        elif nargs == 1:
            ax.setp(grid=args[0])
        else:
            raise TypeError("grid: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def legend(self, *args, **kwargs):
        """Add legend(s) to the current plot.

        Calling::

            legend(string1, string2, string3,...)

        or
            legend([string1, string2, string3,...])

        adds legends to the current plot using the given strings as labels.
        Note that the number of strings should match the number of items in
        the current axis (i.e., getp(gca(), 'numberofitems')), but a
        less legends than curve items are allowed.xo

        Calling::

            legend(string)

        adds the given string as a legend to the last item added to the
        current axis.

        Calling::

            legend(ax, ...)

        affects the Axis object ax instead of the current axis.

        The keyword arguments (**kwargs) are ignored, but makes it
        possible to seemlessly switch between easyviz and matplotlib.
        """
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            # unpack the list/tuple to individual arguments
            args = [e for e in args[0]]

        ax, args, nargs = self._check_args(*args)

        for key in kwargs:
            if key == 'loc':
                value = kwargs[key]
                if isinstance(value, int):
                    if 0 <= value <= 10:
                        for loc in Axis._legend_locs:
                            if Axis._legend_locs[loc] == value:
                                value = loc
                                break
                    else:
                        raise ValueError(
                            'legend: wrong value of loc=%s, '
                            'should be between 0 and 10' % value)
                elif isinstance(value, str):
                    if not value in Axis._legend_locs:
                        raise ValueError(
                            'legend: wrong value of loc=%s, '
                            'should be\n%s' % \
                        (value, str([v for v in Axis._legend_locs])[1:-1]))
                else:
                    raise ValueError('legend: wrong value of loc=%s' % value)

                ax.setp(legend_loc=value)

            elif key == 'fancybox':
                value = kwargs[key]
                if not value in (True, False, None):
                    raise ValueError('legend: wrong value of fancybox=%s' % value)
                ax.setp(legend_fancybox=value)
            else:
                print 'legend: ignoring keyword argument "%s"' % key

        items = ax.getp('plotitems')
        if len(items) == 0:
            print 'plot is empty, cannot add legend'
            return
        if nargs > 1:
            # Consistency check of len(args) and number of items in axis
            if len(items) >= nargs:
                # Iterate over items and set legend
                for i in range(nargs):
                    items[i].setp(legend=str(args[i]))
        elif nargs == 1:
            items[-1].setp(legend=str(args[0]))
        else:
            pass # ok with legend() or legend(loc='...'), as in matplotlib


        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def title(self, *args):
        """Add title to the current plot.

        Calling::

            title(s)

        adds the text given in s at the top of the current axis.

        Calling::

            title(ax, ...)

        adds a title to the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 1:
            ax.setp(title=str(args[0]))
        else:
            raise TypeError("title: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def xlabel(self, *args):
        """Add a label to the x-axis.

        Calling::

            xlabel(s)

        adds the text given in s beside the x-axis on the current axis.

        Calling::

            xlabel(ax, ...)

        adds the label to the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 1:
            ax.setp(xlabel=str(args[0]))
        else:
            raise TypeError("xlabel: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def ylabel(self, *args):
        """Add a label to the y-axis.

        Calling::

            ylabel(s)

        adds the text given in s beside the y-axis on the current axis.

        Calling::

            ylabel(ax, ...)

        adds the label to the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 1:
            ax.setp(ylabel=str(args[0]))
        else:
            raise TypeError("ylabel: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def zlabel(self, *args):
        """Add a label to the z-axis.

        Calling::

            zlabel(s)

        adds the text given in s beside the z-axis on the current axis.

        Calling::

            zlabel(ax, ...)

        adds the zlabel to the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 1:
            ax.setp(zlabel=str(args[0]))
        else:
            raise TypeError("zlabel: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    # 2D Plotting
    def plot(self, *args, **kwargs):
        """Draw line and scatter plots.

        Calling::

            plot(x, y)

        plots y against x, i.e., if x and y are vectors of length n, then
        this will plot all the points (x[i], y[i]) for 0<=i<n.

        Calling::

            plot(y)

        plots values in y on y-axis (same as plot(range(len(y)),y)).

        Calling::

            plot(y, fmt)

        plots values in y on y-axis formated like fmt (see below).

        Calling::

            plot(x1,y1,fmt1, x2,y2,fmt2, ...)

        same as hold('on') followed by multiple plot(x,y,fmt).

        Calling::

            plot(x1,y1,x2,y2,...)

        like above, but automatically chooses different colors.

        Calling::

            plot(y1,y2,...,x=x)

        uses x as the x values for all the supplied curves.
        x='auto' has the same effect as x=range(len(y1)).

        Calling::

            plot(...,log=mode)

        uses logarithmic (base 10) scales on either the x- or y-axes (or both).
        mode can be

          * 'x'  - logarithmic scale on x-axis
          * 'y'  - logarithmic scale on y-axis
          * 'xy' - logarithmic scales on both x- and y-axes.

        Calling::

            plot(ax, ...)

        plots into the Axis object ax instead of the current axis.

        The plot command returns a list a of all Line objects created.

        The following format specifiers exist:

            y     yellow        .     point              -     solid
            m     magenta       o     circle             :     dotted
            c     cyan          x     x-mark             -.    dashdot
            r     red           +     plus               --    dashed
            g     green         *     star
            b     blue          s     square
            w     white         d     diamond
            k     black         v     triangle (down)
                                ^     triangle (up)
                                <     triangle (left)
                                >     triangle (right)
                                p     pentagram
                                h     hexagram

        Examples:

        Draw a line from a Python list:
        >>> plot([1,2,3])

        Draw three red crosses:
        >>> plot([1,2,3], 'rx')

        A somewhat more complex example:
        >>> x = linspace(0, 15, 76)   # 0, 0.2, 0.4, ..., 15
        >>> y1 = sin(x)*x
        >>> y2 = sin(x)*sqrt(x)
        >>> plot(x, y1, 'b-', x, y2, 'ro',
        ...      legend=('x*sin(x)', 'sqrt(x)*sin(x)'))

        Note: loglog, semilogy, and semilogx are like plot(...,log='xy'),
        plot(...,log='y'), and plot(...,log='x'), respectively.
        """
        if 'description' not in kwargs:
            kwargs['description'] = 'plot: 2D curve plot'
        if 'label' in kwargs and 'legend' not in kwargs:
            kwargs['legend'] = kwargs['label']

        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            raise TypeError("plot: not enough arguments given")

        lines = [] # store all Line instances here
        # If first argument is a format string this will be ignored
        # If two format strings are used only the first of them will be used
        if 'x' in kwargs:
            if nargs == 1 or (nargs == 2 and isinstance(args[1], str)):
                if nargs == 1:
                    lines.append(Line(x=kwargs['x'], y=args[0], format=''))
                else:
                    lines.append(Line(x=kwargs['x'],
                                      y=args[0],
                                      format=args[1]))
            else:
                for i in range(len(args)-1):
                    if not isinstance(args[i], str):
                        if isinstance(args[i+1], str):
                            lines.append(Line(x=kwargs['x'],
                                              y=args[i],
                                              format=args[1+i]))
                        else:
                            lines.append(Line(x=kwargs['x'],
                                              y=args[i],
                                              format=''))
                            if i == nargs-2:
                                lines.append(Line(x=kwargs['x'],
                                                  y=args[i+1],
                                                  format=''))
            del kwargs['x']  # x in kwargs is no longer needed
        else: # Normal case
            # If an odd number, larger than 2, of non-strings in args are
            # between two string arguments, something is wrong.
            # If the odd number is one, the argument x='auto' is passed.
            i = 0
            if nargs in (1,2):
                if not isinstance(args[0], str):
                    if nargs == 1:
                        lines.append(Line(x='auto',
                                          y=args[0],
                                          format=''))
                    else:
                        if not isinstance(args[1], str):
                            lines.append(Line(x=args[0],
                                              y=args[1],
                                              format=''))
                        else:
                            lines.append(Line(x='auto',
                                              y=args[0],
                                              format=args[1]))
                    i+100 #return
                else:
                    raise ValueError("plot: cannot plot a formatstring")

            while i <= nargs-3:
                # This item is not string --> y-value, should never be string.
                if not isinstance(args[i], str):
                    if not isinstance(args[i+1], str):
                        if isinstance(args[i+2], str):
                            lines.append(Line(x=args[i],
                                              y=args[i+1],
                                              format=args[i+2]))
                            i = i+3
                        else:
                            lines.append(Line(y=args[i+1],
                                              x=args[i],
                                              format=''))
                            i = i+2

                    # Next element is str --> no x-value
                    else:
                        lines.append(Line(y=args[i],
                                          x='auto',
                                          format=args[i+1]))
                        i = i+2
                    # These last cases could be run outside the while loop
                    if i == nargs-2:
                        # Either y and format or x and y value left
                        if isinstance(args[i+1], str):
                            lines.append(Line(y=args[i],
                                              x='auto',
                                              format=args[i+1]))
                        else:
                            lines.append(Line(x=args[i],
                                              y=args[i+1],
                                              format=''))
                    elif i == nargs-1:
                        # In this case we have only an y value left
                        lines.append(Line(y=args[i],
                                          x='auto',
                                          format=''))

        # add the lines to the axes in ax:
        ax.add(lines)

        # Set legends
        if 'legend' in kwargs:
            no_lines = len(lines) # number of lines added
            legends = kwargs['legend']
            if isinstance(legends, (tuple,list)): # legends is a sequence
                if len(legends) == no_lines:
                    for i in range(no_lines):
                        legend = legends[no_lines-i-1]
                        if isinstance(legend, str):
                            ax.getp('plotitems')[-1-i].setp(legend=legend)
                        else:
                            print "Legend "+legend+" is not a string"
                else:
                    print 'Number of legend items (%d) is not equal to '\
                          'number of lines in plotcommand (%d)' % \
                          (len(legends), no_lines)
            elif isinstance(legends,str): # only one legend
                ax.getp('plotitems')[-1].setp(legend=legends)
            del kwargs['legend']

        if 'legend_loc' in kwargs:
            # No test on validity as in legend method...
            ax.setp(legend_loc=kwargs['legend_loc'])
        if 'legend_fancybox' in kwargs:
            ax.setp(legend_fancybox=kwargs['legend_fancybox'])

        if not ax.getp('hold') and not 'box' in kwargs:
            kwargs['box'] = True

        # set keyword arguments in all the added lines
        for line in lines:
            line.setp(**kwargs)
            # automatically add line colors if this is not specified:
            if not line.getp('linecolor'):
                line.setp(linecolor=ax.get_next_color())
        ax.setp(**kwargs)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()

        return lines

    def loglog(self, *args, **kwargs):
        """Draw a loglog plot with logarithmic scaling on x- and y-axis.

        Calling::

            loglog(...)

        is the same as calling plot(...) with the exception that a
        logarithmic (base 10) scale is used for both x- and y-axes.
        """
        kwargs['log'] = 'xy'
        return self.plot(*args, **kwargs)

    def semilogx(self, *args, **kwargs):
        """Draw a semilog plot with logarithmic scaling on x-axis.

        Calling::

            semilogx(...)

        is the same as calling plot(...) with the exception that a
        logarithmic (base 10) scale is used for the x-axis.
        """
        kwargs['log'] = 'x'
        return self.plot(*args, **kwargs)

    def semilogy(self, *args, **kwargs):
        """Draw a semilog plot with logarithmic scaling on y-axis.

        Calling::

            semilogy(...)

        is the same as calling plot(...) with the exception that a
        logarithmic (base 10) scale is used for the y-axis.
        """
        kwargs['log'] = 'y'
        return self.plot(*args, **kwargs)

    def plot3(self, *args, **kwargs):
        """Draw lines and points in 3D space.

        Calling::

            plot3(x, y, z)

        plots z against x and y, i.e., if x, y, and z are vectors of length n,
        then this will plot all the points (x[i], y[i], z[i]) for 0<=i<n.

        Calling::

            plot3(z)

        plots values in z on the z-axis
        (same as plot3(range(len(z)), range(len(z)), z)).

        Calling::

            plot3(z, fmt)

        plots values in z on z-axis formated like fmt (see the plot command).

        Calling::

            plot3(x1,y1,z1,fmt1,x2,y2,z2,fmt2,...)

        same as hold('on') followed by multiple plot3(x,y,z,fmt).

        Calling::

            plot3(x1,y1,z1,x2,y2,z2,...)

        like above, but automatically chooses different colors.

        Calling::

            plot3(z1,z2,...,x=x,y=y)

        uses x as the values on the x-axis and y as the values on the y-axis
        for all the supplied curves (assuming that all have the same length).
        By setting x='auto' and y='auto' has the same effect as
        x=range(len(z1)) and y=range(len(z1)), respectively.

        Calling::

            plot3(ax, ...)

        plots into the Axis object ax instead of the current axis.

        The plot3 command returns a list containing all the created Line
        objects.

        Examples:

        >>> t = linspace(0,10*pi,301)
        >>> plot3(sin(t), cos(t), t, title='A helix', grid='on')
        """
        if not 'description' in kwargs:
            kwargs['description'] = 'plot3: 3D line plot'
        if not 'hidden' in kwargs:
            kwargs['hidden'] = False
        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            raise TypeError("plot3: not enough arguments given")

        lines = [] # all Line instances are stored here

        # If first argument is a format string this will be ignored
        # If two format strings are used only the first of them will be used
        if 'x' in kwargs and 'y' in kwargs:
            if nargs == 1 or (nargs == 2 and isinstance(args[1], str)):
                if nargs == 1:
                    lines.append(Line(x=kwargs['x'],
                                      y=kwargs['y'],
                                      z=args[0],
                                      format=''))
                else:
                    lines.append(Line(x=kwargs['x'],
                                      y=kwargs['y'],
                                      z=args[0],
                                      format=args[1]))
            else:
                for i in range(len(args)-1):
                    if not isinstance(args[i], str):
                        if isinstance(args[i+1], str):
                            lines.append(Line(x=kwargs['x'],
                                              y=kwargs['y'],
                                              z=args[i],
                                              format=args[1+i]))
                        else:
                            lines.append(Line(x=kwargs['x'],
                                              y=kwargs['y'],
                                              z=args[i],
                                              format=''))
                            if i == nargs-2:
                                lines.append(Line(x=kwargs['x'],
                                                  y=kwargs['y'],
                                                  z=args[i+1],
                                                  format=''))
            # x and y in kwargs are no longer needed:
            del kwargs['x']
            del kwargs['y']
        else: # Normal case
            # If an odd number, larger than 2, of non-strings in args are
            # between two string arguments, something is wrong.
            # If the odd number is one, the argument x='auto' is passed.
            i = 0
            if nargs in (1,2,3,4):
                if not isinstance(args[0], str):
                    if nargs == 1: # plot3(z)
                        lines.append(Line(x='auto', y='auto', z=args[0],
                                          format=''))
                    elif nargs == 2: # plot3(z,fmt)
                        if isinstance(args[1], str):
                            lines.append(Line(x='auto', y='auto', z=args[0],
                                              format=args[1]))
                    elif nargs == 3: # plot3(x,y,z)
                        if not isinstance(args[2], str):
                            lines.append(Line(x=args[0], y=args[1], z=args[2],
                                              format=''))
                    else: # plot(x,y,z,fmt) or plot(z1,fmt1,z2,fmt2)
                        if not isinstance(args[3], str):
                            lines.append(Line(x='auto', y='auto', z=args[0],
                                              format=args[1]))
                            lines.append(Line(x='auto', y='auto', z=args[2],
                                              format=args[3]))
                        else:
                            lines.append(Line(x=args[0], y=args[1], z=args[2],
                                              format=args[3]))
                    i+100 #return
                else:
                    raise ValueError("plot3: cannot plot a formatstring")

            while i <= nargs-5:
                if not isinstance(args[i], str): # should never be string
                    # cases:
                    # 1. plot3(x1,y1,z1,s1, x2,y2,z2,s2, ...)
                    if not isinstance(args[i+1], str):
                        if not isinstance(args[i+2], str):
                            if isinstance(args[i+3], str):
                                lines.append(Line(x=args[i],
                                                  y=args[i+1],
                                                  z=args[i+2],
                                                  format=args[i+3]))
                                i += 4
                            else:
                                lines.append(Line(x=args[i],
                                                  y=args[i+1],
                                                  z=args[i+2],
                                                  format=''))
                                i += 3
                    else: # next element is str --> no x and y values
                        lines.append(Line(x='auto', y='auto', z=args[i],
                                          format=args[i+1]))
                        i += 2

                    # 2. plot3(x1,y1,z1, x2,y2,z2, ...)
                    # 3. plot3(z1,s1, z2,s2, ...)

                    if i == nargs-4:
                        if not isinstance(args[i+1], str):
                            lines.append(Line(x=args[i],
                                              y=args[i+1],
                                              z=args[i+2],
                                              format=args[i+3]))
                        else:
                            lines.append(Line(x='auto', y='auto', z=args[i],
                                              format=args[i+1]))
                            lines.append(Line(x='auto', y='auto', z=args[i+2],
                                              format=args[i+3]))
                    elif i == nargs-3: # x, y, and z left
                        lines.append(Line(x=args[i], y=args[i+1], z=args[i+2],
                                          format=''))
                    elif i == nargs-2: # only z and format string left
                        if isinstance(args[i+1], str):
                            lines.append(Line(x='auto', y='auto', z=args[i],
                                              format=args[i+1]))
                    elif i == nargs-1: # only a z value left
                        lines.append(Line(x='auto', y='auto', z=args[i],
                                          format=''))

        # add the lines to the axes in ax:
        ax.add(lines)

        # Set legends
        if 'legend' in kwargs:
            no_lines = len(lines)
            legends = kwargs['legend']
            if isinstance(legends, (tuple,list)): # legends is a sequence
                if len(legends) == no_lines:
                    for i in range(no_lines):
                        legend = legends[no_lines-i-1]
                        if isinstance(legend, str):
                            ax.getp('plotitems')[-1-i].setp(legend=legend)
                        else:
                            print "Legend "+legend+" is not a string"
                else:
                    print "Number of legend items (%d) is not equal to " \
                          "number of lines (%d) in plotcommand" % \
                          (len(legends), no_lines)
            elif isinstance(legends,str): # only one legend
                ax.getp('plotitems')[-1].setp(legend=legends)
            del kwargs['legend']

        if not ax.getp('hold') and not 'view' in kwargs:
            kwargs['view'] = 3

        # set keyword arguments in all the added lines:
        for line in lines:
            line.setp(**kwargs)
            # automatically add line colors if this is not specified:
            if not line.getp('linecolor'):
                line.setp(linecolor=ax.get_next_color())
        ax.setp(**kwargs)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()

        return lines

    def fill(self, *args, **kwargs):
        """Draw filled 2D polygons."""
        kwargs['description'] = 'fill: filled 2D polygons'
        if not 'edgecolor' in kwargs:
            kwargs['edgecolor'] = 'k'
        return self.plot(*args, **kwargs)

    def stem(self, *args, **kwargs):
        """Draw a stem plot."""
        kwargs['description'] = 'stem: stem plot'
        return self.plot(*args, **kwargs)

    def bar(self, *args, **kwargs):
        """Draw a bar graph.

        Calling::

           bar(data)

        where data is a dictionary on the form

          data = {'method1': {'thing1': value, 'thing2': value},
                  'method2': {'thing1': value, 'thing2': value},
                  'method3': {'thing1': value, 'thing2': value},}

        will draw m bars for every name (key in data), one for each key in
        data[name], where the height indicates the value. The name is placed
        beneath each of the bar groups on the x axis.

        Calling::

            bar(Y)

        will draw a bar for each of the elements in the vector/matrix Y.
        If Y is a matrix, a group of bars from the elements of each row of
        Y will be created.

        Calling::

            bar(x,Y)

        is the same as above only that the values on the x axis is defined
        by the vector x.

        Calling::

            bar(..., width)

        uses the specified width on the bars. The default width is 0.8, while
        a width of 1.0 should make the bars just touch each other (might vary
        in the different backends).

        Calling::

            bar(..., color)

        uses the given color for all the bars.

        Calling::

            bar(ax, ...)

        uses the Axis object ax instead of the current axis.

        @return: A Bars object.

        Examples:

        >>> from numpy.random import rand
        >>> bar(rand(4))

        >>> figure()
        >>> bar(rand(4,3))
        """
        kwargs['description'] = 'bar: bar graph'
        ax, args, nargs = self._check_args(*args)
        h = Bars(*args, **kwargs)
        ax.add(h)
        if not ax.getp('hold'):
            if not 'box' in kwargs:
                kwargs['box'] = True
        ax.setp(**kwargs)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()
        return h

    def quiver(self, *args, **kwargs):
        """Draw arrows from a 2D vector field.

        Calling::

            quiver(X, Y, U, V)

        displays vectors as arrows with components U and V at the grid
        defined by X and Y. The arrays U and V must both have the same shape
        and the grid components X and Y must either have the same shape as
        U or fulfill the requirement len(X)==n and len(y)==m, where
        m,n=shape(u).

        Calling::

            quiver(U, V)

        is the same as calling quiver(range(n),range(m),U,V), where
        m,n=shape(u)).

        Calling::

            quiver(..., 'filled')

        draw filled arrows.

        Calling::

            quiver(..., fmt)

        sets the line specification as given in the format string fmt. See
        the plot command for further details on specifying the format string.

        Examples:

        Plot the gradient field of the function z = x**2 + y**2:
        >>> x = y = linspace(-2, 2, 21)
        >>> xv, yv = meshgrid(x,y)
        >>> values = xv**2 + yv**2
        >>> contour(xv, yv, values, 10, hold='on')
        <scitools.easyviz.common.Contours object at 0xb45f374c>
        >>> uv, vv = gradient(values, 0.2)
        >>> quiver(xv, yv, uv, vv)
        <scitools.easyviz.common.VelocityVectors object at 0xb45435cc>
        >>> hold('off')

        Another example:
        >>> x = linspace(0,3,80)
        >>> y = sin(2*pi*x)
        >>> theta = 2*pi*x+pi/2
        >>> u = sin(theta)/10
        >>> v = cos(theta)/10
        >>> quiver(x,y,u,v,0.04,'b',hold='on')
        <scitools.easyviz.common.VelocityVectors object at 0xb768e1cc>
        >>> plot(x,y,'r')
        [<scitools.easyviz.common.Line object at 0xb768e36c>]
        >>> hold('off')
        """
        if not 'description' in kwargs:
            kwargs['description'] = 'quiver: 2D vector field'
        ax, args, nargs = self._check_args(*args)
        h = VelocityVectors(*args, **kwargs)
        ax.add(h)
        if not ax.getp('hold'):
            if 'quiver3' in kwargs['description']:
                if not 'grid' in kwargs:
                    kwargs['grid'] = True
                if not 'view' in kwargs:
                    kwargs['view'] = 3
            else:
                if not 'box' in kwargs:
                    kwargs['box'] = True
        ax.setp(**kwargs)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()
        return h

    def contour(self, *args, **kwargs):
        """Draw a 2D contour plot.

        Calling::

            contour(X, Y, Z)

        displays a contour plot where the values in the scalar field Z are
        treated as heights above a plane. The grid components X and Y must
        either have the same shape as Z or fulfill the requirement len(X)==n
        and len(Y)==m, where m,n=shape(Z).

        Calling::

            contour(Z)

        is the same as calling contour(range(n),range(m),Z), where
        m,n=shape(Z).

        Calling::

            contour(..., n)

        displays a contour plot with n contour lines (default is 8 lines).

        Calling::

            contour(..., v)

        displays contours at levels given in the array v.

        Calling::

            contour(..., fmt)

        uses the color and line style as given in the format string fmt to
        draw the contour lines (see the plot command for further details on
        format strings). This overrides the default behavior of using the
        current colormap to color the contour lines.

        Calling::

            contours(ax, ...)

        plots into the Axis object ax instead of the current axis.

        Calling::

            contour(...,clabels='on')

        is the same as calling h=contour(...) followed by clabel(h,'on').

        Examples:

        >>> # draw a contour plot of the peaks function:
        >>> x = y = linspace(-3, 3, 13)
        >>> xv, yv = meshgrid(x, y)
        >>> values = peaks(xv, yv)
        >>> contour(xv, yv, values)

        Draw 10 red contour lines with double line width:
        >>> contour(xv, yv, values, 10, 'r', linewidth=2)

        Draw contour lines at -2, 0, 2, and 5:
        >>> contour(xv, yv, values, [-2,0,2,5])
        """
        if not 'description' in kwargs:
            kwargs['description'] = 'contour: 2D contours at base'
        ax, args, nargs = self._check_args(*args)
        h = Contours(*args, **kwargs)
        ax.add(h)
        if not ax.getp('hold'):
            if 'contour3' in kwargs['description']:
                if not 'grid' in kwargs:
                    kwargs['grid'] = True
                if not 'view' in kwargs:
                    kwargs['view'] = 3
            else:  # contour or contourf
                if not 'box' in kwargs:
                    kwargs['box'] = True
        ax.setp(**kwargs)
        if h.getp('function') == 'contour3':
            ax.getp('camera').setp(view=3)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()
        return h

    def contourf(self, *args, **kwargs):
        """Draw filled contour plot.

        Calling::

            contourf(...)

        is the same as calling contour(...) with the exception that the space
        between the contour lines is filled with colors.

        Examples:

        >>> contourf(peaks(), clabel='on', colorbar='on')
        """
        kwargs['description'] = 'contourf: 2D filled contour plot'
        return self.contour(*args, **kwargs)

    # 3D plotting

    def pcolor(self, *args, **kwargs):
        """Draw a 2D pseudocolor plot.

        Calling::

            pcolor(C)

        draw a pseudocolor plot of the 2D array C.

        Calling::

            pcolor(X,Y,C)

        same as above, only that the grid is specified by the X and Y arrays.
        These arrays must either have the same shape as C or fulfill the
        requirement len(X)==n and len(Y)==m, where m,n=shape(C).

        Calling::

            pcolor(ax, ...)

        uses the Axis object ax instead of the current axis.

        Examples:

        Simple pseudocolor plot:
        >>> pcolor(peaks(31))

        Draw a pseudocolor plot with interpolated shading:
        >>> pcolor(peaks(), shading='interp',
        ...        colorbar='on', colormap=hot())
        """
        kwargs['description'] = 'pcolor: pseudocolor plot'
        ax, args, nargs = self._check_args(*args)
        h = Surface(*args, **kwargs)
        ax.add(h)
        if not ax.getp('hold') and not 'box' in kwargs:
            kwargs['box'] = True
        ax.setp(**kwargs)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()
        return h

    def fill3(self):
        """Draw filled 3D polygons."""
        raise NotImplementedError("'fill3' is not implemented.")

    def streamline(self, *args, **kwargs):
        """Draw streamlines from 2D or 3D vector data.

        Calling::

            streamline(X,Y,Z,U,V,W,startx,starty,startz)

        will draw streamlines from the 3D vector field with components
        U,V,W defined on the grid given by X,Y,Z. The arrays U,V,W should
        all have the same shape and the grid components X,Y,Z must either
        have the same shape as U or fulfill the requirement len(X)==n,
        len(Y)==m, and len(Z)==p, where m,n,p=shape(U). The starting
        positions for the streamlines are defined in the arrays startx,
        starty, and startz.

        Calling::

            streamline(U,V,W,startx,starty,startz)

        is the same as above, except that it is assumed that
        X,Y,Z = meshgrid(range(n),range(m),range(p)), where m,n,p=shape(U).

        Calling::

            streamline(X,Y,U,V,startx,starty)

        will draw streamlines from the 2D vector field with components U,V
        defined on the grid given by X,Y. The arrays U,V should have the same
        shape and the grid componetns X,Y mist either have the same shape as
        U or fulfill the requirement len(X)==n and len(Y)==m, where
        m,n=shape(u). The starting positions for the streamlines are defined
        in the arrays startx and starty.

        Calling::

            streamline(U,V,startx,starty)

        is the same as above, except that it is assumed that
        X,Y = meshgrid(range(n),range(m)), where m,n=shape(U).

        Calling::

            streamline(..., stepsize)

        uses the given step size instead of the default step size of 0.1.

        Calling::

            streamline(ax, ...)

        uses the Axis object ax instead of the current axis.

        The streamline command returns a Streams object.

        Examples:

        FIXME: Add streamline example.
        """
        if not 'description' in kwargs:
            kwargs['description'] = "streamline: 2D or 3D streamline"
        ax, args, nargs = self._check_args(*args)
        h = Streams(*args, **kwargs)
        ax.add(h)
        ax.setp(**kwargs)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()
        return h

    def streamtube(self, *args, **kwargs):
        """Draw stream tubes from 3D vector data.

        Calling::

            streamtube(...)

        is the same as calling streamlines(...), except that only 3D vector
        fields are supported by the streamtube command. The optional
        positional argument stepsize is not supported either.

        Calling::

            streamtube(..., [scale, n])

        will scale the width of the tubes according to scale (default is 1),
        while the variable n sets the number of points along the
        circumference of the tube (default is 20).

        Examples:

        FIXME: Add streamtube example.
        """
        kwargs['description'] = "streamtube: 3D stream tube"
        return self.streamline(*args, **kwargs)

    def streamribbon(self, *args, **kwargs):
        """Draw stream ribbons from 3D vector data.

        Calling::

            streamribbon(...)

        is the same as calling streamlines(...), except that only 3D vector
        fields are supported by the streamribbon command. The optional
        positional argument stepsize is not supported either.

        Calling::

            streamribbon(..., width)

        specifies the width of the ribbons.

        Examples:

        FIXME: Add streamribbon example.
        """
        kwargs['description'] = "streamribbon: 3D stream ribbon"
        return self.streamline(*args, **kwargs)

    def mesh(self, *args, **kwargs):
        """Draw a 3D mesh surface.

        Calling::

            mesh(X, Y, Z[, C])

        plots the colored mesh defined by scalar field Z defined on the grid
        given by X and Y. The grid components X and Y must either have the
        same shape as Z or fulfill the requirement len(X)==n and len(Y)==m,
        where m,n=shape(Z). The color is determined by the array C which must
        have the same shape as Z. If the color array C is not given, Z is used
        as the color array (i.e., C=Z).

        Calling::

            mesh(Z[, C])

        is the same as calling mesh(range(n), range(m), Z[, C]),
        where m,n = shape(Z).

        Calling::

            mesh(ax, ...)

        plots into the Axis object ax instead of the current axis.

        @return: A Surface object.

        Examples:

        >>> x = y = linspace(-2, 2, 21)
        >>> xx, yy = meshgrid(x, y)
        >>> zz = exp(-xx**2)*exp(-yy**2)
        >>> mesh(xx, yy, zz)
        """
        if not 'description' in kwargs:
            kwargs['description'] = 'mesh: 3D mesh'
        ax, args, nargs = self._check_args(*args)
        h = Surface(*args, **kwargs)
        ax.add(h)
        if not ax.getp('hold'):
            if not 'grid' in kwargs:
                kwargs['grid'] = True
            if not 'view' in kwargs:
                kwargs['view'] = 3
        ax.setp(**kwargs)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()
        return h

    def meshc(self, *args, **kwargs):
        """Draw a mesh with a contour plot beneath.

        Calling::

            meshc(...)

        is the same as calling mesh(...) only that a contour plot is drawn
        beneath the mesh.

        Examples:

        Draw a mesh with contour lines:
        >>> x = linspace(-2, 2, 21)
        >>> xx, yy = meshgrid(x)
        >>> zz = peaks(xx, yy)
        >>> meshc(xx, yy, zz)

        Draw a mesh with 20 contour lines:
        >>> meshc(xx, yy, zz, clevels=20)

        Draw a mesh with contour lines at height -0.2, -0.5, 0.2, 0.5:
        >>> meshc(xx, yy, zz, cvector=[-0.2,-0.5,0.2,0.5])

        Draw a mesh with contours and label the contours:
        >>> meshc(xx, yy, zz, clabels='on')
        """
        kwargs['description'] = 'meshc: 3D mesh with contours at base'
        return self.mesh(*args, **kwargs)

    def surf(self, *args, **kwargs):
        """Draw a 3D solid surface.

        Calling::

            surf(...)

        is the same as calling mesh(...), except that a solid colored surface
        is drawn instead of a wireframe mesh.

        Examples:

        >>> x = linspace(-2, 2, 21)
        >>> xx, yy = meshgrid(x)
        >>> zz = xx**2 + yy**2
        >>> surf(xx, yy, zz)
        """
        if not 'description' in kwargs:
            kwargs['description'] = 'surf: 3D surface'
        return self.mesh(*args, **kwargs)

    def surfc(self, *args, **kwargs):
        """Draw a solid surface with contours beneath.

        Calling::

            surfc(...)

        is the same as calling surf(...) only that a contour plot is drawn
        beneath the surface.
        """
        kwargs['description'] = 'surfc: 3D surface with contours at base'
        return self.surf(*args, **kwargs)

    def surfl(self, *args, **kwargs):
        """3D shaded surface with lighting."""
        raise NotImplemetedError("'surfl' is not implemented")

    def quiver3(self, *args, **kwargs):
        """Draw velocity vectors in 3D space.

        Calling::

            quiver3(X, Y, Z, U, V, W)

        plots arrows from the 3D vector field with components U,V,W at the
        grid defined by X,Y,Z. The shape of the three vector components is
        assumed to be the same, while the grid components must either have
        the same shape as U or fulfill the requirements len(X)==n, len(Y)==m,
        and len(Z)==p, where m,n,p=shape(U).

        Calling::

            quiver3(Z,U,V,W)

        gives the same result as above, but it is assumed that
        X,Y = meshgrid(range(n),range(m)), where m,n=shape(Z).

        Calling::

            quiver3(..., s)

        scales the arrows by the scale factor given in s. The default is s=1,
        while a value of s=0 turns off automatic scaling.

        Calling::

            quiver3(..., 'filled')

        fills the arrows.

        Calling::

            quiver3(..., fmt)

        sets the specification on the arrows as given in the format string
        fmt (see the plot command for further information on format strings).

        Calling::

            quiver3(ax, ...)

        plots the vectors in the Axis object ax instead of the current axis.

        @return: A VelocityVectors object.

        Examples:

        Draw the "radius vector field" v = (x,y,z):
        >>> x = y = linspace(-3,3,4)
        >>> xv, yv, zv = meshgrid(x, y, sparse=False)
        >>> yv, vv, wv = xv, yv, zv
        >>> quiver3(xv, yv, zv, uv, uv, wv, 'filled', 'r',
        ...         axis=[-7,7,-7,7,-7,7])

        Draw the path of a projectile as a function of time:
        FIXME: This example is taken from ...
        >>> vz = 10  # Velocity
        >>> a = -32  # Acceleration
        >>> t = linspace(0,1,11)
        >>> z = vz*t + 1./2*a*t**2
        >>> vx = 2
        >>> x = vx*t
        >>> vy = 3
        >>> y = vy*t
        >>> u = gradient(x)
        >>> v = gradient(y)
        >>> w = gradient(z)
        >>> scale = 0
        >>> quiver3(x,y,z,u,v,w,0,view=[70,18],grid='on',
        ...         axis=[0,3.5,0,3,-10,2])
        """
        kwargs['description'] = "quiver3: 3D vector field"
        return self.quiver(*args, **kwargs)

    def contour3(self, *args, **kwargs):
        """Draw 3D contour plot.

        Calling::

            contour3(...)

        is the same as calling contour(...), except that the contours are
        drawn at their coresponding height level.

        Examples:

        >>> contour3(peaks())
        """
        kwargs['description'] = "contour3: 3D contours at surface"
        return self.contour(*args, **kwargs)

    # Volume plotting
    def slice_(self, *args, **kwargs):
        """Draw volumetric slice plot.

        Calling::

            slice_(X,Y,Z,V,Sx,Sy,Sz)

        draws orthogonal slice planes through the volumetric data set V
        defined on the grid with components X, Y, and Z. The grid components
        must either have the same shape as V or fulfill the requirement
        len(X)==n, len(Y)==m, and len(Z)==p, where m,n,p=shape(V). The Sx,
        Sy, and Sz arrays defines the slice planes in the x, y, and z
        direction, respectively.

        Calling::

            slice_(V,Sx,Sy,Sz)

        is the same as calling slice_(range(n),range(m),range(p),V,Sx,Sy,Sz),
        where m,n,p = shape(V).

        Calling::

            slice_(X,Y,Z,V,XI,YI,ZI)

        draws slices through the volumetric data set V along the surface
        defined by the arrays XI,YI,ZI.

        Calling::

            slice_(V,XI,YI,ZI)

        is the same as calling slice_(range(n),range(m),range(p)),V,XI,YI,ZI),
        where m,n,p = shape(V).

        Calling::

            slice_(..., method)

        sets which interpolation method to be used, where method can be either
        'linear' (default), 'cubic', or 'nearest'.

        Calling::

            slice(ax, ...)

        plots into the Axis object ax instead of the current axis.

        @return: A Volume object.

        Examples:

        Visualize the function x*exp(-x**2-y**2-z**2) over the range
        -2 > x,y,z < 2:
        >>> xx, yy, zz = meshgrid(linspace(-2,2,21), linspace(-2,2,17),
        ...                       linspace(-2,2,25))
        >>> vv = x*exp(-xx**2-yy**2-zz**2)
        >>> slice_(xx, yy, zz, vv, [-1.2,.8,2], 2, [-2,-.2])
        """
        if not 'description' in kwargs:
            kwargs['description'] = 'slice_: volumetric slices'
        ax, args, nargs = self._check_args(*args)
        h = Volume(*args, **kwargs)
        ax.add(h)
        if not ax.getp('hold'):
            if 'slice_' in kwargs['description']:
                if not 'grid' in kwargs:
                    kwargs['grid'] = True
                if not 'view' in kwargs:
                    kwargs['view'] = 3
        ax.setp(**kwargs)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()
        return h

    def contourslice(self, *args, **kwargs):
        """Draw contour lines in slice planes.

        Calling::

            contourslice(X,Y,Z,V,Sx,Sy,Sz)

        will draw contour lines in planes aligned with the coordinate axes
        at the points in the arrays Sx, Sy, and Sz. The arrays X, Y, and Z
        defines the grid coordinates for the volume V and they must either
        have the same shape as V or fulfill the requirement len(X)==n,
        len(Y)==m, and len(Z)==p, where m,n,p = shape(V).

        Calling::

            contourslice(V,Sx,Sy,Sz)

        is the same as above, but it is assumed that
        X,Y,Z = meshgrid(range(n),range(m),range(p)), where m,n,p = shape(V).

        Calling::

            contourslice(X,Y,Z,V,XI,YI,ZI)

        will draw contour lines through the volume V along the surface given
        in the arrays XI, YI, and ZI.

        Calling::

            contourslice(V,XI,YI,ZI)

        is the same as above, but it is assumed that
        X,Y,Z = meshgrid(range(n),range(m),range(p)), where m,n,p = shape(V).

        Calling::

            contourslice(..., n)

        will draw n contour lines per plane instead of the default of five
        contour lines.

        Calling::

            contourslice(..., v)

        will draw contour lines at the levels given in the array v.

        Calling::

            contourslice(ax, ...)

        uses the Axis object ax instead of the current axis.

        @return: A Volume object.

        Example:
        >>> xx, yy, zz = meshgrid(linspace(-2,2,21), linspace(-2,2,17),
        ...                       linspace(-2,2,25))
        >>> vv = xx*exp(-xx**2-yy**2-zz**2)
        >>> contourslice(xx, yy, zz, vv, [-.7,.7], [], [0], view=3)
        """
        kwargs['description'] = 'contourslice: contours in slice planes'
        return self.slice_(*args, **kwargs)

    def coneplot(self, *args, **kwargs):
        """Draw a 3D cone plot.

        Calling::

            coneplot(X,Y,Z,U,V,W,Cx,Cy,Cz)

        draws velocity vectors as cones from the 3D vector field defined by
        U, V, and W at the points given in the arrays Cx, Cy, and Cz. The
        arrays X, Y, and Z defines the grid coordinates for vector field. The
        shape of U, V, and W is assumed to be the same, while the grid
        components must either have the same shape as U or fulfill the
        requirement len(X)==n, len(Y)==m, and len(Z)==p, where m,n,p=shape(U).

        Calling::

            coneplot(U,V,W,Cx,Cy,Cz)

        is the same as above, but it is assumed that
        X,Y,Z = meshgrid(range(n),range(m),range(p)), where m,n,p = shape(U).

        Calling::

            coneplot(..., scale)

        will automatically scale the cones by the factor scale (default is 1).
        To turn of automatic scaling, use a scale value of 0.

        Calling::

            coneplot(..., C)

        uses the colors in the array C to color the cones (C must have the
        same shape as U).

        Calling::

            coneplot(..., 'quiver')

        will plot arrows instead of cones.

        Calling::

            coneplot(ax, ...)

        uses the Axis object ax instead of the current axis.

        @return: A Streams object.

        Examples:

        FIXME: Add conplot example.
        """
        kwargs['description'] = "coneplot: 3D cone plot"
        ax, args, nargs = self._check_args(*args)
        h = Streams(*args, **kwargs)
        ax.add(h)
        ax.setp(**kwargs)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()
        return h

    def streamslice(self, *args, **kwargs):
        """Draw streamlines in axis aligned slice planes.

        Calling::

            streamslice(X,Y,Z,U,V,W,startx,starty,startz)

        will draw streamlines (with direction arrows) from the 3D vector field
        with components U, V, and W in planes aligned with the coordinate axes
        at the points given in the arrays startx, starty, and startz. The
        arrays U, V, and W must all have the same shape and the grid
        coordinates given in the arrays X, Y, and Z must either have the same
        shape as U or fulfill the requirement len(X)==n, len(Y)==m, and
        len(Z)==p, where m,n,p=shape(U).

        Calling::

            streamslice(U,V,W,startx,starty,startz)

        is the same as above, except that it is assumed that
        X,Y,Z = meshgrid(range(n),range(m),range(p)), where m,n,p=shape(U).

        Calling::

            streamslice(X,Y,U,V)

        will draw streamlines from the 2D vector field with components U and
        V. The vector components must have equal shape and the arrays X and Y
        should either have the same shape as U or fulfill the requirement
        len(X)==n and len(Y)==m, where m,n=shape(U).

        Calling::

            streamslice(U,V)

        is the same as above, except that it is assumed that
        X,Y = meshgrid(range(n),range(m)), where m,n=shape(U).

        Calling::

            streamslice(..., 'arrows')

        will display direction arrows (default).

        Calling::

            streamslice(..., 'noarrows')

        will not display direction arrows.

        Calling::

            streamslice(ax, ...)

        uses the Axis object ax instead of the current axis.

        @return: A ??? object.

        Examples:

        >>> import scipy
        >>> wind = scipy.io.loadmat('wind.mat')
        >>> x = wind['x']
        >>> y = wind['y']
        >>> z = wind['z']
        >>> u = wind['u']
        >>> v = wind['v']
        >>> w = wind['w']
        >>> streamslice(x,y,z,u,v,w,[],[],[4],daspect=[1,1,1])
        """
        raise NotImplementedError("'streamslice' is not implemented.")

    def isocaps(self, *args, **kwargs):
        """Draw isosurface end caps."""
        raise NotImplementedError("'isocaps' is not implemented.")

    def isosurface(self, *args, **kwargs):
        """Draw isosurfaces from 3D scalar fields.

        Calling::

            isosurface(X,Y,Z,V,isovalue)

        creates an isosurface for the volume V at the iso value given by
        isovalue. The arrays X, Y, and Z defines the grid for the volume V
        and they must either have the same shape as V or fulfill the
        requirement len(X)==n, len(Y)==m, and len(Z)==p, where
        m,n,p = shape(V).

        Calling::

            isosurface(V,isovalue)

        is the same as above, but it is assumed that
        X,Y,Z = meshgrid(range(n),range(m),range(p)), where m,n,p = shape(V).

        Calling::

            isosurface(..., C)

        uses the colors in the array C instead of the colors in the
        scalar field V (C and V must have the same shape).

        @return: A Volume object.

        Examples:

        >>> x, y, z, v = flow()
        >>> isosurface(x, y, z, v, -3, daspect=[1,1,1])
        """
        kwargs['description'] = 'isosurface: isosurface extractor'
        ax, args, nargs = self._check_args(*args)
        h = Volume(*args, **kwargs)
        ax.add(h)
        if not ax.getp('hold') and not 'view' in kwargs:
            kwargs['view'] = 3
        ax.setp(**kwargs)
        self.gcf().setp(**kwargs)
        self.setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()
        return h

    def show(self):
        """Redraw the current figure."""
        self._replot()

    def hidden(self, *args):
        """Toggle hidden line removal in the current axis.

        Calling::

            hidden(state)

        turns hidden line removal on if state is 'on' (or True) and off if
        state is 'off' (or False). Hidden line removal is turned on by
        default.

        Calling::

            hidden()

        toggles the hidden state.

        Note: Some backends has no support for hidden line removal (e.g.,
        VTK).
        """
        ax = self.gca()
        nargs = len(args)
        if nargs == 1:
            ax.setp(hidden=args[0])
        elif nargs == 0:
            ax.toggle('hidden')
        else:
            raise TypeError("hidden: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def view(self, *args):
        """Specify viewpoint.

        Calling::

            view(azimuth, elevation)

        sets the viewpoint according to azimuth (horizontal rotation) and
        elevation (vertical). Both azimuth and elevation should be given in
        degrees.

        Calling::

            view([azimuth, elevation])

        is the same as above.

        Calling::

            view(2)

        changes the view to the default 2D view.

        Calling::

            view(3)

        changes the view to the default 3D view.

        Calling::

            view(ax, ...)

        uses the Axis object ax instead of the current axis.

        Examples:

        >>> surf(peaks())
        >>> view(2)      # the default 2D view
        >>> view(40,65)  # azimuth=40 and elevation=65
        >>> view(3)      # back to the default 3D view
        >>> surf(peaks(),view=[35,75])  # as a keyword argument
        """
        ax, args, nargs = self._check_args(*args)

        cam = ax.getp('camera')
        # Allow both view(az,el) and view([az,el])
        if nargs == 1:
            if isinstance(args[0], (tuple,list)):
                args = args[0];  nargs = len(args)
            elif isinstance(args[0], (int,float)) and args[0] in (2,3):
                cam.setp(view=args[0])

        if nargs == 2:
            cam.setp(azimuth=args[0], elevation=args[1])

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def camdolly(self, *args):
        """Dolly camera.

        Calling::

            camdolly(dx, dy, dz)

        moves the camera position along the direction of projection.

        Calling::

            camdolly(ax, ...)

        uses the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        cam = ax.getp('camera')
        if nargs == 3:
            cam.setp(camdolly=args)
        else:
            raise TypeError("camdolly: wrong number of arguments")
        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def camlookat(self, *args):
        """Move camera and target to view specified objects.

        Calling::

            camlookat(obj)

        views the PlotProperties object obj.

        Calling::

            camlookat(ax)

        views the objects in the Axis object ax.

        Calling::

            camlookat()

        views the objects in the current axes.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            self.gca().getp('camera').setp(camlookat=self.gca())
        elif nargs == 1:
            tmparg = args[0]
            if isinstance(tmparg, Axis):
                tmparg.getp('camera').setp(camlookat=tmparg)
            elif isinstance(tmparg, PlotProperties):
                self.gca().getp('camera').setp(camlookat=tmparg)
            else:
                raise ValueError(
                    "camlookat: object must be either %s or %s, not %s" % \
                    (type(Axis), type(PlotProperties), type(tmparg)))
        else:
            raise TypeError("camlookat: wrong number of arguments")
        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def camproj(self, *args):
        """Camera projection.

        Calling::

            camproj()

        returns the camera projection of the current axis.

        Calling::

            camproj(projeciton)

        sets the projection of the camera to projection, where projection can
        be either 'orthographic' (default) or 'perspective'.

        Calling::

            camproj(ax, ...)

        sets or gets the camera projection of the Axis object ax instead of
        the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        cam = ax.getp('camera')
        if nargs == 0:
            return cam.getp('camproj')
        elif nargs == 1:
            cam.setp(camproj=args[0])
        else:
            raise TypeError("camproj: wrong number of arguments")
        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def camup(self, *args):
        """Camera up vector.

        Calling::

            camup()

        returns the up vector of the camera in the current axis.

        Calling::

            camup([x, y, z])

        sets the camera up vector.

        Calling::

             camup(x, y, z)

        is the same as the above.

        Calling::

            camup(ax, ...)

        sets or gets the up vector for the camera in the Axis object ax
        instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        cam = ax.getp('camera')
        if nargs == 0:
            return cam.getp('camup')
        elif nargs == 1:
            cam.setp(camup=args[0])
        elif nargs == 3:
            cam.setp(camup=args)
        else:
            raise TypeError("camup: wrong number of arguments")
        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def camroll(self, *args):
        """Roll camera.

        Calling::

            camroll(angle)

        rotates the camera about the direction of projection.

        Calling::

            camroll(ax, ...)

        rotates the camera in the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        cam = ax.getp('camera')
        if nargs == 1:
            cam.setp(camroll=args[0])
        else:
            raise TypeError("camroll: wrong number of arguments")
        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def camva(self, *args):
        """Camera view angle.

        Calling::

            camva()

        returns the camera view angle of the current axis.

        Calling::

            camva(angle)

        sets the camera view angle.

        Calling::

            camva(ax, ...)

        sets or gets the camera view angle in the Axis object ax instead of
        the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        cam = ax.getp('camera')
        if nargs == 0:
            return cam.getp('camva')
        elif nargs == 1:
            cam.setp(camva=args[0])
        else:
            raise TypeError("camva: wrong number of arguments")
        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def camzoom(self, *args):
        """Zoom camera.

        Calling::

            camzoom(factor)

        zooms the camera the specified factor. A value greater than 1 is a
        zoom-in, while a value less than 1 is a zoom-out.

        Calling::

            camzoom(ax, ...)

        zooms the camera in the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        cam = ax.getp('camera')
        if nargs == 1:
            cam.setp(camzoom=args[0])
        else:
            raise TypeError("camzoom: wrong number of arguments")
        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def campos(self, *args):
        """Camera position.

        Calling::

            campos()

        returns the position of the camera in the current axis.

        Calling::

            campos([x,y,z])

        sets the camera position.

        Calling::

             campos(x,y,z)

        is the same as above.

        Calling::

            campos(ax, ...)

        sets or gets the position of the camera in the Axis object ax instead
        of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        cam = ax.getp('camera')
        if nargs == 0:
            return cam.getp('campos')
        elif nargs == 1:
            cam.setp(campos=args[0])
        elif nargs == 3:
            cam.setp(campos=args)
        else:
            raise TypeError("campos: wrong number of arguments")
        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def camtarget(self, *args):
        """Camera target.

        Calling::

            camtarget()

        returns the camera target of the current axis.

        Calling::

            camtarget([x,y,z])

        sets the target for the camera.

        Calling::

            camtarget(x,y,z)

        is the same as above.

        Calling::

            camtarget(ax, ...)

        sets or gets the camera target in the Axis object ax instead of the
        current axis..
        """
        ax, args, nargs = self._check_args(*args)

        cam = ax.getp('camera')
        if nargs == 0:
            return cam.getp('camtarget')
        elif nargs == 1:
            cam.setp(camtarget=args[0])
        elif nargs == 3:
            cam.setp(camtarget=args)
        else:
            raise TypeError("camtarget: wrong number of arguments")
        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def camlight(self, *args, **kwargs):
        """Create or set position of a light.

        Calling::

            camlight('headlight')

        creates a light in the current axis at the position of the camera.

        Calling::

            camlight('right')

        creates a light right and up from the camera in the current axis.

        Calling::

            camlight('left')

        creates a light left and up from the camera.

        Calling::

            camlight()

        is the same as camlight('right').

        Calling::

            camlight(azimuth, elevation)

        creates a light at azimuth, elevation (both given in degrees) from
        the camera.

        Calling::

            camlight(..., style)

        sets the style of the light, where style can be either 'local'
        (default) or 'inifinite'.

        Calling::

            camlight(l, ...)

        places Light object l at the specified position.

        @return: A Light object.
        """
        # should be implemented in backend
        raise NotImplementedError("'camlight' not implemented in class %s" % \
                                  self.__class__.__name__)

    def light(self, **kwargs):
        """Add a light to the current axis.

        Calling:

            light()

        will add a light to the current axis with default values for all
        light properties.

        Calling::

            light(prop1=value1, prop2=value2, ...)

        adds a light with properties as given in the keyword arguments.

        @return: A Light object.
        """
        l = Light(**kwargs)
        self.gca().setp(light=l)
        if self.getp('interactive') and self.getp('show'):
            self._replot()
        return l

    def colormap(self, *args):
        """Specify colormap.

        Calling::

            colormap(map)

        uses the colormap in map as the current colormap (map is dependent
        on the current backend).

        Calling::

            colormap('default')

        sets the colormap to the default colormap, i.e., jet.

        Calling::

            map = colormap()

        returns the current colormap.

        Calling::

            colormap(ax, ...)

        uses the figure corresponding to the Axis object ax instead of the
        current figure.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            return ax.getp('colormap')
        elif nargs == 1:
            if args[0] == 'default':
                ax.setp(colormap=self.jet())
            else:
                ax.setp(colormap=args[0]) # backend dependent
        else:
            raise TypeError("colormap: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def caxis(self, *args):
        """Set the limits for the color axis.

        Calling::

            caxis([cmin, cmax])

        changes the limits for the color axis to range from cmin to cmax.

        Calling::

             caxis(cmin, cmax)

        gives the same result as above.

        Calling::

            caxis('manual')

        freezes the limits at the current range.

        Calling::

            caxis('auto')

        uses autoranging for the color axis limits (default).

        Calling::

            cmin, cmax = caxis()

        returns the current color axis limits.

        Calling::

            caxis(ax, ...)

        uses the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            cmin, cmax = ax.getp('caxis')
            if cmin is None or cmax is None:
                cmin, cmax = ax.getp('zlim')
            return cmin, cmax
        elif nargs == 1:
            if isinstance(args[0], (tuple,list)):
                args = args[0];  nargs = len(args)
            elif isinstance(args[0], str) and args[0] in ['auto', 'manual']:
                ax.setp(caxismode=args[0])
            else:
                raise TypeError("caxis: argument must be %s, not %s" % \
                                ((type(list),type(tuple),type(str)),
                                 type(args[0])))

        if nargs == 2:
            ax.setp(caxis=args)

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def colorbar(self, *args):
        """Display a color bar.

        Calling::

            colorbar()

        displays a colorbar in the current axis.

        Calling::

            colorbar('off')

        removes the colorbar from the current axis.

        Calling::

            colorbar(loc)

        displays a colorbar in the current axis at the location specified by
        loc, where loc may be any of the following:

          * 'North'        - inside plot box near top
          * 'South'        - inside bottom
          * 'East'         - inside right
          * 'West'         - inside left
          * 'NorthOutside' - outside plot box near top
          * 'SouthOutside' - outside bottom
          * 'EastOutside'  - outside right
          * 'WestOutside'  - outside left

        Calling::

            colorbar(ax, ...)

        uses the Axis object ax instead of the current axis.

        @return: A Colorbar object.
        """
        ax, args, nargs = self._check_args(*args)

        cbar = ax.getp('colorbar')
        if nargs == 0:
            cbar.setp(visible=True)
        elif nargs == 1:
            if args[0] == 'off' or not args[0]:
                cbar.setp(visible=False)
            else:
                cbar.setp(visible=True)
                cbar.setp(cblocation=args[0])
        else:
            raise TypeError("colorbar: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

        return cbar

    def shading(self, *args):
        """Control the color shading of surfaces.

        Calling::

            shading(mode)

        changes the shading mode in the current axis to the one specified by
        by mode. Valid modes are 'flat', 'interp' (interpolated or Gouraud)
        and 'faceted' (default).

        Calling::

            shading(ax, ...)

        uses the Axis object ax instead of the current axis.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 1:
            ax.setp(shading=str(args[0]))
        else:
            raise TypeError("shading: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def brighten(self, *args):
        """Brighten or darken the color map."""
        raise NotImplementedError("'brighten' not implemented in class %s" % \
                                  self.__class__.__name__)

    def clabel(self, *args):
        """Control labeling of contours.

        Calling::

            clabel(obj, 'on')

        adds height labels to a contour plot (obj must be a Contours
        object).

        Calling::

            clabel(obj, 'off')

        removes the labeling of the contour lines (default).
        """
        nargs = len(args)
        if nargs == 2:
            obj = args[0]
            state = args[1]
            obj.setp(clabels=state)
        else:
            raise TypeError("clabel: wrong number of arguments")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def box(self, *args):
        """Display a box around the boundaries of the current axis.

        Calling::

            box('on')

        displays a box at the boundaries of the current axis.

        Calling::

            box('off')

        turns off the box.

        Calling::

            box()

        toggles the display of a box in the current axis.

        Calling::

            box(ax, ...)

        uses the Axis object ax instead of the current axis.

        Note: box(True) and box(False) is the same as box('on') and
        box('off'), respectively.
        """
        ax, args, nargs = self._check_args(*args)

        if nargs == 0:
            ax.toggle('box')
        elif nargs == 1:
            ax.setp(box=args[0])
        else:
            raise TypeError("box: wrong number of argumnts")

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    def material(self, *args):
        """Set the material reflectance mode.

        Calling::

            material([ka, kd, ks[, n[, sc]]])

        changes the ambient/diffuse/specular strength, specular exponent,
        and specular color reflectance of objects.

        Calling::

            material(ka, kd, ks[, n[, sc]])

        is the same as above.

        Calling::

            material(mode)

        sets the material mode, where mode can be one of the following
        strings:

          * 'shiny'   - shiny objects
          * 'dull',   - dull objects
          * 'metal'   - metallic objects
          * 'default' - default material properties
        """
        modes = {'shiny': (None, None, None, None, None),
                 'dull': (None, None, None, None, None),
                 'metal': (None, None, None, None, None),
                 'default': (None, None, None, None, None),
                 }
        ka, kd, ks, n, sc = modes['default']
        nargs = len(args)
        if nargs == 1:
            if isinstance(args[0], (tuple,list)):
                args = args[0]
                nargs = len(args)
            elif args[0] in modes:
                ka, kd, ks, n, sc = modes[args[0]]

        if nargs >= 3:
            ka, kd, ks = args[:3]
        if nargs >= 4:
            n = args[3]
        if nargs == 5:
            sc = args[4]
        if nargs < 1 or nargs > 5:
            raise ValueError("material: wrong nmumber of arguments")

        kwargs = {}
        if ka is not None:
            kwargs['ambient'] = ka
        if kd is not None:
            kwargs['diffuse'] = kd
        if ks is not None:
            kwargs['specular'] = ks
        if n is not None:
            kwargs['specularpower'] = n
        #if sc is not None:
            #kwargs['specularcolorreflectance'] = sc

        ax = self.gca()
        items = ax.getp('plotitems')
        for i in range(ax.getp('numberofitems')):
            items[i].getp('material').setp(**kwargs)

        if self.getp('interactive') and self.getp('show'):
            self._replot()

    # Colormap methods:
    def hsv(self, m=None):
        """Hue-saturation-value color map."""
        raise NotImplementedError('hsv not implemented in class %s' % \
                                  self.__class__.__name__)

    def hot(self, m=None):
        """Black-red-yellow-white color map."""
        raise NotImplementedError('hot not implemented in class %s' % \
                                  self.__class__.__name__)

    def gray(self, m=None):
        """Linear gray-scale color map."""
        raise NotImplementedError('gray not implemented in class %s' % \
                                  self.__class__.__name__)

    def bone(self, m=None):
        """Gray-scale with a tinge of blue color map."""
        raise NotImplementedError('bone not implemented in class %s' % \
                                  self.__class__.__name__)

    def copper(self, m=None):
        """Linear copper-tone color map."""
        raise NotImplementedError('copper not implemented in class %s' % \
                                  self.__class__.__name__)

    def pink(self, m=None):
        """Pastel shades of pink color map."""
        raise NotImplementedError('pink not implemented in class %s' % \
                                  self.__class__.__name__)

    def white(self, m=None):
        """All white color map."""
        raise NotImplementedError('white not implemented in class %s' % \
                                  self.__class__.__name__)

    def flag(self, m=None):
        """Alternating red, white, blue, and black color map."""
        raise NotImplementedError('flag not implemented in class %s' % \
                                  self.__class__.__name__)

    def lines(self, m=None):
        """Color map with the line colors."""
        raise NotImplementedError('lines not implemented in class %s' % \
                                  self.__class__.__name__)

    def colorcube(self, m=None):
        """Enhanced color-cube color map."""
        raise NotImplementedError('colorcube not implemented in class %s' % \
                                  self.__class__.__name__)

    def vga(self, m=None):
        """Windows colormap for 16 colors."""
        raise NotImplementedError('vga not implemented in class %s' % \
                                  self.__class__.__name__)

    def jet(self, m=None):
        """Variant of hsv."""
        raise NotImplementedError('jet not implemented in class %s' % \
                                  self.__class__.__name__)

    def prism(self, m=None):
        """Prism color map."""
        raise NotImplementedError('prism not implemented in class %s' % \
                                  self.__class__.__name__)

    def cool(self, m=None):
        """Shades of cyan and magenta color map."""
        raise NotImplementedError('cool not implemented in class %s' % \
                                  self.__class__.__name__)

    def autumn(self, m=None):
        """Shades of red and yellow color map."""
        raise NotImplementedError('autumn not implemented in class %s' % \
                                  self.__class__.__name__)

    def spring(self, m=None):
        """Shades of magenta and yellow color map."""
        raise NotImplementedError('spring not implemented in class %s' % \
                                  self.__class__.__name__)

    def winter(self, m=None):
        """Shades of blue and green color map."""
        raise NotImplementedError('winter not implemented in class %s' % \
                                  self.__class__.__name__)

    def summer(self, m=None):
        """Shades of green and yellow color map."""
        raise NotImplementedError('summer not implemented in class %s' % \
                                  self.__class__.__name__)


def turn_off_plotting(namespace=globals()):
    """Call turn_off_plotting(globals()) to turn off all plotting."""
    use(namespace['plt'], namespace, True)

def use(plt, namespace=globals(), neutralize=False):
    """
    Export the namespace of backend instance to namespace.
    If neutralize is True, the plt object will be replaced
    by a scitools.misc.DoNothing object so that no plotting
    command will do anything. This can be used to efficiently
    turn off all plotting in a program.
    Just call turn_off_plotting(globals()) before the first
    plot command in your program.
    """
    plt_dict = {}
    plt_orig = plt
    if neutralize:
        import scitools.misc
        plt = scitools.misc.DoNothing()
    plt_dict['plt'] = plt
    for item in plt_orig.__dict__:
        plt_dict[item] = eval('plt.'+item)
    for item in dir(plt_orig.__class__):
        if not '__' in item:
            plt_dict[item] = eval('plt.'+item)
    namespace.update(plt_dict)  # Add to global namespace
    namespace['savefig'] = namespace['hardcopy']   # synonym
    def get_backend():
        return plt._g
    namespace['get_backend'] = get_backend # desired global func

    # If this module is imported
    try:
        __all__
    except:
        __all__ = ['plt']
    try:
        for item in plt_dict:
            __all__.append(item)
    except:
        pass
    del(__all__)


def debug(plt, level=10):

    def print_(item, spaces=10):
        """Indent print"""
        pref = ' '*spaces
        print pref+('\n'+pref).join((str(item)).split('\n'))

    print "plt:"
    print plt
    if level > 0:
        for fignr in plt._figs:
            print "\nFig %d:" % fignr
            fig = plt._figs[fignr]
            print fig

            if level > 1:
                axes_ = fig.getp('axes')
                for axnr in axes_:
                    print_("\nAx %d:" % axnr, 4)
                    ax = axes_[axnr]
                    print_(ax, 8)

                    if level > 2:
                        print_("\nCamera:", 4)
                        print_(ax.getp('camera'), 8)

                        print_("\nColorbar:", 4)
                        print_(ax.getp('colorbar'), 8)

                        print_("\nLights:", 4)
                        for light_ in ax.getp('lights'):
                            print_(light_, 8)

                        print_("\nPlotitems:", 4)
                        for i, item in enumerate(ax.getp('plotitems')):
                            print_('item number %s %s:' %(i, repr(item)), 8)
                            print_(item, 12)

                            if level > 3:
                                print_("Material:", 12)
                                print_(item.getp('material'), 16)

                            print ''
