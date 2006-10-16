#!/usr/bin/env python
import os, sys
debugger = os.path.join(sys.prefix, 'lib', 
                        'python'+sys.version[:3], 'pdb.py')
print debugger
