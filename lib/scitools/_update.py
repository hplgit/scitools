#!/usr/bin/env python
# update all modules (run preprocessor etc.)
import os
# the insertdocstr script is part of the Doconce package
os.system('doconce insertdocstr plain . ')
#os.system('doconce insertdocstr epytext . ')
