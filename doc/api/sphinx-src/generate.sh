#!/bin/sh

this_dir=`pwd`
# make easyviz doc with reST format:
cd ../../../lib/scitools
doconce insertdocstr rst .
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

scitools subst ':maxdepth: 2' ":maxdepth: 1\n\n   scitools\n   BoxField\n   BoxGrid\n   EfficiencyTable\n   FloatComparison\n   Lumpy\n   NumPyDB\n   PrmDictBase\n   Regression\n   StringFunction\n   TkGUI\n   aplotter\n   basics\n   configdata\n   convergencerate\n   debug\n   errorcheck\n   filetable\n   globaldata\n   misc\n   modulecheck\n   MovingPlotWindow\n   multipleloop\n   numpytools\n   numpyutils\n   pprint2\n   redirect_io\n   sound\n   std\n   easyviz\n   blt_\n   common\n   dx_\n   gnuplot_\n   grace_\n   matlab2_\n   matlab_\n   matplotlib_\n   misc\n   movie\n   pyx_\n   template_\n   utils\n   veusz_\n   visit_\n   vtk_\n   vtk_new_\n " index.txt

make html

# run easyviz doc with plain again (for pydoc):
cd ../../../lib/scitools
doconce insertdocstr plain .
cd $this_dir

ls _build/html

