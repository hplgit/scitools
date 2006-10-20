#!/usr/bin/env python
"""
Build the SciTools scitools++ directory with scitools
and utilities.

Utilities:

Easyviz is copied from the original source to scitools/easyviz.
py4cs is replaced by scitools, and easyviz.numpytools is replaced by
scitools.numpytools, and easyviz/numpytools.py is removed (resides
only in the scitools/ parent directory).

pyPDE is copied from the original source to scitools/pyPDE.

Future changes may remove the easyviz original source and put it (and pyPDE)
directly under scitools.
"""

import os, glob, sys, shutil
join = os.path.join

# directories to be used:
#
# build
#    previous-build-of-scitools++
#    scitools++
#       lib
#          scitools
#          IPython
#          epydoc
#          ...
#       bin
#
# put scitools++/lib in PYTHONPATH
# put scitools++/bin in PATH
#
# scitools contains some py4cs modules and some new stuff

olddir = join('build', 'previous-build-of-scitools++')
newdir = join('build', 'scitools++')
libdir = join(newdir, 'lib')
bindir = join(newdir, 'bin')
scitools_dir = join(libdir, 'scitools')
py_package_src = join(os.environ['SYSDIR'],'src','python','tools')
st_src = join('lib', 'scitools')  # source code for scitools package

# start with a fresh scitools directory and move last scitools++ to
# a "copy" directory:
if not os.path.isdir('build'):
    os.mkdir('build')
if os.path.isdir(olddir):
    shutil.rmtree(olddir)
if os.path.isdir(newdir):
    os.rename(newdir, olddir)
os.makedirs(newdir)
os.makedirs(libdir)
os.makedirs(bindir)
os.makedirs(scitools_dir)



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

    # copy bin files:
    bin = join('bin')
    files = glob.glob(join(bin, '*'))
    cmd = 'cp -r ' + ' '.join(files) + ' ' + bindir
    print cmd
    os_system(cmd)
        

def copy_package(package):
    # was used for easyviz, pyPDE, but not used anymore
    """Copy package as sub-package of scitools."""
    print '********* %s **************' % package
    dir = join(os.pardir, package, 'lib', package)
    clean(root=dir)
    # (shutil.copytree does not work properly for this type of copy)
    cmd = 'cp -r ' + dir + ' ' + scitools_dir
    print cmd
    os_system(cmd)

def rename(directory, from_name='py4cs', to_name='scitools'):
    # not used anymore
    """Rename py4cs to scitools in directory/*.py files."""
    pyfiles = ' '.join(glob.glob(join(directory, '*.py')))
    os_system(r"subst.py '%s\.' %s. " % (from_name, to_name) + pyfiles)
    # (some of the "from scitools.... import ..." could be replaced by
    # the standard "from scitools import *")
    for f in glob.glob(join(directory, '*.old~')):
        os.remove(f)
    
def copy_scriptingbook_tools():
    # not used anymore
    """Copy scripting/src/tools scripts to scitools++/bin."""
    print '********* copy $scripting/src/tools **************'
    files = ['_gnuplot.py', 'diff.pl', 'diff.py', 
             'file2interactive.py', 'floatdiff.py', 'gnuplot.bat', 
             'ps2mpeg.py', 'regression.py', 'subst.py', 'timer.py']
    print files
    path = join(os.environ['scripting'], 'src', 'tools')
    for file in files:
        shutil.copy(join(path ,file), bindir)

    rename(bindir, 'py4cs', 'scitools')
    
def copy_py4cs():
    # not used anymore
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
    path = join(os.environ['scripting'], 'src', 'tools', 'py4cs')
    print files, 'to', scitools_dir
    for file in files:
        shutil.copy(join(path, file), scitools_dir)

    rename(scitools_dir, 'py4cs', 'scitools')

def remove_svn_files(root=newdir):
    print '********* remove svn directories **************'
    cmd = 'find %s -name ".svn" -print' % root
    os_system(cmd)
    cmd = 'find %s -name ".svn" -exec rm -rf {} \;' % root
    os.system(cmd)  # drop testing since this removal is always failure

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
    cmd = 'cp -r ' + ' '.join(files) + ' ' + pmw + ' ' + libdir
    print cmd
    os_system(cmd)
    clean(root=join(libdir, 'Pmw'))

def copy_third_party_scripts():
    """
    Copy third party executable scripts to the scitools++/bin directory.
    """
    print '********* copy third-party executable scripts **************'
    scripts = ('ipython', 'f2py', 'epydoc', 'epydocgui')
    print scripts
    for script in scripts:
        os_system("cp `which %s` %s" % (script, bindir))
    # fix headers:
    for f in scripts:
        os_system(r'subst.py "#!.+" "#!/usr/bin/env python" %s' % \
                  join(bindir, f))
    for f in glob.glob(join(bindir, '*.old~')):
        os.remove(f)


def check_numpytools():
    # not used anymore
    ev = '/home/store/scriptingsuite/trunk/packages/easyviz/lib/easyviz'
    orig = join(os.environ['scripting'],'src','tools','py4cs')
    failure = os.system('diff %s/numpytools.py %s/numpytools.py' % (orig,ev))
    if failure:
        print 'numpytools in\n  %s\nand\n  %s\ndiffer!' % (ev, orig)
        sys.exit(1)

def fix_easyviz_numpytools():
    # not used anymore
    dir = join(scitools_dir, 'easyviz')
    os.remove(join(dir, 'numpytools.py'))
    pyfiles = ' '.join(glob.glob(join(dir, '*.py')))
    os_system(r"subst.py 'easyviz.numpytools' 'scitools.numpytools' " + pyfiles)
    for f in glob.glob(join(dir, '*.old~')):
        os.remove(f)
    

def main():
    # Large parts of this script is not needed anymore.
    # It built a scitools++ directory when
    # the original version of many scitools files were stored in
    # different places.
    # Now the official versions are stored under scitools and other packages
    # (like py4cs) must make a copy from scitools.
    
    # The only thing left is copying scitools and third-party modules to
    # a scitools++ directory and removing .svn directories.

    #check_numpytools()
    copy_pure_scitools_files()

    #copy_package('pyPDE')
    #copy_package('easyviz')
    #rename(join(scitools_dir, 'easyviz'), 'py4cs', 'scitools')
    #fix_easyviz_numpytools()
    
    #copy_scriptingbook_tools()
    #copy_py4cs()
    remove_svn_files(newdir)
    copy_third_party_modules()
    copy_third_party_scripts()
    shutil.copy('setup.py', newdir)
    print '\nSciTools++ umbrella was successfully made'

if __name__ == '__main__':
    main()

    
