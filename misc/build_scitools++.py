#!/usr/bin/env python
"""
Build the scitools++ directory, consisting of scitools and several
useful associated packages such as Doconce, IPython, Epydoc, Preprocess, etc.

NumPy is required and not a part of scitools++.

Method: plain copy of already installed packages and scripts 
(lib and bin files).
"""

MODULES = (
    'doconce',
    'scitools',
    'Gnuplot',
    'IPython',
    'Scientific',
    'epydoc',
    'preprocess',
    'matplotlib',
    )

SCRIPTS = (
    'ipython',
    'epydoc',
    'epydocgui',
    'preprocess',
    'doconce_insertdocstr',
    'doconce2format',
    'diff.pl',
    'diff.py',
    'gnuplot.bat',
    '_gnuplot.py',
    'locate_pdb.py',
    'pdb',
    'timer.py',
    )


import os, glob, sys, shutil
join = os.path.join

# directories to be used:
#
# build
#    previous-build-of-scitools++
#    scitools++
#       lib
#          doconce
#          scitools
#          IPython
#          epydoc
#          preprocess
#          ...
#       bin
#
# put scitools++/lib in PYTHONPATH
# put scitools++/bin in PATH
#
# scitools contains some py4cs modules and some new stuff

thisdir = os.getcwd()
olddir = join('build', 'previous-build-of-scitools++')
newdir = join('build', 'scitools++')
libdir = join(newdir, 'lib')
bindir = join(newdir, 'bin')
scitools_dir = join(libdir, 'scitools')
py_package_src = join(os.environ['SYSDIR'],'src','python','tools')
st_src = join(os.pardir, 'lib', 'scitools')  # source code for scitools package

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

from scitools.misc import system
        
def clean(root, filetypes=['*.pyc', '*~', '*.pyo', '*.p.py', '_update.py']):
    for type in filetypes:
        os.system("find %s -name '%s' -exec rm -rf {} \;" % (root, type))
        

def copy_installed_modules():
    """
    Copy installed modules to scitools++.
    An alternative is to copy the source of these modules and
    run multiple setup.py in scitools++ to install each dir in scitools++.
    The set-up now is that scitools++ should just be in PYTHONPATH and
    then everything is correctly installed.
    """
    print '********* copy installed modules to scitools++ **************'
    path = join(sys.prefix, 'lib', 'python' + sys.version[:3], 'site-packages')
    files = MODULES  # see top of this file
    print files
    
    files = [join(path, file) for file in files]
    pmw = join(py_package_src, 'Pmw_1_3', 'Pmw')
    files.append(pmw)
    # copy files to libdir:
    # (shutil.copytree does not work properly for this type of copy)
    cmd = 'cp -r ' + ' '.join(files) + ' ' + libdir
    print cmd
    system(cmd)

def copy_installed_scripts():
    """
    Copy installed executable scripts to the scitools++/bin directory.
    """
    print '********* copy installed executable scripts **************'
    scripts = SCRIPTS  # see top of this file
    print scripts
    for script in scripts:
        system("cp `which %s` %s" % (script, bindir))

    # fix headers (replace user-specific install path):
    for f in scripts:
        system(r'subst.py "#!.+" "#!/usr/bin/env python" %s' % \
                  join(bindir, f))
    for f in glob.glob(join(bindir, '*.old~')):
        os.remove(f)


def main():
    copy_installed_modules()
    copy_installed_scripts()
    shutil.copy('scitools++_setup.py', join(newdir, 'setup.py'))
    clean(newdir, ['*.pyc', '*~', '*.pyo', '*.p.py', '_update.py', '.svn'])
    print '\nThe scitools++ umbrella was successfully made'
    print 'Go to the build/ directory and tarpack scitools++'

if __name__ == '__main__':
    main()

    
