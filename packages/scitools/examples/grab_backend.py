#!/usr/bin/env python
"""
Grab matplotlib backend to create thicker frame around plot
Use both major and minor tick marks
"""

__author__ = 'Rolv Erlend Bredesen <rolv@simula.no>'

from scitools.all import *
#from scitools.easyviz import *
#from scitools.easyviz.matplotlib_ import *

def _pylab_setup_frame(lines=10,  width=5, size=8, labelsize=20):
    """
    @param lines: width of plot lines
    @param width: width of frame line and tick marks
    @param size: length of tickmarks
    @param labelsize: size of ticklables

    Developers notice:
      lines.markeredgewidth will also change size of markers used in plots
      It appears that this is the only way to set the width of tickmarks
    """
    plt._g.rcParams.update({
        'lines.linewidth': lines ,         # Plotline width
        'ytick.labelsize': labelsize,
        'ytick.major.pad': size,
        'ytick.minor.pad': size,
        'ytick.major.size': size*1.8,          # Tickmark length
        'ytick.minor.size': size,
        'xtick.labelsize': labelsize,
        'xtick.major.pad': size,
        'xtick.minor.pad': size,
        'xtick.major.size': size*1.8,        
        'xtick.minor.size': size,
        'lines.markeredgewidth': width,   # Tickmark width
        'axes.linewidth': width,          # Frame width
        })
    
# Alternative syntax
def _pylab_setup_frame_(plot_line_width=10, frame_width=10, tick_length=20):
    """Setup frame before plotting with matplotlib"""
    if backend != 'matplotlib':
        return
    # Grab backend
    pylab = plt._g
    rc = pylab.rc
    #  set width of plotlines
    rc('lines', linewidth=plot_line_width)                   
    # Length of tick marks
    rc('xtick', color='k', labelsize=20) 
    rc('xtick.major', pad=10, size=tick_length) 
    rc('xtick.minor', pad=10, size=tick_length/2.)
    rc('ytick', color='k', labelsize=20) 
    rc('ytick.major', pad=10, size=tick_length) 
    rc('ytick.minor', pad=10, size=tick_length/2.)
    # Set width of tick marks and surrounding frame
    rc('lines', markeredgewidth=5)
    rc('axes', linewidth=5)
    
def _pylab_major_minor(axis='y', major_tick_interval=1, minor_tick_interval=.2):
    """Fix major/minor ticks as a postprocess after easyviz plot"""

    if backend != 'matplotlib':
        return

    pylab = get_backend()
    
    # Use both major and minor ticks
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter
    majorLocator = MultipleLocator(major_tick_interval)
    majorFormatter = FormatStrFormatter("%d")
    minorLocator = MultipleLocator(minor_tick_interval)
    if axis == 'x':
        axis = pylab.gca().xaxis
    elif axis == 'y':
        axis = pylab.gca().yaxis
    axis.set_minor_locator(minorLocator)
    axis.set_major_locator(majorLocator)
    axis.set_major_formatter(majorFormatter)
    # update backend
    pylab.draw()

if __name__ == '__main__' and backend == 'matplotlib':
    # Thicker frame and tickmarks
    _pylab_setup_frame()
            
    x = linspace(0, 5, 101)
    y = sin(2*pi*x)
    plot(y, '-x', x=x, log='x', xmin=.04, xmax=1, ymin=-1.1, ymax=1.1)
        
    plt._g.title('y=sin(2*pi*x)', fontsize=20)
    plt._g.text(0.1, -.5, 'Check out the nice thick frame')

    # Major and minor ticks for the y axis
    _pylab_major_minor(axis='y')
    plt._g.savefig('thick_frame.png')
