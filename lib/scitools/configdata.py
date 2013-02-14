"""
The Python module ConfigParser supports configuration files with the
usual Windows .INI file syntax. The present configdata module extends
the syntax of configuration files and provides a more easy-to-use
interface to such files. Variables can also be defined on the
command-line and through environment variables in addition to the
configuration file.

"""
__author__ = 'Hans Petter Langtangen <hpl@simula.no>'

_configfile_description = """\
User-friendly reading of configuration files with an extended
Windows .INI syntax.

The configuration file has sections in square brackets
(e.g., [modes]) and option=value assignments in each section.
The extended syntax offers type specification of the options.
After the = sign the type appears in <> brackets followed by
the value, e.g.::

  [my section]
  my first option = <bool> off   # can be on, off, yes, no, 1, 0
  my second option = <float> 3.2
  my third option = <eval> [1, 4, 'tmp.ps']  # a list as option value
  my fourth option = MyClass     # no type specification here
  my fifth option = <eval> StringFunction('sin(x)*cos(x)')

The type must be bool, int, float, str, or eval.
As an example, the 'my second option' value will be a Python
float object with the value 3.2 (without this type facility,
the value would be the string "3.2"). In case of eval,
the value is processed as eval(value) such that values can become
lists, dictionaries, or other user-defined objects. In the latter
case, the globals_ keyword must be set explicitly so that this
function has access to the user's classes (eval(value, globals_)).
For example, 'my fifth option' will evaluate to StringFunction
object, but this requires supply of globals_ with the user's
imported modules (from StringFunction and math).

There is also a syntax for marking options to be read-only, i.e.,
these options are meant to be set in configuration files and
not changed later in the program. Preceeding the type specification
by an r or R indicates the read-only property, e.g.::

  my first option = r<bool> off

Options set in the configuration file can be overridden by
associated environment variables whose names are on the form::

  prefix_section_option

For example, an option 'DEBUG' in section 'globals' can have
an associated environment variable MYPACK_globals_DEBUG,
if the prefix is MYPACK. The prefix is set in a special section
called 'modes' (see below).

Options can also be overridden by command-line arguments. The
command-line options have the same names as the associated
environment variable names, but additionally prefixed by a double
hyphen, e.g. --MYPACK_globals_DEBUG.
The 'command line arguments' option in the 'modes' section
must have a true value for this functionality to be active.

Here is an example of the 'modes' section::

  [modes]
  envir prefix = MATHPACK
  command line arguments = yes

If section or option names contain space(s), the corresponding
environment variable name and command-line option have the space(s)
replaced by underscore(s), e.g.::

  MATHPACK_my_section_my_first_option
  --MATHPACK_my_section_my_first_option

Such command-line options and values are removed from sys.argv after
being read.

A convenient feature of configuration files is that variable interpolation
is possible(see the documentation of ConfigParser in the Python
Library Reference). Here is an example::

  [DEFAULT]
  path = /my/home/dir/

  [storage]
  datapath = %(path)s/data
  input = %(path)s/%(datapath)s/input

One can also provide variables for being used in variable interpolation
throught the default_dict4intpl argument to this function.

A configuration file is searched for and read in as follows
(in the listed order):

  1. basename.cfg in the default_file_location directory,
  2. basename.cfg files for each directory in other_locations list,
  4. .basename.cfg in the user's home directory,
  3. .basename.cfg in the directory where the main script is running.

This priority implies that the a config file in the current working
directory will override any user or any other system settings.
"""
__doc__ += _configfile_description


import os, sys

VALUE=0; STR2TYPE=1; READONLY=2  # logical names for list indices

__all__ = ['tobool', 'config_parser_frontend', 'values_only', 'dict2xml']

def tobool(value):
    """
    Convert value (1, '1', 0, '0', 'yes', 'true', 'no', 'false', 'on',
    'off', or any integer) to a bool object. The string values are
    treated in a case-insensitive way.
    """
    trues  = "1", "yes", "Yes", "YES", "true",  "True",  "on",  1
    falses = "0", "no",  "No",  "NO",  "false", "False", "off", 0
    value = value.lower() # case-insensitive check

    if value in trues:
        value = True
    elif value in falses:
        value = False
    elif isinstance(value, int):
        return bool(value)
    else:
        raise ValueError('the value %s cannot be converted to bool' % value)
    return value

def _option_interpolation_error(files, section, option, value,
                                str2type, read_only):
    if read_only:
        r = 'r'
    else:
        r = ''
    raise ValueError('configuration file error in %s\n'\
                     'section [%s], option "%s": do not use %s<%s>\n'\
                     'specifications in options that are to be '\
                     'substituted in other options: %s' % \
                     (files, section, option, r, str2type, value))

def load_config_file(name,
                     default_file_location=None,
                     extension='.cfg',
                     other_locations=[],
                     case_sensitive_options=True,
                     default_dict4intpl={}):
    """
    Load a config file with the format implied by the ConfigParser
    module (Windows .INI files).

    A config file is searched for and read in as follows (in the listed order):

      1. name.cfg in the default_file_location directory,
      2. name.cfg files for each directory in other_locations list,
      4. .name.cfg in the user's home directory,
      3. .name.cfg in the directory where the main script is running.

    This priority implies that the a config file in the current working
    directory will override any user or any other system settings.

    @param name: name stem of config file, e.g., "mytools" (then
    "mytools.cfg" is the complete name of the config file if extension
    is ".cfg").
    @param default_file_location: name of directory containing a
    file name.extension with default values (to be read before other
    configuration files). If None, the directory where this module
    (configdata) resides will be tried. A typical value for a system
    configuration file is os.path.dirname(__file__) (i.e., the same
    directory as the calling module in the package).
    @param extension: extension of config file (name.extension is the
    complete name).
    @param other_locations: list of directories with name.extension files.
    @param default_dict4intpl: dictionary with variable names and values
    for use in variable interpolation in the configuration file.
    @param case_sensitive_options: by default, the options in configuration
    files are transformed to lower case, so setting this parameter to True,
    makes options case sensitive.
    @param default_dict4intpl: dictionary with variable names and values
    for use in variable interpolation in the configuration file.
    @return: a SafeConfigParser object and a list of filenames of the
    files that were read to set parameters in the SafeConfigParser object.
    """
    import ConfigParser
    config = ConfigParser.SafeConfigParser(default_dict4intpl)
    if case_sensitive_options:
        config.optionxform = str

    if default_file_location is None:
        # try the directory where this module resides:
        default_file_location = os.path.dirname(__file__)

    default_config_file = os.path.join(default_file_location,
                                       '%s%s' % (name, extension))
    read_files = []
    if os.path.isfile(default_config_file):
        config.readfp(open(default_config_file, 'r'))
        read_files.append(default_config_file)
    #else:
    #    print 'No data in', default_config_file
    dirs = other_locations
    candidate_files = [os.path.join(loc, '.%s%s' % (name, extension)) \
                       for loc in dirs] + \
                       [os.path.expanduser('~/.%s%s' % (name, extension))] + \
                       [os.path.join(os.curdir, '.%s%s' % (name, extension))]
    #print candidate_files
    files = config.read(candidate_files)
    read_files = read_files + files
    return config, read_files


def config_parser_frontend(basename,
                           default_file_location,
                           extension='.cfg',
                           other_locations=[],
                           default_dict4intpl={},
                           globals_=None):
    """
    =======================  =============================================
    Parameter                  Description
    =======================  =============================================
    basename                 name stem of config file, e.g., "mytools"
                             (then "mytools.cfg" is the complete name
                             of the config file if extension is ".cfg").
    extension                extension of config file (basename.extension
                             is the complete name)
    default_file_location    name of directory containing a file
                             basename.extension with default values
                             (to be read before other configuration files).
    other_locations          list of directories with basename.extension
                             files
    default_dict4intp        dictionary with variable names and values
                             for use in variable interpolation in the
                             configuration file
    globals_                 dictionary of global names that are used when
                             running eval on option values. If None, the
                             global names in this module are used
    return                   a dictionary with [section][option] keys and
                             a values of the form of a three-element list
                             holding the option value, the string to right
                             type conversion function (callable), and a bool
                             indicator if the value is read-only.
                             The other returned object is a list of filenames
                             of the configuration files that were loaded
    =======================  =============================================

Regarding default_file_location, a None value indicates the directory
where this module (configdata) resides will be tried. A typical value
for a system configuration file is ``os.path.dirname(__file__)`` (i.e.,
the same directory as the calling module in the package).
    """
    if globals_ is None:
        globals_ = globals()

    # load configuration file:
    config, files = \
            load_config_file(basename,
                             default_file_location=default_file_location,
                             extension=extension,
                             other_locations=other_locations,
                             case_sensitive_options=True,
                             default_dict4intpl=default_dict4intpl)

    # dictionary with [section][option] keys and values as a
    # list [value, str2type, readonly]
    data = {}

    # read 'modes' section first to see if settings in the config
    # file can be overridden by environment variables and/or
    # command-line options:
    envir_prefix = ''
    cml_arg = False
    section = 'modes'
    if config.has_section(section):
        data[section] = {}
        for option in ('envir prefix', 'environment variable prefix'):
            if config.has_option(section, option):
                envir_prefix = config.get(section, option)
                data[section][option] = [envir_prefix, str, True]
            break
        for option in ('command line arguments',):
            if config.has_option(section, option):
                cml_arg = config.getboolean(section, option)
            data[section][option] = [cml_arg, bool, True]

    for section in config.sections():
        if section == 'modes':   # 'modes' is already processed above
            continue
        data[section] = {}
        for option in config.options(section):
            value = config.get(section, option)
            # check if value has the syntax "<str2type> expression"
            str2type = None
            if value.startswith('<'):
                read_only = False
                gt = value.find('>')
                str2type = value[1:gt]
                value = value[gt+1:].strip()
                # variable interpolation are destroyed by <str> specs;
                # could process all values without %(...)s first and
                # then remove all <type> specifications to make
                # variable interpolation correct
                if '<%s>' % str2type in value:
                    _option_interpolation_error(files, section, option,
                                                value, str2type, False)
            elif value.lower().startswith('r<'):
                read_only = True
                gt = value.find('>')
                str2type = value[2:gt]
                value = value[gt+1:].strip()
                # set this option in the config file so that
                # variable interpolation may work:
                config.set(section, option, value)
                if 'r<%s>' % str2type in value:
                    _option_interpolation_error(files, section, option,
                                                value, str2type, True)
            if str2type is not None:
                if str2type == 'bool' or str2type == 'tobool':
                    value = tobool(value)
                    data[section][option] = [value, tobool, read_only]
                elif str2type == 'float':
                    data[section][option] = [float(value), float, read_only]
                elif str2type == 'int':
                    data[section][option] = [int(value), int, read_only]
                elif str2type == 'str':
                    data[section][option] = [str(value), str, read_only]
                elif str2type == 'eval':
                    data[section][option] = \
                                   [eval(value, globals_), eval, read_only]
            else:
                # no type specification, value becomes a string:
                data[section][option] = [value, str, False]

            # override file value by environment variable or
            # command-line argument?

            envir_var_name = envir_prefix + '_' + section + '_' + option
            envir_var_name = envir_var_name.replace(' ', '_')

            if envir_prefix:
                # override by environment variable:
                if envir_var_name in os.environ:
                    data[section][option][VALUE] = \
                    data[section][option][STR2TYPE](os.environ[envir_var_name])
            if cml_arg:
                cml_option = '--' + envir_var_name
                if cml_option in sys.argv:
                    try:
                        i = sys.argv.index(cml_option)
                        v = sys.argv[i+1]
                        # remove config option and value from sys.argv:
                        del sys.argv[i]  # option
                        del sys.argv[i]  # value
                    except IndexError:
                        print """
%s command-line option must be followed by a value!
""" % cml_option
                        sys.exit(1)

                    data[section][option][VALUE] = \
                           data[section][option][STR2TYPE](v)

    return data, files

config_parser_frontend.__doc__ = _configfile_description


def dict2xml(data, syntax='gnosis',
             section_name='section', option_name='option'):
    """
    Takes a data dictionary, as output from the config_parser_frontend
    function, and stores in a string with XML syntax.

    @param data: dictionary of the form data[section][option] = (v, s2t, ro),
    where v is a Python object (value), s2t is a callable, and ro is
    a bool.
    @param syntax: 'gnosis' gives gnosis XML_Pickler syntax, 'plain' gives
    a simpler to read syntax.
    @param section_name: the name of sections (highest key level) in the
    data dictionary to be used as XML tagname. ("section" and "option" are
    the terms used by the Python ConfigParser tool.)
    @param option_name: the name of options (lowest key level) in the
    data dictionary to be used as XML tagname.
    @return: a string with XML syntax.
    """
    if syntax == 'gnosis':
        from gnosis.xml.pickle import XML_Pickler
        class ClassWrapper(XML_Pickler):
            def __init__(self, data):
                self.data = data

        datawrap = ClassWrapper(data)
        return datawrap
    else:
        # simpler XML syntax:
        from .errorcheck import get_type
        s = '<data dictionary>\n'
        indent = 4
        for section in data:
            current_indent = ' '*indent
            s += '%s<%s>%s</%s>\n' % \
                 (current_indent, section_name, section, section_name)
            for option in data[section]:
                value, str2type, read_only = data[section][option]
                current_indent = ' '*indent*2
                s += '%s<%s>%s</%s>\n' % \
                     (current_indent, option_name, option, option_name)
                current_indent = ' '*indent*3
                s += '%s<value type="%s" readonly="%s">%s</value>\n' % \
                (current_indent, get_type(value), read_only, value)
        s += '</data dictionary>\n'
        return s

def values_only(data):
    """
    Strip the three-tuple (value, str2type, readonly) in the dictionary
    returned from config_parser_frontend to a dictionary with option
    values only.
    """
    import copy
    rdata = copy.deepcopy(data)   # data.copy() is only shallow copy!
    for section in rdata:
        for option in rdata[section]:
            rdata[section][option] = rdata[section][option][0]
    return rdata

def _test():
    configdata = """
[modes]
; Enable setting variables by environment variables with
; prefix_variablename, e.g., MyProject_section_option
envir prefix = MyProject

; Enable reading from command line through --MyProject_section_option
command line arguments = on

[global directories]
projects = r<str> projects
templates = r<str> templates
project template = r<str> %(templates)s/project

[file extensions]
project = .igm
report = r<eval> ['.html', '.htm']

[debugging]
DEBUG = <int> 0
VERBOSE = <int> 1

[system messages]
run.warning.text = <str>
    Not all parent worksteps are checked in.
    Since the results must be reproducible, only those that are checked in will
    be used as data sources.

unknowndir.overwrite.title = <str> Overwrite selected directory?

[data files]
data glob = <str> *_simulation_results.*
"""
    f = open('tmp.cfg', 'w'); f.write(configdata); f.close()

    data, files = config_parser_frontend('tmp', os.curdir)
    import pprint
    pprint.pprint(data)
    data_values = values_only(data)
    pprint.pprint(data_values)
    print dict2xml(data)
    print dict2xml(data, syntax='plain')

if __name__ == '__main__':
    _test()
