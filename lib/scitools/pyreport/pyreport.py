#!/usr/bin/env python
"""
Tool that takes python script and runs it. Returns the results and special
comments (literate comments) embedded in the code in a pdf (or html, or rst...)
"""
# Author: Gael Varoquaux  <gael dot varoquaux at normalesup dot org>
# Copyright (c) 2005 Gael Varoquaux
# License: BSD Style

#TODO: - Extend unit tests
#      - Rework error reporting code to print the line where the error
#        happened
#      - Bug in the HTML pretty printer ? Line returns seem to big.
#      - Proper documentation
#      - Rework to API to allow better use from external programs
#      - Process some strings as literal-comments:
#               Strings starting a new line
#               Need an option to enable this
#               Maybe a strict mode, where the string has to be preceeded by
#               A line with a special comment
#      - Numbering in html + switch to remove numbering
#      - Inverse mode: process a rest file and execute some special blocks
#      - some output to make man pages ?
#      - Long, long term: use reportlab to avoid the dependencies on
#          LaTeX

# Standard library import
import sys

# Local imports
from main import main
from options import parse_options, option_parser

#------------------------------- Entry point ---------------------------------
def commandline_call():
    """ Entry point of the program when called from the command line
    """
    options, args = parse_options(sys.argv[1:])
    
    if not len(args)==1:
        if len(args)==0:
            option_parser.print_help()
        else:
            print  >> sys.stderr, "1 argument: input file"
        sys.exit(1)

    import time
    t1 = time.time()
    if args[0] == "-":
        pyfile = sys.stdin
    else:
        pyfile = open(args[0],"r")

    # Store the name of the input file for later use
    options.update({'infilename':args[0]})

    main(pyfile, overrides=options)
    # FIXME: wath about the options defined in the script: options.quiet
    if not 'quiet' in options:
        print >>sys.stderr, "Ran script in %.2fs" % (time.time() - t1)


if __name__ == '__main__':
    commandline_call()
