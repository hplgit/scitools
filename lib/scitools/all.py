# just let all be a synonym for std (for backward compatibility)
print 'Deprecation warning: scitools.all has changed name to scitools.std'
from scitools.std import *
import std as _s
sys.modules['scitools.all'] = _s
del _s

