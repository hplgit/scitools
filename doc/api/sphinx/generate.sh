#!/bin/sh

rm -rf _build/ _static/ _templates/ conf.py index.txt

sphinx-quickstart <<EOF
.
n
_
SciTools
H. P. Langtangen, J. Ring, ++
0.7
0.7
.txt
index
y
n
n
n
n
y
n
n
y
n
EOF

scitools subst '\#sys\.path\.append.+' "sys.path.append(os.path.join(os.path.abspath('.'), os.pardir, os.pardir, os.pardir, 'lib', 'scitools'))" conf.py

scitools subst ':maxdepth: 2' ":maxdepth: 1\n\n   scitools\n   BoxField\n   BoxGrid\n   EfficiencyTable\n   FloatComparison\n   Lumpy\n   NumPyDB\n   PrmDictBase\n   Regression\n   StringFunction\n   TkGUI\n   aplotter\n   basics\n   configdata\n   convergencerate\n   debug\n   errorcheck\n   filetable\n   globaldata\n   misc\n   modulecheck\n   multipleloop\n   numpytools\n   numpyutils\n   pprint2\n   redirect_io\n   sound\n   std\n   easyviz\n   blt_\n   common\n   dx_\n   gnuplot_\n   grace_\n   matlab2_\n   matlab_\n   matplotlib_\n   misc\n   movie\n   pyx_\n   template_\n   utils\n   veusz_\n   visit_\n   vtk_\n   vtk_new_\n " index.txt

#scitools subst ':maxdepth: 2' ":maxdepth: 2\n\n   scitools\n   BoxField\n   BoxGrid\n   EfficiencyTable\n   FloatComparison\n   Lumpy\n   NumPyDB\n   PrmDictBase\n   Regression\n   StringFunction\n   TkGUI\n   aplotter\n   basics\n   configdata\n   convergencerate\n   debug\n   errorcheck\n   filetable\n   globaldata\n   misc\n   modulecheck\n   multipleloop\n   numpytools\n   numpyutils\n   pprint2\n   redirect_io\n   sound\n   std\n   easyviz\n   blt_\n   common\n   dx_\n   gnuplot_\n   grace_\n   matlab2_\n   matlab_\n   matplotlib_\n   misc\n   movie\n   pyx_\n   template_\n   utils\n   veusz_\n   visit_\n   vtk_\n   vtk_new_" index.txt

make html

ls _build/html

