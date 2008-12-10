#!/usr/bin/env python
import sys, os
try:
    script = sys.argv[1]
except:
    print "Usage: profiler.py scriptfile options"; sys.exit(1)
resfile = '.tmp.profile'
# add the directory of the script to sys.path in case the script
# employs local modules from that directory:
sys.path.insert(0, os.path.dirname(script))
# hide 'profiler.py' from sys.argv:
del sys.argv[0]

# The hotshot or profile module will be used, depending on
# the value of the environment variable PYPROFILE
# (default is hotshot, the fastest of them)
profiler_module = os.environ.get('PYPROFILE', 'hotshot')

if profiler_module == 'profile':  # old
    import profile, pstats
    profile.run('execfile(' + `script` + ')', resfile)
    # recall `s` is the same as repr(s)
    p = pstats.Stats(resfile)
elif profiler_module == 'hotshot':  # new
    import hotshot, hotshot.stats
    prof = hotshot.Profile(resfile)
    prof.run('execfile(' + `script` + ')')
    p = hotshot.stats.load(resfile)
    
p.strip_dirs().sort_stats('time').print_stats(20)

