#!/usr/bin/python

"""Wrapper classes for use with tkinter.

This module provides the following classes:

Gui: a sublass of Tk that provides wrappers for most of the
widget-creating methods from Tk.  The advantage of these wrappers is
that they use Python's optional argument capability to provide
appropriate default values, and that they combine widget creation and
packing into a single step.  They also eliminate the need to name the
parent widget explicitly by keeping track of a current frame and
packing new objects into it.

GuiCanvas: a subclass of Canvas that provides wrappers for most of the
item-creating methods from Canvas.  The advantage of the wrappers
is, again, that they use optional arguments to provide appropriate
defaults, and that they perform coordinate transformations.

Transform: an abstract class that provides basic methods inherited
by CanvasTransform and the other transforms.

CanvasTransform: a transformation that maps standard Cartesian
coordinates onto the 'graphics' coordinates used by Canvas objects.

Callable: the standard recipe from Python Cookbook for encapsulating
a function and its arguments in an object that can be used as a
callback.

The most important idea in this module is using a stack of frames to
avoid keeping track of parent widgets explicitly.


    WIDGET WRAPPERS:

    The Gui class contains wrappers for the widgets in tkinter.
    All of the wrappers invoke widget() to create and pack the new widget.

    The first four positional
    arguments determine how the widget is packed.  Some widgets
    take additional positional arguments.  In most cases, the
    keyword arguments are passed as options to the widget
    constructor.

    The default pack arguments are
    side=TOP, fill=NONE, expand=0, anchor=CENTER

    Widgets that use these defaults can just pass along
    args and options unmolested.  Widgets (like fr and en)
    that want different defaults have to roll the arguments
    in with the other options and then underride them
    (underride means set only if not already set).

    ITEM WRAPPERS:

    GuiCanvas provides wrappers for the canvas item methods.

"""

"""
  Copyright 2005 Allen B. Downey

    This file contains wrapper classes I use with tkinter.  It is
    mostly for my own use; I don't support it, and it is not very
    well documented.

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see
    http://www.gnu.org/licenses/gpl.html or write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
    02110-1301 USA 
"""



from math import *
from Tkinter import *
from tkFont import *

class Gui(Tk):
    """Gui provides wrappers for many of the methods in the Tk
    class; also, it keeps track of the current frame so that
    you can create new widgets without naming the parent frame
    explicitly."""

    def __init__(self, debug=False):
        """initialize the gui.
        turning on debugging changes the behavior of Gui.fr so
        that the nested frame structure is apparent.
        """
        Tk.__init__(self)
        self.debug = debug
        self.frames = [self]           # the stack of nested frames

    # accessing frame as an attribute returns the last frame on
    # the stack
    frame = property(lambda self: self.frames[-1])

    def endfr(self):
        """end the current frame (and return it)"""
        return self.frames.pop()

    # popfr and endgr are synonyms for endfr
    popfr = endfr
    endgr = endfr

    def pushfr(self, frame):
        """push a frame onto the frame stack"""
        self.frames.append(frame)

    def tl(self, **options):
        """make a return a top level window."""
        return Toplevel(**options)

    argnames = ['side', 'fill', 'expand', 'anchor']

    def fr(self, *args, **options):
        """make a return a frame.
        As a side effect, the new frame becomes the current frame
        """
        options.update(dict(zip(Gui.argnames,args)))
        underride(options, fill=BOTH, expand=1)
        if self.debug:
            override(options, bd=5, relief=RIDGE)

        # create the new frame and push it onto the stack
        frame = self.widget(Frame, **options)
        self.pushfr(frame)
        return frame

    def gr(self, cols, cweights=[1], rweights=[1], **options):
        """create a frame and switch to grid mode.
        cols is the number of columns in the grid (no need to
        specify the number of rows).  cweight and rweight control
        how the widgets expand if the frame expands (see colweights
        and rowweights below).  options are passed along to the frame
        """
        underride(options, fill=BOTH, expand=1)
        fr = self.fr(**options)
        fr.gridding = True
        fr.cols = cols
        fr.i = 0
        fr.j = 0
        self.colweights(cweights)
        self.rowweights(rweights)
        return fr

    def colweights(self, weights):
        """attach weights to the columns of the current grid.
        These weights control how the columns in the grid expand
        when the grid expands.  The default weight is 0, which
        means that the column doesn't expand.  If only one
        column has a value, it gets all the extra space.
        """
        for i, weight in enumerate(weights):
            self.frame.columnconfigure(i, weight=weight)

    def rowweights(self, weights):
        """attach weights to the rows of the current grid.
        These weights control how the rows in the grid expand
        when the grid expands.  The default weight is 0, which
        means that the row doesn't expand.  If only one
        row has a value, it gets all the extra space.
        """
        for i, weight in enumerate(weights):
            self.frame.rowconfigure(i, weight=weight)

    def grid(self, widget, i=None, j=None, **options):
        """pack the given widget in the current grid.
        By default, the widget is packed in the next available
        space, but parameters i and j can override.
        """
        if i == None: i = self.frame.i
        if j == None: j = self.frame.j
        widget.grid(row=i, column=j, **options)

        # increment j by 1, or by columnspan
        # if the widget spans more than one column.
        try:
            incr = options['columnspan']
        except KeyError:
            incr = 1

        self.frame.j += 1
        if self.frame.j == self.frame.cols:
            self.frame.j = 0
            self.frame.i += 1

    # entry
    def en(self, *args, **options):
        """make an entry widget."""
        
        # roll the positional arguments into the option dictionary
        options.update(dict(zip(Gui.argnames,args)))

        # underride fill and expand
        underride(options, fill=BOTH, expand=1)

        # pull the text option out
        text = options.pop('text', '')

        # create the entry and insert the text
        en = self.widget(Entry, **options)
        en.insert(0, text)
        return en

    # canvas
    def ca(self, *args, **options):
        """make a canvas widget."""
        
        underride(options, fill=BOTH, expand=1, sticky=N+S+E+W)
        return self.widget(GuiCanvas, *args, **options)

    # label
    def la(self, *args, **options):
        """make a label widget."""
        
        return self.widget(Label, *args, **options)

    # listbox
    def lb(self, *args, **options):
        """make a listbox."""
        return self.widget(Listbox, *args, **options)

    # button
    def bu(self, *args, **options):
        """make a button"""
        return self.widget(Button, *args, **options)

    # menu button
    def mb(self, *args, **options):
        """make a menubutton"""
        underride(options, relief=RAISED)
        mb = self.widget(Menubutton, *args, **options)
        mb.menu = Menu(mb, tearoff=False)
        mb['menu'] = mb.menu
        return mb

    # menu item
    def mi(self, mb, label='', **options):
        """make a menu item"""
        mb.menu.add_command(label=label, **options)        

    # text entry
    def te(self, *args, **options):
        """make a text entry"""
        return self.widget(Text, *args, **options)

    # scrollbar
    def sb(self, *args, **options):
        """make a text scrollbar"""
        return self.widget(Scrollbar, *args, **options)

    # WARNING: in the following two functions (cb and rb), I
    # attach new attributes to objects (Checkbutton and
    # RadioButton) created by tkinter.  There is no name
    # collision in current versions, but there might be in
    # the future!

    # check button
    def cb(self, *args, **options):
        """make a checkbutton."""
        
        # if the user didn't provide a variable, create one
        try:
            var = options['variable']
        except KeyError:
            var = IntVar()
            override(options, variable=var)
            
        w = self.widget(Checkbutton, *args, **options)
        w.var = var
        return w

    # radio button
    def rb(self, *args, **options):
        """make a radiobutton"""

        w = self.widget(Radiobutton, *args, **options)
        w.var = options['variable']
        w.val = options['value']
        return w

    class ScrollableText:
        """a scrollable text entry is a
        compound widget with a frame that contains a
        text entry on the left and a scrollbar on the right.
        """
        def __init__(self, gui,
                     *args, **options):
            self.frame = gui.fr(*args, **options)
            self.scrollbar = gui.sb(RIGHT, fill=Y)
            self.text = gui.te(LEFT, fill=Y, wrap=WORD,
                                 yscrollcommand=self.scrollbar.set)
            self.scrollbar.configure(command=self.text.yview)
            gui.endfr()

    def st(self, *args, **options):
        """make a scrollable text entry"""
        return self.ScrollableText(self, *args, **options)

    class ScrollableCanvas:
        """a compound widget with a grid that contains a canvas
        and two scrollbars
        """
        def __init__(self, gui, width=200, height=200, **options):
            self.grid = gui.gr(2, **options)
            self.canvas = gui.ca(width=width, height=height, bg='white')

            self.yb = gui.sb(command=self.canvas.yview, sticky=N+S)
            self.xb = gui.sb(command=self.canvas.xview, orient=HORIZONTAL,
                              sticky=E+W)

            self.canvas.configure(xscrollcommand=self.xb.set,
                                  yscrollcommand=self.yb.set,
                                  scrollregion=(0, 0, 400, 400))
            gui.endgr()

    def sc(self, *args, **options):
        """make a scrollable canvas.
        The options provided  apply to the frame only;
        if you want to configure the other widgets, you have to do
        it after invoking st"""
        return self.ScrollableCanvas(self, *args, **options)

    def widget(self, constructor, *args, **options):
        """this is the kernel of the widget constructors.
        (constructor) is the function that will
        be called to build the new widget. (args) is rolled
        into (options), and then (options) is split into widget
        options, pack options and grid options
        """

        # roll the positional arguments into the option dictionary,
        # then divide into options for the widget constructor, pack
        # or grid
        options.update(dict(zip(Gui.argnames,args)))
        widopt, packopt, gridopt = split_options(options)

        # make the widget and either pack or grid it
        widget = constructor(self.frame, **widopt)
        if hasattr(self.frame, 'gridding'):
            self.grid(widget, **gridopt)
        else:
            widget.pack(**packopt)
        return widget


def pop_options(options, names):
    """options is a dictionary; names is a list of keys.
    Remove the given keys from options and
    return a new dictionary with those key-value pairs.
    """
    new = {}
    for name in names:
        if name in options:
            new[name] = options.pop(name)
    return new

def get_options(options, names):
    """options is a dictionary; names is a list of keys.
    return a new dictionary that contains the key-value
    pairs for each key that appears in options.
    """
    new = {}
    for name in names:
        if name in options:
            new[name] = options[name]
    return new

def remove_options(options, names):
    """remove from (options) all the keys in (names)."""
    for name in names:
        if name in options:
            del options[name]

def split_options(options):
    """take a dictionary of options and split it into pack
    options and grid options; anything left is assumed to
    be a widget option
    """
    
    packnames = ['side', 'fill', 'expand', 'anchor',
                 'padx', 'pady', 'ipadx', 'ipady']
    gridnames = ['column', 'columnspan', 'row', 'rowspan',
                 'padx', 'pady', 'ipadx', 'ipady', 'sticky']

    # notice that some options will appear in both packopts
    # and gridopts, so that's why I didn't use pop_options.
    packopts = get_options(options, packnames)
    gridopts = get_options(options, gridnames)

    remove_options(options, packopts)
    remove_options(options, gridopts)

    return options, packopts, gridopts


class BBox(list):
    """a bounding box is a list of coordinates, where each
    coordinate is a list of numbers.  The first pair is the
    upper-left corner; the second pair is the lower-right.

    Creating a new bounding box makes a _shallow_ copy of
    the list of coordinates.  For a deep copy, use Bbox.copy().
    """
    __slots__ = ()

    def copy(self):
        t = [Pos(coord) for coord in bbox]
        return BBox(t)

    # top, bottom, left, and right can be accessed as attributes
    def setleft(bbox, val): bbox[0][0] = val 
    def settop(bbox, val): bbox[0][1] = val 
    def setright(bbox, val): bbox[1][0] = val 
    def setbottom(bbox, val): bbox[1][1] = val 
    
    left = property(lambda bbox: bbox[0][0], setleft)
    top = property(lambda bbox: bbox[0][1], settop)
    right = property(lambda bbox: bbox[1][0], setright)
    bottom = property(lambda bbox: bbox[1][1], setbottom)

    def width(bbox): return bbox.right - bbox.left
    def height(bbox): return bbox.bottom - bbox.top

    # upperleft returns the upper left corner as a new Pos object)
    # lowerright returns the lower right corner.
    def upperleft(bbox): return Pos(bbox[0])
    def lowerright(bbox): return Pos(bbox[1])

    def midright(bbox):
        """return the midpoint of the right edge as a Pos object
        """
        x = bbox.right
        y = (bbox.top + bbox.bottom) / 2.0
        return Pos([x, y])

    def midleft(bbox):
        """return the midpoint of the left edge as a Pos object
        """
        x = bbox.left
        y = (bbox.top + bbox.bottom) / 2.0
        return Pos([x, y])

    def union(self, other):
        """return a new bbox that covers self and other,
        assuming that the positive y direction is UP"""
        left = min(self.left, other.left)
        right = max(self.right, other.right)
        top = max(self.top, other.top)
        bottom = min(self.bottom, other.bottom)
        return BBox([[left, top], [right, bottom]])

    def offset(bbox, pos):
        """return the vector between the upper-left corner of bbox and
        the given position"""
        return Pos([pos[0]-bbox.left, pos[1]-bbox.top])

    def pos(bbox, offset):
        """return the position at the given offset from bbox upper-left"""
        return Pos([offset[0]+bbox.left, offset[1]+bbox.top])

    def flatten(bbox):
        """return a list of four coordinates"""
        return bbox[0] + bbox[1]


class Pos(list):
    """a position is a list of coordinates.

    Because Pos inherits __init__ from list, it makes a copy
    of the argument to the constructor.
    """
    __slots__ = ()

    copy = lambda pos: Pos(pos)

    # x and y can be accessed as attributes
    def setx(pos, val): pos[0] = val 
    def sety(pos, val): pos[1] = val 
    
    x = property(lambda pos: pos[0], setx)
    y = property(lambda pos: pos[1], sety)


# pairiter, pair and flatten are utilities for dealing with
# lists of coordinates

def pairiter(seq):
    """return an iterator that yields consecutive pairs from seq"""
    it = iter(seq)
    while True:
        yield [it.next(), it.next()]

def pair(seq):
    """return a list of consecutive pairs from seq"""
    return [x for x in pairiter(seq)]

def flatten(seq):
    """given a list of lists, return a new list that concatentes
    the elements of (seq).  This just does one level of flattening;
    it is not recursive.
    """
    return sum(seq, [])

# underride and override are utilities for dealing with options
# dictionaries

def underride(d, **kwds):
    """Add entries from (kwds) to (d) only if they are not already set"""
    for key, val in kwds.iteritems():
        if key not in d:
            d[key] = val

def override(d, **kwds):
    """Add entries from (kwds) to (d) even if they are already set"""
    d.update(kwds)


class GuiCanvas(Canvas):
    """this is a wrapper for the Canvas provided by tkinter.
    The primary difference is that it supports coordinate
    transformations, the most common of which is the CanvasTranform,
    which makes canvas coordinates Cartesian (origin in the middle,
    positive y axis going up).

    It also provides methods like circle that provide a
    nice interface to the underlying canvas methods.
    """
    def __init__(self, w, transforms=None, **options):
        Canvas.__init__(self, w, **options)

        # the default transform is a standard CanvasTransform
        if transforms == None:
            self.transforms = [CanvasTransform(self)]
        else:
            self.transforms = transforms

    # the following properties make it possbile to access
    # the width and height of the canvas as if they were attributes
    width = property(lambda self: int(self['width']))
    height = property(lambda self: int(self['height']))

    def add_transform(self, transform, index=None):
        """add the given transform at the given index in the
        transform list (appending is the default).
        """
        if index == None:
            self.transforms.append(transform)
        else:
            self.transforms.insert(index, transform)            
            
    
    def trans(self, coords):
        """apply each of the transforms for this canvas, in order."""
        for trans in self.transforms:
            coords = trans.trans_list(coords)
        return coords

    def invert(self, coords):
        """apply the inverse of each of the transforms, in reverse
        order."""
        t = self.transforms[:]
        t.reverse()
        for trans in t:
            coords = trans.invert_list(coords)
        return coords

    def bbox(self, item):
        """compute the bounding box of the given item
        (transformed from pixel coordinates to transformed
        coordinates).
        """
        if isinstance(item, list):
            item = item[0]
        bbox = Canvas.bbox(self, item)
        if bbox == None: return bbox
        bbox = pair(bbox)
        bbox = self.invert(bbox)
        return BBox(bbox)

    def tcoords(self, item, coords=None):
        """provides get and set access to item coordinates,
        with coordinate translation in both directions.
        """
        if coords != None:
            coords = self.trans(coords)
            coords = flatten(coords)
            Canvas.coords(self, item, *coords)
        else:
            "have to get the coordinates and invert them"
            coords = Canvas.coords(self, item)
            coords = pair(coords)
            coords = self.invert(coords)
            return coords

    # WARNING: the following functions, tmove and flipx, are
    # not thought through very carefully.  The notion of distance
    # can be funny if one of the transforms implements a nonlinear
    # mapping.
        
    def tmove(self, tags, dx=0, dy=0):
        """move all items with the given tags, with dx and dy
        in untransformed coordinates"""
        tags = self.find_withtag(tags)
        for tag in tags:
            coords = self.tcoords(tag)
            for i in range(len(coords)):
                coords[i][0] += dx
                coords[i][1] += dy
            self.tcoords(tag, coords)

    def flipx(self, item):
        """warning: this works in pixel coordinates"""
        coords = Canvas.coords(self, item)
        for i in range(0, len(coords), 2):
            coords[i] *= -1
        Canvas.coords(self, item, *coords)

    # the following are wrappers for the create_ methods
    # inherited from the Canvas class.

    def circle(self, x, y, r, fill='', **options):
        """make a circle with center at (x, y) and radius (r)
        """
        options['fill'] = fill
        coords = self.trans([[x-r, y-r], [x+r, y+r]])
        tag = self.create_oval(coords, options)
        return tag
    
    def oval(self, coords, fill='', **options):
        """make an oval with bounding box (coords) and fill color (fill)
        """
        options['fill'] = fill
        return self.create_oval(self.trans(coords), options)

    def rectangle(self, coords, fill='', **options):
        """make an oval with bounding box (coords) and fill color (fill)
        """
        options['fill'] = fill
        return self.create_rectangle(self.trans(coords), options)

    def line(self, coords, fill='black', **options):
        """make a polyline with vertices at each point in (coords)
        and pen color (fill).
        """
        options['fill'] = fill
        tag = self.create_line(self.trans(coords), options)
        return tag
    
    def polygon(self, coords, fill='', **options):
        """make a close polygon with vertices at each point in (coords)
        and fill color (fill).
        """
        options['fill'] = fill
        return self.create_polygon(self.trans(coords), options)

    def text(self, coord, text='', fill='black', **options):
        """make a text item with the given text and fill color.
        The default anchor is center.
        """
        options['text'] = text
        options['fill'] = fill
        return self.create_text(self.trans([coord]), options)

    def image(self, coord, image, **options):
        """make an image item with the given image at the given position.
        The default anchor is center.
        """
        options['image'] = image
        return self.create_image(self.trans([coord]), options)

    def dump(self, filename='canvas.eps'):
        """create a PostScipt file with the given name and dump
        the contents of the canvas into it.
        """
        bbox = Canvas.bbox(self, ALL)
        if bbox:
            x, y, width, height = bbox
        else:
            x, y, width, height = 0, 0, 100, 100
            
        width -= x
        height -= y
        ps = self.postscript(x=x, y=y, width=width, height=height)
        fp = open(filename, 'w')
        fp.write(ps)
        fp.close()


class Transform:
    """the parent class of transforms, Transform provides methods
    for transforming lists of coordinates.  Subclasses of Transform
    are supposed to implement trans() and invert()
    """
    def trans_list(self, points, func=None):
        """apply (func) to a list of points.
        If (func) is none, apply self.trans.
        """
        if func == None:
            func = self.trans

        if isinstance(points[0], (list, tuple)):
            return [Pos(func(p)) for p in points]
        else:
            return Pos(func(points))

    def invert_list(self, points):
        """apply the inverse transform to the list of points"""
        return self.trans_list(points, self.invert)
    

class CanvasTransform(Transform):
    """under a CanvasTransform, the origin is in the middle of
    the canvas, the positive y-axis is up, and the coordinate
    [1, 1] maps to the point specified by scale.
    """
    def __init__(self, ca, scale=[1, 1]):
        self.ca = ca
        self.scale = scale
    
    def trans(self, p):
        x =  p[0] * self.scale[0] + self.ca.width/2
        y = -p[1] * self.scale[1] + self.ca.height/2      
        return [x, y]

    def invert(self, p):
        x =  (p[0] - self.ca.width/2) / self.scale[0]
        y = - (p[1] - self.ca.height/2) / self.scale[1]
        return [x, y]


class ScaleTransform(Transform):
    """a ScaleTransform scales the coordinates in the x and y directions.
    The origin is half a unit from the upper-left corner; the y axis
    points down.
    """
    def __init__(self, scale=[1, 1]):
        self.scale = scale
    
    def trans(self, p):
        x = p[0] * self.scale[0]
        y = p[1] * self.scale[1]
        return [x, y]

    def invert(self, p):
        x = p[0] / self.scale[0]
        y = p[1] / self.scale[1]
        return [x, y]


class RotateTransform(Transform):
    """rotate the coordinate system
    """
    def __init__(self, theta):
        """rotate the coordinate system (theta) radians counterclockwise.
        """
        self.theta = theta

    def rotate(self, p, theta):
        """rotate the point p counterclockwise (theta) radians and
        return a new point.
        """
        s = sin(theta)
        c = cos(theta)
        x =   c * p[0] + s * p[1]
        y =  -s * p[0] + c * p[1]
        return [x, y]
    
    def trans(self, p):
        return self.rotate(p, self.theta)

    def invert(self, p):
        return self.rotate(p, -self.theta)


class SwirlTransform(RotateTransform):
    """rotate the coordinate system (d) radians counterclockwise,
    where (d) is proportional to the distance from the origin
    """

    def trans(self, p):
        d = sqrt(p[0]*p[0] + p[1]*p[1])
        return self.rotate(p, self.theta*d)

    def invert(self, p):
        d = sqrt(p[0]*p[0] + p[1]*p[1])
        return self.rotate(p, -self.theta*d)


class Callable:
    """this class is used to wrap a function and its arguments
    into an object that can be passed as a callback parameter
    and invoked later.  It is from the Python Cookbook 9.1, page 302
    """
    
    def __init__(self, func, *args, **kwds):
        self.func = func
        self.args = args
        self.kwds = kwds

    def __call__(self):
        return apply(self.func, self.args, self.kwds)

    def __str__(self):
        return self.func.__name__


def tk_example():
    """this example creates a simple GUI using only tkinter
    functions
    """
    tk = Tk()
    
    def hello():
        ca.create_text(100, 100, text='hello', fill='blue')
    
    ca = Canvas(tk, bg='white')
    ca.pack(side=LEFT)

    fr = Frame(tk)
    fr.pack(side=LEFT)

    bu1 = Button(fr, text='Hello', command=hello)
    bu1.pack()
    bu2 = Button(fr, text='Quit', command=tk.quit)
    bu2.pack()
    
    tk.mainloop()

def gui_example():
    """this example creates the same GUI as the previous function,
    but it uses the classes defined in this file
    """
    gui = Gui()

    ca = gui.ca(LEFT, bg='white')
    def hello():
        ca.text([0,0], 'hello', 'blue')
    
    gui.fr(LEFT)
    gui.bu(text='Hello', command=hello)
    gui.bu(text='Quit', command=gui.quit)
    gui.endfr()
    
    gui.mainloop()


def widget_demo():
    """demonstrate a variety of widgets
    """
    g = Gui()

    # FRAME 1

    g.fr(LEFT)

    # a label
    la1 = g.la(TOP, text='This is a label.')

    # an entry
    en = g.en(TOP, fill=NONE)
    en.insert(END, 'This is an entry widget.')

    # another label
    la2 = g.la(TOP, text='')

    def press_me():
        """read the text from the entry and display it as a label
        """
        text = en.get()
        la2.configure(text=text)

    # a button
    bu = g.bu(TOP, text='Press me', command=press_me)

    g.endfr()


    # FRAME 2

    g.fr(LEFT)

    def get_selection():
        """figure out which color is selected in the listbox
        """
        t = lb.curselection()
        try:
            index = int(t[0])
            color = lb.get(index)
            return color
        except:
            return None

    def print_selection(event):
        """print the current color in the listbox
        """
        print get_selection()

    def apply_color():
        """get the current color from the listbox and apply it
        to the circle in the canvas
        """
        color = get_selection()
        if color:
            ca.itemconfig(item1, fill=color)

    # create a frame with a label, listbox and scrollbar
    g.fr(TOP)
    la = g.la(TOP, text='List of colors:')
    lb = g.lb(LEFT, fill=Y)

    # when the user raises the button after selecting a color,
    # print the new selection (if you bind to the button press
    # you get the _previous_ selection)
    lb.bind('<ButtonRelease-1>', print_selection)

    # scrollbar
    sb = g.sb(RIGHT, fill=Y)
    g.endfr()

    # button
    bu = g.bu(BOTTOM, text='Apply color', command=apply_color)
    g.endfr()

    # fill the listbox with color names; if the X11 color list
    # is in the usual place, read it; otherwise use a short list.
    try:
        colors = open('/usr/X11R6/lib/X11/rgb.txt')
        colors.readline()
    except:
        colors = ['\t\t red', '\t\t orange', '\t\t yellow',
                  '\t\t green', '\t\t blue', '\t\t purple']
        
    for line in colors:
        t = line.split('\t')
        name = t[2].strip()
        lb.insert(END, name)

    # tell the listbox and the scrollbar about each other
    lb.configure(yscrollcommand=sb.set)
    sb.configure(command=lb.yview)


    # FRAME 3

    g.fr(LEFT)

    # scrollable canvas
    sc = g.sc()
    ca = sc.canvas

    # make some items
    item1 = ca.circle(0, 0, 70, 'red')
    item2 = ca.rectangle([[0, 0], [60, 60]], 'blue')
    item3 = ca.text([0, 0], 'This is a canvas.', 'white')

    # photo = PhotoImage(file='danger.gif')
    # item4 = ca.create_image(200, 300, image=photo)

    # menubutton
    mb = g.mb(TOP, text='Choose a color')

    def set_color(color):
        ca.itemconfig(item2, fill=color)

    # put some items in the menubutton
    for color in ['red', 'green', 'blue']:
        g.mi(mb, color, command=Callable(set_color, color))

    g.endfr()


    # FRAME 4

    g.fr(LEFT)

    def set_font():
        """get the current settings from the font control widgets
        and configure item3 accordingly
        """
        family = 'helvetica'
        size = fontsize.get()
        weight = b1.var.get()
        slant = b2.var.get()
        font = Font(family=family, size=size, weight=weight, slant=slant)
        print font.actual()
        ca.itemconfig(item3, font=font)

    g.la(TOP, text='Font:')

    # fontsize is the variable associated with the radiobuttons
    fontsize = IntVar()

    # make the radio buttons
    for size in [10, 12, 14, 15, 17, 20]:
        rb = g.rb(TOP, text=str(size), variable=fontsize, value=size,
                  command=set_font)

    # make the check buttons
    b1 = g.cb(TOP, text='Bold', command=set_font, variable=StringVar(),
              onvalue=BOLD, offvalue=NORMAL)
    b1.deselect()
    
    b2 = g.cb(TOP, text='Italic', command=set_font, variable=StringVar(),
              onvalue=ITALIC, offvalue=ROMAN)
    b2.deselect()

    # choose the initial font size
    fontsize.set(10)
    set_font()

    g.endfr()


    # FRAME 5

    g.fr(LEFT)

    # text widget
    te = g.te(TOP, fill=X, height=5, width=40)
    te.insert(END, "This is a Text widget.\n")
    te.insert(END, "It's like a little text editor.\n")
    te.insert(END, "It has more than one line, unlike an Entry widget.\n")

    # scrollable text widget
    st = g.st(TOP)
    st.text.configure(height=5, width=40)
    st.text.insert(END, "This is a Scrollable Text widget.\n")
    st.text.insert(END, "It is defined in Gui.py\n")

    # add some text
    for i in range(100):
        st.text.insert(END, "All work and no play.\n")

    g.endfr()


    # FRAME 6

    # label
    g.la(TOP, text='A grid of buttons:')

    # start a grid with three columns (the weights control how
    # the buttons expand if there is extra space)
    g.gr(3, rweights=[1,1,1], cweights=[1,1,1], side=LEFT)

    def print_num(i):
        print i

    # grid the buttons
    for i in range(1, 10):
        g.bu(text=str(i), sticky=NS, command=Callable(print_num, i))

    g.endgr()

    g.mainloop()


def main(script, function=None, *args):
    if function == None:
        widget_demo()
    else:
        # function is normally tk_example or gui_example
        function = eval(function)
        function()

if __name__ == '__main__':
    main(*sys.argv)

