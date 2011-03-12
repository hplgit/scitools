"""
Trick to make a nickname for a module!
Can be used to make a nickname py4cs for scitools to keep
backward compatibility with the TCSE3 book.
"""

import sys
import scitools
nickname = 'stcopy'
sys.modules[nickname] = sys.modules['scitools']
