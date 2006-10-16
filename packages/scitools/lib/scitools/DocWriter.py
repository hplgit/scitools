"""
DocWriter is a tool for writing documents in ASCII, HTML, 
LaTeX, and other formats based on input from Python
datastructures. The base class DocWriter holds the contents
of the document, while other classes can filter the contents
to formatted text.
"""

"""
Better ideas:
Make class URL, Section, Table, Figure, etc., each with a repr()
to recreate the object (or perhaps not necessary).
Make a nested data structure of URL, Section, etc. (document writing).
Process the data structure and translate to dialects (HTML, LaTeX, ASCII)
(document formatting).
"""

from StringIO import StringIO
import re, os, glob

class DocWriter:
    def __init__(self):
        self.format = None
        # represent all data structures as a list:
        self.content = []

        # use StringIO as a string "file" for writing the document:
        self.doc = StringIO()

    def document(self):
        """Return formatted document as a string."""
        return self.doc.getvalue()

    def write_to_file(self, filename):
        """
        Write formatted document to a file.
        Just give the stem of the file name;
        the extension will be automatically added (depending on the
        document format).
        """
        f = open(filename + self.filename_extension(), 'w')
        f.write(self.document())
        f.close()

    def __str__(self):
        """Return formatted document."""
        return str(self.doc.getvalue())
    
    def title_etc(self, title, authors_and_institutions=[]):
        # no, append(Title(title, authors_and_institutions))
        self.content.append(('title_etc', {'title': title,
                             'authors': authors_and_institutions}))

    def section(self, title, level=1, label=None):
        """
        Write a section heading.
        level: 0=chapter, 1=section, 2=subsection, 3=subsubsection, ...
        """
        self.content.append(('section', title, level))

    def subsection(self, title, level=2, label=None):
        """
        Write a section heading.
        level: 0=chapter, 1=section, 2=subsection, 3=subsubsection, ...
        """
        self.content.append(('section', title, level))

    def list(self, items=[], listtype='bulletized', headline=''):
        """
        items: Python list/tuple of strings
        headline: optional line right before the list
        listtype: 'bulletized', 'enumerated', 'definition'
        In case of 'definition' list, the word to be defined must
        be followed by a newline (everything after the newline is
        the definition).

        Nested lists is typically typeset using nested calls to
        the list method:

          docwriter.list(
            ['item1', 'item2',
            docwriter.list(headline='item3:', items=['item3, subitem1',
            'item3, subitem2'], listtype='enumerated'), 'item4'])
        """
        self.content.append(('list', items, listtype, headline))

    def plaintext(self, text):
        """
        text: string, to be processed by expandtext before output
        """
        self.content.append(('plaintext', 'append'))

    def para(self):
        """Make new paragraph."""
        self.content.append(('para',))

    def verbatim(self, code):
        """Write code in fixed-width form (typically for computer code)."""
        self.content.append(('verbatim', code))

    def raw(self, text):
        """Write text directly 'as is' to output."""
        self.content.append(('raw', text))

    def figure_conversion(self, filename, extensions):
        """
        Convert filename to an image with type according to
        extension(s).
        """
        if not isinstance(extensions, (list,tuple)):
            extensions = [extensions]
        for ext in extensions:
            final = filename + ext
            if os.path.isfile(final):
                return final

        final = filename + extensions[0]  # convert to first mentioned type
        files = glob.glob(filename + '*')
        # first convert from ps or eps to other things:
        for file in files:
            stem, ext = os.path.splitext(file)
            if ext == '.ps' or ext == '.eps':
                cmd = 'convert %s %s' % (file, final)
                print cmd
                failure = os.system(cmd)
                if failure:
                    print 'Could not convert;\n  %s' % cmd
                return final
        # try to convert from the first file to the disired format:
        file = files[0]
        cmd = 'convert %s %s' % (file, final)
        print cmd
        failure = os.system(cmd)
        if failure:
            print 'Could not convert;\n  %s' % cmd
        return final
        
    def figure(self, filename, caption, width=None, height=None, label=None):
        """
        Insert a figure into the document.
        filename should be without extension; a proper extension is added,
        and if the figure is not available in that image format, the
        convert utility from ImageMagick is called to convert the format.
        """
        self.content.append(('figure', filename, caption,
                             width, height, label))

    def table(self, table, column_headline_pos='c', column_pos='c'):
        """
        Translates a two-dimensional list of data, containing strings or
        numbers, to a suitable "tabular" environment in the output.

        column_pos   : specify the l/c/r position of data entries in columns,
                       give either (e.g.) 'llrrc' or one char (if all are equal)
        column_headline_pos : position l/c/r for the headline row
        """
        self.content.append(('table', table, column_headline_pos, column_pos))


formatting_regex = {'italic': r'\s\*([^*]+?)\*\s',
              'bold': r'\s\*\*([^*]+?)\*\*\s',
              'fixed-width': r'\s``([^*]+?)``\s',
              }

class Formatter:
    def __init__(self):
        self.format = None

    def notimpl(self, func):
        s = "\nFormatter: %s not impl. for format %s (class %s)\n" % \
            (func, self.format, self.__class__.__name__)
        print s
        self.doc.write(s)
        return s

    def filename_extension(self):
        self.notimpl('filename_extension')
        
    def expandtext(self, text):
        """
        Format emphasized, boldface, etc. words in a running text.
        The syntax follow reStructured text, i.e., writing *and* means
        the word "and" typeset in italic, **and** implies boldface, etc.
        """
        self.notimpl('expandtext')
        
    def url(address, text=''):
        """
        Write an URL with text as link. If text is empty, the address
        is used as text.
        """
        self.notimpl("url")

    def header(self):
        self.notimpl('header')

    def footer(self):
        self.notimpl('footer')

    def title_etc(self, title, authors_and_institutions=[]):
        self.notimpl('title_etc')

    def section(self, title, level, label=None):
        """
        Write a section heading.
        level: 0=chapter, 1=section, 2=subsection, 3=subsubsection, ...
        """
        self.notimpl("section")

    def list(self, items=[], listtype='bulletized', headline=''):
        """
        items: Python list/tuple of strings
        headline: optional line right before the list
        listtype: 'bulletized', 'enumerated', 'definition'
        In case of 'definition' list, the word to be defined must
        be followed by a newline (everything after the newline is
        the definition).

        Nested lists are typically typeset using nested calls to
        the list method:

          docwriter.list(
            ['item1', 'item2',
            docwriter.list(headline='item3:', items=['item3, subitem1',
            'item3, subitem2'], listtype='enumerated'), 'item4'])
        """
        self.notimpl("list")

    def plaintext(self, text):
        """
        text: string, to be processed by expandtext before output
        """
        self.notimpl("list")

    def para(self):
        """Make new paragraph."""
        self.notimpl("para")

    def verbatim(self, code):
        """Write code in fixed-width form (typically for computer code)."""
        self.notimpl("verbatim")

    def raw(self, text):
        """Write text directly 'as is' to output."""
        self.notimpl("raw")

    def figure_conversion(self, filename, extensions):
        """
        Convert filename to an image with type according to
        extension(s).
        """
        if not isinstance(extensions, (list,tuple)):
            extensions = [extensions]
        for ext in extensions:
            final = filename + ext
            if os.path.isfile(final):
                return final

        final = filename + extensions[0]  # convert to first mentioned type
        files = glob.glob(filename + '*')
        # first convert from ps or eps to other things:
        for file in files:
            stem, ext = os.path.splitext(file)
            if ext == '.ps' or ext == '.eps':
                cmd = 'convert %s %s' % (file, final)
                print cmd
                failure = os.system(cmd)
                if failure:
                    print 'Could not convert;\n  %s' % cmd
                return final
        # try to convert from the first file to the disired format:
        file = files[0]
        cmd = 'convert %s %s' % (file, final)
        print cmd
        failure = os.system(cmd)
        if failure:
            print 'Could not convert;\n  %s' % cmd
        return final
        
    def figure(self, filename, caption, width=None, height=None, label=None):
        """
        Insert a figure into the document.
        filename should be without extension; a proper extension is added,
        and if the figure is not available in that image format, the
        convert utility from ImageMagick is called to convert the format.
        """
        self.notimpl("fig")

    def table(self, table, column_headline_pos='c', column_pos='c'):
        """
        Translates a two-dimensional list of data, containing strings or
        numbers, to a suitable "tabular" environment in the output.

        column_pos   : specify the l/c/r position of data entries in columns,
                       give either (e.g.) 'llrrc' or one char (if all are equal)
        column_headline_pos : position l/c/r for the headline row
        """
        self.notimpl('table')


formatting_regex = {'italic': r'\s\*([^*]+?)\*\s',
              'bold': r'\s\*\*([^*]+?)\*\*\s',
              'fixed-width': r'\s``([^*]+?)``\s',
              }


class HTML(Formatter):
    formatting = {'italic': ' <EM>\g<1></EM> ',
                  'bold': ' <B>\g<1></B> ',
                  'fixed-width': ' <TT>\g<1></TT> ',
                  }

    table_border = '0'
    table_cellpadding = '2'
    table_cellspacing = '0'
    
    def __init__(self):
        self.format = 'HTML'
        DocWriter.__init__(self)
        
    def filename_extension(self):
        return '.html'
    
    def expandtext(self, text):
        for item in formatting_regex:
            c = re.compile(formatting_regex[item], re.S)
            text = c.sub(HTML.formatting[item], text)
        return text
        
    def url(address, text=''):
        if not text:
            text = address
        s = '<A HREF="%s">%s</A>' % (address, text)
        return s
        
    def header(self):
        s = """\
<!-- HTML document generated by %s.%s -->
<HTML>
<BODY BGCOLOR="white">
""" % (__name__, self.__class__.__name__)
        self.doc.write(s)
        return s

    def footer(self):
        s = """
</BODY>
</HTML>
"""
        self.doc.write(s)
        return s

    def title_etc(self, title, authors_and_institutions=[]):
        s = """
<TITLE>%(title)s</TITLE>
<CENTER>
<H1>%(title)s</H1>
""" % locals()
        for author, inst in authors_and_institutions:
            s += """
<H4>%(author)s</H4>
<BR><EM>%(inst)s</EM><BR>
""" % locals()
        s += """
<HR>
</CENTER>
"""
        return s

    def section(self, title, level=1, label=None):
        if level == 0:
            s = '\n<H1>%s</H1>\n' % title
        elif level == 1:
            s = '\n<H3>%s</H3>\n' % title
        elif level >= 2:
            s = '\n<H5>%s</H5>\n' % title
        return s

    def list(self, items=[], listtype='bulletized', headline=''):
        if not isinstance(items, (list,tuple)):
            raise TypeError, 'items must be either list or tuple, '\
                  'not %s, containing\n%s' % (type(items), items)
        # first resolve nested lists within the list:
        for i in range(len(items)):
            if isinstance(items[i], (list,tuple)):
                items[i] = self._list(items[i], listtype=listtype)

        s = self._list(items, listtype=listtype, headline=headline)
        return s
    
    def _list(self, items=[], listtype='bulletized', headline=''):
        if listtype == 'bulletized':
            tp = 'UL'
        elif listtype == 'enumerated':
            tp = 'OL'
        elif listtype == 'definition':
            tp = 'DL'

        if headline:
            s = headline + '\n'
        else:
            s = ''
        s += '<%s>\n' % tp
        for item in items:
            if listtype == 'definition':
                words = item.split('\n')
                word = words[0]
                definition = words[1:]
                s += '<DT>%s</DT> <DD>%s</DD>\n' % (word, definition)
            else:
                s += '<LI>%s</LI>\n' % item
        s += '</%s>\n' % tp
        return s
    
    def plaintext(self, text):
        s = self.expandtext(text)
        return s

    def para(self):
        s = '\n<P>\n'
        return s

    def verbatim(self, code):
        s = '<PRE>\n%s\n</PRE>\n' % code
        return s

    def raw(self, text):
        # check for <, >, etc.
        # NOT YET DONE!
        return text

    def figure(self, filename, caption, width=None, height=None, label=None):
        filename = self.figure_conversion(filename, ('.jpg', '.gif', '.png'))
        if width:
            width = ' WIDTH=%s ' % width
        else:
            width = ''
        if height:
            height = ' WIDTH=%s ' % width
        else:
            height = ''
        s = '\n<HR><IMG SRC="%s"%s%s>\n<P><EM>%s</EM>\n<HR><P>\n' % \
            (filename, width, height, caption)
        return s

    def table(self, table, column_headline_pos='c', column_pos='c'):
        s = '\n<TABLE BORDER="%s" CELLPADDING="%s" CELLSPACING="%s">\n' % \
            (HTML.table_border, HTML.table_cellpadding, HTML.table_cellspacing)
        for line in table:
            s += '<TR>'
            for column in line:
                s += '<TD>%s</TD>' % column
            s += '</TR>\n'
        s += '</TABLE>\n'
        return s
    
    
# note: DocFactor does not allow nested calls (d.raw(d.list...))
class DocFactory:
    def __init__(self, *formats):
        self.formats = []
        for format in formats:
            self.formats.append(eval(format+'()'))
        self.history = []
        

    def dispatcher(self, *args, **kwargs):
        #print 'in dispatcher for', self.method_name, 'with args', args, kwargs
        self.history = (self.method_name, args, kwargs)
        for format in self.formats:
            s = getattr(format, self.method_name)(*args, **kwargs)
        
    def __getattr__(self, name):
        print 'calling __getattr__ with', name
        self.method_name = name
        return self.dispatcher

    # simpler solution in case all calls are to be directed to one other format
    #def __getattr__(self, name):
    #    return getattr(some_other_instance, name)
    

def test(d):
    d.header()
    d.title_etc('Example on Using DocWriter',
                author='Kaare Dump', institution='Doc Writer Inc.')
    d.section('First Section', level=1)
    d.plaintext("""
This is a *first* example of using the **DocWriter
module** for writing documents from **Python** scripts.
It could be a nice tool since we do not need to bother
with special typesetting, such as ``fixed width fonts``
in plain text.
""")
    d.section('A Subsection', level=2)
    d.plaintext('Here we exemplify lists and tables.')
    d.list(headline='First a bulletized list:',
           items=['first item', 'second item',
                  'a third item has a sublist:',
                  ['item 1', 'item 2'],
                  'a fourth item'
                  ]
           )
    d.section('Figures', level=1)
    d.plaintext('We may insert *figures* into the document.')
    d.figure('fig1', 'Example on a GUI written in Python/Tkinter', width=600)
    d.footer()
    d.write_to_file('tmp')

if __name__ == '__main__':
    #d = HTML()
    d = DocFactory('HTML', 'LaTeX', 'ReStructuredText')
    test(d)

    
