#!/usr/bin/env python
import scitools.Regression, sys

usage = "Usage: " + sys.argv[0] + " verify|update|template rootdir|filename" 


try:
  task = sys.argv[1]
except IndexError:
  print usage; sys.exit(1)

try:
  name = sys.argv[2]
except IndexError:
  print usage; sys.exit(1)

if task == 'verify' or task == 'update':
    v = scitools.Regression.Verify(root=name, task=task)
elif task == 'template':
    scitools.Regression.verify_file_template(name)
else:
    print "1st command-line argument must be verify, update, or template"
    

  
