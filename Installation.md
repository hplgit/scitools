# Installing SciTools #
## Dependencies and requirements ##
In addition to a working installation of Python, SciTools only
dependency is some sort of Numerical Python. Either
[NumPy](http://numpy.scipy.org),
[Numeric](http://sourceforge.net/project/showfiles.php?group_id=1369&package_id=1351),
or
[Numarray](http://www.stsci.edu/resources/software_hardware/numarray/numarray.html)
can be used, however, we recommend to use NumPy. To take full advantage of what SciTools has to offer,
you should also install some of the optional packages listed below
(Debian/Ubuntu packages inside parentheses).

  * [SciPy](http://scipy.org) (`python-scipy`)

  * [ScientificPython](http://sourcesup.cru.fr/projects/scientific-py/) (`python-scientific`)

You should also install at least one of the following packages to add
plotting support with Easyviz:

  * [Gnuplot](http://www.gnuplot.info/) with Python support (`python-gnuplot`)

  * [VTK](http://www.vtk.org/) with Python support (`python-vtk`)

  * [Matplotlib](http://matplotlib.sourceforge.net/) (`python-matplotlib`)

  * [PyX](http://pyx.sourceforge.net/) (`python-pyx`)

  * BLT (`blt` and `python-pmw`)

  * [OpenDX](http://www.opendx.org/) (`dx` and `libdx4-dev`) and [PY2DX](http://www.psc.edu/general/software/packages/mfix/tools/index.php)

  * [Grace](http://plasma-gate.weizmann.ac.il/Grace/) (`grace`) and [pygrace](http://www.its.caltech.edu/~mmckerns/software.html)

  * [Veusz](http://home.gna.org/veusz/) version 0.9

  * [Visit](http://www.llnl.gov/visit/)

The recommended choice for most users is to install Gnuplot since it has
many useful features and should be easy to install on most platforms. If
more advanced 2D and 3D plotting are needed, then VTK is a good
choice. However, this could be difficult to install on the Windows
platform since we need Python support which means you have to compile it
by your self.

SciTools is packaged for several different platforms. Simply follow the
instructions below. You may also install SciTools directly from the
sources.
## Sources ##
The latest sources are available under the [Downloads](http://code.google.com/p/scitools/downloads/list) tab as a `.tar.gz'
file. Unpack the sources into a suitable folder and run the usual

```
python setup.py install
```
This will install SciTools into the default location, usually
`/usr/lib/pythonX.Y/site-packages` on Linux and
`C:\PythonXY\Lib\site-packages` on Windows, where `X` and `Y` is the
version of Python running on your system.

Use the `--prefix` option if you want to install SciTools into a
different location. However, in this case you also have to update the
`PATH` and the `PYTHONPATH` environment variables to reflect this
directory.

If you want to try out SciTools without installing it, you can add the
`lib` folder under the SciTools root tree to your `PYTHONPATH`
environment variable. In Linux you can do this, e.g., by running
(depending on the shell)

```
export PYTHONPATH=$PYTHONPATH:/path/to/scitools/lib
```
You should also add the `bin` folder to the systems `PATH` environment
variable:

```
export PATH=$PATH:/path/to/scitools/bin
```
## Packages ##
### Debian ###
SciTools is now available in Debian. To install, simply run
```
sudo apt-get install python-scitools
```
### Ubuntu ###
SciTools is available in Ubuntu as of Ubuntu 10.04. To install, simply run
```
sudo apt-get install python-scitools
```
Because of Ubuntu's policy of not updating the version of a shipped application, the SciTools version that is available might be old. To stay current with the latest releases, add the SciTools Personal Package Archive (PPA) to your Ubuntu system. You can do this simply by running the following command:
```
sudo add-apt-repository ppa:scitools/ppa
```
Then make sure you reload the package sources
```
sudo apt-get update
```
and finally install the latest SciTools package:
```
sudo apt-get install python-scitools
```
### Windows ###
SciTools is available as a self-extracting ZIP file for Windows under the [Downloads](http://code.google.com/p/scitools/downloads/list) tab. Just download the file to your hard drive and double-click the file. Then simply follow the instructions on the
screen.
## Testing ##
To verify that the installation was successful, start up an interactive
Python session and try to import SciTools, that is

```
>>> from scitools.std import *
```
You may need to edit the `scitools.cfg` file to match your needs. Also
try out some of the examples in the `examples` folder under the SciTools
root folder.