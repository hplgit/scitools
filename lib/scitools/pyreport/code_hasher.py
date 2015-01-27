"""
This module provides a CodeHasher object that groups raw code lines in
full code blocks ready for execution.
"""

import token
import tokenize
import re
import StringIO
import platform

from options import parse_options

PYTHON_VERSION = int(''.join(str(s) for s in 
                            platform.python_version_tuple()[:2]))

def xreadlines(s):
    """ Helper function to use a string in the code hasher:
    blocks = iterblock(xreadlines('1\n2\n\n3'))
    """
    if  s and not s[-1]=="\n":
        s += "\n"
    return (line for line in StringIO.StringIO(s))


##############################################################################
class Token(object):
    """ A token object"""

    def __init__(self, token_desc):
        """ Builds a token object from the output of
            tokenize.generate_tokens"""
        self.type = token.tok_name[token_desc[0]]
        self.content = token_desc[1]
        self.start_row = token_desc[2][0]
        self.start_col = token_desc[2][1]
        self.end_row = token_desc[3][0]
        self.end_col = token_desc[3][1]

    def __repr__(self):
        return str((self.type, self.content))


##############################################################################
class CodeLine(object):
    """ An object representing a full logical line of code """
    string = ""
    open_symbols = {'{':0, '(':0, '[':0}
    closing_symbols = {'}':'{', ')':'(', ']':'['} 
    brakets_balanced = True
    end_col = 0
    last_token_type = ""
    complete = False
    options = {}

    def __init__(self, start_row):
        self.start_row = start_row
        self.end_row = start_row
    
    def append(self, token):
        """ Appends a token to the line while keeping the integrity of
            the line, and checking if the logical line is complete.
        """
        # The token content does not include whitespace, so we need to pad it
        # adequately
        token_started_new_line = False
        if token.start_row > self.end_row:
            self.end_col = 0
            token_started_new_line = True
        self.string += (token.start_col - self.end_col) * " " + token.content
        self.end_row = token.end_row
        self.end_col = token.end_col
        self.last_token_type = token.type

        # Keep count of the open and closed brakets.
        if token.type == 'OP':
            if token.content in self.open_symbols:
                self.open_symbols[token.content] += 1
            elif token.content in self.closing_symbols:
                self.open_symbols[self.closing_symbols[token.content]] += -1
            self.brakets_balanced = ( self.open_symbols.values() == [0, 0, 0] ) 
        
        self.complete = ( self.brakets_balanced 
                          and ( token.type in ('NEWLINE', 'ENDMARKER')
                                or ( token_started_new_line
                                      and token.type == 'COMMENT' )
                              )
                        )
        if ( token.type == 'COMMENT' 
                    and token_started_new_line 
                    and token.content[:10] == "#pyreport " ):
            self.options.update(parse_options(self.string[10:].split(" "))[0])

    def isnewblock(self):
        """ This functions checks if the code line start a new block.
        """
        # First get read of the leading empty lines:
        string = re.sub(r"\A([\t ]*\n)*", "", self.string)
        if re.match(r"elif|else|finally|except| |\t", string):
            return False
        else:
            return True        

    def __repr__(self):
        return('<CodeLine object, id %i, line %i, %s>'
                    % (id(self), self.start_row, repr(self.string) ) )


##############################################################################
class CodeBlock(object):
    """ Object that represents a full executable block """
    string = ""
    options = {}

    def __init__(self, start_row):
        self.start_row = start_row
        self.end_row = start_row

    def append(self, codeline):
        self.string += codeline.string
        self.options.update(codeline.options)

    def __repr__(self):
        return('<CodeBlock object, id %i, line %i, options %s\n%s>'
                    % (id(self), self.start_row, 
                            repr(self.options), self.string ) )


##############################################################################
class CodeHasher(object):
    """ Implements a object that transforms an iterator of raw code lines
        in an iterator of code blocks.

        Input:
            self.xreadlines: iterator to raw lines of code, such as 
                                 file.xreadlines()

        Output: Generators :
            self.itercodeblocks
            self.itercodelines
            self.itertokens
    """
    options = {}

    def __init__(self, xreadlines):
        """ The constructor takes as an argument an iterator on lines such 
            as the xreadline method of a file, or what is returned by the 
            xreadline function of this module.
        """
        self.xreadlines = xreadlines

    def next_line_generator(self):
        return self.xreadlines.next().expandtabs()

    def itercodeblocks(self):
        """ Returns a generator on the blocks of this code.
        """
        codeblock = CodeBlock(0)
        last_line_has_decorator = False
        for codeline in self.itercodelines():            
            if codeline.isnewblock() and not last_line_has_decorator :
                if codeblock.string:
                    self.options.update(codeblock.options)
                    codeblock.options.update(self.options)
                    yield codeblock
                codeblock = CodeBlock(codeline.start_row)
                codeblock.append(codeline)
                line_start = codeline.string.lstrip('\n')
                if line_start and line_start[0] == '@':
                        last_line_has_decorator = True
                        continue
# FIXME: I don't understand the purpose of this code. Until I don't have
# a test case that fail, I leave it commented out.
#                line_end = codeline.string.rstrip(" \n")
#                if line_end and line_end == ':' : 
#                    if codeblock.string:
#                        self.options.update(codeblock.options)
#                        codeblock.options.update(self.options)
#                        yield codeblock
#                    codeblock = CodeBlock(codeline.start_row)
            else:
                codeblock.append(codeline)
            last_line_has_decorator = False
        else:
            self.options.update(codeblock.options)
            codeblock.options.update(self.options)
            yield codeblock

    def itercodelines(self):
        """ Returns a generator on the logical lines of this code.
        """
        codeline = CodeLine(0)
        for token in self.itertokens():
            codeline.append(token)
            if codeline.complete:
                codeline.string = '\n'.join(s.rstrip(' ') 
                                    for s in codeline.string.split('\n'))
                yield codeline
                codeline = CodeLine(codeline.end_row + 1)
        if codeline.string:
            codeline.string = '\n'.join(s.rstrip(' ') 
                                    for s in codeline.string.split('\n'))
            yield codeline

    def itertokens(self):
        """ Returns a generator on the tokens of this code.
        """
        last_token = None
        for token_desc in tokenize.generate_tokens(self.next_line_generator):

            if PYTHON_VERSION < 26:
                yield Token(token_desc)
            else:
                # As of 2.6, tokenize.generate_tokens() chops newlines off
                # then end of comments and returns them as NL tokens. This
                # confuses the logic of the rest of pyreport, so we append
                # missing \n to COMMENT tokens, and gobble NL following a
                # comment.
                if token_desc[0] == tokenize.NL and \
                        last_token == tokenize.COMMENT:
                    last_token = token_desc[0]
                    continue
                else:
                    if token_desc[0] == tokenize.COMMENT \
                            and token_desc[1][-1] != '\n':
                        new_td = (token_desc[0], token_desc[1]+'\n', 
                                  token_desc[2], token_desc[3], token_desc[4])
                        token_desc = new_td

                    last_token = token_desc[0]
                    yield Token(token_desc)


iterblocks = lambda xreadlines: CodeHasher(xreadlines).itercodeblocks()



