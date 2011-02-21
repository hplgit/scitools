#!/bin/bash -x
# Create Easyviz documentation.
# clean:
rm -rf tmp_*

# Make .p.py -> .py files and make sure most recent documentation of
# Easyviz is in the __init__.py file:
cd ../..
python _update.py
cd easyviz/doc

# Prepare Doconce files and filter them to various formats:
cp easyviz.do.txt tmp_easyviz.do.txt

doconce2format HTML tmp_easyviz.do.txt
doconce2format plain tmp_easyviz.do.txt

doconce2format LaTeX tmp_easyviz.do.txt
ptex2tex tmp_easyviz
scitools subst slice_ 'slice\_' tmp_easyviz.tex   # _ fix
latex -shell-escape tmp_easyviz
latex -shell-escape tmp_easyviz
dvipdf tmp_easyviz.dvi

# note: Unknown target name "slice" will always be reported by rst
# conversion because we write slice_ in the list of Matlab-like commands...

doconce2format gwiki tmp_easyviz.do.txt
doconce_gwiki_figsubst.py tmp_easyviz.gwiki https://scitools.googlecode.com/hg/doc/easyviz

doconce2format sphinx tmp_easyviz.do.txt
rm -rf sphinx-rootdir
mkdir sphinx-rootdir
sphinx-quickstart <<EOF
sphinx-rootdir
n
_
Easyviz Documentation
H. P. Langtangen and J. H. Ring
1.0
1.0
.rst
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
mv tmp_easyviz.rst sphinx-rootdir
# index-sphinx is a ready-made version of index.rst:
cp index-sphinx sphinx-rootdir/index.rst
cp -r figs sphinx-rootdir/figs   # important for finding the figures...
rm -f sphinx-rootdir/figs/*.*ps  # save some diskspace
cd sphinx-rootdir
make clean
make html
cd ..

doconce2format rst tmp_easyviz.do.txt
scitools subst '(figs/.+?)\.eps' '\g<1>.png' tmp_easyviz.rst
rst2html.py tmp_easyviz.rst > tmp_easyviz_rst.html

cp tmp_easyviz.pdf   ../../../../doc/easyviz/easyviz.pdf
cp tmp_easyviz.html  ../../../../doc/easyviz/easyviz.html
cp tmp_easyviz_rst.html  ../../../../doc/easyviz/easyviz_rst.html
cp tmp_easyviz.gwiki ../../../../doc/easyviz/easyviz.gwiki
cp tmp_easyviz.txt   ../../../../doc/easyviz/easyviz.txt
preprocess tmp_easyviz.do.txt > tmp.do.txt
cp tmp.do.txt  ../../../../doc/easyviz/easyviz.do.txt
#cp tmp_easyviz_sphinx.pdf ../../../../doc/easyviz/easyviz_sphinx.pdf
# must remove old dirs, otherwise new files won't overwrite
rm -rf ../../../../doc/easyviz/easyviz_sphinx_html
rm -rf ../../../../doc/easyviz/figs
rm -rf ../../../../doc/easyviz/easyviz_sphinx_html/figs
cp -r sphinx-rootdir/_build/html ../../../../doc/easyviz/easyviz_sphinx_html
cp -r figs ../../../../doc/easyviz/figs  # to make HTML work
cp -r figs ../../../../doc/easyviz/easyviz_sphinx_html/figs  # to make Sphinx work
rm -f ../../../../doc/easyviz/figs/*.*ps ../../../../doc/easyviz/easyviz_sphinx_html/figs/*.*ps  # save some diskspace

ls ../../../../doc/easyviz/





