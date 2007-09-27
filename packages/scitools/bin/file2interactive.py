#!/usr/bin/env python
"""
Execute a Python script and present output such that it seems that
each statement is executed in the interactive interpreter.

A funny feature is to add 'human' as a second command-line argument:
it then seems that the text in the interpreter is written by a
human, char by char. This can be used to fake typing in an interactive
shell ;-)

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
import sys, random, time

def printline(prompt, line, human_typing=0):
    """
    Print a line with Python code in the interpreter.
    If human_typing is not 0, the line will be printed as if
    a human types it. human_typing=1: characters are written
    with a random delay, human_typing=2: characters are written
    when the user hits any character on the keyboard
    (not yet implemented).
    """
    # human_typing=2 can make use of a getch()-like function from
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/134892
    # or
    # http://www.freenetpages.co.uk/hp/alan.gauld/tutevent.htm
    
    if not human_typing:
        print prompt, line
    else:
        print prompt,
        # type one and one character with a random sleep in between
        max_delay = 0.6  # seconds
        for char in line:
            delay = random.uniform(0, max_delay)
            time.sleep(delay)
            sys.stdout.write(char)
            sys.stdout.flush()
        dummy = raw_input('')
        
        
class RunFileInInterpreter(InteractiveInterpreter):
    def __init__(self, locals=None):
        self._ip = InteractiveInterpreter(locals=locals)

    def run(self, source_code):
        buffer = []  # collect lines that belong together
        prompt = '>>>'
        for line in source_code.split('\n'):
            #line = line.rstrip()  # indicates wrong end of buffer list
            printline(prompt, line, human_typing)
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

def _test():
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
    return _sc
    
if __name__ == '__main__':        
    try:
        _filename = sys.argv[1]
    except:
        print 'Usage: interpret.py filename'
        sys.exit(1)

    human_typing = 0  # global variable
    try:
        if sys.argv[2] == 'human':
            human_typing = 1
    except:
        pass
        
    # define the complete source code file as _sc string:
    if _filename == 'demo':
        _sc = _test()
    else:
        _sc = open(_filename, 'r').read()
    del _filename
    RunFileInInterpreter(locals()).run(_sc)




        
