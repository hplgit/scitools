"""

Easyviz
=======

Easyviz is a light-weight interface to various packages for scientific
visualization and plotting.  The Easyviz interface is written in
Python with the purpose of making it very easy to visualize data in
Python scripts. Both curve plots and more advanced 2D/3D visualization
of scalar and vector fields are supported.  The Easyviz interface was
designed with three ideas in mind: 1) a simple, Matlab-like syntax; 2)
a unified interface to lots of visualization engines (called backends
later): Gnuplot, Vtk, Matlab, Matplotlib, PyX, etc.; and 3) a
minimalistic interface which offers only basic control of plots
(fine-tuning is left to programming in the specific backend directly).

Guiding Principles
------------------

*First principle.* Array data can be plotted with a minimal
set of keystrokes using a Matlab-like syntax. A simple::

      t = linspace(0, 3, 51)    # 51 points between 0 and 3
      y = t**2*exp(-t**2)
      plot(t, y) 

plots the data in (the NumPy array) t versus the data in (the NumPy
array) y. If you need legends, control of the axis, as well as
additional curves, all this is obtained by the standard Matlab-style
commands::

      y2 = t**4*exp(-t**2)
      # pick out each 4 points and add random noise:
      t3 = t[::4]
      random.seed(11)
      y3 = y2[::4] + random.normal(loc=0, scale=0.02, size=len(t3))
      
      plot(t, y1, 'r-')
      hold('on')
      plot(t, y2, 'b-')
      plot(t3, y3, 'bo')
      legend('t^2*exp(-t^2)', 't^4*exp(-t^2)', 'data')
      title('Simple Plot Demo')
      axis([0, 3, -0.05, 0.6])
      xlabel('t')
      ylabel('y')
      show()
      
      hardcopy('tmp0.ps')  # this one can be included in latex
      hardcopy('tmp0.png') # this one can be included in HTML

Easyviz also allows these additional function calls to be executed
as a part of the plot call::

      plot(t, y1, 'r-', t, y2, 'b-', t3, y3, 'bo',
           legend=('t^2*exp(-t^2)', 't^4*exp(-t^2)', 'data'),
           title='Simple Plot Demo',
           axis=(0, 3, -0.05, 0.6),
           xlabel='t', ylabel='y',
           hardcopy='tmp1.ps',
           show=True)
      
      hardcopy('tmp0.png') # this one can be included in HTML

A scalar function f(x,y) may be visualized
as an elevated surface with colors using these commands::

      x = seq(-2, 2, 0.1)      # -2 to 2 with steps of 0.1
      xv, yv = meshgrid(x, x)  # define a 2D grid with points (xv,yv)
      values = f(xv, yv)       # function values
      surfc(xv, yv, values,
            shading='interp',
            clevels=15,
            clabels='on',
            hidden='on',
            show=True)


*Second princple.* Easyviz is just a unified interface to other plotting
packages that can be called from Python. Such plotting packages are
referred to as backends. Several backends are supported: Gnuplot,
Matplotlib, Pmw.Blt.Graph, PyX, Matlab, Vtk. In other words, scripts
that use Easyviz commands only, can work with a variety of backends,
depending on what you have installed on the machine in question and
what quality of the plots you demand. For example, swiching from
Gnuplot to Matplotlib is trivial.

Scripts with Easyviz commands will most probably run anywhere since at
least the Gnuplot package can always be installed right away on any
platform. In practice this means that when you write a script to
automate investigation of a scientific problem, you can always quickly
plot your data with Easyviz (i.e., Matlab-like) commands and postpone
to marry any specific plotting tool. Most likely, the choice of
plotting backend can remain flexible. This will also allow old scripts
to work with new fancy plotting packages in the future if Easyviz
backends are written for those packages.

*Third principle.* The Easyviz interface is minimalistic, aimed at
rapid prototyping of plots. This makes the Easyviz code easy to read
and extend (e.g., with new backends). If you need more sophisticated
plotting, like controlling tickmarks, inserting annotations, etc., you
must grab the backend object and use the backend-specific syntax to
fine-tune the plot. The idea is that you can get away with Easyviz
and a plotting package-independent script "95%" of the time - only now
and then there will be demand for package-dependent code for
fine-tuning and customization of figures.

These three principles and the Easyviz implementation make simple things
simple and unified, and complicated things are not more complicated than
they would otherwise be. You can always start out with the simple
commands - and jump to complicated fine-tuning only when strictly needed.

Controlling the Backend
-----------------------

The Easyviz backend can either be set in a config file (see Config File
below) or by a command-line option::

       --SCITOOLS_easyviz_backend name

where name is the name of the backend: gnuplot, vtk, matplotlib,
blt. Which backend you
choose depends on what you have available on your computer system and
what kind of plotting functionality you want.


Config File
-----------

Easyviz is a subpackage of SciTools, and the the SciTools configuration
file, called scitools.cfg has a section [easyviz] where the
backend in Easyviz can be set::

      [easyviz]
      backend = vtk_

A scitools.cfg can be placed in the current working directory, thereby
affecting plots made in this directory, or it can be located in the
user's home directory, which will affect all plotting sessions for the
user in question.


Tutorial
========

This tutorial starts with plotting a single curve with a simple
plot(x,y) command. Then we add a legend, axis labels, a title, etc.
Thereafter we show how multiple curves are plotted together. We also
explain how line styles and axis range can be controlled. The
next section deals with animations and making movie files. More advanced
topics such as fine tuning of plots (using plotting package-specific
commands) and working with Axis and Figure objects close the curve
plotting part of the tutorial.

Various methods for visualization of scalar fields in 2D are treated
next, before we show how 2D vector fields can be handled.


Plotting a Single Curve
-----------------------


Let us plot the curve y = t^2\exp(-t^2) for t values between 0 and 3.
First we generate equally spaced coordinates for t, say 51 values (50
intervals). Then we compute the corresponding y values at these
points, before we can call the plot(t,y) command.
Here is the complete program::

      from scitools.all import *
      
      def f(t):
          return t**2*exp(-t**2)
      
      t = linspace(0, 3, 51)    # 51 points between 0 and 3
      y = zeros(len(t), 'd')    # 51 doubles ('d')
      for i in xrange(len(t)):
          y[i] = f(t[i])
      
      plot(t, y)


The first line imports all of SciTools and Easyviz that can be handy
to have when doing scientific computations. In this program we
pre-allocate the y array and fill it with values, element by
element, in a (slow) Python loop. Operations on the whole t at once
is legal and yields faster and shorter code::

      from scitools.all import *
      
      def f(t):
          return t**2*exp(-t**2)
      
      t = linspace(0, 3, 51)    # 51 points between 0 and 3
      y = f(t)                  # compute all f values at once
      plot(t, y)

The f function can also be skipped, if desired::

      y = t**2*exp(-t**2)


To include the plot in reports, we need 
a hardcopy of the figure in PostScript, PNG, or another image format.
The hardcopy command produces files with images in various formats::

      hardcopy('tmp1.ps')  # produce PostScript
      hardcopy('tmp1.png') # produce PNG


The filename extension determines the format: .ps or
.eps for PostScript, and .png for PNG. 
Figure fig:plot1a displays the resulting plot.

FIGURE:[figs/plot1a.eps] A simple plot in PostScript format.


Decorating the Plot
-------------------

The x and y axis in curve plots should have labels, here t and
y, respectively. Also the curve should be identified with a label
(or legend as it is often called).  A title above the plot is also
common.  All such things are easily added after the plot command::

      xlabel('t')
      ylabel('y')
      legend('t^2*exp(-t^2)')
      axis([0, 3, -0.05, 0.6])   # t in [0,3], y in [-0.05,0.6]
      title('My First Easyviz Demo')


This syntax is inspired by Matlab to make the switch between
SciTools/Easyviz and Matlab almost trivial.
Easyviz has also introduced a more "Pythonic" plot command where
all the plot properties can be set at once::

      plot(t, y,
           xlabel='t',
           ylabel='y',
           legend='t^2*exp(-t^2)',
           axis=[0, 3, -0.05, 0.6],
           title='My First Easyviz Demo',
           hardcopy='tmp1.ps',
           show=True)


With show=False one can avoid the plot window on the screen and
just make the hardcopy.

Note that we in the curve legend write t square as t^2 (LaTeX style)
rather than t**2 (program style).
The modified plot appears in Figure fig:plot1c.


FIGURE:[figs/plot1c.eps] A single curve with label, title, and axis adjusted.


Plotting Multiple Curves
------------------------

One often wants to compare curves to each other, and this requires
multiple curves to be drawn in the same plot.
Suppose we want to plot the two functions f_1(t)=t^2\exp(-t^2)
and f_2(t)=t^4\exp(-t^2). If we issue two plot commands after
each other, two separate plots will be made. To make the second
plot command draw the curve in the previous plot, we need to
issue a hold('on') command. Alternatively, we can provide all
data in a single plot command. A complete program illustrates the
different approaches::

      from scitools.all import *   # for curve plotting
      
      def f1(t):
          return t**2*exp(-t**2)
      
      def f2(t):
          return t**2*f1(t)
      
      t = linspace(0, 3, 51)
      y1 = f1(t)
      y2 = f2(t)
      
      # Matlab-style syntax:
      plot(t, y1)
      hold('on')
      plot(t, y2)
      
      xlabel('t')
      ylabel('y')
      legend('t^2*exp(-t^2)', 't^4*exp(-t^2)')
      title('Plotting two curves in the same plot')
      hardcopy('tmp2.ps')
      
      # alternative:
      plot(t, y1, t, y2, xlabel='t', ylabel='y',
           legend=('t^2*exp(-t^2)', 't^4*exp(-t^2)'),
           title='Plotting two curves in the same plot',
           hardcopy='tmp2.ps')

The sequence of the multiple legends is such that the first legend 
corresponds to the first curve, the second legend to the second curve,
and so on. The visual result appears in Figure fig:plot2a.



FIGURE:[figs/plot2a.eps] Two curves in the same plot.



Controlling Axis and Line Styles
--------------------------------

A plotting program will normally compute sensible ranges of
the axis. For example, the Gnuplot program has in our examples
so far used an y axis from 0 to 0.6 while the x axis goes from
0 to 3. Sometimes it is desired to adjust the range
of the axis. Say we want the x axis to go from 0 to 4 (although the
data stops at x=3), while y axis goes from -0.1 to 0.6.
In the Matlab-like syntax new axis specifications are 
done by the axis command::

      axis([0, 4, -0.1, 0.6])


In a single plot command we must use the axis keyword::

      plot(t, y1, t, y2, ...
           axis=[0, 4, -0.1, 0.6],
           ...)


In both cases, the axis specification is a list of the
x_{\rm min}, x_{\rm max}, y_{\rm min}, and y_{\rm max}
values.

The two curves get distinct default line styles, depending on the
program that is used to produce the curve (and the settings for this
program). It might well happen that you get a green and a red curve
(which is bad for a significant portion of the male population).  We
therefore often want to control the line style in detail. Say we want
the first curve (t and y1) to be drawn as a red solid line and the
second curve (t and y2) as blue circles at the discrete data
points.  The Matlab-inspired syntax for specifying line types applies
a letter for the color and a symbol from the keyboard for the line
type. For example, r- represents a red (r) line (-), while bo
means blue (b) circles (o). The line style specification is added
as an argument after the x and y coordinate arrays of the curve::

      plot(t, y1, 'r-')
      hold('on')
      plot(t, y2, 'bo')
      
      # or
      plot(t, y1, 'r-', t, y2, 'bo')

The effect of controlling the line styles can be seen in 
Figure fig:plot2c.

FIGURE:[figs/plot2c.eps] Two curves in the same plot, with controlled line styles.

Assume now that we want to plot the blue circles at only each 4 points.
We can grab each 4 points out of the t array by using an appropriate
slice: t2 = t[::4]. Note that the first colon means the range from the
first to the last data point, while the second colon separates this
range from the stride, i.e., how many points we should "jump over"
when we pick out a set of values of the array.

In this plot we also adjust the size of the line and the circles by
adding an integer: r-6 means a red line with thickness 6 and bo5
means red circles with size 5. The effect of the given line thickness
and symbol size depends on the underlying plotting program. For
the Gnuplot backend one can view the effect in Figure fig:plot2g::

      from scitools.all import *
      
      def f1(t):
          return t**2*exp(-t**2)
      
      def f2(t):
          return t**2*f1(t)
      
      t = linspace(0, 3, 51)
      y1 = f1(t)
      t2 = t[::4]
      y2 = f2(t2)
      
      plot(t, y1, 'r-6', t2, y2, 'bo3',
           xlabel='t', ylabel='y',
           axis=[0, 4, -0.1, 0.6],
           legend=('t^2*exp(-t^2)', 't^4*exp(-t^2)'),
           title='Plotting two curves in the same plot',
           hardcopy='tmp2.ps')


FIGURE:[figs/plot2g.eps] Circles at every 4 points and extended line thickness (6) and circle size (3).


The different available line colors include 
  * yellow:   'y'
  * magenta:  'm'
  * cyan:     'c'
  * red:      'r'
  * green:    'g'
  * blue:     'b'
  * white:    'w'
  * black:    'k'

The different available line types are
  * solid line:      '-'
  * dashed line:     '--'
  * dotted line:     ':'
  * dash-dot line:   '-.'

We remark that in the Gnuplot backend all the different line types are
drawn as solid lines on the screen. The hardcopy chooses automatically
different line types (solid, dashed, etc.) and not in accordance with
the line type specification.

Lots of markers at data points are available:
  * plus sign:                     '+'
  * circle:                        'o'
  * asterix:                       '*'
  * point:                         '.'
  * cross:                         'x'
  * square:                        's'
  * diamond:                       'd'
  * upward-pointing triangle:      '^'
  * downward-pointing triangle:    'v'
  * right-pointing triangle:       '>'
  * left-pointing triangle:        '<'
  * five-point star (pentagram):   'p'
  * six-point star (hexagram):     'h'
  * no marker (default): None

Symbols and line styles may be combined, for instance as in 'kx-',
which means a black solid line with black crosses at the data points.

The line thickness can be added as a number in the line style specification
string. For example, 'r-2' means red solid line with thickness 2.

*Another Example.* Let us extend the previous example with a third
curve where the data points are slightly randomly distributed around
the f_2(t) curve::

      from scitools.all import *
      
      def f1(t):
          return t**2*exp(-t**2)
      
      def f2(t):
          return t**2*f1(t)
      
      t = linspace(0, 3, 51)
      y1 = f1(t)
      y2 = f2(t)
      
      # pick out each 4 points and add random noise:
      t3 = t[::4]      # slice, stride 4
      random.seed(11)  # fix random sequence
      noise = random.normal(loc=0, scale=0.02, size=len(t3))
      y3 = y2[::4] + noise
      
      plot(t, y1, 'r-')
      hold('on')
      plot(t, y2, 'ks-')   # black solid line with squares at data points
      plot(t3, y3, 'bo')
      
      legend('t^2*exp(-t^2)', 't^4*exp(-t^2)', 'data')
      title('Simple Plot Demo')
      axis([0, 3, -0.05, 0.6])
      xlabel('t')
      ylabel('y')
      show()
      hardcopy('tmp3.ps') 
      hardcopy('tmp3.png')

The plot is shown in Figure fig:plot3.

FIGURE:[figs/plot3.eps] A plot with three curves.

*Minimalistic Plotting.* When exploring mathematics in the interactive Python shell, most of us
are interested in the quickest possible commands.
Here is an example on minimalistic syntax for
comparing the two sample functions we have used in the previous examples::

      t = linspace(0, 3, 51)
      plot(t**2*exp(-t**2), t**4*exp(-t**2))



Interactive Plotting Sessions
-----------------------------

All the Easyviz commands can of course be issued in an interactive
Python session. The only thing to comment is that the plot command
returns an argument:
\bccq
>>> plot(x, y)
[<scitools.easyviz.common.Line object at 0xb5727f6c>]
\eccq
Most users will just ignore this output line.

All Easyviz commands that produce a plot return an object reflecting the
particular type of plot. The plot command returns a list of
Line objects, one for each curve in the plot. These Line
objects can be invoked to see, for instance, the value of different
parameters in the plot (Line.get()):
\bccq
>>> lines = plot(x, y, 'b')
>>> pprint.pprint(lines[0].get())
{'description': '',
 'dims': (4, 1, 1),
 'legend': '',
 'linecolor': 'b',
 'pointsize': 1.0,
 ...
\eccq
Such output is mostly of interest to advanced users.


Making Animations
-----------------

A sequence of plots can be combined into an animation and stored in a
movie file. First we need to generate a series of plots stored in
files, i.e., hardcopies. Thereafter we must use a tool to combine
the individual plot files into a movie file. We shall illustrate the
process with an example.

Consider the "Gaussian bell" function::

      \[ f(x; m, s) = 
      {1\over\sqrt{2\pi }s} 
      \exp{\left[-{1\over2}\left({x-m\over s}\right)^2\right]},
      \]

which is a "wide" function for large s and "peak-formed" for small s,
see Figure fig:plot4,
Our goal is to make an animation where we see how this function evolves
as s is increased. In Python we implement the formula above as
a function f(x, m, s). 

FIGURE:[figs/plot4.eps] Different shapes of a Gaussian bell function.

The animation is created by varying s in a loop and for each s
issue a plot command. A moving curve is then visible on the screen.
One can also make a movie file that can be played as any other
computer movie using a standard movie player. To this end, each plot
is saved to a file, and all the files are combined together using some
suitable tool, which is reached through the movie function in
Easyviz. All necessary steps will be apparent in the complete program
below, but before diving into the code we need to comment upon a
couple of issues with setting up the plot command for animations.

The underlying plotting program will normally adjust the axis to the
maximum and minimum values of the curve if we do not specify the axis
ranges explicitly. For an animation such automatic axis adjustment is
misleading - the axis ranges must be fixed to avoid a jumping
axis. The relevant values for the axis range is the minimum and
maximum value of f. The minimum value is zero, while the maximum
value appears for x=m and increases with decreasing s. The range
of the y axis must therefore be [0,f(m; m, \min s)].

The function f is defined for all -\infty < x < \infty, but the
function value is very small already 3s away from x=m. We may therefore
limit the x coordinates to [m-3s,m+3s].

Now we are ready to take a look at the complete code
for animating how the Gaussian bell curve evolves as the s parameter
decreases from 2 to 0.2:

!bc  
      from scitools.all import *
      import time
      
      def f(x, m, s):
          return (1.0/(sqrt(2*pi)*s))*exp(-0.5*((x-m)/s)**2)
      
      m = 0
      s_start = 2
      s_stop = 0.2
      s_values = linspace(s_start, s_stop, 30)
      x = linspace(m -3*s_start, m + 3*s_start, 1000)
      # f is max for x=m; smaller s gives larger max value
      max_f = f(m, m, s_stop)
      
      # show the movie, and make hardcopies of frames simulatenously:
      counter = 0
      for s in s_values:
          y = f(x, m, s)
          plot(x, y, axis=[x[0], x[-1], -0.1, max_f],
               xlabel='x', ylabel='f', legend='s=%4.2f' % s,
               hardcopy='tmp_%04d.ps' % counter)
          counter += 1
          #time.sleep(0.2)  # can insert a pause to control movie speed
      
      # make movie file:
      movie('tmp_*.ps')


First note that the s values are decreasing (linspace handles this
automatically if the start value is greater than the stop value).
Also note that we, simply because we think it is visually more
attractive, let the y axis go from -0.1 although the f function is
always greater than zero.

For each frame (plot) in the movie we store the plot in a file.  The
different files need different names and an easy way of referring to
the set of files in right order. We therefore suggest to use filenames
of the form stem0001.ext, stem0002.ext, stem0003.ext, etc.,
since the expression stem*.ext then lists all files in the right
order. In our example, stem is tmp_, and .ext is .ps
(PostScript format in the hardcopy).

Having a set of stem*.ext files, one can simply generate a movie
by a movie('stem*.ext') call. When a movie file is not wanted (it may
take some time to generate it), one can simply skip the hardcopy
argument and the call to movie.


Importing Just Easyviz
----------------------

The from scitools.all import * statement imports many modules and packages:
  * Easyviz
  * SciPy (if it exists)
  * NumPy (if SciPy is not installed)
  * the Python modules sys, os, math, operator
  * the SciTools module StringFunction and the SciTools 
    functions watch and trace for debugging

The scipy import can take some time and lead to slow start-up of plot 
scripts. A more minimalistic import for curve plotting is 
!bc  
      from scitools.easyviz import *
      from numpy import *

Alternatively, one can edit the scitools.cfg configure file or add
one's own .scitools.cfg file with redefinition of selected options,
such as load in the scipy section. The user .scitools.cfg must 
be placed in the directory where the plotting script in action resides, 
or in the user's home directory. Instead of editing a configuration
file, one can just add the command-line argument --SCITOOLS_scipy_load no
to the curve plotting script (all sections/options in the configuration
file can also be set by such command-line arguments).


Advanced Easyviz Topics
-----------------------


Working with the Plotting Program Directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Easyviz supports just the most common plotting commands, typically the
commands you use "95 percent" of the time when exploring curves.
Various plotting packages have lots of additional commands for
different advanced features.  When Easyviz does not have a command
that supports a particular feature, one must grab the Python object
that communicates with the underlying plotting program and work with
this object directly, using the plotting program-specific command
syntax.  Let us illustrate this principle with an example where we add
a text and an arrow in the plot, see Figure fig:plot2i.

FIGURE:[figs/plot2i.eps] A plot with three curves.

Easyviz does not support text and arrows at arbitrary places inside the
plot, but Gnuplot does. If we use Gnuplot as backend, we may
grab the Gnuplot object and issue Gnuplot commands to this object
directly::

      g = get_backend()
      if g.__class__.__name__ == 'Gnuplot':
          # g is a Gnuplot object, work with Gnuplot commands directly:
          g('set label "local maximum" at 0.1,0.5 font "Times,18"')
          g('set arrow from 0.5,0.48 to 0.98,0.37 linewidth 2')
      g.refresh()
      g.hardcopy('tmp2.ps')  # make new hardcopy


We refer to the Gnuplot manual for the features of this package and
the syntax of the commands. The idea is that you can quickly generate
plots with Easyviz, using standard commands that are independent of
the underlying plotting package. However, when you need to advanced
features, you have to write plotting package-specific code as shown
above. This principle makes Easyviz a light-weight interface, but
without limiting the available functionality of various plotting programs.


Working with Axis and Figure Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Easyviz supports the concept of Axis objects, as in Matlab.
The Axis object represent a set of axis, with curves drawn in the
associated coordinate system. A figure is the complete physical plot.
One may have several axis in one figure, each axis representing a subplot.
One may also have several figures, represented by different
windows on the screen or separate hardcopies.

*Axis Objects.* Users with Matlab experience may prefer to set axis
labels, ranges, and the title using an Axis object instead of
providing the information in separate commands or as part of a plot
command. The gca (get current axis) command returns an Axis
object, whose set method can be used to set axis properties::

      plot(t, y1, 'r-', t, y2, 'bo',
           legend=('t^2*exp(-t^2)', 't^4*exp(-t^2)'),
           hardcopy='tmp2.ps')
      
      ax = gca()   # get current Axis object
      ax.set(xlabel='t', ylabel='y',
             axis=[0, 4, -0.1, 0.6],
             title='Plotting two curves in the same plot')
      show()  # show the plot again after ax.set actions


*Figure Objects.* The figure() call makes a new figure, i.e., a
new window with curve plots. Figures are numbered as 1, 2, and so on.
The command figure(3) sets the current figure object to figure number
3. 

Suppose we want to plot our y1 and y2 data in two separate windows::

      plot(t, y1, 'r-', xlabel='t', ylabel='y',
           axis=[0, 4, -0.1, 0.6])
      
      figure()  # new figure
      
      plot(t, y2, 'bo', xlabel='t', ylabel='y')

We may then go back to the first figure (with the y1 data) and
set a title and legends in this plot, show the plot, and make a PostScript
version of the plot::

      figure(1)  # go back to first figure
      title('One curve')
      legend('t^2*exp(-t^2)')
      show()
      hardcopy('tmp2_1.ps')

We can also adjust figure 2:
!bc  
      figure(2)  # go to second figure
      title('Another curve')
      hardcopy('tmp2_2.ps')
      show()

The current Figure object is reached by gcf (get current figure),
and the dump method dumps the internal parameters in the Figure
object::

      fig = gcf(); print fig.dump()

These parameters may be of interest for troubleshooting when Easyviz
does not produce what you expect.

Let us then make a third figure with two plots, or more precisely, two
axes: one with y1 data and one with y2 data.
Easyviz has a command subplot(r,c,a) for creating r
rows and c columns and set the current axis to axis number a.
In the present case subplot(2,1,1) sets the current axis to
the first set of axis in a "table" with two rows and one column.
Here is the code for this third figure::

      figure()  # new, third figure
      # plot y1 and y2 as two axis in the same figure:
      subplot(2, 1, 1)
      plot(t, y1, xlabel='t', ylabel='y')
      subplot(2, 1, 2)
      plot(t, y2, xlabel='t', ylabel='y')
      title('A figure with two plots')
      show()
      hardcopy('tmp2_3.ps')

We remark that the hardcopy command does not work with the Gnuplot backend
in this case with multiple axes in a figure.

If we need to place an axis at an arbitrary position in the figure, we
must use the::

      ax = axes(viewport=[left, bottom, width, height])

command. The four parameteres left, bottom, width, height
are location values between 0 and 1 ((0,0) is the lower-left corner 
and (1,1) is the upper-right corner).


Visualization of Scalar Fields
------------------------------

A scalar field is a function from space or space-time to a real value,
typically used to express the value of a scalar physical parameter
a every point in space (or in space and time). One example is temperature,
which is a scalar quantity defined everywhere in space and time.
In a visualization context, we work with discrete scalar fields that are
defined on a grid. Each point in the grid is then associated with a
scalar value.

There are several ways to visualize a scalar field in Easyviz. Both
two- and three-dimensional scalar fields are supported. In 2D we can
create elevated surface plots, contour plots, and pseudocolor plots,
while in 3D we can create isosurface plots, volumetric slice plots,
and contour slice plots.

Elevated Surface Plots
~~~~~~~~~~~~~~~~~~~~~~

To create elevated surface plots
we can use either the surf or the mesh command. Both
commands have the same syntax, but the mesh command creates a
wireframe mesh while the surf command creates a solid colored
surface. We will first look at the mesh command. 

Design
======

Main Objects
------------

All code that is common to all backends is gathered together in a file
called common.py. For each backend there is a separate file where
the backend dependent code is stored. For example, code that are
specific for the Gnuplot backend, are stored in a file called
gnuplot_.py and code specific for the VTK backend are stored in
vtk_.py (note the final underscore in the stem of the filename - all
backend files have this underscore). 

Each backend is a subclass of class BaseClass. The BaseClass code
is found in common.py and contains all common code for the backends.
Basically, a backend class extends BaseClass with
rendering capabilities and backend-specific functionallity. 

The most important method that needs to be implemented in the backend
is the _replot method, which updates the backend and the plot after a
change in the data. Another important method for the backend class is
the hardcopy method, which stores an image of the data in the current
figure to a file.

Inspired by Matlab, the Easyviz interface is organized around figures and
axes. A figure contains an arbitrary number of axes, and the axes can
be placed in arbitrary positions in the figure window. Each figure appears
in a separate window on the screen. The current figure is accessed by
the gcf() call. Similarly, the current axes are accessed by calling
gca().

It is
natural to have one class for figures and one for axes. Class Figure
contains a dictionary with one (default) or more Axis objects in
addition to several properties such as figure width/height. Class Axis
has another dictionary with the plot data as well as lots of
parameters for colors, text fonts, labels on the axes, hidden surfaces, etc.
For example, when adding an
elevated surface to the current figure, this surface will be
appended to a list in the current Axis object. 
Optionally one can add the surface to another Axis
object by specifying the Axis instance as an argument. 


All the objects that are to be plotted in a figure such as curves,
surfaces, vectors, and so on, are stored in repsectively classes.  An
elevated surface, for instance, is represented as an instance of class
Surface.  All such classes are subclasses of
PlotProperties. Besides being the base class of all objects that can
be plotted in a figure
(Line, 
Surface, 
Contours, 
VelocityVectors, 
Streams, 
Volume), 
class PlotProperties also stores various properties that are common
to all objects in a figure. Examples include line properties, material
properties, storage arrays for x and y values for Line objects,
and x, y, and z values for 3D objects such as Volume.

The classes mentioned above, i.e., BaseClass with subclasses, class
PlotProperties with subclasses, as well as class Figure and class
Axis constitute the most important classes in the Easyviz interface.
Other less important classes are Camera, Light, Colorbar, and
MaterialProperties.

All the classes in common.py follows a convention where class parameters
are set by a set method and read by a get method. For
example, we can set axis limits using the set methods in a
Axis instance::

      ax = gca()                  # get current axies
      ax.set(xmin=-2, xmax=2)

To extract the values of these limits we can write::

      xmin = ax.get('xmin')
      xmax = ax.get('xmax')

Normal use will seldom involve set and get functions, since most
most users will apply the Matlab-inspired interface and set, e.g., axis
limits by::

      axis([-2, 2, 0, 6])





"""

__author__ = "Johannes H. Ring, Rolv Erlend Bredesen, Hans Petter Langtangen"
__version__ = "0.1"

_import_list = []  # used as in basics.py
import time as _time; _t0 = _time.clock();
_import_times = 'easyviz import times: '

from scitools.globaldata import backend, VERBOSE   # read-only import
_import_list.append("from scitools.globaldata import backend, VERBOSE")

_t1 = _time.clock(); _import_times += 'config: %s ' % (_t1 - _t0)

cmd = 'from %s_ import *' % backend
exec(cmd)
_t2 = _time.clock(); _import_times += '%s: %s ' % (backend, _t2 - _t1)
_import_list.append(cmd)

from utils import *
from movie import movie
_import_list.append('from utils import *\nfrom movie import movie')

_t3 = _time.clock(); _import_times += 'utils: %s ' % (_t3 - _t2)

if VERBOSE >= 2:
    for i in _import_list:
        print i
if VERBOSE >= 3:
    print _import_times
if VERBOSE >= 1:
    print "scitools.easyviz backend is %s" % backend

__doc__ += '\nImport statements in this module:\n' + '\n'.join(_import_list)


# add plot doc string to package doc string:
#__doc__ += plot.__doc__

def get_backend():
    """Return the current backend object (used for direct access
    to the underlying plotting package when there is need for
    advanced plotting beyond the plain easyplot functionality).
    """
    return plt._g
