#!/usr/bin/env python
# update all modules (run preprocessor etc.)
import os
# the insertdocstr script is part of the Doconce package
os.system('insertdocstr plain . ')
"""
import os, shutil

from misc import preprocess_all_files

fileinfo = preprocess_all_files(os.curdir)
print 'The following files have been preprocessed:'
success_str = {True: 'success', False: 'failure'}
for files, success in fileinfo:
    d, f, fp = files
    print 'directory %s   %s -> %s (%s)' % (d, f, fp, success_str[success])
"""
