"""
Python synthax higlighting

Borrowed from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52298
"""

# Original copyright : 2001 by Juergen Hermann <jh@web.de>
import cgi, cStringIO, keyword, token, tokenize

class PythonParser:
    """ Send colored python source.
    """

    _KEYWORD = token.NT_OFFSET + 1
    _TEXT    = token.NT_OFFSET + 2

    def __init__(self):
        """ Store the source text.
        """
        self._tags = {
            token.NUMBER: 'pynumber',
            token.OP: 'pyoperator',
            token.STRING: 'pystring',
            tokenize.COMMENT: 'pycomment',
            tokenize.ERRORTOKEN: 'pyerror',
            self._KEYWORD: 'pykeyword',
            self._TEXT: 'pytext',
        }
        self.pysrcid = 0;


    def __call__(self, raw):
        """ Parse and send the colored source.
        """
        self.out = cStringIO.StringIO()
        self.raw = raw.expandtabs().strip()
        # store line offsets in self.lines
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = self.raw.find('\n', pos) + 1
            if not pos: break
            self.lines.append(pos)
        self.lines.append(len(self.raw))
        #
        # parse the source and write it
        self.pos = 0
        text = cStringIO.StringIO(self.raw)
        self.out.write("<table width=100% cellpadding=0 cellspacing=0 " +
                     """onclick="toggle_hidden('pysrc%d','toggle%d');"><tr>
                        <td rowspan="3"> """ % (self.pysrcid, self.pysrcid) )
        self.out.write("""<div class="pysrc" id="pysrc%dinv" style="display:
                       none">...</div>"""% self.pysrcid)
        self.out.write('<div class="pysrc" id="pysrc%d" style="display: block ">'% self.pysrcid)

        try:
            tokenize.tokenize(text.readline, self.format)
        except tokenize.TokenError, ex:
            msg = ex[0]
            line = ex[1][0]
            print >> self.out, ("<h3>ERROR: %s</h3>%s" %
                (msg, self.raw[self.lines[line]:]))
        self.out.write('</div>')
        self.out.write('''
                       </td> 
                       <td colspan="2" class="collapse bracket"></td>
                       </tr>
                       <tr>
                       <td class="bracketfill"></td>
                       <td width=5px class="collapse"> 
                           <div id="toggle%d">
                           <small>.</small>
                           </div>
                       </td>
                       </tr>
                       <tr><td colspan="2" class="collapse bracket"></td>
                       </tr>
                       </table>
                       ''' % (self.pysrcid))
        self.pysrcid += 1
        return self.out.getvalue()

    def format(self, toktype, toktext, (srow, scol), (erow, ecol), line):
        """ Token handler.
        """
        
        # calculate new positions
        oldpos = self.pos
        newpos = self.lines[srow] + scol
        self.pos = newpos + len(toktext)
        #
        # handle newlines
        if toktype in [token.NEWLINE, tokenize.NL]:
            # No need, for that: the css attribute "white-space: pre;" will 
            # take care of that.
            self.out.write("\n")
            return
        #
        # send the original whitespace, if needed
        if newpos > oldpos:
            self.out.write(self.raw[oldpos:newpos])
        #
        # skip indenting tokens
        if toktype in [token.INDENT, token.DEDENT]:
            self.pos = newpos
            return
        #
        # map token type to a color group
        if token.LPAR <= toktype and toktype <= token.OP:
            toktype = token.OP
        elif toktype == token.NAME and keyword.iskeyword(toktext):
            toktype = self._KEYWORD
        style = self._tags.get(toktype, self._tags[self._TEXT])
        #
        # send text
        self.out.write('<span class="%s">' % (style, ))
        self.out.write(cgi.escape(toktext))
        self.out.write('</span>')

python2html = PythonParser()


