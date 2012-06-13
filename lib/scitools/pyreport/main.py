"""
The main code of pyreport.
"""
# Author: Gael Varoquaux  <gael dot varoquaux at normalesup dot org>
# Copyright (c) 2009 Gael Varoquaux
# License: BSD Style

# Standard library import
import sys
import re
import os
# to treat StdIn, StdOut as files:
import cStringIO
from docutils import core as docCore
from docutils import io as docIO
import copy
from traceback import format_exc
import __builtin__ # to override import ! :->
import platform
import tokenize
import token

# Local imports
from options import allowed_types, default_options, HAVE_PDFLATEX, \
        verbose_execute, silent_execute
import code_hasher
from python_parser import python2html

DEBUG = False
PYTHON_VERSION = int(''.join(str(s) for s in
                            platform.python_version_tuple()[:2]))

#------------------------ Initialisation and option parsing ------------------
def guess_names_and_types(options, allowed_types=allowed_types):
    """ This function tries to transform the current state of the options 
        to something useable. It tries to match user requests with the 
        different types possible.
    """
    # If we processing the stdin and no output has been chosen yet, output to
    # stdout
    if options.infilename == "-" and not options.outfilename :
        options.outfilename = "-"
    if not options.infilename == "-" and hasattr(options.infilename, "startswith"):
        options.infilename = os.path.abspath(options.infilename).replace(os.sep, '/')
        os.chdir(os.path.dirname(options.infilename))
    # If we are outputing to a stream rather than a file not every output
    # type is allowed
    if options.outfilename == "-" or options.outfile:
        for extension in set(("pdf", "ps", "eps", "dvi")):
                allowed_types.pop(extension,None)
    elif not options.outfilename:
        options.outfilename = os.path.splitext(options.infilename)[0]

    # Find types for figures and output:
    if options.outtype is None:
        if options.figuretype:
            for key in allowed_types.keys():
                if not options.figuretype in allowed_types[key]:
                    allowed_types.pop(key)
        # FIXME: pdf should not be hard coded, but this should be the first 
        # Along the list of allowed types.
        if "pdf" in  allowed_types:
            options.outtype = "pdf"
        elif "html" in allowed_types:
            options.outtype = "html"
        else:
            options.outtype = "rst"
        if options.verbose:
            print >> sys.stderr, "No output type specified, outputting to %s" \
                            % options.outtype

    if options.outtype in allowed_types:
        if options.figuretype is None:
            options.figuretype = allowed_types[options.outtype][0]
        elif not options.figuretype in allowed_types[options.outtype]:
            print >> sys.stderr, "Warning: %s figures requested incompatible with %s output" % (options.figuretype, options.outtype)
            options.figuretype = allowed_types[options.outtype][0]
            print >> sys.stderr, "Using %s figures" % options.figuretype
    else:
        print >> sys.stderr, "Error: unsupported output type requested"
        sys.exit(1)

    return options

def open_outfile(options):
    """ This make sure we have an output stream or file to write to.
        It is the last step setting up the options before compilation
    """
    # If no file-like object has been open yet, open one now.
    # Reminder: options.outfile should always be without the extention
    if options.outfilename == "-":
        options.outfile = sys.stdout
    elif not options.outfile:
        outfilename = "%s.%s" % (options.outfilename, options.outtype)
        if not options.quiet:
            print >> sys.stderr, "Outputing report to " + outfilename
        # Special case (ugly): binary files:
        if options.outtype in set(("pdf", "ps", "eps", "dvi")):
            outfilename = "%s.tex" % (options.outfilename)
        options.outfile = open(outfilename,"w")

#---------------------------- Subroutines ------------------------------------
if DEBUG:
    try:
        os.mkdir("DEBUG")
    except OSError:
        pass
    def DEBUGwrite(variable, filename):
        """ If DEBUG is enabled, writes variable to the file given by "filename"
        """
        debug_file = open("DEBUG" + os.sep + filename,'w')
        debug_file.write(variable.__repr__())
        debug_file.close()
else:
    def DEBUGwrite(variable, filename):
        pass

#-------------- Subroutines for python code hashing --------------------------
def first_block(options):
    """ This function creates the first block that is injected in the code to 
        get it started.
    """
    # Overload sys.argv
    new_argv = []
    if not options.infilename == None:
        new_argv = [options.infilename, ]
    if not options.arguments == None:
        new_argv += options.arguments.split(' ')
    codeblock = code_hasher.CodeBlock(0)
    codeblock.string = "\n\nimport sys\nsys.argv = %s\n" % new_argv
    return codeblock

#-------------- Subroutines for python code execution ------------------------
class SandBox(object):
    """ Implements a sandbox environement for executing code into.
    """
    
    # List holding the figures created by the call last executed
    current_figure_list = ()
    
    # List holding all the figures created through all the calls.
    total_figure_list = ()
    
    namespace = {}

    def __init__(self, myshow, options = default_options):
        """ This object acts as a memory for the code blocks. The
            reason we pass it pylab, is so that it can retrieve the figurelist
        """
        self.initial_options = options
        self.options = copy.copy(options)
        self.myshow = myshow
    
        self.__call__(first_block(options))
    
    def __call__(self, block):
        return self.executeblock(block)

    def executeblock(self, block):
        """ Excute a python command block, returns the stderr and the stdout 
        generated, and the list of figures generated."""
    
        block_text = "\n\n" + block.string
        line_number = block.start_row
        #self.options._update_loose(block.options)
        out_value = ""
    
        # This import should not be needed, but it works around a very
        # strange bug I encountered once.
        import cStringIO
        # create file-like string to capture output
        code_out = cStringIO.StringIO()
        code_err = cStringIO.StringIO()
   
        captured_exception = None
        # capture output and errors
        sys.stdout = code_out
        sys.stderr = code_err
        try:
            exec block_text in self.namespace
        except Exception, captured_exception:
            if isinstance(captured_exception, KeyboardInterrupt):
                raise captured_exception
            print >> sys.stderr, format_exc()      
        
        # restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
            
        out_value = code_out.getvalue()
        error_value = code_err.getvalue()
            
        code_out.close()
        code_err.close()

        if captured_exception: 
            print >> sys.stderr, "Error in executing script on block starting line ", line_number ,": " 
            print >> sys.stderr, error_value
        self.namespace = globals()
        self.namespace.update(locals())

        if out_value and not self.options.noecho:
            if self.options.outfilename == "-" :
                print >> sys.stderr, out_value
            else:
                print out_value
        if self.myshow:
            self.current_figure_list = self.myshow.figure_list[
                                        len(self.total_figure_list):]
            self.total_figure_list = self.myshow.figure_list

        #if self.options.silent:
        #    error_value = ""
            
        return (block.start_row, block.string, out_value, error_value, 
                                                self.current_figure_list)

# FIXME: Check the structure of the code doing the overloading, it may not be 
# optimal.

class MyShow(object):
    """ Factory for creating a function to replace the show command
        from either pylab or scitools.easyviz.
    """
    figure_list = ()
    
    figure_extension = "eps"

    use_easyviz = False

    def _set_options(self,options):
        if not options.outfilename in set(("-", None)):
            self.basename =  "%s_pyreport_" % os.path.splitext(
                        os.path.basename(options.infilename))[0]
        else:
            self.basename =  "_pyreport_"
        # XXX: Use pylab's pdf output
        #if options.figuretype == "pdf":
        #    self.figure_extension = "eps"
        #else:
        self.figure_extension = options.figuretype
        
    def __call__(self):
        figure_name = '%s%d.%s' % ( self.basename,
                len(self.figure_list), self.figure_extension )
        self.figure_list += (figure_name, )
        print "Here goes figure %s" % figure_name
        if self.use_easyviz:
            import scitools.easyviz
            scitools.easyviz.hardcopy(figure_name)
        else:
            import pylab
            pylab.savefig(figure_name)


myshow = MyShow()

class MyImport(object):
    """ Factory to create an __import__ call to override the builtin.
    """
    
    original_import = __import__
    
    def __init__(self, options):
        self.options = options
    
    
    def __call__(self, name, globals=None, locals=None, fromlist=None, 
                    **kwargs):
        if name == "pylab":
            return self.pylab_import(name, globals, locals, fromlist,
                        **kwargs)
        elif name == "matplotlib.pyplot":
            from pylab import *
            return self.pylab_import(name, globals, locals, fromlist,
                        **kwargs)
        elif name in ["scitools.easyviz", "scitools.std"]:
            myshow.use_easyviz = True
            return self.easyviz_import(name, globals, locals, fromlist,
                        **kwargs)
        return self.original_import(name, globals, locals, fromlist,
                        **kwargs)

    if PYTHON_VERSION >= 26:
        def __call__(self, name, globals=None, locals=None,
                        fromlist=None, level=-1):
            if name == "pylab":
                return self.pylab_import(name, globals, locals, fromlist,
                        level=level)
            elif name == "matplotlib.pyplot":
                from pylab import *
                return self.pylab_import(name, globals, locals, fromlist,
                        level=level)
            elif name in ["scitools.easyviz", "scitools.std"]:
                myshow.use_easyviz = True
                return self.easyviz_import(name, globals, locals, fromlist,
                        level=level)
            return self.original_import(name, globals, locals, fromlist,
                        level=level)
    
    
    def pylab_import(self, name, globals=None, locals=None,
                     fromlist=None, level=-1):
        matplotlib = self.original_import("matplotlib")
        matplotlib.interactive(False)
        # FIXME: Still no good solution to plot without X. The following
        # trick does not work well as all features have not been
        # implemented in the ps and gd backends.
        # Set the backend to just about anything that does not
        # display (althought using gd just doesn't do the trick
        ##if self.options.figuretype in set(("pdf", "ps", "eps")):
        ##    matplotlib.use('ps')
        ##else:
        ##    matplotlib.use('gd')
        imported = self.original_import(name, globals, locals, fromlist)
        imported.show = myshow
        return imported

    def easyviz_import(self, name, globals=None, locals=None,
                       fromlist=None, level=-1):
        scitools = self.original_import("scitools.easyviz")
        #scitools.easyviz.setp(interactive=False)
        imported = self.original_import(name, globals, locals, fromlist)
        if hasattr(imported, "show"):
            imported.show = myshow
        elif hasattr(imported, "std"):
            imported.std.show = myshow
        elif hasattr(imported, "easyviz"):
            imported.easyviz.show = myshow
        else:
            imported.show = myshow
        return imported

def execute_block_list(block_list, options=copy.copy(default_options)):
    """ Executes the list of statement in a sandbox. Returns a list of the
        results for each statement: 
        (line number, statement, stdout, stdin, figure_list)
    """
    if not options.noexecute:
        if not options.quiet :
            print >> sys.stderr, "Running python script %s:\n" % \
                                                        options.infilename
        # FIXME: I really have to have a close look at this code path. It
        # smells
        myshow._set_options(options)
        #__builtin__.__import__ = myimport
        __builtin__.__import__ = MyImport(options)
        
        execute_block = SandBox(myshow, options=options)

    else:
        execute_block = lambda block : [block.start_row, block.string, 
                                                None, None, ()] 

    output_list = map(execute_block, block_list)
  
    # python can have strange histerisis effect, with kwargs and passing by
    # reference. We need to reinitialise these to there defaults:
    execute_block.figure_list = ()
    return output_list
 

#-------------- Subroutines for formatting blocks hashing --------------------
def hash_block(block, options):
    """ Separate an answer block into comment blocks, input blocks, error 
        blocks and output blocks.

    >>> hash_block((1,'print "foo"',"foo",None,()),default_options)
    [['inputBlock', 'print "foo"', 2], ['outputBlock', 'foo', ()]]
    """
    output_list = py2commentblocks( block[1], block[0], options)
    lastindex = _last_input_block(output_list)
    out = output_list[:lastindex]
    if block[2]:
        out += [['outputBlock', block[2], block[4]], ]
    if block[3]:
        out += [['errorBlock', block[3]], ]
    out += output_list[lastindex:]
    return out


def shape_output_list(output_list, options):
    """ Transform the output_list from a simple capture of stdout, stderr...
        to a list of blocks that can be passed to the compiler.

    >>> shape_output_list([(1,'print "foo"',"foo",None,())], default_options)
    [['rstBlock', ''], ['inputBlock', 'print "foo"', 2], ['outputBlock', 'foo', ()]]
    """
    # FIXME: Where does this options comme from ? Looks like it has become 
    # global, maybe pyreport.options shouldn't be called like this to avoid
    # this kind of errors.
    output_list =  [ hash_block(block, options) for block in output_list ]
    # FIXME: We are going to need to find a better way of doing this !
    DEBUGwrite(output_list, 'output_list3')

    # Maybe the condense and the reduce should be the same operation.
    output_list = condense_output_list(output_list, options)

    DEBUGwrite( output_list, 'condensedoutputlist')

    output_list = map(check_rst_block, output_list)
    DEBUGwrite( output_list, 'checkedoutput_list')
    return output_list


def py2commentblocks(string, firstlinenum, options):
    r""" Hashes the given string into a list of code blocks, litteral comments 
        blocks and latex comments.

        >>> py2commentblocks("a\n#!b\n#c", 1, default_options)
        [['inputBlock', 'a\n', 2], ['textBlock', 'b\n'], ['commentBlock', '#c\n', 3]]
        >>> default_options._update_loose({'latexliterals': True})
        >>> py2commentblocks("a\n#$Latex\n", 1, default_options)
        [['inputBlock', 'a\n', 2], ['latexBlock', 'Latex\n']]
    """
    input_stream = cStringIO.StringIO(string)
    block_list = []
    pos = 0
    current_block = ""
    newline = True
    linenum = 0
    last_token = None
    for tokendesc in tokenize.generate_tokens(input_stream.readline):

        if PYTHON_VERSION >= 26:
            # As of 2.6, tokenize.generate_tokens() chops newlines off
            # then end of comments and returns them as NL tokens. This
            # confuses the logic of the rest of pyreport, so we gobble
            # NL following a comment.
            if last_token == tokenize.COMMENT and \
                    tokendesc[0] == tokenize.NL:
                last_token = tokendesc[0]
                continue
            else:
                last_token = tokendesc[0]

        tokentype = token.tok_name[tokendesc[0]]
        startpos = tokendesc[2][1]
        tokencontent = tokendesc[1]
        if tokendesc[2][0] > linenum:
            # We just started a new line
            tokencontent = startpos * " " + tokencontent
            newline = True
        elif startpos > pos :
            tokencontent = (startpos - pos) * " " + tokencontent
        pos = startpos + len(tokendesc[1])
        linenum = tokendesc[2][0]
        reallinenum = linenum + firstlinenum - 1
        if newline and tokentype == 'COMMENT' :
            if current_block:
                block_list += [ [ "inputBlock", current_block, reallinenum ], ]
            current_block = ""
            pos = 0
            lines = tokencontent.splitlines()
            lines = map(lambda z : z + "\n", lines[:])
            for line in lines:
                if line[0:3] == "#!/" and reallinenum == 1:
                    # This is a "#!/foobar on the first line, this 
                    # must be an executable call
                    block_list += [ ["inputBlock", line, reallinenum], ]
                elif line[0:3] == "#%s " % options.commentchar :
                    block_list += [ [ "textBlock", line[3:]], ]
                elif line[0:2] == "#%s" % options.commentchar :
                    block_list += [ ["textBlock", line[2:]], ]
                elif options.latexliterals and line[0:2] == "#$" :
                    block_list += [ ["latexBlock", line[2:]], ]
                else:
                    block_list += [ ["commentBlock", line, reallinenum], ]
        else:
            current_block += tokencontent
        newline = False
    if current_block :
        block_list += [ [ "inputBlock", current_block, reallinenum ], ]
    return block_list


def condense_output_list(output_list, options):
    """ Takes the "output_list", made of list of blocks of different 
        type and merges successiv blocks of the same type.

    >>> condense_output_list([[['inputBlock', 'a', 4]], 
    ...             [['inputBlock', "b", 2], ['outputBlock', 'c', ()]]],
    ...             default_options)
    [['textBlock', ''], ['inputBlock', 'ab', 4], ['outputBlock', 'c', ()]]
    """
    out_list = [['textBlock', ''], ]
    for blocks in output_list:
        for block in blocks:
            if block[0] == "commentBlock":
                block[0] = "inputBlock"
            if options.nocode and block[0] == "inputBlock":
                continue
            elif block[0] == out_list[-1][0]:
                out_list[-1][1] += block[1]
                if block[0] == 'outputBlock':
                    out_list[-1][2] += block[2]
                    out_list[-1][1] = re.sub(r"(\n)+", r"\n", out_list[-1][1])
            else:
                out_list += [block]
    return out_list


def _last_input_block(output_list):
    """ return the index of the last input block in the given list of blocks.
    """
    lastindex = 0
    for index, block in enumerate(output_list):
        if block[0] == "inputBlock":
            lastindex = index
    return lastindex + 1


#-------------- Subroutines for report output --------------------------------
def protect(string):
    r''' Protects all the "\" in a string by adding a second one before

    >>> protect(r'\foo \*')
    '\\\\foo \\\\*'
    '''
    return re.sub(r"\\", r"\\\\", string)


def safe_unlink(filename):
    """ Remove a file from the disk only if it exists, if not r=fails silently
    """
    if os.path.exists(filename):
        os.unlink(filename)



def tex2pdf(filename, options):
    """ Compiles a TeX file with pdfLaTeX (or LaTeX, if or dvi ps requested)
        and cleans up the mess afterwards
    """
    if options.verbose:
        execute = verbose_execute
    else:
        execute = silent_execute
    if not options.quiet :
        print >> sys.stderr, "Compiling document to "+options.outtype
    if options.outtype == "ps":
        execute("latex --interaction scrollmode %s.tex -output-directory=%s" %(filename, os.path.dirname(filename)))
        execute("dvips %s.dvi -o %s.ps" % (filename, filename) )
    elif options.outtype == "dvi":
        execute("latex --interaction scrollmode %s.tex " % filename)
    elif options.outtype == "eps":
        execute("latex --interaction scrollmode %s.tex -output-directory=%s" %(filename, os.path.dirname(filename)))
        execute("dvips -E %s.dvi -o %s.eps" % (filename, filename))
    elif options.outtype == "pdf":
        if HAVE_PDFLATEX:
            execute( "pdflatex --interaction scrollmode %s.tex -output-directory=%s" %(filename, os.path.dirname(filename)))
        else:
            execute("latex --interaction scrollmode %s.tex -output-directory=%s" %(filename, os.path.dirname(filename)))
            execute("dvips -E %s.dvi -o %s.eps" % (filename, filename))
            print "Doing pdf %s" % filename
            execute("epstopdf %s.eps" % filename)

    safe_unlink(filename+".tex")
    safe_unlink(filename+".log")
    safe_unlink(filename+".aux")
    safe_unlink(filename+".out")


def epstopdf(figure_name):
    """ Converts eps file generated by the script to a pdf file, using epstopdf
        with the right flags.
    """
    os.environ['GS_OPTIONS'] = "-dCompressPages=false -dAutoFilterColorImages=false -dDownsampleColorImages=false -dDownsampleColorImages=false -dColorImageResolution=1200 -dAutoFilterGrayImages=false -dGrayImageResolution=1200 -dDownsampleMonoImages=false -dMonoImageResolution=1200 -dColorImageFilter=/FlateEncode -dGrayImageFilter=/FlateEncode -dMonoImageFilter=/FlateEncode"
    os.environ['GS_OPTIONS'] = "-dUseFlatCompression=true -dPDFSETTINGS=/prepress -sColorImageFilter=FlateEncode -sGrayImageFilter=FlateEncode -dAutoFilterColorImages=false -dAutoFilterGrayImages=false -dEncodeColorImages=false -dEncodeGrayImages=false -dEncodeMonoImages=false"
    os.system("epstopdf --nocompress " + figure_name)
    #safe_unlink(figure_name)
    return (os.path.splitext(figure_name)[0]+".pdf")


def rst2latex(rst_string):
    """ Calls docutils' engine to convert a rst string to a LaTeX file.
    """
    overrides = {'output_encoding': 'latin1', 'initial_header_level': 0}
    tex_string = docCore.publish_string(
                source=rst_string, 
                writer_name='latex', settings_overrides=overrides)
    return tex_string


def rst2html(rst_string):
    """ Calls docutils' engine to convert a rst string to an html file.
    """
    overrides = {'output_encoding': 'latin1', 'initial_header_level': 1}
    html_string = docCore.publish_string(
                source=rst_string, 
                writer_name='html', settings_overrides=overrides)
    return html_string

def check_rst_block(block):
    """ Check if every textBlock can be compiled as Rst. Change it to 
        textBlock if so.

    >>> check_rst_block(["textBlock","foo"])
    ['rstBlock', 'foo']
    >>> check_rst_block(["textBlock","**foo"])
    ['textBlock', '**foo']
    """
    publisher = docCore.Publisher( source_class = docIO.StringInput,
                        destination_class = docIO.StringOutput )
    publisher.set_components('standalone', 'restructuredtext', 'pseudoxml')
    publisher.process_programmatic_settings(None, None, None)
    if block[0] == "textBlock":
        publisher.set_source(block[1], None)
        compiled_rst = publisher.reader.read(publisher.source,
                                publisher.parser, publisher.settings)
        if compiled_rst.parse_messages:
            # FIXME: It would be nice to add the line number where the error 
            # happened
            print >> sys.stderr, """Error reading rst on literate comment line 
falling back to plain text"""
        else:
            block[0] = "rstBlock"
    return block


class ReportCompiler(object):
    """ Compiler obejct that contains all the data and the call to produce 
        the final document from the output block list
    """

    preamble = ".. header:: Compiled with pyreport\n"
    #preamble = ""
   
    inputBlocktpl = r"""
::

    %(textBlock)s

"""
    latexBlocktpl = r"""

.. raw:: LaTeX

    %s
    
"""
    errorBlocktpl = r"""

.. error::

  ::

    %s
    
"""

    outputBlocktpl = r"""
.. class:: answer

  ::

    %s
    
"""

    figuretpl = r"""
.. image:: %s.eps

"""


    textBlocktpl = r"""::

    %s
"""

    figure_list = ()

    indent = True

    def __init__(self, options):
        self.empty_listing = re.compile(re.escape(self.outputBlocktpl[:-5] % ''), re.DOTALL)

    def add_indent(self, string):
        if self.indent:
            return string.replace("\n","\n    ")
        else:
            return string

    def block2rst(self, block):
        """given a output block, returns a rst string
        """
        # FIXME: Do this with a dictionary. Actually, the objects dictionary
        # It self, just name the attributes and methods well
        if block[0] == "inputBlock":
            if callable(self.inputBlocktpl):
                rst_text = self.inputBlocktpl(block[1], block[2])
            else:
                data = {'linenumber' : block[2],
                        'textBlock' : self.add_indent(block[1]),
                        }
                rst_text = self.inputBlocktpl % data
                rst_text = re.sub(self.empty_listing ,"" , rst_text)
        elif block[0] == "errorBlock":
            rst_text = self.errorBlocktpl % (self.add_indent(block[1]))
        elif block[0] == "latexBlock":
            rst_text = self.latexBlocktpl % (self.add_indent(block[1]))
        elif block[0] == "rstBlock":
            rst_text = "\n" + block[1] + "\n" 
        elif block[0] == "textBlock":
            rst_text = self.textBlocktpl % (self.add_indent(block[1])) 
        elif block[0] == "outputBlock":
            rst_text = self.outputBlocktpl % ((block[1]).replace("\n","\n    "))
            for figure_name in block[2]:
                rst_text = re.sub("Here goes figure " + re.escape(figure_name),
                        self.figuretpl % (os.path.splitext(figure_name)[0]),
                        rst_text)
            rst_text = re.sub(self.empty_listing, "", rst_text)
            self.figure_list += block[2]
        return rst_text

    def blocks2rst_string( self, output_list ):
        """ given a list of output blocks, returns a rst string ready to 
        be compiled"""
        output_list = map( self.block2rst, output_list)
        rst_string = "".join(output_list)
        # To make the ouput more compact and readable:
        rst_string = re.sub(r"\n\n(\n)+","\n\n",rst_string)
        DEBUGwrite( rst_string, "pyreport.rst")
        return rst_string

    def compile( self, output_list, fileobject, options):
        """ Compiles the output_list to the rst file given the filename"""
        rst_string = self.preamble + self.blocks2rst_string(output_list)
        print >>fileobject, rst_string


class TracCompiler(ReportCompiler):
    def inputBlocktpl(self, pythonstring, startlinnum):
        if re.search(r'\S', pythonstring):
            return r"""
    .. code-block:: python

        %s

""" % pythonstring.replace("\n","\n        ")
        else:
            return "\n"


class MoinCompiler(ReportCompiler):
    figuretpl = r"""

inline:%s

"""
    textBlocktpl = """
%s
"""
    inputBlocktpl = r"""

{{{#!python
%(textBlock)s
}}}
"""
    rstBlocktpl = r"""
{{{#!rst
%s
}}}
"""
    indent = False
    preamble = "## Compiled with pyreport"

    def __init__(self):
        self.empty_listing = re.compile( "("
            + re.escape(self.outputBlocktpl[:-5] % '')
            + ")|("
            + re.escape(self.inputBlocktpl % {"textBlock" : "\n\n"})
            + ")"
            , re.DOTALL)


class HtmlCompiler(ReportCompiler):
    figuretpl = r"""

.. image:: %s.png
"""

    textBlocktpl = r"""
.. class:: text

  ::

    %s
    
"""

    def inputBlocktpl(self, pythonstring, startlinnum):
        """ Given a python string returns a raw html rst insert with the pretty 
            printing implemented in html.
        """
        return r"""
.. raw:: html

    %s

""" % (python2html(pythonstring)).replace("\n","\n    ")


    def compile(self, output_list, fileobject, options):
        """ Compiles the output_list to the html file given the filename
        """
        html_string = rst2html(self.blocks2rst_string(output_list))
        cssextra = r"""
        pre.answer {
            margin-bottom: 1px ;
            margin-top: 1px ;
            margin-left: 6ex ;
            font-family: serif ;
            font-size: 100% ;
            background-color: #cccccc ; 
        }
        pre.text {
        }
        .pysrc {
            font-weight: normal;
            /*background-color: #eeece0;*/
            background-color: #eef2f7;
            background-image: url("yellow-white.png");
            background-position:  right;
            background-repeat: repeat-y;
            border: 1px solid;
            border-color: #999999;
            margin: 20px;
            padding:10px 10px 10px 20px;
            font-size: smaller;
            white-space: pre ;
        }

        .pykeyword {
            font-weight: bold;
            color: #262668 ;
        }
        .pycomment { color: #007600; }
        /*.pystring { color: #ad0000; }*/
        .pystring { color: #0000bb; }
        .pynumber { color:purple; }
        .pyoperator { color:purple; font-weight: bold; }
        .pytext { color:black; }
        .pyerror { font-weight: bold; color: red; }

        .bracket {
            height: 4px;
            width: 10px;
        }
        .bracketfill {
            width: 10px;
            background-color: #FFFFFF; 
        }
        .collapse {
            border: 0px; 
            background-color: #99CCFF; 
            padding: 0px;
            font-size: xx-small;
            text-align: right;
        }
        </style>

<!-- http://www.randomsnippets.com/2008/02/12/how-to-hide-and-show-your-div/ -->
<script language="javascript"> 
function toggle_hidden(showHideDiv, switchTextDiv) {
    var ele = document.getElementById(showHideDiv);
    var eleinv = document.getElementById(showHideDiv+'inv');
    var text = document.getElementById(switchTextDiv);
    if(ele.style.display == "block") {
        ele.style.display = "none";
        eleinv.style.display = "block";
        text.innerHTML = "<small>+</small>";
        }
    else {
        ele.style.display = "block";
        eleinv.style.display = "none";
        text.innerHTML = " <small>&nbsp;</small>" ;
        }
    } 

function hide_all(contentDiv,controlDiv){
    var text = document.getElementById('hideall');
    if (contentDiv.constructor == Array) {
        for(i=0; i < contentDiv.length; i++) {
        toggle_hidden(contentDiv[i], controlDiv[i]);
        }
    }
    else {
        toggle_hidden(contentDiv, controlDiv);
    }

}
</script>
        """
        html_string = re.sub(r"</style>", protect(cssextra), html_string)
        hideall = r"""<body><div id="hideall" class="collapse"
            onclick="hide_all("""
        hideall += str( ['pysrc%d' % x for x in range(python2html.pysrcid)])
        hideall += ","
        hideall += str( ['toggle%d' % x for x in range(python2html.pysrcid)])
        hideall += r""")">toggle all code blocks</div><br>
        """
        html_string = re.sub(r"<body>", protect(hideall), html_string)
        print >>fileobject, html_string


class TexCompiler(ReportCompiler):
    empty_listing = re.compile(
            r"""\\begin\{lstlisting\}\{\}\s*\\end\{lstlisting\}""", re.DOTALL)
    
    inputBlocktpl = r"""
    
.. raw:: LaTeX

    {\inputBlocksize
    \lstset{escapebegin={\color{darkgreen}},backgroundcolor=\color{lightblue},fillcolor=\color{lightblue},numbers=left,name=pythoncode,firstnumber=%(linenumber)d,xleftmargin=0pt,fillcolor=\color{white},frame=single,fillcolor=\color{lightblue},rulecolor=\color{lightgrey},basicstyle=\ttfamily\inputBlocksize}
    \begin{lstlisting}{}
    %(textBlock)s
    \end{lstlisting}
    }
    
    
"""
    outputBlocktpl =  r"""
.. raw:: LaTeX

    \lstset{backgroundcolor=,numbers=none,name=answer,xleftmargin=3ex,frame=none}
    \begin{lstlisting}{}
    %s
    \end{lstlisting}
    
"""
    errorBlocktpl = r"""

.. raw:: LaTeX


    {\color{red}{\bfseries Error: }
    \begin{verbatim}%s\end{verbatim}}
    
"""
    figuretpl = r'''
    \end{lstlisting}
    \\centerline{\includegraphics[scale=0.5]{%s}}
    \\begin{lstlisting}{}'''
    
    def __init__(self, options):
        self.preamble = r"""
    \usepackage{listings}
    \usepackage{color}
    \usepackage{graphicx}

    \definecolor{darkgreen}{cmyk}{0.7, 0, 1, 0.5}
    \definecolor{darkblue}{cmyk}{1, 0.8, 0, 0}
    \definecolor{lightblue}{cmyk}{0.05,0,0,0.05}
    \definecolor{grey}{cmyk}{0.1,0.1,0.1,1}
    \definecolor{lightgrey}{cmyk}{0,0,0,0.5}
    \definecolor{purple}{cmyk}{0.8,1,0,0}

    \makeatletter
        \let\@oddfoot\@empty\let\@evenfoot\@empty
        \def\@evenhead{\thepage\hfil\slshape\leftmark
                        {\rule[-0.11cm]{-\textwidth}{0.03cm}
                        \rule[-0.11cm]{\textwidth}{0.03cm}}}
        \def\@oddhead{{\slshape\rightmark}\hfil\thepage
                        {\rule[-0.11cm]{-\textwidth}{0.03cm}
                        \rule[-0.11cm]{\textwidth}{0.03cm}}}
        \let\@mkboth\markboth
        \markright{{\bf %s }\hskip 3em  \today}
        \def\maketitle{
            \centerline{\Large\bfseries\@title}
            \bigskip
        }
    \makeatother


    \lstset{language=python,
            extendedchars=true,
            aboveskip = 0.5ex,
            belowskip = 0.6ex,
            basicstyle=\ttfamily,
            keywordstyle=\sffamily\bfseries,
            identifierstyle=\sffamily,
            commentstyle=\slshape\color{darkgreen},
            stringstyle=\rmfamily\color{blue},
            showstringspaces=false,
            tabsize=4,
            breaklines=true,
            numberstyle=\footnotesize\color{grey},
            classoffset=1,
            morekeywords={eyes,zeros,zeros_like,ones,ones_like,array,rand,indentity,mat,vander},keywordstyle=\color{darkblue},
            classoffset=2,
            otherkeywords={[,],=,:},keywordstyle=\color{purple}\bfseries,
            classoffset=0""" % ( re.sub( "_", r'\\_', options.infilename) ) + options.latexescapes * r""",
            mathescape=true""" +"""
            }
    """

        if options.nocode:
            latex_column_sep = r"""
    \setlength\columnseprule{0.4pt}
    """
        else:
            latex_column_sep = ""


        latex_doublepage = r"""
    \usepackage[landscape,left=1.5cm,right=1.1cm,top=1.8cm,bottom=1.2cm]{geometry}
    \usepackage{multicol}
    \def\inputBlocksize{\small}
    \makeatletter
        \renewcommand\normalsize{%
        \@setfontsize\normalsize\@ixpt\@xipt%
        \abovedisplayskip 8\p@ \@plus4\p@ \@minus4\p@
        \abovedisplayshortskip \z@ \@plus3\p@
        \belowdisplayshortskip 5\p@ \@plus3\p@ \@minus3\p@
        \belowdisplayskip \abovedisplayskip
        \let\@listi\@listI}
        \normalsize
        \renewcommand\small{%
        \@setfontsize\small\@viiipt\@ixpt%
        \abovedisplayskip 5\p@ \@plus2\p@ \@minus2\p@
        \abovedisplayshortskip \z@ \@plus1\p@
        \belowdisplayshortskip 3\p@ \@plus\p@ \@minus2\p@
        \def\@listi{\leftmargin\leftmargini
                    \topsep 3\p@ \@plus\p@ \@minus\p@
                    \parsep 2\p@ \@plus\p@ \@minus\p@
                    \itemsep \parsep}%
        \belowdisplayskip \abovedisplayskip
        }
        \renewcommand\footnotesize{%
        \@setfontsize\footnotesize\@viipt\@viiipt
        \abovedisplayskip 4\p@ \@plus2\p@ \@minus2\p@
        \abovedisplayshortskip \z@ \@plus1\p@
        \belowdisplayshortskip 2.5\p@ \@plus\p@ \@minus\p@
        \def\@listi{\leftmargin\leftmargini
                    \topsep 3\p@ \@plus\p@ \@minus\p@
                    \parsep 2\p@ \@plus\p@ \@minus\p@
                    \itemsep \parsep}%
        \belowdisplayskip \abovedisplayskip
        }
        \renewcommand\scriptsize{\@setfontsize\scriptsize\@vipt\@viipt}
        \renewcommand\tiny{\@setfontsize\tiny\@vpt\@vipt}
        \renewcommand\large{\@setfontsize\large\@xpt\@xiipt}
        \renewcommand\Large{\@setfontsize\Large\@xipt{13}}
        \renewcommand\LARGE{\@setfontsize\LARGE\@xiipt{14}}
        \renewcommand\huge{\@setfontsize\huge\@xivpt{18}}
        \renewcommand\Huge{\@setfontsize\Huge\@xviipt{22}}
        \setlength\parindent{14pt}
        \setlength\smallskipamount{3\p@ \@plus 1\p@ \@minus 1\p@}
        \setlength\medskipamount{6\p@ \@plus 2\p@ \@minus 2\p@}
        \setlength\bigskipamount{12\p@ \@plus 4\p@ \@minus 4\p@}
        \setlength\headheight{12\p@}
        \setlength\headsep   {25\p@}
        \setlength\topskip   {9\p@}
        \setlength\footskip{30\p@}
        \setlength\maxdepth{.5\topskip}
    \makeatother

    \AtBeginDocument{
    \setlength\columnsep{1.1cm}
    """ + latex_column_sep + r"""
    \begin{multicols*}{2}
    \small}
    \AtEndDocument{\end{multicols*}}
    """

        if options.double:
            self.preamble += latex_doublepage
        else:
            self.preamble += r"""\usepackage[top=2.1cm,bottom=2.1cm,left=2cm,right=2cm]{geometry}
    \def\inputBlocksize{\normalsize}
        """

        if options.outtype == "tex":
            self.compile = self.compile2tex
        else:
            self.compile = self.compile2pdf


    def compile2tex(self, output_list, fileobject, options):
        """ Compiles the output_list to the tex file given the filename
        """
        tex_string = rst2latex(self.blocks2rst_string(output_list))
        tex_string = re.sub(r"\\begin{document}", 
                        protect(self.preamble) + r"\\begin{document}", tex_string)
        tex_string = re.sub(self.empty_listing, "", tex_string)
        # XXX: no need to use epstopdf: we are now using MPL'pdf output
        #if options.figuretype == "pdf":
        #    if options.verbose:
        #        print >> sys.stderr, "Compiling figures"
        #    self.figure_list = map(epstopdf, self.figure_list)
        print >>fileobject, tex_string


    def compile2pdf(self, output_list, fileobject, options):
        """ Compiles the output_list to the tex file given the filename
        """
        self.compile2tex( output_list, fileobject, options)
        fileobject.close()
        tex2pdf(options.outfilename, options)
        map(safe_unlink, self.figure_list)
        self.figure_list = ()


compilers = {
    'html': HtmlCompiler,
    'rst' : ReportCompiler,
    'moin': MoinCompiler,
    'trac': TracCompiler,
}

#------------------------------- Entry point ---------------------------------

def main(pyfile, overrides={}, initial_options=copy.copy(default_options), 
                global_allowed_types=allowed_types):
    """ Process the stream (file or stringIO object) given by pyfile, execute
        it, and compile a report at the end.
        
        Default options that can be overriden by the script should be given 
        through the initial_options objects (that can by created by using the 
        pyreport.options object, and its method _update_careful).

        Overrides that impose options can be given through the overrides 
        dictionary. It takes the same keys and values than the initial_options 
        object and is the recommended way to specify output type,...

        To retrive the report in the calling program, just pass a StringIO 
        object as the outfile, in the overides.

        example:
            pyreport.main(StringIO_object, overrides={'outtype':'html',
                    'outfile':StringIO_object, 'silent':True,
                    'infilename':'Report generated by me'}
    """
    # Beware of passing by reference. We need to make copies of options as
    # Much as possible to avoid histerisis effects:
    options = copy.copy(initial_options)
    allowed_types = global_allowed_types.copy()

    # Options used to start the parsing:
    parsing_options = copy.copy(options)
    parsing_options._update_loose(overrides)
    # Slice the input file into code blocks
    block_list = code_hasher.iterblocks(pyfile)
    # FIXME: Need to deal with the script's options
    script_options = {}

    # Override the options given by the script by the command line switch
    script_options.update(overrides)
    # And now merge this to the default options (! this a not a dict)
    options._update_loose(script_options)
    options = guess_names_and_types(options, allowed_types=allowed_types)

    # Process the blocks
    output_list = execute_block_list(block_list, options)
    DEBUGwrite( output_list, 'output_list')

    open_outfile(options)
   
    output_list = shape_output_list(output_list, options)
    
    global compilers
    compiler = compilers.get(options.outtype, TexCompiler)(options)
    compiler.compile( output_list, options.outfile, options)

