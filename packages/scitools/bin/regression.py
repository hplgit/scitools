#!/usr/bin/env python
import scitools.Regression, sys

usage = "Usage: " + sys.argv[0] + " verify|update|template rootdir|filename" 


try:
  task = sys.argv[1]
except:
  print usage; sys.exit(1)

try:
  root = sys.argv[2]
except:
  print usage; sys.exit(1)

# options sys.argv[3] is only relevant for Diffpack applications:
try:
  mode = sys.argv[3]
except:
  mode = "opt"

legal = ('verify', 'update', 'template')
if task == 'verify' or task == 'update':
    #v = scitools.Regression.Verify(root=root, task=task, makemode=mode)
    # use VerifyDiffpack as this handles all simple .verify scripts
    # and also scripts requiring compilation of Diffpack applications
    v = scitools.Regression.VerifyDiffpack(root=root, task=task, makemode=mode)
    # the constructor does it all...
elif task == 'template':
    scitools.Regression.verify_file_template(root)  # sys.argv[2] is the name...
else:
    print "1st command-line argument must be verify, update, or template"
    

  
