# What?

SciTools is a Python package containing many useful tools for scientific
computing in Python. The package is built on top of other widely used
packages such as NumPy, SciPy, ScientificPython, Matlotlib, Gnuplot,
VisIt, etc.

# Dependencies

SciTools only strict requirements are Python v2.7 (http://python.org)
and Numerical Python (http://numpy.org). Some functionality requires
SciPy (http://scipy.org/). Plotting requires a plotting package, e.g.,
Matplotlib, Gnuplot, VisIt, or similar.

# Installation

There are several different ways of installing SciTools.

_Anaconda_.
If you have Anaconda, SciTools is available as a conda package:

   conda install --channel johannr scitools

_Normal install_ ([, ... ] means optional).
First check out the scitools package from GitHub:
https://github.com/hplgit/scitools. Then go to the scitools
directory and run

     python setup.py install [,--prefix=$PREFIX]

This install makes SciTools use Matplotlib as plotting engine, if a
a working Matplotlib is found. Otherwise Gnuplot is used (which requires
both the Gnuplot program in C and the Python interface Gnuplot.py to
be installed). If neither Matplotlib nor Gnuplot is found, Matplotlib
is still used as default plotting engine. (The rest of SciTools will
work well, of course.)

Installing Matplotlib is easy on most platforms: just download the
tarball, pack it out, and run python setup.py install.

You can explicitly specify the desired plotting engine on the command line,
using the `--easyviz_backend` option:

     python setup.py install --easyviz_backend gnuplot [,--prefix=$PREFIX]

The default plotting engine is specified in the file scitools.cfg in the
scitools package directory, and the --easyviz_backend option leads to
an automatic edit of the "backend" line in the [easyviz] section of
that configuration file.

Don't edit the scitools.cfg file manually before installation (use
the `--easyviz_backend` option) because setup.py will override your
edits of the easyviz backend.  However, all other edits of the
configuration file can be edited.  For example, the Matplotlib GUI
is set to TkAgg (i.e., using Tkinter, which is standard in most
Python installations). The GUI can be set to other values, such as
Qt4Agg (provided you have Qt4 and a Python interface to it).

After SciTools is installed, you may edit the installed version of
scitools.cfg, or (better) have your own .scitools.cfg file in your
home directory.

_Setuptools using eggs._
First build the egg with the following command

     python setupegg.py [, egg_info --tag-svn-revision ] bdist_egg

The --easyviz_backend option can be used, as described above, to
change the default plotting engine.

Then install the created egg using easy_install

     easy_install [, --prefix=$PREFIX] dist/Scitools-0.7-py2.6.egg

(Version numbers of SciTools and Python in this filename may vary.)

_Debian/Ubuntu packages._
If you have Debian, or a Debian based platform like Ubuntu, you can do

     sudo apt-get install python-scitools

as SciTools is now a part of Debian.
NOTE: The Debian packages are often old - it is better to rely
on checking out the repo and running setup.py.

# Configuration File

The behavior of many parts of SciTools and in particular the
subpackage Easyviz (for plotting) can be controlled in a configuration
file.  Please read the subsection "Setting Parameters in the
Configuration File" under the section "Advanced Easyviz Topics" in the
Easyviz tutorial (pydoc scitools.easyviz will show the tutorial). In
particular, if you use Matplotlib as the default plotting engine, you
may want to turn on the use of LaTeX for rendering legends, titles,
and numbers.  By default, LaTeX is turned off when SciTools is
installed. It is easy to change this by locating the scitools.cfg file
in the folder where the SciTools package is installed and edit the
line with text.usetex in the [matplotlib] section of this file. A
better solution is to copy the system scitools.cfg file to
.scitools.cfg in your home folder and edit that file. You can also
change the GUI used by Matplotlib. Users who do not apply Matplotlib
for plotting will seldom need to edit the configuration file.

# License

SciTools is licensed under the new BSD license, see the LICENSE file.

Lumpy.py and Gui.py are licensed under GPL, however, permission is
granted by Allen Downey to include these under a BSD license.

# Credits

SciTools was initially mainly developed by Hans Petter Langtangen
<hpl@simula.no> for his book "Python Scripting for Computational
Science" (Springer, 1st edition 2003, 3rd edition 2009).
The Easyviz package was mainly developed by Johannes H. Ring
<johannr@simula.no>. Johannes H. Ring has been the principal
maintainer of SciTools. The package was extended for the
book "A Primer on Scientific Programming with Python", by H. P. Langtangen,
4th edition, Springer, 2014.

Some modules included in SciTools are written by others:

 * Allen B. Downey <downey@allendowney.com> wrote Lumpy.py and Gui.py
 * Imri Goldberg <lorgandon@gmail.com> wrote aplotter.py
 * Fred L. Drake, Jr. <fdrake@acm.org> wrote pprint2.py
 * Gael Varoquaux <gael.varoquaux@normalesup.org> wrote pyreport

Code contributors include:

 * Rolv E. Bredesen <rolveb@simula.no>
 * Joachim B. Haga <jobh@simula.no>
 * Mario Pernici <Mario.Pernici@mi.infn.it>
 * Ilmar Wilbers <ilmarw@simula.no>
 * Arve Knudsen <arvenk@simula.no>
