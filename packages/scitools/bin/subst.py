#!/usr/bin/env python
import os, re, sys, shutil

def usage():
    print 'Usage: subst.py [-s -m -x --restore] pattern '\
          'replacement file1 file2 file3 ...'
    sys.exit(1)

def subst(pattern, replacement, files,
          pattern_matching_modifiers=None):
    """
    for file in files:
        replace pattern by replacement in file
        (a copy of the original file is taken, with extension .old~)

    files can be list of filenames, or a string (name of a single file)
    pattern_matching_modifiers: re.DOTALL, re.MULTILINE, etc.
    """
    if isinstance(files, str):
        files = [files]  # convert single filename to list
    return_str = ''
    for file in files:
        if not os.path.isfile(file):
            print '%s is not a file!' % file;  continue
        shutil.copy2(file, file+'.old~')  # back up file
        f = open(file, 'r');
        filestr = f.read()
        f.close()
        if pattern_matching_modifiers is not None:
            cp = re.compile(pattern, pattern_matching_modifiers)
        else:
            cp = re.compile(pattern)
        if cp.search(filestr):  # any occurence of pattern?
            filestr = cp.sub(replacement, filestr)
            f = open(file, 'w')
            f.write(filestr)
            f.close()
            if not return_str:  # initialize return_str:
                return_str = pattern + ' replaced by ' + \
                             replacement + ' in'
            return_str += ' ' + file
    return return_str


if __name__ == '__main__':
    if len(sys.argv) < 3: usage()
    from getopt import getopt
    optlist, args = getopt(sys.argv[1:], 'smx', 'restore')
    restore = False
    pmm = None  # pattern matching modifiers (re.compile flags)
    for opt, value in optlist:
        if opt in ('-s',):
            if pmm is None:  pmm = re.DOTALL
            else:            pmm = pmm|re.DOTALL
        if opt in ('-m',):
            if pmm is None:  pmm = re.MULTILINE
            else:            pmm = pmm|re.MULTILINE
        if opt in ('-x',):
            if pmm is None:  pmm = re.VERBOSE
            else:            pmm = pmm|re.VERBOSE
        if opt in ('--restore',):
            restore = True

    if restore:
        for oldfile in args:
            newfile = re.sub(r'\.old~$', '', oldfile)
            if not os.path.isfile(oldfile):
                print '%s is not a file!' % oldfile; continue
            os.rename(oldfile, newfile)
            print 'restoring %s as %s' % (oldfile,newfile)
    else:
        pattern = args[0]; replacement = args[1]
        s = subst(pattern, replacement, args[2:], pmm)
        print s  # print info about substitutions
