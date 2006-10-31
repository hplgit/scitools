from common import *
from misc import arrayconverter
from scitools.numpytools import ones, ravel, shape, NewAxis, rank, transpose
import Gnuplot, tempfile, os

class GnuplotBackend(BaseClass):
    """
    Backend using the Gnuplot.py Python module.
    
    Tip:
        To close figure window, press <q> when active
    """

    def __init__(self):
        BaseClass.__init__(self)
        self.init()
        
    def init(self):
        #self._g = self.figs[self._attrs['curfig']]._g
        #self.replot = self._g.replot  # Replot all plotobjects (python ojects)
        #self.clear = self._g.clear    # Clear all plotobjects (python objects)
        #self.reset = self._g.reset    # Reset Gnuplot, i.e. blank screen
        # Necessary to add a Gnuplot Session  as _g to the Figure instance
        # self._g will now point to the correct intance saved as _g in curfig
        self.figure(self._attrs['curfig'])

        # Convert table for formatstrings
        self._colors = {'': None,
                        'k':-1,  # Black
                        'r': 1,  # Red 
                        'g': 2,  # Green
                        'b': 3,  # Blue
                        'm': 4,  # Magenta-->Purple
                        'c': 5,  # Cyan-->Aqua
                        'w':-1,  # White-->Black, white on a white is not good
                        'y': 7,  # Yellow-->Orange    
                        }
        
        self._line_types = {'': None,           # No line --> point
                            '-': 'lines',       # Solid 
                            ':': 'lines',       # Dotted line -->solid
                            '-.':'lines',       # Dot-dashed line -->solid
                            '--':'lines',       # Dashed line -->solid
                            }
        
        self._point_types = {'':  None,
                             #'v': 1, # Down-triangle -->Diamond
                             #'+': 2, # Plus
                             #'s': 3, # Square
                             #'x': 4, # Cross
                             #'^': 5, # Triangle
                             #'.': 6, # Dot
                             #'o': 1, # Circle-->Diamond  
                             '.': 0, # point
                             'o': 6, # circle
                             '+': 1, # plus
                             'x': 2, # x-mark
                             '*': 3, # star
                             's': 4, # square
                             'd': 12,# diamond
                             'v': 10,# triangle (down)
                             '^': 8, # triangle (up)
                             '<': 10,# triangle (left) --> (down)
                             '>': 10,# triangle (right) --> (down)
                             'p': 5, # pentagram --> square
                             'h': 5  # hexagram --> square
                             }

        self._shading_types = {'flat': "",
                               'interp': "",
                               'faceted': ""
                               }

        self._colorbar_styles = {
            'North': ('horizontal',.2,.74,.6,.04),
            'South': ('horizontal',.2,.26,.6,.04),
            'East': ('vertical',.76,.21,.03,.6),
            'West': ('vertical',.21,.21,.03,.6),
            'NorthOutside': ('horizontal',.2,.92,.6,.04),
            'SouthOutside': ('horizontal',.2,.06,.6,.04),
            'EastOutside': ('vertical',.9,.21,.03,.6),
            'WestOutside': ('vertical',.01,.21,.03,.6)
            }
        
        self._ismultiplot = False
        
    def _set_labels(self, ax):
        self._g('set xlabel "%s"' % ax.get('xlabel'))
        self._g('set ylabel "%s"' % ax.get('ylabel'))
        self._g('set zlabel "%s"' % ax.get('zlabel'))

    def _set_title(self, ax):
        self._g.title(ax.get('title'))

    def _set_axis_ranges(self, ax):
        fail = False
        for item in ['xmin', 'xmax']:
            if not isinstance(ax.get(item), (float, int)):
                fail = True;  break        
        if not fail:
            self._g('set xrange[%g:%g]' % (ax.get('xmin'), ax.get('xmax')))

        fail = False
        for item in ['ymin', 'ymax']:
            if not isinstance(ax.get(item), (float, int)):
                fail = True;  break
        if not fail:       
            self._g('set yrange[%g:%g]' % (ax.get('ymin'), ax.get('ymax')))

        fail = False
        for item in ['zmin', 'zmax']:
            if not isinstance(ax.get(item), (float, int)):
                fail = True;  break
        if not fail:       
            self._g('set zrange[%g:%g]' % (ax.get('zmin'), ax.get('zmax')))

    def _set_viewpoint(self, ax):
        cam = ax.get('camera')
        self._g('unset view')
        if cam.get('view') == 3:
            az = cam.get('azimuth')
            el = cam.get('elevation')
            if az is None or el is None:
                az, el = (60,325) # default 3D view in Gnuplot
            if (az >= 0 and az <= 180) and (el >= 0 and el <= 360):
                self._g('set view %d,%d' % (az,el))
            else:
                print 'view (%s,%s) out of range [0:180,0:360]' % (az,el)
        else: # view == 2:
            #az, el = (0,0) # default 2D view in Gnuplot
            self._g('set view map')
            # self._g('unset view') or self._g('set view auto') ???

    def _set_hidden_state(self, ax):
        """Set hidden line removal on or off."""
        if ax.get('hidden'):
            self._g('set hidden3d')
        else:
            self._g('unset hidden3d')

    def _set_colorbar_state(self, ax):
        """Set colorbar on or off."""
        colorbar = ax.get('colorbar')
        cbstyle = self._colorbar_styles[colorbar.get('cblocation')]
        if colorbar.get('visible'):
            self._g('set style line 2604 linetype -1 linewidth .4')
            #self._g('set colorbox vertical user border 2604 size .03,.6')
            self._g('set colorbox %s user border 2604 origin %g,%g size %g,%g'\
                    % cbstyle)
        else:
            self._g('unset colorbox')

    def _set_colormap(self, ax):
        colormap = ax.get('colormap')
        if isinstance(colormap, str):
            self._g(colormap)
        elif isinstance(colormap, (tuple,list)) and len(colormap) == 3 and \
                 isinstance(colormap[0], int) and \
                 isinstance(colormap[1], int) and \
                 isinstance(colormap[2], int):
            self._g('set palette rgbformulae %d,%d,%d' % colormap) # model RGB?
        else: # use default colormap
            self._g('set palette model RGB defined (0 "blue", 3 "cyan", ' \
                    '4 "green", 5 "yellow", 8 "red", 10 "black")')

    def _set_caxis(self, ax):
        if ax.get('caxismode') == 'manual':
            self._g('set cbrange [%d:%d]' % \
                    (int(ax.get('caxis')[0]),int(ax.get('caxis')[1])))
        else: # use autoranging
            self._g('set cbrange [*:*]')            

    def _set_wireframe_state(self, plotitem):
        if not plotitem.get('wireframe'):
            self._g('set pm3d at s solid')
        else: 
            self._g('unset pm3d')

    def _set_contour_state(self, plotitem):
        if isinstance(plotitem, Contours):
            clevels = plotitem.get('clevels')
            cvector = plotitem.get('cvector')
            clocation = plotitem.get('clocation')
            self._g('set contour %s' % clocation)
            if cvector is not None:
                cvector = ','.join(['%s' % i for i in cvector])
                self._g('set cntrparam levels discrete %s' % cvector)
            else:
                self._g('set cntrparam levels auto %d' % clevels)
            if plotitem.get('clabels'):
                self._g('set clabel')
            else:
                self._g('unset clabel')
        else:
            self._g('unset contour')

    def _set_scale(self, ax):
        scale = ax.get('scale')
        if scale == 'loglog':
            self._g('set logscale x')
            self._g('set logscale y')
            self._g('set autoscale')
        elif scale == 'logx':
            self._g('set logscale x')
            self._g('set nologscale y')
            self._g('set autoscale')
        elif scale == 'logy':
            self._g('set logscale y')
            self._g('set nologscale x')
            self._g('set autoscale')
        elif scale == 'linear':
            self._g('set nologscale y')
            self._g('set nologscale x')
            self._g('set autoscale')

    def _set_grid_state(self, ax):
        if ax.get('grid'):
            self._g('set grid')
        else:
            self._g('unset grid')

    def _set_box_state(self, ax):
        if ax.get('box'):
            #self._g('set style line 2604 linetype -1 linewidth .4')
            self._g('set border 4095 linetype -1 linewidth .4')
        else: # set default borders
            self._g('set border 1+2+4+8+16 linetype -1 linewidth .4')

    def _set_axis_appearance(self, ax):
        if ax.get('mode') == 'tight':
            #self._g('set autoscale fix')
            pass
        if not ax.get('visible'):
            self._g('unset border')
            self._g('unset grid')
            self._g('unset xtics')
            self._g('unset ytics')
            self._g('unset ztics')
  
    def _get_withstring(self, item):
        linetype = self._line_types[item.get('linetype')]
        color = self._colors[item.get('linecolor')]
        pointtype = self._point_types[item.get('linemarker')]
        try: pointsize = int(item.get('pointsize')) # "" gives error
        except: pointsize = 1
        # ex: set linestyle 2 lt 1 lw 3 pt 6
        # Can't use linetype/lt since it's not supported \
        # for all versions of gnuplot (lt indicated dotted dashed etc.) 

        withstring = ''
        if color: 
            if linetype == None:
                if pointtype:
                    withstring = "points lt %d pt %d ps %d " \
                                 % (color, pointtype, pointsize)
                else:
                    withstring = "lines lt %d" % color # Lines is default
            elif linetype == 'lines':
                if pointtype == None: # Pointtype is not set
                    withstring = "lines lt %d " % color
                else: 
                    withstring = "linespoints lt %d pt %d" % (color, pointtype)
        else: # No color
            if linetype == None:
                if pointtype:
                    withstring = "points pt %d ps %d " % (pointtype, pointsize)
                else:
                    withstring = "lines" # No color, no linestyle, no marker
            elif linetype == 'lines':
                if pointtype == None: # Pointtype is not set
                    withstring = "lines" 
                else: 
                    withstring = "linespoints pt %d" % pointtype
        return withstring

    def _set_common_3D_properties(self, ax, item):
        #self._set_viewpoint(ax)
        self._set_hidden_state(ax)
        self._set_colorbar_state(ax)
        self._set_colormap(ax)
        self._set_wireframe_state(item)
        self._set_contour_state(item)
        self._set_grid_state(ax)
        self._set_box_state(ax)

    def _set_common_2D_properties(self, ax, item):
        self._set_colormap(ax)
        self._set_contour_state(item)
        self._set_grid_state(ax)
        self._g('set border 4095 linetype -1 linewidth .4')
        
    def _create_gnuplot_data(self, ax):
        self._use_splot = False
        ax._gdata = []

        for item in ax.get('plotitems'):
            if isinstance(item, Line):
                self._use_splot = False
                withstring = self._get_withstring(item)
                x = arrayconverter(item.get('xdata'))
                y = arrayconverter(item.get('ydata'))
                ax._gdata.append(Gnuplot.Data(x, y,
                                              title=item.get('legend'),
                                              with=withstring))
            elif isinstance(item, Surface):
                self._use_splot = True
                self._set_wireframe_state(item)
                self._g('set surface')
                x = asarray(item.get('xdata'))
                y = asarray(item.get('ydata'))
                z = asarray(item.get('zdata'))
                if item.get('memoryorder') == 'yxz':
                    if rank(x) == 2 and rank(y) == 2:
                        x = x[0,:];  y = y[:,0]
                    z = transpose(z, [1,0])
                else:
                    if rank(x) == 2 and rank(y) == 2:
                        x = x[:,0];  y = y[0,:]
                data = Gnuplot.GridData(arrayconverter(z),
                                        arrayconverter(x),
                                        arrayconverter(y),
                                        title=item.get('legend'),
                                        with='l palette',
                                        binary=0)
                self._set_contour_state(item.get('contours'))
                ax._gdata.append(data)
            elif isinstance(item, Contours):
                self._use_splot = True
                self._set_contour_state(item)
                self._g('set surface')
                x = asarray(item.get('xdata'))
                y = asarray(item.get('ydata'))
                z = asarray(item.get('zdata'))
                if item.get('memoryorder') == 'yxz':
                    z = transpose(item.get('zdata'), [1,0])
                    if rank(x) == 2 and rank(y) == 2:
                        x = x[0,:];  y = y[:,0]
                else:
                    if rank(x) == 2 and rank(y) == 2:
                        x = x[:,0];  y = y[0,:]
                tmp_data = Gnuplot.GridData(arrayconverter(z),
                                            arrayconverter(x),
                                            arrayconverter(y),
                                            title=item.get('legend'),
                                            binary=0,
                                            with='l palette')
                #self._g('set view map') #self._g('set view 0,0,1,1') 
                self._g('unset surface')
                #self._g('unset pm3d')
##                 fname = tempfile.mktemp(suffix='.dat')
##                 self._g('set term push')
##                 self._g('set term table')
##                 self._g('set out "%s"' % fname)
##                 self._g.splot(tmp_data)
##                 self._g('set out')
##                 self._g('set term pop')
##                 data = Gnuplot.File(fname,
##                                     title=item.get('legend'),
##                                     with='l palette')
                ax._gdata.append(tmp_data)
            elif isinstance(item, VelocityVectors):
                if item.get('function') == 'quiver3':
                    print "quiver3 not supported under Gnuplot"
                    continue
                item.scale_vectors()
                withstring = 'vectors'
                color = self._colors[item.get('linecolor')]
                if color:
                    withstring += ' lt %d' % color
                linewidth = item.get('linewidth')
                if linewidth:
                    withstring += ' lw %g' % float(item.get('linewidth'))
                x = asarray(item.get('xdata'))
                y = asarray(item.get('ydata'))
                u = asarray(item.get('udata'))
                v = asarray(item.get('vdata'))
                if shape(x) != shape(u):
                    if len(shape(x)) == 2:
                        x = x*ones(shape(u))
                    else:
                        if item.get('memoryorder') == 'yxz':
                            x = x[NewAxis,:]*ones(shape(u))
                        else:
                            x = x[:,NewAxis]*ones(shape(u))
                if shape(y) != shape(u):
                    if len(shape(y)) == 2:
                        y = y*ones(shape(u))
                    else:
                        if item.get('memoryorder') == 'yxz':
                            y = y[:,NewAxis]*ones(shape(u))
                        else:
                            y = y[NewAxis,:]*ones(shape(u))
                data = Gnuplot.Data(arrayconverter(ravel(x)),
                                    arrayconverter(ravel(y)),
                                    arrayconverter(ravel(u)),
                                    arrayconverter(ravel(v)),
                                    title=item.get('legend'),
                                    with=withstring)
                ax._gdata.append(data)
                self._use_splot = False
            else:
                print "plotting of %s objects, is not supported under Gnuplot"\
                      % type(item)
                
        self._gdata = ax._gdata
        #print "withstring", withstring
        #print fig._gdata[0].get_command_option_string()
                
    def figure(self, *args, **kwargs):
        """Extension of BaseClass.figure:
        adds a gnuplot instance as figure._g then creates a link to it as
        object._g
        """
        
        BaseClass.figure(self, *args, **kwargs) 
        fig = self.gcf()

        try:
            fig._g
        except:
            try:
                fig._g = Gnuplot.Gnuplot(persist=1)
                # Plotwindow will now persist
                # To close the gnuplot session run fig._g('quit')
                # Python will only remove the binding to the session and not
                # stop it when _g is deleted            
                # This is due to the persist=1 parameter
            except:
                fig._g = Gnuplot.Gnuplot() # Persist is not supported under win

        self._g = fig._g # Creates link for faster access
        
    def _replot_old(self):
        fig = self.gcf()
        fig_axes = fig.get('axes')
        for ax in fig_axes.values():
            pass

        #self._g.reset() # reset everytime?
        ax = self.gca()

        axshape = fig.get('axshape')
        if axshape != (1,1): # subplots
            if not self._ismultiplot:
                self._g('set multiplot')
                self._ismultiplot = True
                #print 'setting multiplot'
            viewport = ax.get('viewport')
            origin = viewport[:2]
            #print 'origin:', origin
            self._g('set origin %g,%g' % origin)
            size = 1./axshape[1], 1./axshape[0]
            #print 'size:', size
            self._g('set size %g,%g' % size)
        else:
            self._ismultiplot = False
            self._g('unset multiplot')
        
        self._create_gnuplot_data()

        self._set_viewpoint(ax)
        self._set_hidden_state(ax)
        self._set_colorbar_state(ax)
        self._set_colormap(ax)
        self._set_grid_state(ax)
        self._set_box_state(ax)
        self._set_scale(ax)            
        self._set_labels(ax)
        self._set_title(ax)
        self._set_axis_ranges(ax)
        self._set_caxis(ax)
        #self._g('set border 4095 linetype -1 linewidth .4')
        
        # Plot data
        if len(ax._gdata) > 0:
            if self._use_splot:
                #self._g('set style data points') # not here
                #self._g('set data style points')
                self._g.splot(ax._gdata[0])
            else:
                self._g.plot(ax._gdata[0])
            
            if len(ax._gdata) > 1:
                for item in ax._gdata[1:]:
                    self._g.replot(item)

            # Why is this now necessary to get titles and labels right?
            #self._g.replot()

    def _replot(self):
        fig = self.gcf()
        fig_axes = fig.get('axes')
        self._g.reset() # reset everytime
        self._ismultiplot = False
        self._g('unset multiplot')
        for ax in fig_axes.values():
            axshape = fig.get('axshape')
            if axshape != (1,1): # subplots
                if not self._ismultiplot:
                    self._g('set multiplot')
                    self._ismultiplot = True
                    #print 'setting multiplot'
                viewport = ax.get('viewport')
                if not viewport:
                    viewport = (0,0,1,1)
                origin = viewport[:2]
                size = 1./axshape[1], 1./axshape[0]
                self._g('set origin %g,%g' % origin)
                self._g('set size %g,%g' % size)
            else:
                self._ismultiplot = False
                self._g('unset multiplot')

            if len(ax.get('plotitems')) > 0:
                self._create_gnuplot_data(ax)

                self._set_viewpoint(ax)
                self._set_hidden_state(ax)
                self._set_colorbar_state(ax)
                self._set_colormap(ax)
                self._set_grid_state(ax)
                self._set_box_state(ax)
                self._set_scale(ax)            
                self._set_labels(ax)
                self._set_title(ax)
                self._set_axis_ranges(ax)
                self._set_caxis(ax)
                #self._g('set border 4095 linetype -1 linewidth .4')
                self._set_axis_appearance(ax)

        
                # Plot data
                if len(ax._gdata) > 0:
                    if self._use_splot:
                        #self._g('set style data points') # not here
                        #self._g('set data style points')
                        self._g.splot(ax._gdata[0])
                    else:
                        self._g.plot(ax._gdata[0])
            
                    if len(ax._gdata) > 1:
                        for item in ax._gdata[1:]:
                            self._g.replot(item)

                    # Why is this now necessary to get titles and labels right?
                    #self._g.replot()

    def clf(self):
        """Clear current figure."""
        BaseClass.clf(self)
        self._g.reset() # reset gnuplot instance

    def closeall(self):
        """close figurewindows and stop gnuplot """
        for key in self._figs.keys():
            self._figs[key]._g('quit')
        del self._g
        self._figs = {1:Figure()}
        self._figs[1]._g = Gnuplot.Gnuplot()
        self._g = self._figs[1]._g

    def hardcopy(self, filename=None, **kwargs):
        """The Gnuplot backend supports currently the following file formats:
        '.ps' (Postscript), '.eps' (Encapsulated Postscript), and
        '.png' (Portable Network Graphics).
        """
        if not filename:
            raise TypeError, "hardcopy: no file name given"
        ext2term = {'.ps': 'postscript',
                    '.eps': 'postscript',
                    '.png': 'png'}
        junk, ext = os.path.splitext(filename)
        if ext not in ext2term:
            ext = '.ps'
            filename += ext
        terminal = ext2term.get(ext, 'postscript')
        
        self.set(**kwargs)
        fontname = kwargs.get('fontname', 'Times-Roman')
        fontsize = kwargs.get('fontsize', 20)
        color = self.get('color')
                  
        self._g('unset multiplot') # is this necessary?
        
        if self.get('show'): # OK to display to screen
            self._replot()
            kwargs = {'filename': filename, 'terminal': terminal}
            if terminal == 'postscript':
                kwargs.update({'color': color, 'enhanced': True,
                               'fontname': fontname, 'fontsize': fontsize})
                if ext == '.eps':
                    kwargs['mode'] = 'eps'
                else:
                    kwargs['mode'] = 'portrait'
            self._g.hardcopy(**kwargs)
        else: # Manually set terminal and don't show windows
            if color:
                colortype = 'color'
            else:
                colortype = 'monochrome'
                        
            # Create a new Gnuplot instance only for now
            self._g = Gnuplot.Gnuplot()
            kwargs = {'filename': filename, 'terminal': terminal}
            if terminal == 'postscript':
                kwargs.update({'color': color, 'enhanced': True, 
                               'fontname': fontname, 'fontsize': fontsize})
                if ext == '.eps':
                    self._g('set term postscript eps %s' % colortype)
                    kwargs['mode'] = 'eps'
                else:
                    self._g('set term postscript portrait %s' % colortype)
                    kwargs['mode'] = 'portrait'
            elif terminal == 'png':
                self._g('set term png')
            self._g('set output "%s"' % filename)
            self._replot()
            self._g.hardcopy(**kwargs)
            self._g('quit')
            self._g = self.gcf()._g # set _g to the correct instance again

    hardcopy.__doc__ = BaseClass.hardcopy.__doc__ + hardcopy.__doc__
            
    # Colormaps:
    def hsv(self, m=0, model='HSV'):
        c = 'rgbformulae 3,2,2'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def hot(self, m=0, model='RGB'):
        c = 'rgbformulae 21,22,23'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def gray(self, m=0, model='RGB'):
        c = 'defined (0 "black", 1 "white")'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def bone(self, m=0, model='RGB'):
        c = 'defined (0 "black", 4 "light-blue", 5 "white")'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def copper(self, m=0, model='RGB'):
        c = 'defined (0 "black", 1 "coral")'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def pink(self, m=0, model='RGB'):
        c = 'defined (0 "black", 1 "pink", 8 "pink", 10 "white")'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def white(self, m=0, model='RGB'):
        c = 'defined (0 "white", 1 "white")'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def flag(self, m=0, model='RGB'):
        colors = "red,white,blue,black".split(',')
        j=k=0
        c = 'defined ('
        while k < 16:
            i = 0
            while i < len(colors)-1:
                j += 1;  i += 2
                c += '%d "%s", %d "%s", ' % (j-1,colors[i-2],j,colors[i-1])
            k += 1
        c = c[:-2]+')'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
                
    def lines(self, m=0, model='RGB'):
        # Note: not finished
        colors = "blue,green,red,cyan,magenta,yellow,black".split(',')
        j=k=0
        c = 'defined ('
        while k < 9:
            i = 0
            c += '%d "%s"' % (j,colors[0])
            while i < len(colors)-1:
                j += 1;  i += 2
                c += ', %d "%s", %d "%s"' % (j,colors[i-1],j,colors[i])
            k += 1
            c += ', '
        c = c[:-2]+')'
        #print c
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def colorcube(self, m=0, model='RGB'):
        colors = "white,black,gray0,gray10,grey20,grey30,gray40,gray50,"\
                 "gray60,grey70,grey80,gray90,grey100,grey,light-grey,"\
                 "dark-grey,red,light-red,dark-red,yellow,light-yellow,"\
                 "dark-yellow,green,light-green,dark-green,spring-green,"\
                 "forest-green,sea-green,blue,light-blue,dark-blue,"\
                 "midnight-blue,navy,medium-blue,royalblue,skyblue,cyan,"\
                 "light-cyan,dark-cyan,magenta,light-magenta,dark-magenta,"\
                 "turquoise,light-turquoise,dark-turquoise,pink,light-pink,"\
                 "dark-pink,coral,light-coral,orange-red,salmon,light-salmon,"\
                 "dark-salmon,aquamarine,khaki,dark-khaki,gold,goldenrod,"\
                 "light-goldenrod,dark-goldenrod,beige,brown,orange,"\
                 "dark-orange,violet,dark-violet,plum,purple".split(',')
        i=j=0
        c = 'defined (%d "%s"' % (i,colors[0])
        while i < len(colors)-1:
            j += 1;  i += 2
            c += ', %d "%s", %d "%s"' % (j,colors[i-1],j,colors[i])
        c += ')'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def vga(self, m=0, model='RGB'):
        return None
    
    def jet(self, m=0, model='RGB'):
        c = 'defined (0 "blue", 3 "cyan", 4 "green", 5 "yellow", '\
            '8 "red", 10 "black")' # stop at red (remove black)
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def prism(self, m=0, model='RGB'):
        return None

    def cool(self, m=0, model='RGB'):
        c = 'defined (0 "cyan", 1 "magenta")'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def autumn(self, m=0, model='RGB'):
        c = 'defined (0 "red", 1 "yellow")'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def spring(self, m=0, model='RGB'):
        c = 'defined (0 "magenta", 1 "yellow")'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def winter(self, m=0, model='RGB'):
        c = 'defined (0 "blue", 1 "spring-green")'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
    def summer(self, m=0, model='RGB'):
        c = 'defined (0 "green", 1 "yellow")'
        return 'set palette model %s maxcolors %d %s' % (model,m,c)
    
                      
plt = GnuplotBackend() # Create backend instance
use(plt, globals()) # Export public namespace of plt to globals()

def get_backend():
    return plt._g

