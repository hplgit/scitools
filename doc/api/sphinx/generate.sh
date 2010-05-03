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

scitools subst ':maxdepth: 2' ":maxdepth: 2\n\n\n    BoxField\n    BoxGrid\n    EfficiencyTable\n    FloatComparison\n    Lumpy\n    NumPyDB\n    aplotter\n    basics\n    configdata\n    convergencerate\n    debug\n    easyviz\n    errorcheck\n    filetable\n    globaldata\n    modulecheck\n    multipleloop\n    numpytools\n    numpyutils\n    pprint2\n    PrmDictBase\n    Regression\n    sound\n    std\n    StringFunction" index.txt

make html

ls _build/html

