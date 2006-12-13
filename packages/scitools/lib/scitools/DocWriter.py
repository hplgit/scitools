"""
DocWriter is a tool for writing documents in ASCII, HTML, 
LaTeX, and other formats based on input from Python
datastructures. The base class _BaseWriter defines common
functions and data structures, while subclasses HTML, etc.
implement (i.e., write to) various formats.
"""

from StringIO import StringIO
import re, os, glob, commands

class _BaseWriter:
    """
    Base class for document writing classes.
    Each subclass implements a specific format (HTML, LaTeX,
    reStructuredText, etc.).
    """
    def __init__(self, format, filename_extension):
        # use StringIO as a string "file" for writing the document:
        self.file = StringIO()
        self.filename_extension = filename_extension
        self.format = format
        self._footer_called = False
        
    document = property(fget=lambda self: self.file.getvalue(),
                        doc='Formatted document as a string')

    def write_to_file(self, filename):
        """
        Write formatted document to a file.
        Just give the stem of the file name;
        the extension will be automatically added (depending on the
        document format).
        """
        # footer?
        if not self._footer_called:
            self.footer()
            self._footer_called = True
            
        f = open(filename + self.filename_extension, 'w')
        f.write(self.document)
        f.close()

    def __str__(self):
        """Return formatted document."""
        return self.document

    def header(self):
        """Header as required by format. Called in constructor."""
        pass
    
    def footer(self):
        """Footer as required by format. Called in write_to_file."""
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

    def paragraph(self, title, ending='.', label=None):
        """
        Write a paragraph heading with the given title and an ending
        (period, question mark, colon) and an optional label (for navigation).
        """
        self.not_impl('paragraph')

    def paragraph_separator(self):
        """
        Add a (space) separator between running paragraphs.
        """
        self.not_impl('paragraph_separator')

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
        # call _BaseWriter.unfold_list to traverse the list
        # and use self.item_handler to typeset each item
        self.not_impl('list')
        
    def unfold_list(self, items, item_handler, listtype, level=0):
        """
        Traverse a possibly nested list and call item_handler for
        each item. To be used in subclasses for easy list handling.

        @param items: list to be processed.
        @param item_handler: callable, see that method for doc of arguments.
        @param listtype: 'itemize', 'enumerate', or 'description'.
        @param level: the level of a sublist (0 is main list, increased by 1
        for each sublevel).
        """
        # check for common error (a trailing comma...):
        if isinstance(items, tuple) and len(items) == 1:
            raise ValueError, 'list is a 1-tuple, error? If there is '\
                  'only one item in the list, make a real Python list '\
                  'object instead - current list is\n(%s,)' % items
        item_handler('_begin', listtype, level)
        for i, item in enumerate(items):
            if isinstance(item, (list,tuple)):
                self.unfold_list(item, item_handler, listtype, level+1)
            elif isinstance(item, basestring):
                if listtype == 'description':
                    # split out keyword in a description list:
                    parts = item.split(':')
                    keyword = parts[0]
                    item = ':'.join(parts[1:])
                    item_handler(item, listtype, level, keyword)
                else:
                    item_handler(item, listtype, level)
            else:
                raise TypeError, 'wrong %s for item' % type(item)
        item_handler('_end', listtype, level)

    def item_handler(self, item, listtype, level, keyword=None):
        """
        Write out the syntax for an item in a list.

        @param item: text assoicated with the current list item. If item
        equals '_begin' or '_end', appropriate begin/end formatting of
        the list is written instead of an ordinary item.
        @param listtype: 'itemize, 'enumerate', or 'description'.
        @param level: list level number, 0 is the mainlist, increased by 1
        for each sublist (the level number implies the amount of indentation).
        @param keyword: the keyword of the item in a 'description' list.
        """
        self.not_impl('item_handler')
                    
    def verbatim(self, code):
        """
        Write verbatim text in fixed-width form
        (typically for computer code).
        """
        self.not_impl('verbatim')

    def math(self, text):
        """Write block of mathematical text (equations)."""
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

        @param table: list of list with rows/columns in table, including
        (optional) column-headline 1st row and row-headline 1st column.
        @param column_pos: specify the l/c/r position of data
        entries in columns, give either (e.g.) 'llrrc' or one char
        (if all are equal).
        @param column_headline_pos : position l/c/r for the headline row
        """
        self.not_impl('table')

    def url(self, url_address, link_text=None):
        """Typeset an URL (with an optional link)."""
        self.not_impl('url')

    def link(self, link_text, link_target):
        """Typeset a hyperlink."""
        self.not_impl('link')

    # what about LaTeX references to labels in equations, pages, labels?

def makedocstr(parent_class, subclass_method):
    """
    Compose a string (to be used as doc string) from a method's
    doc string in a parent class and an additional doc string
    in a subclass version of the method.

    @param parent_class: class object for parent class.
    @param subclass_method: method object for subclass.
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
inline_tag_end = r'(?P<end>($|[.,?!;:)\s]))'
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

class Doconce(_BaseWriter):
    def __init__(self):
        _BaseWriter.__init__(self, 'Doconce', '.dco')
    
    def title(self, title, authors_and_institutions=[], date='today'):
        s = '\nTITLE: %s\n' % title
        for ai in authors_and_institutions:
            authorinfo = '; '.join(ai)
            s += 'AUTHOR: %s\n' % authorinfo
        if date is not None:
            if date == 'today':
                date = self.today_date()
            s += 'DATE: %s\n' % date
        self.file.write(s)
        self.paragraph_separator()

    def heading(self, underscores, title, label=None):
        underscores = '_'*underscores
        self.file.write('\n%s%s%s\n\n' % (underscores, title, underscores))

    def section(self, title, label=None):
        self.heading(7, title, label)

    def subsection(self, title, label=None):
        self.heading(5, title, label)

    def subsubsection(self, title, label=None):
        self.heading(3, title, label)

    def paragraph(self, title, ending='.', label=None):
        s = '\n\n__%s%s__ ' % (title, ending)
        self.file.write(s)

    def paragraph_separator(self):
        self.file.write('\n\n')

    def text(self, text, indent=0):
        text = _BaseWriter.text(self, text, indent)
        # not necessary since Doconce is the format for text:
        #text = _BaseWriter.expandtext(self, text,
        #                              INLINE_TAGS, HTML.INLINE_TAGS_SUBST)
        self.file.write(text)
        
    def list(self, items, listtype='itemize'):
        self.unfold_list(items, self.item_handler, listtype)

    def item_handler(self, item, listtype, level, keyword=None):
        indent = '  '*level
        s = ''
        if item == '_begin':
            if level == 1:
                s += '\n'
        elif item == '_end':
            if level == 1:
                s += '\n'
        else:
            # ordinary item:
            if item is not None:
                if listtype == 'itemize':
                    s += '\n%s%s* %s' % (indent, indent, item)
                elif listtype == 'enumerate':
                    s += '\n%s%so %s' % (indent, indent, item)
                elif listtype == 'description':
                    s += '\n%s%s- %s: %s' % (indent, indent, keyword, item)
        self.file.write(s)
                    
    def verbatim(self, code):
        self.file.write('\n!bc\n' + r'%s' % code + '\n!ec\n')

    def figure(self, filename, caption, width=None, height=None, label=None):
        filename = self.figure_conversion(filename, \
                            ('.jpg', '.gif', '.png', '.ps', '.eps'))
        s = '\nFIGURE:[%s,' % filename
        if width:
            s += '  width=%s ' % width
        if height:
            s += '  height=%s ' % width
        s += '] ' + caption + '\n'
        self.file.write(s)

    def table(self, table, column_headline_pos='c', column_pos='c'):
        # find max column width
        mcw = 0
        for row in table:
            mcw = max(mcw, max([len(str(c)) for c in row]))
        formatted_table = []  # table where all columns have equal width
        column_format = '%%-%ds' % mcw
        for row in table:
            formatted_table.append([column_format % c for c in row])
        s = '\n\n'
        for row in formatted_table:
            s += '   | ' + ' | '.join(row) + ' |\n'
        s += '\n'
        self.file.write(s)
    
    def url(self, url_address, link_text=None):
        if link_text is None:
            link_text = 'link'  # problems with Doconce and empty link text
        self.file.write(' %s<%s>' % (url_address, link_text))

    def link(self, link_text, link_target):
        self.file.write('%s (%s)' % (link_text, link_target))

    # autogenerate doc strings by combining parent class doc strings
    # with subclass doc strings:
    for method in [title, section, subsection, subsubsection,
                   paragraph, text,
                   verbatim, # not defined here: math, raw,
                   figure, table, url,
                   list, item_handler,]:
        method.__doc__ = makedocstr(_BaseWriter, method)



class HTML(_BaseWriter):
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
        _BaseWriter.__init__(self, 'HTML', '.html')
        self.header()

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
        self.paragraph_separator()

    def heading(self, level, title, label=None):
        if label is None:
            s = """\n<H%d>%s</H%d>\n""" % (level, title, level)
        else:
            s = """\n<H%d><A HREF="%s">%s</H%d>\n""" % \
                (level, label, title, level)
        self.file.write(s)

    def section(self, title, label=None):
        self.heading(1, title, label)

    def subsection(self, title, label=None):
        self.heading(3, title, label)

    def subsubsection(self, title, label=None):
        self.heading(4, title, label)

    def paragraph(self, title, ending='.', label=None):
        s = '\n\n<P><!-- paragraph with heading -->\n<B>%s%s</B>\n' \
            % (title, ending)
        if label is not None:
            s += '<A NAME="%s">\n' % label
        self.file.write(s)

    def paragraph_separator(self):
        self.file.write('\n<P>\n')

    def text(self, text, indent=0):
        text = _BaseWriter.text(self, text, indent)
        text = _BaseWriter.expandtext(self, text,
                                      INLINE_TAGS, HTML.INLINE_TAGS_SUBST)
        self.file.write(text)
        
    def list(self, items, listtype='itemize'):
        self.unfold_list(items, self.item_handler, listtype)

    def item_handler(self, item, listtype, level, keyword=None):
        indent = '  '*level
        s = ''
        if item == '_begin':
            if listtype == 'itemize':
                s += '\n%s<UL>' % indent
            elif listtype == 'enumerate':
                s += '\n%s<OL>' % indent
            elif listtype == 'description':
                s += '\n%s<DL>' % indent
            s += ' <!-- start of "%s" list -->\n' % listtype
        elif item == '_end':
            if listtype == 'itemize':
                s += '%s</UL>' % indent
            elif listtype == 'enumerate':
                s += '%s</OL>' % indent
            elif listtype == 'description':
                s += '%s</DL>' % indent
            s += ' <!-- end of "%s" list -->\n' % listtype
        else:
            # ordinary item:
            if item is not None:
                if listtype in ('itemize', 'enumerate'):
                    s += '%s%s<P><LI> %s\n' % (indent, indent, item)
                else:
                    s += '%s%s<P><DT>%s</DT><DD>%s</DD>\n' % \
                         (indent, indent, keyword, item)
        self.file.write(s)
                    
    def verbatim(self, code):
        self.file.write('\n<PRE>' + r'%s' % code + '\n</PRE>\n')

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
        self.file.write(s)

    def table(self, table, column_headline_pos='c', column_pos='c'):
        s = '\n<P>\n<TABLE BORDER="%s" CELLPADDING="%s" CELLSPACING="%s">\n' %\
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

    def link(self, link_text, link_target):
        self.file.write('\n<A HREF="%s">%s</A>\n' % (link_text, link_target))

    # autogenerate doc strings by combining parent class doc strings
    # with subclass doc strings:
    for method in [title, section, subsection, subsubsection,
                   paragraph, text,
                   verbatim, # not defined here: math, raw,
                   figure, table, url,
                   list, item_handler,]:
        method.__doc__ = makedocstr(_BaseWriter, method)



# Efficient way of generating class DocWriter.
# A better way (for pydoc and other API references) is to
# explicitly list all methods and their arguments and then add
# the body for writer in self.writers: writer.method(arg1, arg2, ...)

class DocWriter:
    """
    DocWriter can write documents in several formats at once.
    """
    methods = 'title', 'section', 'subsection', 'subsubsection', \
              'paragraph', 'paragraph_separator', 'text', 'list', \
              'verbatim', 'math', 'raw', 'url', 'link', \
              'write_to_file', 'figure', 'table', 
    
        
    def __init__(self, *formats):
        """
        @param formats: sequence of strings specifying the desired formats.
        """
        self.writers = [eval(format)() for format in formats]

    def documents(self):
        return [writer.document for writer in self.writers]

    def __str__(self):
        s = ''
        for writer in self.writers:
            s += '*'*60 + \
                  '\nDocWriter: format=%s (without footer)\n' % \
                  writer.__class__.__name__ + '*'*60
            s += str(writer)
        return s
            
    def dispatcher(self, *args, **kwargs):
        #print 'in dispatcher for', self.method_name, 'with args', args, kwargs
        #self.history = (self.method_name, args, kwargs)
        for writer in self.writers:
            s = getattr(writer, self.method_name)(*args, **kwargs)

    '''
    Alternative to attaching separate global functions:
    def __getattribute__(self, name):
        print 'calling __getattribute__ with', name
        if name in DocWriter.methods:
            self.method_name = name
            return self.dispatcher
        else:
            return object.__getattribute__(self, name)

    # can use inspect module to extract doc of all methods and
    # put this doc in __doc__
    '''
    
# Autogenerate methods in class DocWriter (with right
# method signature and doc strings stolen from class _BaseWriter (!)):

import inspect

def func_to_method(func, class_, method_name=None):
    setattr(class_, method_name or func.__name__, func)

for method in DocWriter.methods:
    docstring = eval('_BaseWriter.%s.__doc__' % method)
    # extract function signature:
    a = inspect.getargspec(eval('_BaseWriter.%s' % method))
    if a[3] is not None:  # keyword arguments?
        kwargs = ['%s=%r' % (arg, value) \
                  for arg, value in zip(a[0][-len(a[3]):], a[3])]
        args = a[0][:-len(a[3])]
        allargs = args + kwargs
    else:
        allargs = a[0]
    #print method, allargs, '\n', a
    signature_def = '%s(%s)' % (method, ', '.join(allargs))
    signature_call = '%s(%s)' % (method, ', '.join(a[0][1:]))  # exclude self
    code = """\
def _%s:
    '''\
%s
    '''
    for writer in self.writers:
        writer.%s

func_to_method(_%s, DocWriter, '%s')
""" % (signature_def, docstring, signature_call, method, method)
    #print 'Autogenerating\n', code
    exec code
  

def _test(d):
    # d is formatclass() or DocWriter(HTML, LaTeX, ...)
    print '\n\n', '*'*70, \
          '\n*** Testing class "%s"\n' % d.__class__.__name__, '*'*70
    
    d.title('My Test of Class %s' % d.__class__.__name__,
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
    d.text("""
Some paragraph text taken from "Documenting Python": The Python language
has a substantial body of documentation, much of it contributed by various
authors. The markup used for the Python documentation is based on
LaTeX and requires a significant set of macros written specifically
for documenting Python. This document describes the macros introduced
to support Python documentation and how they should be used to support
a wide range of output formats.

This document describes the document classes and special markup used
in the Python documentation. Authors may use this guide, in
conjunction with the template files provided with the distribution, to
create or maintain whole documents or sections.

If you're interested in contributing to Python's documentation,
there's no need to learn LaTeX if you're not so inclined; plain text
contributions are more than welcome as well.
""")
    d.text('Here is an enumerate list:')
    samplelist = ['item1', 'item2',
                  ['subitem1', 'subitem2'],
                  'item3',
                  ['subitem3', 'subitem4']]
    d.list(samplelist, listtype='enumerate')
    d.text('...with some trailing text.')
    d.subsubsection('First Subsubsection with an Itemize List')
    d.list(samplelist, listtype='itemize')
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
    d.text('Here is a description list:')
    d.list(['keyword1: item1', 'keyword2: item2 goes here, with a colon : and some text after',
        ['key3: subitem1', 'key4: subitem2'],
        'key5: item3',
        ['key6: subitem3', 'key7: subitem4']],
           listtype='description')
    d.paragraph_separator()
    d.text('And here is a table:')
    d.table([['a', 'b'], ['c', 'd'], ['e', 'f', 'and a longer text']])
    print d
    d.write_to_file('tmp_%s' % d.__class__.__name__)
        
if __name__ == '__main__':
    formats = HTML, Doconce
    for format in formats:
        d = format()
        _test(d)
    formats_str = [format.__name__ for format in formats]
    d = DocWriter(*formats_str)
    _test(d)
