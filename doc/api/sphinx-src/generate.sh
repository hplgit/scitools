#!/bin/sh

this_dir=`pwd`
version=`python -c "import scitools as st; print st.version"`

# make easyviz doc with reST/Sphinx format:
cd ../../../lib/scitools
doconce insertdocstr sphinx .
cd $this_dir

rm -rf _build/ _static/ _templates/ conf.py index.txt *.old~

sphinx-quickstart <<EOF
.
n
_
SciTools
H. P. Langtangen, J. Ring, ++
0.8
0.8
.txt
index
n
y
n
n
n
n
y
n
n
y
y
y
EOF

scitools subst '\#sys\.path\.append.+' "sys.path.append(os.path.join(os.path.abspath('.'), os.pardir, os.pardir, os.pardir, 'lib', 'scitools'))" conf.py

#scitools subst ':maxdepth: 2' ":maxdepth: 1\n\n   scitools\n   BoxField\n   BoxGrid\n   EfficiencyTable\n   FloatComparison\n   Lumpy\n   NumPyDB\n   PrmDictBase\n   Regression\n   StringFunction\n   TkGUI\n   aplotter\n   basics\n   configdata\n   convergencerate\n   debug\n   errorcheck\n   filetable\n   globaldata\n   misc\n   modulecheck\n   MovingPlotWindow\n   multipleloop\n   numpytools\n   numpyutils\n   pprint2\n   redirect_io\n   sound\n   std\n   easyviz\n   blt_\n   common\n   dx_\n   gnuplot_\n   grace_\n   matlab2_\n   matlab_\n   matplotlib_\n   misc\n   movie\n   pyx_\n   template_\n   utils\n   veusz_\n   visit_\n   vtk_\n   vtk_new_\n " index.txt

cp index.txt-orig index.txt  # overwrite

# Also add more extensions
doconce subst "extensions = .*" "extensions = [
  'sphinx.ext.autodoc',
  'sphinx.ext.mathjax',
  'sphinx.ext.viewcode',
  'numpydoc',
  'sphinx.ext.autosummary',
  'sphinx.ext.doctest',
  'matplotlib.sphinxext.only_directives',
  'matplotlib.sphinxext.plot_directive',
  'matplotlib.sphinxext.ipython_directive',
  'matplotlib.sphinxext.ipython_console_highlighting',
  'sphinx.ext.inheritance_diagram']" conf.py
# Add support for other themes
doconce subst "html_theme = 'default'" "html_theme = [
  'default',
  'agogo',
  'haiku',
  'pyramid',
  'sphinxdoc',
  'basic',
  'epub',
  'nature',
  'scrolls',
  'traditional'][0]  # standard themes in sphinx" conf.py
# Add support for customizing themes
doconce subst "\#html_theme_options = \{\}" "\
# See http://sphinx.pocoo.org/theming.html for setting options
# This is a customization of the default theme:
html_theme_options = {
    'rightsidebar': 'true',
    'sidebarbgcolor': bg,
    'footerbgcolor': bg,
    'relbarbgcolor': bg,
    'headbgcolor': bg,
}" conf.py
# Add logo
doconce replace "#html_logo = None" "html_logo = 'scitools_logo.jpg'" conf.py


# Make sure we have the numpydoc module
python -c 'import numpydoc'
if [ $? -ne 0 ]; then echo; echo "Install numpydoc: download numpy (or get the latest github version, cd doc/sphinxext; sudo python setup.py install"; exit 1; fi

# Generate HTML documentation
make html

# run easyviz doc with plain again (for pydoc):
cd ../../../lib/scitools
doconce insertdocstr plain .
cd $this_dir

ls _build/html

