#!/bin/bash -x
this_dir=`pwd`
# make easyviz doc with reST format:
cd ../../../lib/scitools
doconce insertdocstr rst .
cd $this_dir

make html
rm ../sphinx/html/*
cp -r _build/html/* ../sphinx-html/

# run easyviz doc with plain again (for pydoc):
cd ../../../lib/scitools
doconce insertdocstr plain .
cd $this_dir

ls _build/html
