#!/usr/bin/env python
"""
Execute a Python script and present output such that it seems that
each statement is executed in the interactive interpreter.

Troubleshooting:

Each multi-line command must be ended by a pure '\n' line. If there
is more whitespace, the interpreter waits for additional lines and
the command is corrupted. For example, when defining a class,
blank lines between the methods must have some whitespace to ensure
continuation, but the line below the class definition must be empty
so the command is ended.
"""

from code import InteractiveInterpreter
# see InteractiveConsole for example on using InteractiveInterpreter
import sys

class RunFileInInterpreter(InteractiveInterpreter):
    def __init__(self, locals=None):
        self._ip = InteractiveInterpreter(locals=locals)

    def run(self, source_code):
        buffer = []  # collect lines that belong together
        prompt = '>>>'
        for line in source_code.split('\n'):
            #line = line.rstrip()  # indicates wrong end of buffer list
            print prompt, line
            buffer.append(line)
            source = '\n'.join(buffer)
            try:
                need_more = self._ip.runsource(source)
            except (SyntaxError,OverflowError), e:
                print self._ip.showsyntaxerror()
                sys.exit(1)
            if need_more:
                #print 'need more..., source=\n', source
                prompt = '...'
                continue # proceed with new line
            else:
                #print 'successful execution of final source=\n',source
                prompt = '>>>'
                buffer = []

if __name__ == '__main__':        
    try:
        _filename = sys.argv[1]
    except:
        print 'Usage: interpret.py filename'
        sys.exit(1)

    # define the complete source code file as _sc string:
    if _filename == 'demo':
        # just provide some demo code for testing:
        _sc = """
a = 1
def f(x):
    x = x + 2
    return x

b = f(2)
dir()
print 'correct?', b == 4
    """
    else:
        _sc = open(_filename, 'r').read()
    del _filename
    RunFileInInterpreter(locals()).run(_sc)




        
