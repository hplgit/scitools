#!/usr/bin/env python

"""
Regression module for automating regression tests.

    ================   =================================================
          Class                          Description
    ================   =================================================
    TestRun            utilities for easy set up of regression tests
    TestRunNumerics    extensions of TestRun for numerical computing
    Verify             search for test scripts, run them, compare
                       new results with reference results
    VerifyDiffpack     tailored Verify for Diffpack (incl. compilation)
    FloatDiff          visual diff between files with real numbers
    ================   =================================================

Usage
-----

Let us start with a very simple Python script, circle.py, for which we
would like to create a regression test::

  #!/usr/bin/env python
  '''Numerical integration of circular motion.'''
  import math, sys, os

  R=1; w=2*math.pi;  # global constants
  def advance(x, y, dt, t):
      '''advance (x,y) point one time step dt with Forward Euler,
         the equations describe circular motion of a body:
         dx/dt = -w*R*cos(2pi*w*t), dy/dt = w*R*sin(2pi*w*t)
      '''
      x = x - dt*w*R*math.sin(w*t);  y = y + dt*w*R*math.cos(w*t)
      return (x,y)

  # integrate from 0 to tstop
  try:
      tstop = float(sys.argv[1]); dt = float(sys.argv[2])
  except:
      print 'Usage: %s tstop dt' % sys.argv[0]; sys.exit(1)

  # make output format compatible with the plotpairs.py script:
  xmax = R*1.8; xmin = -xmax; ymin = xmin; ymax = xmax
  print xmin, xmax, ymin, ymax
  n = int(tstop/dt) + 1;
  x = R; y = 0
  for i in range(n):
      t = i*dt
      x, y = advance(x, y, dt, t)
      print x, y
  print 'end'

This script takes two input parameters from the command line:
the stop time for the simulation, and the time step.
The output is a series of numbers. We may run the script as::

  unix> python circle.py 3 0.1 > result

Let us assume that we are sure that the produced results in this
case are correct. A regression test then means that we can
automatically (in the future) run the above command and compare
the new results with archived correct results.

The procedure for using the Regression module in this examples
goes as follows.

  1. Create a name of the test, say "circle".
  2. Create circle.verify for running the test and saving
     desired results in a file circle.v.
  3. If we believe the results are correct, copy circle.v to
     circle.r. This circle.r file represents the archived correct
     results.

Later, we may run::

  unix> regression.py verify circle

to rerun the test and investigate differences between circle.v
(new results) and circle.r (archived correct results).
A whole directory tree can be examined for tests (.verify files)
by a similar command::

  unix> regression.py verify root-of-tree

Sometimes the new results are correct, but there are significant
differences between old and new results, because of, e.g., a change
in output formatting. New results can in this case be updated to
archive status by::

  unix> regression.py update root-of-tree

For the circle.py script, a typical circle.verify script takes
the following trivial form if we write it in bash::

  #!/bin/sh
  ./circle.py 3 0.1 > circle.v

The Regression module has tools for running programs, automatically
measuring CPU time, selecting lines from a file to put in the .v
file, ignoring round-off errors in numerical results, etc.
A more sophisticated test, which also accounts for numerical precision
in the output, goes as follows (to understand the various statements
you will need to consult Appendix B.4 in the textbook "Python Scripting
for Computational Science", by H. P. Langtangen)::

  #!/usr/bin/env python
  import os, sys
  from Regression import TestRunNumerics, defaultfilter
  test = TestRunNumerics('circle2.v')
  test.run('circle.py', options='1 0.21')
  # truncate numerical expressions in the output:
  test.approx(defaultfilter)
  # generate circle2.vd file in correct format:
  fd = open('circle2.vd', 'w')
  fd.write('## exact data\n')
  # grab the output from circle.py, throw away the
  # first and last line, and merge the numbers into
  # one column:
  cmd = 'circle.py 1 0.21'
  output = os.popen(cmd)
  res = output.readlines()
  output.close()
  numbers = []
  for line in res[1:-1]: # skip first and last line
      for r in line.split():
          numbers.append(r)
  # dump length of numbers and its contents:
  fd.write('%d\n' % len(numbers))
  for r in numbers: fd.write(r + '\n')
  fd.close()

This sample script can be adapted to a wide range of cases.
"""

import os, time, sys, string, re
from scitools.misc import system as os_system
from types import *
try:
    import Tkinter, Pmw
    _has_TkPmw = True
except ImportError:
    # cannot run floatdiff tools
    _has_TkPmw = False
    pass


class TestRun:
    """
    Utility for writing individual regression tests.
    Example on usage:
    from scitools.Regression import TestRun
    test = TestRun("test1.v")
    # run a program, place output on test1.v:
    test.run("myprog", options="-g -p 3.2", inputfile="test1.i")
    # append a file to test1.v:
    test.append("res1.dat")
    """


    def __init__(self,
                  logfile,         # .v file
                  removepath=' '   # remove this from sys.argv[0] output
                  ):
        """Clean up logfile, create a new one with header."""

        # use absolute path such that it is easy to write to the
        # logfile even after an os.chdir is performed

        self.logfile  = os.path.join(os.getcwd(),logfile)
        if string.find(logfile, '.v') == -1:
            raise ValueError('error in logfile name; must contain .v suffix')

        # remove logfile if it exists:
        if os.path.isfile(self.logfile): os.remove(self.logfile)

        # remove the detailed version as well:
        self.dlogfile = logfile + '-d'
        if os.path.isfile(self.dlogfile): os.remove(self.dlogfile)

        # make the logfile:
        vfile = open(self.logfile, 'w')
        tm = time.localtime(time.time())
        removepath = removepath + '/'
        self.scriptfilename = string.replace(sys.argv[0],removepath,'')
        vfile.write('%s: test performed on %d.%02d.%02d ' % \
                    (self.scriptfilename,tm[0],tm[1],tm[2]))
        if os.name == 'posix':  # is 'posix', 'nt' or 'mac'
            # unix
            u = os.uname()
            #vfile.write('(%s %s running %s)' % (u[1],u[4],u[0]))
            # this information is repeated at the end
        vfile.write('\n\n')
        vfile.close()

        # make a scratch directory for storing, e.g., gif-files:
        if 'HOME' in os.environ:
            self.scratchdir = os.path.join(os.environ['HOME'], 'tmp')
        else:
            if sys.platform.startswith('win'):
                self.scratchdir = r'C:\regression_temp'
            else:
                self.scratchdir = '/tmp/regresson_temp'
        if os.path.isfile(self.scratchdir):
            os.remove(self.scratchdir)
        if not os.path.isdir(self.scratchdir):
            os.mkdir(self.scratchdir)

        # add current working directory to the path:
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + os.curdir

    def run(self, program, options='', inputfile=''):
        """Run program, store output on logfile."""
        # the logfile is always opened in the constructor so
        # we can safely append here
        vfile = open(self.logfile, 'a')
        vfile.write('\n#### Test: %s' % (self.scriptfilename))
        vfile.write(' running %(program)s %(options)s\n' % vars())
        vfile.close()

        # do not use time.clock() to measure CPU time; it will not
        # notice the CPU time(here waiting time) of a system command
        t0 = os.times()  # [user,system,cuser,csystem,elapsed]
        if inputfile == '':
            cmd = '%s %s >> %s' % (program,options,self.logfile)
        else:
            cmd = '%s %s < %s >> %s' % (program,options,inputfile,self.logfile)
        failure, output = os_system(cmd, failure_handling='silent')
        if failure:
            vfile = open(self.logfile, 'a')
            msg = 'ERROR in %s: execution failure arose from the ' \
                  'command\n  %s\n\n%s\n\n' % (self.scriptfilename,cmd,output)
            vfile.write(msg)
            vfile.close()
            print msg
        # write CPU time of system command(user+system time
        # of child processes):
        t1 = os.times(); tm = t1[2] - t0[2] + t1[3] - t0[3]
        vfile = open(self.logfile, 'a')
        vfile.write('CPU time of %(program)s: %(tm).1f seconds' % vars())
        #if re.search('(x|sun)',sys.platform):
        if os.name == 'posix':  # is 'posix', 'nt' or 'mac'
            # unix
            u = os.uname()
            vfile.write(' on %s %s, %s' % (u[1],u[4],u[0]))
        vfile.write('\n\n')

    def loadfile(self, file):
        """Return a file as a list of lines for text processing."""

        if not os.path.isfile(file):
            print 'File',file,'does not exist'; sys.exit(1)
        FILE = open(file, 'r')
        lines = FILE.readlines()
        FILE.close()
        return lines

    def grepfile(self, regex, file, return_lineinfo=1):
        """
        Return a text consisting of the lines matching regex
        (regex can be string or list of strings, and
        return_lineinfo is true if each matched line is
        prefixed with the filename and the line file as
        a list of lines for text processing).
        """

        if type(regex) == type(''):
            regex = [regex]  # assume regex is a list of regex

        if not os.path.isfile(file):
            print 'File',file,'does not exist'; sys.exit(1)

        FILE = open(file, 'r')
        lines = FILE.readlines()
        FILE.close()
        matched_lines = []
        line_counter = 0
        for line in lines:
            line_counter += 1
            for r in regex:
                if re.search(r, line):
                    if return_lineinfo:
                        line = '%s %5d: ' % (file,line_counter) + line
                    matched_lines.append(line)
        return string.join(matched_lines, '\n')

    def write(self, text):
        """Write message to logfile."""
        vfile = open(self.logfile, 'a')
        vfile.write('\n--------------------------------------------------\n')
        vfile.write(text + '\n')
        vfile.write(  '--------------------------------------------------\n')
        vfile.close()

    def silentrun(self, program, options=''):
        """Run program without storing output on logfile."""

        if os.name == 'posix':
            # can write to /dev/null:
            failure = os.system('%s %s > /dev/null' % (program,options))
        else:
            failure = os.system('%s %s' % (program,options))
        if failure:
            vfile = open(self.logfile, 'a')
            msg = 'ERROR in %s: execution failure with %s %s\n' % \
                 (self.scriptfilename,program,options)
            vfile.write(msg)
            print msg

    def graphics(self, program, options=''):
        """
        Run e.g. graphics program if the environment variable
        BATCH_REGRESSION is not set.
        """
        batch = int(os.environ.get('BATCH_REGRESSION', 0))
        if not batch:
            failure, output = os_system('%s %s' % (program,options),
                                        failure_handling='silent')
            if failure:
                vfile = open(self.logfile, 'a')
                msg = 'ERROR in %s: execution failure with %s %s\n%s\n' % \
                      (self.scriptfilename,program,options,output)
                vfile.write(msg)
                print msg

    def append(self, file, maxlines=0):
        """Append a file or a list of files to the logfile."""

        vfile = open(self.logfile, 'a')

        # We need different code depending in whether file is a string
        # (a filename) or a list of filenames(e.g. from glob.glob).
        # The types module defines the names of the built-in types
        # in Python(here we need StringType and ListType)

        if isinstance(file, str):
            filelist = [file]  # make a list
        elif isinstance(file, list):
            filelist = file
        else:
            print 'ERROR in %s: append(file,...), the arg is of illegal '\
                  'type %s' % (self.scriptfilename,type(file))

        for f in filelist:
            if not os.path.isfile(f):
                vfile.write('%s: No file named %s was found by Regression.TestRun.append' % \
                            (self.scriptfilename,f))
                print 'No file named',f,'was found by Regression.TestRun.append'
                sys.exit(1)
            FILE = open(f, 'r')
            lines = FILE.readlines()
            FILE.close()
            vfile.write('\n\n----- appending file %s ' % f)
            if maxlines <= 0:
                printlines=len(lines)   # print all lines
            else:
                printlines = maxlines
                if printlines > len(lines):
                    printlines = len(lines)
                else:
                    vfile.write('(just %d lines) ' % printlines)
            vfile.write('------\n')
            #print 'treating file',f,'with',printlines,'lines'
            for i in range(printlines):
                vfile.write(lines[i])
        vfile.close()

    def picture(self, psfile):
        """Insert HTML commands for a gif picture."""
        # convert to gif:
        filestem = re.sub(r'(.*)\.[e]?ps', '', psfile)
        print 'picture: psfile=',psfile,'filestem=',filestem
        os_system('convert %s gif:%s.gif' % (psfile, filestem))
        pid = os.getpid()  # use pid to makea unique giffile name
        giffile_with_full_path = '%s/%s-%d.gif' % \
                                (self.scratchdir,pid,filestem)
        os.rename('%s.gif %s' % (filestem, giffile_with_full_path))
        self._insertgif (giffile_with_full_path)

    def movie(self, list_of_psfiles):
        """Insert HTML commands for an animated gif picture."""
        # convert to animated gif:
        filelist = string.join(list_of_psfiles, ' ')
        pid = os.getpid()  # use pid to make unique giffile name
        giffile_with_full_path = '%s/anim-%d.gif' % \
                                (self.scratchdir,pid)
        print 'making an animated gif sequence of psfiles:',filelist
        os_system('convert -loop 60 -delay 10 %s %s' % \
                  (filelist,giffile_with_full_path))
        self._insertgif (giffile_with_full_path)


    def _insertgif (self, giffile_with_full_path):
        vfile = open(self.logfile, 'a')
        vfile.write('<IMG SRC="%s">' % giffile_with_full_path)
        # always trigger a diff by inserting a comment containing time.time():
        vfile.write(' <!-- diff-triggering comment: %f -->\n<P>\n' %\
                     time.time())



class TestRunNumerics(TestRun):
    """
    Extends class TestRun with an additional logfile for
    dump of large sets of floating-point numbers for a second-level
    regression test.
    """

    def __init__(self, logfile, removepath='  '):
        TestRun.__init__(self, logfile, removepath)
        self.floatlogfile = logfile + 'd'
        if os.path.isfile(self.floatlogfile):
            os.remove(self.floatlogfile)
        # don't bring the float logfile into existence if not necessary


    def _approxline(self, line, realfilter):
        """
        Replace floating-point numbers in line by approximate
        numbers(computed by realfilter)(called from approx).
        """

        # the returned line has name newline
        newline = line

        # regex for real numbers (but not integers, \. must be a part!)
        c = re.compile(r"""
        (                            # start group
        [+\-]?\d\.\d+[Ee][+\-]\d\d   # -1.34E-01 etc
        |                            # OR
                                     # %f format with more than 3 decimals:
        [+\-]?\d+\.\d\d\d\d+         # -1.2556, not 7, not 7., not 7.22
        |                            # OR
        [+\-]?\.\d\d\d\d+            # .3656 (more than 4 decimals)
        )                            # end group
        """,
                       re.VERBOSE)
        # possible problem: 0 or 0.0 is never approximated by the
        # regex above (but 0.00E+00 is!)

        b = c.search(line)
        index = 0   # start of substring to test for next match
        while b:
            strno = b.group()
            no = float(strno)
            newno = realfilter(no)
            newline = string.replace(newline, strno, newno, 1)
            #print 'found %s, replaced by %s, to form\n   %s\n' % (strno, newno, newline)
            # b.end() refers to local index in current substring:
            index = index + b.end()
            # further search in the substring starting with index:
            b = c.search(line[index:])
        return newline

    def approx(self, realfilter):
        """
        Run through logfile, find all real numbers and replace
        them by approximate real numbers computed by realfilter.
        """

        logfile_copy = self.logfile+'.tmp'
        os.rename(self.logfile, logfile_copy)
        vfile = open(logfile_copy, 'r')
        afile = open(self.logfile, 'w') # new approximate logfile
        for line in vfile:
            # strip some digits:
            line = self._approxline(line, realfilter)
            # replace -0 by 0:
            line = re.sub(r'[eE]-00', 'e+00', line)
            line = re.sub(r'-0([, )])', '0\g<1>', line)
            afile.write(line)
        vfile.close()
        afile.close()

    def floatdump(self, program, options=''):
        """Run program and direct output to self.floatlogfile."""
        if not os.path.isfile(self.floatlogfile):
            # bring the float logfile into existence:
            ff = open(self.floatlogfile, 'w'); ff.close()

        cmd = '%s %s >> %s' % (program,options,self.floatlogfile)
        failure, output = os_system(cmd, failure_handling='silent')
        if failure:
            msg = 'ERROR in %s: execution failure arose from the ' \
                  'command\n  %s\n%s\n\n' % (self.scriptfilename,cmd,output)
            print msg

        # improvement: load output from system command into a list
        # of strings and examine the output format (must be in the
        # valid format!) OR: dump in a separate file, read it line
        # by line (better) and if the format is ok, append it

        # format specification: see test program at the end of the file

def defaultfilter(r):
    if abs(r) < 1.0E-14: r = 0.0  # set very small numbers to 0 exactly
    p = '%11.4e' % r
    return p

def exactfilter(r):
    if abs(r) < 1.0E-14: r = 0.0  # set very small numbers to 0 exactly
    p = '%g' % r                  # keep the precision
    return p

import stat
def walk(top, func, arg):
    """
    Simple copy of os.path.walk, but does not break when a file
    marked for visit is deleted during the process.
    """
    try:
        names = os.listdir(top)
    except os.error:
        return
    names.sort()
    func(arg, top, names)
    for name in names:
        name = os.path.join(top, name)
        try:
            st = os.lstat(name)
            if stat.S_ISDIR(st[stat.ST_MODE]):
                walk(name, func, arg)
        except:
            #print 'walk: could not work with the file',name
            #many files are naturally cleaned up during regression
            #tests (.o files e.g.)
            pass

class Verify:
    """
    Automates regression tests by running through a directory
    tree, searching for .verify files, executing them and
    comparing .v with .r files. The result of the comparison
    (the differing lines) are reported in HTML documents.
    """
    def __init__(self,
                 root='.',        # root directory or a single file
                 task='verify',   # 'verify' or 'update'
                 diffsummary = 'verify_log',
                 diffprog = None  # alternatives: diff, diff.py, diff.pl
                 ):
        # files are opened with changing os.getcwd so we need full path:
        self.diffsummary = os.path.join(os.getcwd(),
                                        diffsummary + '.htm')
        self.diffdetails = os.path.join(os.getcwd(),
                                        diffsummary + '_details.htm')
        if diffprog is None:
            self.diffprog = os.environ.get('DIFFPROG', 'diff.py')
            #self.diffprog = os.environ.get('DIFFPROG', 'diff')  # Unix diff
        else:
            self.diffprog = diffprog

        # remove old files, create new ones:
        if os.path.isfile(self.diffsummary):
            os.remove(self.diffsummary)
        if os.path.isfile(self.diffdetails):
            os.remove(self.diffdetails)

        # use font colors in the HTML file to indicated the kind of diff
        self.GREEN = 'green'; self.RED = 'red'

        # bring files into existence and write HTML header:
        ds = open(self.diffsummary, 'w');
        ds.write('<html><body>\n'\
                  '<font color=%s>%s color</font>: true differences<br>\n'\
                  '<font color=%s>%s color</font>: CPU time differences '\
                  'only\n<p>\n' % (self.RED,self.RED,self.GREEN,self.GREEN))
        ds.close()
        ds_d = open(self.diffdetails, 'w')
        ds_d.write('<html><body>\n')
        ds_d.close()
        self.testcounter = 0

        # the main action: run tests and diff!
        if os.path.isdir(root):
            # walk through a directory structure:
            walk(root, self._search4verify, task)
        elif os.path.isfile(root):
            # run just a single test:
            file = root   # root is just a file
            dirname = os.path.dirname(file)
            if dirname == '': dirname = os.getcwd()
            self._singlefile(dirname, task, os.path.basename(file))
        else:
            print 'Verify: root=',root,'does not exist'
            sys.exit(1)

        # write HTML footer:
        ds = open(self.diffsummary, 'a');
        ds.write('\n</body></html>\n')
        ds.close()
        ds_d = open(self.diffdetails, 'a')
        ds_d.write('\n</body></html>\n')
        ds_d.close()

    def _singlefile(self, dirname, task, file):
        """Run a single regression test."""
        # does the filename end with .verify?
        #if re.search(r'\.verify$', file):
        #    basename = re.sub(r'\.verify$', '', file)
        if file.endswith('.verify'):
            basename = file[:-7]
            if task == 'update':
                self._update(dirname, basename)
            elif task == 'verify':
                print '\n\nrunning verification test in', dirname,
                self._diff(dirname, basename, file)

    def _search4verify(self, task, dirname, files):
        """Called by function walk."""
        # change directory to current directory:
        origdir = os.getcwd(); os.chdir(dirname)
        for file in files:
            self._singlefile(dirname, task, file)
        if task == 'verify':
            self.clean(dirname)
        # change directory back again (required by walk):
        os.chdir(origdir)

    def _update(self, dirname, basename):
        vfile = basename + '.v';  rfile = basename + '.r'
        if os.path.isfile(vfile):
            os.rename(vfile, rfile)
            print '   %s -> %s in %s' % (vfile,rfile,dirname)
        vfile = basename + '.vd';  rfile = basename + '.rd'
        if os.path.isfile(vfile):
            os.rename(vfile, rfile)
            print '   %s -> %s' % (vfile,rfile)

    def _diff(self, dirname, basename, scriptfile):
        """Run script and find differences from reference results."""
        # run scriptfile, but ensure that it is executable
        os.chmod(scriptfile, 0o755)
        # 0o755: owner all, group+others can read and execute
        # 0o644: owner r+w, group+others r
        self.run(scriptfile)

        # compare new output (.v) with reference results (.r)
        vfile = basename + '.v';  rfile = basename + '.r'
        if os.path.isfile(vfile):
            if not os.path.isfile(rfile):
                # if no rfile exists, copy vfile to rfile:
                os.rename(vfile, rfile)
            else:
                # compute difference:
                diffprog = self.diffprog
                if diffprog == 'diff.pl' or diffprog.startswith('diff.py'):
                    # diff.pl is slow for large files
                    # choose another program if filesize > 50K
                    Kb = os.path.getsize(vfile)/1000
                    if Kb > 50:
                        diffprog = 'diff -w'  # Unix C program
                        print 'Warning: switching diff program from',\
                              self.diffprog, 'to', diffprog
                diffcmd = '%s %s %s' % (diffprog,rfile,vfile)
                print '...' + diffcmd
                time.sleep(1)
                res = os.popen(diffcmd).readlines()
                ndifflines = len(res)
                summaryline = '%(dirname)s: %(rfile)s '\
                              '%(vfile)s   %(ndifflines)d lines' % vars()

                # no of tests so far:
                self.testcounter = self.testcounter + 1

                ds = open(self.diffsummary, 'a')
                if ndifflines == 0:
                    ds.write(summaryline); ds.write(' differ')
                else:
                    # write more detailed info about differences

                    # check if the diff lines are only CPU-time diffs
                    if self.diffCPUonly(res):
                        cpu_msg = ' (CPU time only!)'
                        font_color = self.GREEN
                    else:
                        cpu_msg = ''
                        font_color = self.RED
                    ds.write('<FONT COLOR=%s>%s</FONT>' % \
                             (font_color,summaryline))

                    # link to file with details:
                    anchor = 'part' + str(self.testcounter)
                    ds.write(' <A HREF="%s#%s">differ</A>%s' % \
                             (self.diffdetails,anchor,cpu_msg))

                    # write the detailed summary:
                    ds_d = open(self.diffdetails, 'a')
                    ds_d.write('<P><A NAME="%s">'\
                    '<B>%s differ</B></A>'\
                    '<BR>The differences were calculated by %s.'\
                    '<PRE>\n' % (anchor,summaryline,diffprog))
                    ds_d.writelines(res)
                    ds_d.write('\n</PRE>\n')
                    if diffprog != self.diffprog:
                        ds_d.write('<P><B>NOTE: %s was used instead of %s '\
                                   'because of the large filesizes!</B><P>' % \
                                   (diffprog,self.diffprog))

                    # check if floating-point files are present:
                    vfile = basename + '.vd';  rfile = basename + '.rd'
                    if os.path.isfile(vfile):
                        if not os.path.isfile(rfile):
                            os.rename(vfile, rfile)
                        else:
                            # write a shell file that can be
                            # executed from a link:
                            shfilename = os.path.join(os.getcwd(),'tmp.'+basename+'_fdiff.sh')
                            shfile = open(shfilename, 'w')
                            shfile.write('floatdiff.py %s %s\n' %\
                                         (vfile, rfile))
                            shfile.close()
                            os.chmod(shfilename, 0o755)
                            ds_d.write(
                             '<P><A HREF="%s">Floating-point difference '\
                             'between %s and %s without any approximations</A>\n' % \
                               (shfilename,vfile, rfile))
                            # check if there _are_ differences...
                            if os.name == 'posix':
                                diff = os.popen('diff %s %s | wc -l' % (vfile,rfile)).readlines()
                                diff = int(diff[0])
                                if diff == 0:
                                    ds_d.write(' (no differences!)\n')

                    ds_d.close()

                ds.write('<BR>\n')
                ds.close()
        else:
            print 'ran %s, but no %s.v file found - check that %s.verify defines %s.v as logfile' % (scriptfile,basename,basename,basename)
            sys.exit(1)

    def diffCPUonly(self, difflines):
        # do all differing lines contain something with cpu or date?
        cpu_only = 1
        for line in difflines:
            # avoid special diff.pl lines and date:
            if  not re.search(r'---', line) \
            and not re.search(r'Diffpack Version ', line) \
            and not re.search(r': test performed on ', line) \
            and not re.search(r'^\d+c\d+$', line) \
            and not re.search(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun) \w{3}\s+\d+ \d\d:\d\d:\d\d \d{4}', line) \
            and not re.search(r'diff-triggering comment', line):
                if not re.search(r'cpu', line, re.IGNORECASE):
                    cpu_only = 0; break
        return cpu_only

    # the run function can be overrided in subclasses and tailored to special
    # tests where it is necessary to, e.g., compile special applications
    # prior to running the script

    def run(self, scriptfile):
        # recall that os.chdir has been taken to the scriptfiles's dir
        path = os.path.join(os.curdir, scriptfile)
        # path is executable since we made an os.chmod in self._diff
        failure, output = os_system(path, failure_handling='silent')
        if failure:
            print 'Failure in regression test', path
            print output

    def clean(self, dirname):
        return


class VerifyDiffpack(Verify):
    """
    Extend class Verify with compilation of Diffpack applications,
    clean-up of applications, and a parameter self.makemode for running
    applications in opt or nopt mode.
    """

    def __init__(self, root='.', task='verify',
                 diffsummary = 'verify_log',
                 diffprog = None,
                 makemode = 'opt'):
        self.makemode = makemode
        # run all the stuff:
        Verify.__init__(self, root, task, diffsummary, diffprog)

    def run(self, scriptfile):
        """Run script, but compile the application first."""
        # is this a Verify directory? (recall that we have chdir'ed to dir)
        if string.count(os.getcwd(), '/Verify'):
            # go to parent directory (os.pardir is '..'):
            thisdir = os.getcwd();  os.chdir(os.pardir)
            #print '\na Verify dir with a parent dir\n  ',os.getcwd(),\
            #      '\nLet's compile!\n'
            print '\n...compile app in', os.getcwd()
            if os.path.isfile('Makefile'):
                # yes, we have a makefile!
                failure, output = os_system('Make MODE=%s' % self.makemode,
                                            failure_handling='silent')
                if failure:
                    print 'Could not compile in directory', os.getcwd()
            os.chdir(thisdir) # back to Verify dir

            print '\n\n...run regression test ''+scriptfile+'' for VerifyDiffpack.run:'
        # call parent class' run function:
        Verify.run(self,scriptfile)

    def clean(self, dirname):
        """Clean up files, typically executables etc."""
        # is this a Verify directory? (recall that we have chdir'ed to dir)
        if string.count(os.getcwd(), '/Verify'):
            # go to parent directory and clean application:
            thisdir = os.getcwd();  os.chdir(os.pardir)
            if os.path.isfile('Makefile'):
                # yes, we have a makefile!
                failure, output = os_system('Make clean',
                                            failure_handling='silent')
                if failure:
                    print 'Could not run Make clean in directory', os.getcwd()
            os.chdir(thisdir)

class FloatDiff:
    def __init__(self, master, file1, file2):
        if not _has_TkPmw:  # global variable set in top of the script
            raise ImportError('Could not import Tkinter and Pmw')

        self.master = master
        self.top = Tkinter.Frame(master, borderwidth=5)
        self.top.pack()
        self.GUI = 1  # true or false
        list = self.loadfiles(file1, file2)
        self.buildGUI(list, file1, file2)

        if self.GUI:
            self.canvas.resizescrollregion() # make the scrollbars right

        return

    def loadfiles(self, file1, file2):
        """
        Purpose: build "list", a list of relevant info for
        all differences found between file1 and file2
        (list can afterwards be visualized in buildGUI).
        """

        # first check if the files are identical:
        if os.name == 'posix':
            diff = os.popen('diff %s %s | wc -l' % (file1,file2)).readlines()
            diff = int(diff[0])
            if diff == 0:
                print 'files %s and %s are identical, no need to launch GUI' \
                      % (file1,file2)
                self.GUI = 0
                return None

        list = []
        f1 = open(file1, 'r');  f2 = open(file2, 'r')
        while 1:
            line1 = f1.readline(); line2 = f2.readline()
            if not line1 or not line2: break
            if re.search('^##',line1):
                if line1 != line2:
                    # strange; the two comment lines are different
                    print 'two comment lines are different!'
                    print 'line1:\n  ', line1
                    print 'line2:\n  ', line2
                comment = line1
            line1 = f1.readline(); line2 = f2.readline()
            if not line1 or not line2:
                print 'wrong datafile format; '\
                      'comment line not proceeded by data'
                sys.exit(1)
            if line1 != line2:
                print '%s has %s items, whereas %s has %s items' % \
                     (file1,line1,file2,line2)
                break
            nitems1 = int(line1)
            differences = []
            max = -1E+20; min = -max; avg = 0;
            for i in range(nitems1):
                s1 = f1.readline(); s2 = f2.readline()
                if not s1 or not s2:
                    print 'wrong datafile format'; sys.exit(1)
                # test that only one number is there... (no space)
                if re.search(' ', s1) or re.search(' ', s2):
                    print 'wrong datafile format'
                    print 'lines:','\n',s1,'\n',s2; sys.exit(1)
                r1 = float(s1); r2 = float(s2)
                # statistics:
                if (r1 > max):  max = r1
                if (r1 < min):  min = r1
                avg = avg + r1
                # difference?
                if s1 != s2:
                    # report this difference:
                    r = r1 - r2
                    differences.append((i, s1, s2, str(r)))
            avg = avg / nitems1
            list.append((comment, differences, max, min, avg))
        f1.close(); f2.close()
        return list

    def buildGUI(self, list, file1, file2):
        """Build list of fields and canvas (text and plot)."""

        if not list or not self.GUI:
            return

        buttonframe = Tkinter.Frame(self.top)
        buttonframe.pack(side='left')
        canvasframe = Tkinter.Frame(self.top)
        canvasframe.pack(side='right')

        self.fieldlist = Pmw.ScrolledListBox(buttonframe,
                listbox_selectmode = 'extended',
                vscrollmode='dynamic',
                label_text = 'list of fields',
                labelpos = 'n',  # needed if label_text is present
                listbox_width = 20,
                listbox_height = 20,
                selectioncommand = self.selectfield)
        self.fieldlist.pack()

        self.canvas = Pmw.ScrolledCanvas(canvasframe,
            borderframe = 1, labelpos = 'n',
            label_text = 'intelligent float diff between %s and %s' \
                                          % (file1,file2),
            usehullsize = 1, hull_width = 800, hull_height = 500,
            vscrollmode = 'static', hscrollmode = 'static'
            )
        self.canvas.pack(fill='both', expand=1)

        counter = 0
        self.graphs = []
        self.textdiffs = []
        self.rdata = []
        self.vdata = []
        self.ycoor = []
        maxdiffs = 0
        for (comment, differences, max, min, avg) in list:
            n = len(differences)
            if n > maxdiffs: maxdiffs = n

        for (comment, differences, max, min, avg) in list:
            tag = 'tag' + str(counter)
            n = len(differences)
            if n == 0:
                continue  # no diff, proceed with next

            textdiff = Tkinter.Text(self.canvas.interior(),
                                    width=52,height=maxdiffs+3,wrap='none')
                                    #width=52,height=str(maxdiffs)+'c',wrap='none')
            self.textdiffs.append(textdiff)
            textwin = self.canvas.create_window(0,0, anchor='nw',
                      window=self.textdiffs[counter], tag=tag)
            textdiff.insert('end',
            'line: %-10s      %-10s      float diff\n\n' % (file1,file2))
            for (i,s1,s2,r) in differences:
                textdiff.insert('end', '%4d: ' % i)
                self.highlight(textdiff, s1.strip(), s2.strip())
                textdiff.insert('end', '%-16g\n' % float(r))

            # create graph:

            self.rdata.append(Pmw.Blt.Vector())
            self.vdata.append(Pmw.Blt.Vector())
            self.ycoor.append(Pmw.Blt.Vector())
            # note: these vectors are recreated in the next part
            # of the loop, must have a list of such vectors, indexed
            # by counter!
            for j in range(n): self.ycoor[counter].append(j)
            for (i,s1,s2,r) in differences:
                self.vdata[counter].append(float(s1))
                self.rdata[counter].append(float(s2))
                graph = Pmw.Blt.Graph(self.canvas.interior(), width=300,
                                      height=str(maxdiffs)+'c')
            self.graphs.append(graph)
            graph.line_create('v',
                              xdata=self.vdata[counter],
                              ydata=self.ycoor[counter],
                              label='new results',
                              color='green', linewidth=2,
                              dashes='', symbol='')
            graph.line_create('r',
                              xdata=self.rdata[counter],
                              ydata=self.ycoor[counter],
                              label='reference',
                              color='red', linewidth=2,
                              dashes='', symbol='')
            graph.configure(title='plot of %s vs %s' % (file1,file2))
            #self.vavg = Pmw.Blt.Vector(); self.vavg = [avg]*n # does not work!

            plotwin = self.canvas.create_window(420,0, anchor='nw',
                      window=self.graphs[counter], tag=tag)
            graph.xaxis_configure(min=min, max=max)
            if n > 1: ymax = n-1
            else:     ymax = 1
            graph.yaxis_configure(min=0, max=ymax, descending=1)

            # insert item in list:
            self.fieldlist.insert('end',comment.strip()) # strip trailing \n
#            button = Tkinter.Button(buttonframe,
#                                    text=comment,
#                     command=lambda f=self.lift, c=self.canvas,
#                     p=self.graphs[counter], t=self.textdiffs[counter]:
#                               f(c,p,t))
#            button.pack(side='top')
            counter = counter + 1
        Tkinter.Button(buttonframe, text='QUIT',
                       command=self.master.quit).pack(side='top',pady=5)

    def selectfield(self):
        counter = int(self.fieldlist.curselection()[0])
        self.lift(self.graphs[counter],self.textdiffs[counter])

    def lift(self, win1, win2):
        win1.lift()
        win2.lift()
        # adapt the scroll region:
        self.canvas.resizescrollregion()

        #does not work with embedded windows:
        #self.canvas.lift(win1)
        #self.canvas.component('canvas').lift(win1)

    def highlight(self, text, s1, s2):
        markers = [1] * max(len(s1),len(s2))
        for i in range(min(len(s1),len(s2))):
            if s1[i] == s2[i]: markers[i] = 0
        for i in range(len(s1)):
            if markers[i] == 0:
                text.insert('end', str(s1[i]), 'equal')
            else:
                text.insert('end', str(s1[i]), 'diff')
        for i in range(16-len(s1)):
            text.insert('end', ' ', 'equal')
        for i in range(len(s2)):
            if markers[i] == 0:
                text.insert('end', str(s2[i]), 'equal')
            else:
                text.insert('end', str(s2[i]), 'diff')
        text.tag_configure('diff', background='cyan')
        for i in range(16-len(s2)):
            text.insert('end', ' ', 'equal')


def verify_file_template(casename, floats=False):
    s = """\
#!/usr/bin/env python
import os, sys
from scitools.Regression import TestRunNumerics, defaultfilter
test = TestRunNumerics('%s.v')
test.run('%s.py', options='...')
# test.append(somefile)
# truncate numerical expressions in the output:
test.approx(defaultfilter)
""" % (casename, casename)
    if floats:
        s += """
# generate %s.vd file in correct format:
fd = open('%s.vd', 'w')
fd.write('## exact data\n')
# write out float data in some way
# ...
fd.close()
""" % (casename, casename)
    vf = casename + '.verify'
    f = open(vf, 'w')
    f.write(s)
    f.close()
    print 'a template regression script is written to', vf


# tests of the current module:

def _test_floatdiff():
    root = Tkinter.Tk()
    #Pmw.initialise(root, fontScheme='pmw1')
    root.title('intelligent float diff')

    # make two files with almost equal data:
    file1 = 'tmptest.v';  file2 = 'tmptest.r'
    f1 = open(file1, 'w');  f2 = open(file2, 'w')
    f1.write("""## field1
10
1.345
3.45
6.9
4
9
8.999999
1.065432E-01
1.07E-01
1.06E-01
0.04E-01
## field2
11
1.6
3.1
2.0
1.1
1.7
1.8
1.9
0
-9.3
-14.4
-1.6
## field3
10
1.9
3.3
2.7
0.8
0.88
0.8000
0.8001
0.8002
0.8003
0.8004
""")
    f2.write("""## field1
10
1.344
3.66
7.0
4
9
8.999999
1.065432E-01
1.07E-01
1.06E-01
1.0376243E-01
## field2
11
1.61
3.11
2.01
1.11
1.7
1.8
1.9
0
-9.3
-14.400
-1.6000E+00
## field3
10
1.9
3.3
2.7
0.8001
0.88001
0.8000001
0.8001
0.8002
0.8003
0.8001
""")
    f1.close(); f2.close()
    fd = FloatDiff(root, file1, file2)
    root.mainloop()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s [template | verify | update | floatdiff] [verify/update-root]' % sys.argv[0]
        sys.exit(1)
    task = sys.argv[1]
    try:
        verifyroot = sys.argv[2]
    except:
        verifyroot = os.getcwd()

    if task == 'floatdiff':
        _test_floatdiff()
    elif task == 'template':
        verify_file_template('somecase')
    else:
        # task == 'verify' or task == 'update'
        v = Verify(verifyroot, task, 'verify_log')
        if task == 'verify':
            print 'check verify_log.htm'

