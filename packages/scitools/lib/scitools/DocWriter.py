"""
DocWriter is a tool for writing documents in ASCII, HTML, 
LaTeX, and other formats based on input from Python
datastructures. The base class DocWriter defines common
functions and data structures, while subclasses implement
(i.e., write to) various formats.
"""

"""
Other ideas:
Make class URL, Section, Table, Figure, etc., each with a repr()
to recreate the object (or perhaps not necessary).
Make a nested data structure of URL, Section, etc. (document writing).
Process the data structure and translate to dialects (HTML, LaTeX, ASCII)
(document formatting).
"""

from StringIO import StringIO
import re, os, glob, commands

class DocWriter:
    def __init__(self, format, filename_extension):
        # use StringIO as a string "file" for writing the document:
        self.file = StringIO()
        self.filename_extension = filename_extension
        self.format = format
        
    document = property(fget=lambda self: self.file.getvalue(),
                        doc='Formatted document as a string')

    def write_to_file(self, filename):
        """
        Write formatted document to a file.
        Just give the stem of the file name;
        the extension will be automatically added (depending on the
        document format).
        """
        f = open(filename + self.filename_extension, 'w')
        f.write(self.document)
        f.close()

    def __str__(self):
        """Return formatted document."""
        return self.document

    def header(self):
        pass
    
    def footer(self):
        pass
    
    def not_impl(self, method):
        raise NotImplementedError, \
              'method "%s" in class "%s" is not implemented' % \
              (method, self.__class__.__name__)
    
    def title(self, title, authors_and_institutions=[], date='today'):
        """
        Provide title and authors.

        @param title: document title (string).
        @param authors_and_institutions: list of authors and their
        associated institutions, where each list item is a tuple/list
        with author as first element followed by the name of all
        institutions this author is associated with.
        @param date: None implies no date, while 'today' generates
        the current date, otherwise a string is supplied.
        """
        self.not_impl('title')

    def today_date(self):
        """Return a string with today's date suitably formatted."""
        import time
        return time.strftime('%a, %d %b %Y (%H:%M)')
    
    def section(self, title, label=None):
        """
        Write a section heading with the given title and an optional
        label (for navigation).
        """
        self.not_impl('section')

    def subsection(self, title, label=None):
        """
        Write a subsection heading with the given title and an optional
        label (for navigation).
        """
        self.not_impl('subsection')

    def subsubsection(self, title, label=None):
        """
        Write a subsubsection heading with the given title and an optional
        label (for navigation).
        """
        self.not_impl('subsubsection')

    def paragraph(self, title, label=None):
        """
        Write a paragraph heading with the given title and an optional
        label (for navigation).
        """
        self.not_impl('paragraph')

    def text(self, text, indent=0):
        """
        Write plain text. Each line can be idented by a given number
        of spaces.
        """
        # do the indentation here, subclasses should call this method first
        text = '\n'.join([' '*indent + line for line in text.split('\n')])
        # subclasses must substitute Doconce simple formatting
        # using the expandtext method
        return text

    def expandtext(self, text, tags, tags_replacements):
        """
        In a string text, replace all occurences of strings defined in tags
        by the corresponding strings defined in tags_replacements.
        Both tags and tags_replacements are dictionaries with keys such
        as 'bold', 'emphasize', 'verbatim', 'math', and values consisting of
        regular expression patterns.

        This method allows application code to use some generic ways of
        writing emphasized, boldface, and verbatim text, typically in the
        Doconce format with *emphasized text*, _boldface text_, and
        `verbatim fixed font width text`.
        """
        for tag in tags:
            tag_pattern = tags[tag]
            c = re.compile(tag_pattern, re.MULTILINE)
            try:
                tag_replacement = tags_replacements[tag]
            except KeyError:
                continue
            if tag_replacement is not None:
                text = c.sub(tag_replacement, text)
        return text
    
    def list(self, items, listtype='itemize'):
        """
        Write list or nested lists.

        @param items: list of items.
        @param listtype: 'itemize', 'enumerate', or 'description'.
        """
        # call DocWriter.unfold_list to traverse the list
        # and use self.item_handler to typeset each item
        self.not_impl('list')
        
    def unfold_list(self, items, item_handler, listtype):
        """
        Traverse a possibly nested list and call item_handler for
        each item. To be used in subclasses for easy list handling.

        @param items: list to be processed.
        @param item_handler: callable taking the item text as
        first argument; a second argument which is 'begin', 'item',
        or 'end', depending on the position of the current item in the list;
        a third argument reflecting the list type ('enumerate', 'description',
        or 'itemize'); and an optional fourth argument 'keyword' holds
        the keyword in case the item belongs to a 'description' list.
        """
        # position: mapping from items index number to 'begin', 'end', 'item'
        position = ['item' for i in range(1,len(items)-1)]
        position.insert(0, 'begin')
        position.append('end')
        for i, item in enumerate(items):
            if isinstance(item, (list,tuple)):
                self.unfold_list(item, item_handler, listtype)
                if i == len(items)-1:
                    # sublist as last item, need to end list:
                    item_handler(None, 'end', listtype, None)
            elif isinstance(item, basestring):
                if listtype == 'description':
                    # split out keyword in a description list:
                    parts = item.split(':')
                    keyword = parts[0]
                    item = ':'.join(parts[1:])
                    item_handler(item, position[i], listtype, keyword)
                else:
                    item_handler(item, position[i], listtype)
            else:
                raise TypeError, 'wrong %s for item' % type(item)

    def item_handler(self, item, position, listtype, keyword=None):
        """
        Write out the syntax for an item in a list.

        @item: text assoicated with the current list item. If None,
        no item, just end of list.
        @param position: position in list, 'begin' means the 1st item,
        'end' the last, and 'item' signifies an item in between.
        @listtype: 'itemize, 'enumerate', or 'description'.
        @keyword: the keyword of the item in a 'description' list.
        """
        self.not_impl('item_handler')
                    
    def verbatim(self, code):
        """
        Write verbatim text in fixed-width form
        (typically for computer code).
        """
        self.not_impl('verbatim')

    def math(self, text):
        """Write mathematical text."""
        # default: dump raw
        self.raw(text)

    def raw(self, text):
        """Write text directly 'as is' to output."""
        self.file.write(text)

    def figure_conversion(self, filename, extensions):
        """
        Convert filename to an image with type according to
        extension(s).

        The first existing file with an extension encountered in the extensions
        list is returned. If no files with the right extensions are found,
        the convert utility from the ImageMagick suite is used to
        convert filename.ps or filename.eps to filename + extensions[0].
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
        failure, outtext = commands.getstatusoutput(cmd)
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
        self.not_impl('figure')

    def table(self, table, column_headline_pos='c', column_pos='c'):
        """
        Translates a two-dimensional list of data, containing strings or
        numbers, to a suitable "tabular" environment in the output.

        column_pos   : specify the l/c/r position of data entries in columns,
                       give either (e.g.) 'llrrc' or one char (if all are equal)
        column_headline_pos : position l/c/r for the headline row
        """
        self.not_impl('table')

    def url(self, url_address, link_text=None):
        """Typeset an URL (with an optional link)."""
        self.not_impl('url')


def makedocstr(parent_class, subclass_method):
    """
    Compose a string (to be used as doc string) from a method's
    doc string in a parent class and an additional doc string
    in a subclass version of the method.

    @parent_class: class object for parent class.
    @subclass_method: method object for subclass.
    @return: parent_class.method.__doc__ + subclass_method.__doc__
    """
    parent_method = getattr(parent_class, subclass_method.__name__)
    docstr = parent_method.__doc__
    if subclass_method.__doc__ is not None and \
           subclass_method is not parent_method:
        docstr += subclass_func.__doc__
    return docstr


# regular expressions for inline tags:
inline_tag_begin = r'(?P<begin>(^|[(\s]))'
inline_tag_end = r'(?P<end>[.,?!;:)\s])'
INLINE_TAGS = {
    # math: text inside $ signs, as in $a = b$, with space before the
    # first $ and space, comma, period, colon, semicolon, or question
    # mark after the enclosing $.
    'math':
    r'%s\$(?P<subst>[^ `][^$`]*)\$%s' % \
    (inline_tag_begin, inline_tag_end),
    
    'emphasize':
    r'%s\*(?P<subst>[^ `][^*`]*)\*%s' % \
    (inline_tag_begin, inline_tag_end),
    
    'verbatim':
    r'%s`(?P<subst>[^ ][^`]*)`%s' % \
    (inline_tag_begin, inline_tag_end),
    
    'bold':
    r'%s_(?P<subst>[^ `][^_`]*)_%s' % \
    (inline_tag_begin, inline_tag_end),
    }

class Doconce(DocWriter):
    pass

class HTML(DocWriter):
    # class variables:
    table_border = '2'
    table_cellpadding = '5'
    table_cellspacing = '2'
    
    INLINE_TAGS_SUBST = {  # from inline tags to HTML tags
        # keep math as is:
        'math': None,  # indicates no substitution
        'emphasize':     r'\g<begin><em>\g<subst></em>\g<end>',
        'bold':          r'\g<begin><b>\g<subst></b>\g<end>',
        'verbatim':      r'\g<begin><tt>\g<subst></tt>\g<end>',
        }
    
    def __init__(self):
        DocWriter.__init__(self, 'HTML', '.html')
        
    def header(self):
        s = """\
<!-- HTML document generated by %s.%s -->
<HTML>
<BODY BGCOLOR="white">
""" % (__name__, self.__class__.__name__)
        self.file.write(s)
    
    def footer(self):
        s = """
</BODY>
</HTML>
"""
        self.file.write(s)
    
    def title(self, title, authors_and_institutions=[], date='today'):
        s = """
<TITLE>%s</TITLE>
<CENTER><H1>%s</H1></CENTER>
""" % (title, title)
        for ai in authors_and_institutions:
            author = ai[0]
            s += """
<CENTER>
<H4>%s</H4>""" % author
            for inst in ai[1:]:
                s += """
<H6>%s</H6>""" % inst
            s += """\n</CENTER>\n\n"""
        if date is not None:
            if date == 'today':
                date = self.today_date()
            s += """<CENTER>%s</CENTER>\n\n\n""" % date

        self.file.write(s)

    def heading(self, level, title, label=None):
        if label is None:
            s = """\n\n\n<H%d>%s</H%d>\n\n""" % (level, title, level)
        else:
            s = """\n\n\n<H%d><A HREF="%s">%s</H%d>\n\n""" % \
                (level, label, title, level)
        self.file.write(s)

    def section(self, title, label=None):
        self.heading(1, title, label)

    def subsection(self, title, label=None):
        self.heading(3, title, label)

    def subsubsection(self, title, label=None):
        self.heading(4, title, label)

    def paragraph(self, title, label=None):
        s = """\n\n<P>\n<B>%s.</B>\n""" % title
        if label is not None:
            s += """<A NAME="%s">\n""" % label
        self.file.write(s)

    def text(self, text, indent=0):
        text = DocWriter.text(self, text, indent)
        text = DocWriter.expandtext(self, text,
                                    INLINE_TAGS, HTML.INLINE_TAGS_SUBST)
        self.file.write(text)
        
    def list(self, items, listtype='itemize'):
        self.file.write("\n<!-- list -->\n")
        self.unfold_list(items, self.item_handler, listtype)
        self.file.write("<!-- end of list -->\n\n")

    def item_handler(self, item, position, listtype, keyword=None):
        s = ''
        if position == 'begin':
            if listtype == 'itemize':
                s += '\n<UL>\n'
            elif listtype == 'enumerate':
                s += '\n<OL>\n'
            elif listtype == 'description':
                s += '\n<DL>\n'
        # item:
        if item is not None:
            if listtype in ('itemize', 'enumerate'):
                s += '<P><LI> ' + item + '\n'
            else:
                s += '<P><DT>%s</DT><DD>%s</DD>\n' % (keyword, item)
        if position == 'end':
            if listtype == 'itemize':
                s += '</UL>\n'
            elif listtype == 'enumerate':
                s += '</OL>\n'
            elif listtype == 'description':
                s += '</DL>\n'
        self.file.write(s)
                    
    def verbatim(self, code):
        self.file.write('\n<PRE>' + r'%s' % code + '\n</PRE>\n')

    def figure(self, filename, caption, width=None, height=None, label=None):
        # unfinished
        s = '\n<IMG SRC="%s">\n' % filename
        s += caption
        self.file.write(s)

    def table(self, table, column_headline_pos='c', column_pos='c'):
        s = '\n\n<TABLE BORDER="%s" CELLPADDING="%s" CELLSPACING="%s">\n' % \
            (HTML.table_border, HTML.table_cellpadding, HTML.table_cellspacing)
        for line in table:
            s += '<TR>'
            for column in line:
                s += '<TD>%s</TD>' % column
            s += '</TR>\n'
        s += '</TABLE>\n\n'
        self.file.write(s)
    
    def url(self, url_address, link_text=None):
        if link_text is None:
            link_text = url_address
        self.file.write('\n<A HREF="%s">%s</A>\n' % (url_address, link_text))

    # autogenerate doc strings by combining parent class doc strings
    # with subclass doc strings:
    for method in [title, section, subsection, subsubsection,
                   paragraph, text,
                   verbatim, # not defined here: math, raw,
                   figure, table, url,
                   list, item_handler,]:
        method.__doc__ = makedocstr(DocWriter, method)
        

def _test(formatclass):
    d = formatclass()
    d.header()
    d.title('My Test of DocWriter',
            [('Hans Petter Langtangen',
              'Simula Research Laboratory',
              'Dept. of Informatics, Univ. of Oslo'),
             ])
    d.section('First Section')
    d.text("""
Here is some
text for section 1.

This is a *first* example of using the _DocWriter
module_ for writing documents from *Python* scripts.
It could be a nice tool since we do not need to bother
with special typesetting, such as `fixed width fonts`
in plain text.
""")
    d.subsection('First Subsection')
    d.text('Some text for the subsection.')
    d.paragraph('Test of a Paragraph')
    d.text('Some paragraph text.....')
    d.list(['item1', 'item2',
            ['subitem1', 'subitem2'],
            'item3',
            ['subitem3', 'subitem4']],
           listtype='enumerate')
    d.text('Here is some Python code:')
    d.verbatim("""
class A:
    pass

class B(A):
    pass

b = B()
b.item = 0  # create a new attribute
""")
    d.section('Second Section')
    d.list(['keyword1: item1', 'keyword2: item2 goes here, with a colon : and some text after',
        ['key3: subitem1', 'key4: subitem2'],
        'key5: item3',
        ['key6: subitem3', 'key7: subitem4']],
           listtype='description')
    d.table([['a', 'b'], ['c', 'd'], ['e', 'f']])
    d.footer()
    print d
        
'''
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
'''

if __name__ == '__main__':
    _test(HTML)

    
