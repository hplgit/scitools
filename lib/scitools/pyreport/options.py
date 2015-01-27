"""
This files is where all the options-related code is.
"""

# Standard library imports
import copy
import os
from optparse import OptionParser
import sys

# Local imports
from version import __version__

def silent_execute( string, return_stderr=True):
    """ Execute the given shell adding '> /dev/null' if under a posix OS 
        and '> nul' under windows.
    """
    if sys.platform.startswith('win') or return_stderr:
        return os.system(string + " > " + os.devnull)
    else:
        return os.system('%s >%s 2>%s' % (string, os.devnull,
                                                    os.devnull))


def verbose_execute(string):
    """ Execute getting errors """
    if os.system(string) != 0:
        raise RuntimeError('Unable to execute %r' % string)

# A dictionary describing the supported output type (as the keys of the
# dictionnary) and the figure type allowed for each.
allowed_types = {
        "html": ("png", "jpg") ,
        "rst" : ("png", "pdf", "ps", "jpg"), 
        "moin": ("png", "jpg") ,
        "trac" : ("png", "pdf", "ps", "jpg"), 
}

# Find out what output type we can provide (do we have latex ? epstopdf ?)
# FIXME: Have a look at mpl to see how they do this.
if not silent_execute("latex --help"):
    allowed_types.update({
        "tex" : ("pdf", "eps", "ps"),
        "dvi" : ("eps",),
        "ps"  : ("eps",),
        "eps" : ("eps",),
    })
    # Why the hell does epstopdf return 65280 !!
    if  silent_execute("epstopdf --help", return_stderr=False) in (0, 65280):
        allowed_types.update({
            "pdf" : ("pdf",),
            "tex" : ("pdf", "eps","ps"),
        })

if not silent_execute("pdflatex --help"):
    HAVE_PDFLATEX = True
else:
    HAVE_PDFLATEX = False

# Build a parser object
usage = """usage: %prog [options] pythonfile

Processes a python script and pretty prints the results using LateX. If 
the script uses "show()" commands (from pylab or scitools.easyviz) they
are caught by %prog and the resulting graphs are inserted in the output pdf.
Comments lines starting with "#!" are interprated as rst lines
and pretty printed accordingly in the pdf.
    By Gael Varoquaux"""

# Defaults are put to None and False in order to be able to track the changes.
option_parser = OptionParser(usage=usage, version="%prog " +__version__ )

option_parser.add_option("-o", "--outfile", dest="outfilename",
                help="write report to FILE", metavar="FILE")
option_parser.add_option("-x", "--noexecute",
                action="store_true", dest="noexecute", default=False,
                help="do not run the code, just extract the literate comments")
option_parser.add_option("-n", "--nocode",
                dest="nocode", action="store_true", default=False,
                help="do not display the source code")
option_parser.add_option("-d", "--double",
                dest="double", action="store_true", default=False,
                help="compile to two columns per page "
                     "(only for pdf or tex output)")
option_parser.add_option("-t", "--type", metavar="TYPE",
                action="store", type="string", dest="outtype",
                default=None,
                help="output to TYPE, TYPE can be " + 
                                        ", ".join(allowed_types.keys()))
option_parser.add_option("-f", "--figuretype", metavar="TYPE",
                action="store", type="string", dest="figuretype",
                default=None,
                help="output figure type TYPE  (TYPE can be of %s depending on report output type)" 
                % (", ".join(reduce(lambda x, y : set(x).union(y) , allowed_types.values()) )) )
option_parser.add_option("-c", "--commentchar",
                action="store", dest="commentchar", default="!",
                metavar="CHAR",
                help='literate comments start with "#CHAR" ')
option_parser.add_option("-l", "--latexliterals",
                action="store_true", dest="latexliterals",
                default=False,
                help='allow LaTeX literal comment lines starting with "#$" ')
option_parser.add_option("-e", "--latexescapes",
                action="store_true", dest="latexescapes",
                default=False,
                help='allow LaTeX math mode escape in code wih dollar signs ')
option_parser.add_option("-p", "--nopyreport",
                action="store_true", dest="nopyreport", default=False,
                help="disallow the use of #pyreport lines in the processed "
                     "file to specify options")
option_parser.add_option("-q", "--quiet",
                action="store_true", dest="quiet", default=False,
                help="don't print status messages to stderr")
option_parser.add_option("-v", "--verbose",
                action="store_true", dest="verbose", default=False,
                help="print all the message, including tex messages")
option_parser.add_option("-s", "--silent",
                dest="silent",action="store_true",
                default=False,
                help="""Suppress the display of warning and errors in the report""")
option_parser.add_option( "--noecho",
                dest="noecho",action="store_true",
                default=False,
                help="""Turns off the echoing of the output of the script on the standard out""")
option_parser.add_option("-a", "--arguments",
                action="store", dest="arguments",
                default=None, type="string", metavar="ARGS",
                help='pass the arguments "ARGS" to the script')

# Create default options
default_options, _not_used = option_parser.parse_args(args =[])
default_options._update_loose({
                                   'infilename': None,
                                   'outfile': None,
                               })

def parse_options(arguments, initial_options=copy.copy(default_options), 
                                    allowed_types=allowed_types):
    """ Parse options in the arguments list given.
        Return a dictionary containing all the options different specified,
        and only these, and the arguments.
        Returns outfilename without the extension ! (important)

    >>> parse_options(['-o','foo.ps','-s',])
    ({'outfilename': 'foo', 'outtype': 'ps', 'silent': True}, [])
    """
    (options, args) = option_parser.parse_args(args=arguments)
    if (options.outtype == None and 
            options.outfilename and 
            '.' in options.outfilename) :
        basename, extension = os.path.splitext(options.outfilename)
        if extension[1:] in allowed_types:
            options.outtype = extension[1:]
            options.outfilename = basename
    options_dict = options.__dict__
    initial_options_dict = initial_options.__dict__
    
    return diff_dict(options_dict, initial_options_dict), args

def diff_dict(dict1, dict2):
    """ Returns a dictionary with all the elements of dict1 that are not in
        dict 2.

    >>> diff_dict({1:2, 3:4}, {1:3, 3:4, 2:4})
    {1: 2}
    """
    return_dict = {}
    for key in dict1:
        if key in dict2:
            if not dict1[key] == dict2[key]:
                return_dict[key] = dict1[key]
        else:
            return_dict[key] = dict1[key]
    return return_dict



