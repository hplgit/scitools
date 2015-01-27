# -*- coding: utf-8 -*-
"""
=========
Pyreport
=========

Pyreport makes notes out of a python script. It can run the script in a
sandbox and capture its output. It allows for embedding RestructuredText
or LaTeX comments in the code for literate programming and generates a
report made of the literate comments, the code, pretty printed, and the
output of the script (pyreport can capture pylab figures). This is useful
for documentations, making tutorials, but also for sharing python-based
calculations with colleagues.
"""

#*****************************************************************************
#       Copyright (C) 2006-2007 Gaël Varoquaux.
#                                           <gael.varoquaux@normalesup.org>
#
#  Distributed under the terms of the BSD License.
#*****************************************************************************

__author__   = 'Gael Varoquaux'
__license__  = 'BSD'
__revision__ = "$Revision: $"

from version import __version__
