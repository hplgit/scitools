;;; This file is named .cfg.py although it is not a valid Python code.
;;; The reason for the .py extension is that the more natural filename
;;; scitools.cfg implies a data file, which is not installed together
;;; with the scitools package by Distutils.

[modes]
SAFECODE = on        ; boolean: safety checks or not
OPTIMIZATION = off   ; 'F77', 'C', 'vectorization', 'on', etc.
VERBOSE = 3          ; an int for the level of verbosity

[scipy]
load = yes           ; true: from scipy import * (may have side effects)

[easyviz]
backend = gnuplot_
