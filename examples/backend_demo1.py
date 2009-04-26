#!/usr/bin/env python
"""Configure a plot by grabbing the matplotlib backend

This example demonstrates the use of setp and getp, which is a
typical matlab/pylab way to set properties of objects

setp(handler, 'something', value) or getp(handler [, 'something'])
will call set_something or get_something from handler 

getp with only the handler argument will show full property list
"""
__author__ = 'Rolv Erlend Bredesen <rolv@simula.no'

from scitools.std import *

def _pylab_patch_alpha(alpha=0.2):
    """Makes patches (e.g. fill objects) located in the current axes
    transparent with given opacity coefficient."""
    pylab = get_backend()
    setp = pylab.setp
    getp = pylab.getp 
    ax = pylab.gca()
    for child in getp(ax, 'children'):
        if not isinstance(child, pylab.matplotlib.patches.Polygon):
            continue
        if __debug__:
            print 'Old alpha value:', getp(child, 'alpha'), 'new:', alpha
        setp(child, 'alpha', alpha)

if __name__ == '__main__':

    if backend == 'matplotlib':
        # override some properties for nicer plots:
        plt._g.rcParams.update({'font.size' : 10,
                                'axes.labelsize' : 10,
                                'text.fontsize' : 10, 
                                'xtick.labelsize' : 8,
                                'ytick.labelsize' : 8,
                                })
    
    x = linspace(0.0, 10., 101)
    y1 = sin(x)
    y2 = cos(3*x)
        
    # fix fill boundaries so we color between zero-line and values
    x_ = concatenate([x[:], x[::-1]])
    y1_ = concatenate([y1[:], 0*y1[:]])
    y2_ = concatenate([y2[:], 0*y2[:]])

    subplot(2,1,1)
    fill(y1_, 'b', y2_, 'g', x=x_, grid=True, title='no transparency')
    subplot(2,1,2)
    fill(y1_, 'b', y2_, 'g', x=x_, alpha=0.2, title='transparent fill')
    
    if backend == 'matplotlib':
        # Set alpha on patches
        _pylab_patch_alpha(0.3)
        # Don't use normal hardcopy after an update in backend
        plt._g.savefig('transparent_fill.png') 

    raw_input('press enter')
    
