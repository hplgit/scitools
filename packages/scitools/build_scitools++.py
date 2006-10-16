#!/usr/bin/env python
# build the SciTools scitools++ directory with scitools
# and utilities

import os, glob, sys, shutil
join = os.path.join

# directories to be used:
olddir = 'previous-build-of-scitools++'
newdir = 'scitools++'
libdir = join('scitools++', 'lib')
bindir = join('scitools++', 'bin')
scitools_dir = join(libdir, 'scitools')
py_package_src = join(os.environ['SYSDIR'],'src','python','tools')

# start with a fresh scitools directory and move last scitools++ to
# a "copy" directory:
if os.path.isdir(olddir):
    shutil.rmtree(olddir)
if os.path.isdir(newdir):
    os.rename(newdir, olddir)
os.makedirs(newdir)
os.makedirs(libdir)
os.makedirs(bindir)
os.makedirs(scitools_dir)


st_src = join('lib', 'scitools')  # source code for scitools package

def os_system(cmd):
    failure = os.system(cmd)
    if failure:
        print 'FAILURE of command:\n', cmd
        sys.exit(1)
        
def clean(root, filetypes=['*.pyc', '*~', '*.pyo']):
    for type in filetypes:
        os_system("find %s -name '%s' -exec rm -f {} \;" % (root, type))
        
def copy_pure_scitools_files():
    """Copy pure scitools files from original place to new scitools++ tree."""
    print '********* copy pure scitools files **************'
    clean(root=st_src)
    files = glob.glob(join(st_src, '*'))
    # (shutil.copytree does not work properly for this type of copy)
    cmd = 'cp -r ' + ' '.join(files) + ' ' + scitools_dir
    print cmd
    os_system(cmd)

def copy_package(package):
    """Copy package as sub-package of scitools."""
    print '********* %s **************' % package
    clean()
    dir = join(os.pardir, package, 'lib', package)
    # (shutil.copytree does not work properly for this type of copy)
    cmd = 'cp -r ' + dir + ' ' + scitools_dir
    print cmd
    os_system(cmd)

def rename_py4cs_to_scitools(directory):
    """Rename py4cs to scitools in directory/*.py files."""
    pyfiles = glob.glob(join(directory, '*.py'))
    for file in pyfiles:
        os_system(r"subst.py 'py4cs\.' scitools. " + file)
    # (some of the "from scitools.... import ..." could be replaced by
    # the standard "from scitools import *")
    
def copy_scriptingbook_tools():
    """Copy scripting/src/tools scripts to scitools++/bin."""
    print '********* copy $scripting/src/tools **************'
    files = ['_gnuplot.py', 'diff.pl', 'diff.py', 
             'file2interactive.py', 'floatdiff.py', 'gnuplot.bat', 
             'ps2mpeg.py', 'regression.py', 'subst.py', 'timer.py']
    print files
    path = join(os.environ['scripting'], 'src', 'tools')
    for file in files:
        shutil.copy(join(path ,file), bindir)

    rename_py4cs_to_scitools(bindir)
    
def copy_py4cs():
    """
    Copy py4cs to scitools directory.
    This is convenient since scripts do import py4cs.mod and we
    substitute this by import scitools.mod. Hence, mod should be in
    the scitools directory.
    """
    print '********* copy $scripting/src/tools/py4cs **************'
    files = ['BoxField.py', 'BoxGrid.py', 'CanvasCoords.py', 'DrawFunction.py',
             'FuncDependenceViz.py', 'FunctionSelector.py', 'NumPyDB.py',
             'ParameterInterface.py', 'PrmDictBase.py', 'Regression.py',
             'StringFunction.py', 'convergencerate.py', 'errorcheck.py',
             'filetable.py', 'misc.py', 'multipleloop.py', 'numpytools.py']
    print files
    path = join(os.environ['scripting'], 'src', 'tools', 'py4cs')
    for file in files:
        shutil.copy(join(path, file), scitools_dir)
        print join(path, file), scitools_dir

    rename_py4cs_to_scitools(scitools_dir)

def remove_svn_files(root=st_src):
    print '********* remove svn directories **************'
    cmd = 'find %s -name ".svn" -print -exec rm -rf {} \;' % root
    os_system(cmd)

def copy_third_party_modules():
    """
    Copy installed modules to scitools++.
    An alternative is to copy the source of these modules and
    run multiple setup.py in scitools++ to install each dir in scitools++.
    The set-up now is that scitools++ should just be in PYTHONPATH and
    then everything is correctly installed.
    """
    print '********* copy third-party modules to scitools++ **************'
    path = join(sys.prefix, 'lib', 'python' + sys.version[:3], 'site-packages')
    clean(root=path)
    files = ['Gnuplot', 'IPython', 'Scientific', 'epydoc', ]
    print files
    # shutil.copytree does not work properly for this type of copy
    files = [join(path, file) for file in files]
    pmw = join(py_package_src, 'Pmw')
    cmd = 'cp -r ' + ' '.join(files) + ' ' + pmw + libdir
    print cmd
    os_system(cmd)
    clean(root=join(libdir, 'Pmw')

def copy_third_party_scripts():
    """
    Copy third party executable scripts to the scitools++/bin directory.
    """
    print '********* copy third-party executable scripts **************'
    scripts = ('ipython', 'f2py', 'epydoc', 'epydocgui')
    print scripts
    for script in scripts:
        os_system("cp `which %s` %s" % (script, bindir))


def main():
    copy_pure_scitools_files()
    copy_package('pyPDE')
    copy_package('easyviz')
    copy_scriptingbook_tools()
    copy_py4cs()
    remove_svn_files()
    copy_third_party_modules()
    copy_third_party_scripts()

if __name__ == '__main__':
    main()

    
