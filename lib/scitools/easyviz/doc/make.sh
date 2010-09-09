#!/bin/bash -x
# clean:
rm -rf tmp_*

cp easyviz.do.txt tmp_easyviz.do.txt

doconce2format HTML tmp_easyviz.do.txt
doconce2format plain tmp_easyviz.do.txt

doconce2format LaTeX tmp_easyviz.do.txt
ptex2tex tmp_easyviz
scitools subst slice_ 'slice\_' tmp_easyviz.tex   # _ fix
latex tmp_easyviz
latex tmp_easyviz
dvipdf tmp_easyviz.dvi

# note: Unknown target name "slice" will always be reported by rst
# conversion because we write slice_ in the list of Matlab-like commands...

doconce2format gwiki tmp_easyviz.do.txt
doconce_gwiki_figsubst.py tmp_easyviz.gwiki https://scitools.googlecode.com/svn/trunk/lib/scitools/easyviz/doc

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
cp -r figs tmp-figs
find tmp-figs -name .svn -exec rm -rf {} \; 2> /dev/null
cp -r tmp-figs sphinx-rootdir/figs  # important for finding the figures...
cd sphinx-rootdir
make clean
make html
cd ..

cp tmp_easyviz.pdf   ../../../../doc/easyviz/easyviz.pdf
cp tmp_easyviz.html  ../../../../doc/easyviz/easyviz.html
cp tmp_easyviz.gwiki ../../../../doc/easyviz/easyviz.gwiki
cp tmp_easyviz.txt   ../../../../doc/easyviz/easyviz.txt
preprocess tmp_easyviz.do.txt > tmp.do.txt
cp tmp.do.txt  ../../../../doc/easyviz/easyviz.do.txt
#cp tmp_easyviz_sphinx.pdf ../../../../doc/easyviz/easyviz_sphinx.pdf
cp -r sphinx-rootdir/_build/html ../../../../doc/easyviz/easyviz_sphinx_html
cp -r figs tmp-figs
find tmp-figs -name .svn -exec rm -rf {} \; 2> /dev/null
cp -r tmp-figs       ../../../../doc/easyviz/figs  # to make HTML work

ls ../../../../doc/easyviz/

# HTML and sphinx doesn't work well at googlecode directly from the
# svn tree, so we copy these to another location:
cd ../../../../doc/
rm -rf tmp
cp -r easyviz tmp
cd tmp
find . -name .svn -exec rm -rf {} \; 2> /dev/null
echo
echo "cd ../../../../doc/tmp"
echo scp -r easyviz.html easyviz_sphinx_html figs easyviz.do.txt easyviz.pdf hpl@gogmagog.simula.no:www_docs/easyviz/
echo "cd ..;  rm -rf tmp"





