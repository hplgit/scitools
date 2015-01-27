#!/bin/sh
# Make sure latest scitools is installed

this_dir=`pwd`
version=`python -c "import scitools as st; print st.version"`

# make easyviz doc with reST/Sphinx format:
doconce insertdocstr sphinx ../easyviz
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
$version
$version
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
    'sidebarbgcolor': 'bg',
    'footerbgcolor': 'bg',
    'relbarbgcolor': 'bg',
    'headbgcolor': 'bg',
}" conf.py
# Add logo
doconce replace "#html_logo = None" "html_logo = 'scitools_logo.jpg'" conf.py


# Make sure we have the numpydoc module
python -c 'import numpydoc'
if [ $? -ne 0 ]; then echo; echo "Install numpydoc: download numpy (or get the latest github version, cd doc/sphinxext; sudo python setup.py install"; exit 1; fi

# Generate HTML documentation
rm -rf _build
if [ ! -d figs ]; then
ln -s ../easyviz/figs .
fi
make html

# equip doc with plain text format (for pydoc):
cd ../../../lib/scitools
doconce insertdocstr plain .
cd $this_dir

cp -r ../easyviz/figs _build/html/
ls _build/html
#cp -r _build/html ../../api/

