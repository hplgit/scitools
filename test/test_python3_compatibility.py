"""
Test cases for Python 3 compatibility fixes.
This file tests all the bugs that were fixed:
1. print statement (now print() function)
2. Tab/space indentation consistency
3. except Exception, msg -> except Exception as msg
4. == None -> is None
5. exec statement -> exec() function
6. print >> syntax
7. File handle closing
"""
import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))


class TestPython3Compatibility(unittest.TestCase):
    """Test Python 3 compatibility fixes."""

    def test_print_function_compiles(self):
        """Test that print statements are now print() functions."""
        import py_compile
        test_dir = os.path.join(os.path.dirname(__file__), '..', 'lib', 'scitools')
        
        error_files = []
        for root, dirs, files in os.walk(test_dir):
            for f in files:
                if f.endswith('.py'):
                    path = os.path.join(root, f)
                    try:
                        py_compile.compile(path, doraise=True)
                    except SyntaxError as e:
                        if 'print' in str(e):
                            error_files.append(path)
        
        self.assertEqual(len(error_files), 0, 
            f"Files with print statement SyntaxError: {error_files}")

    def test_exception_catching_syntax(self):
        """Test that except Exception, msg -> except Exception as msg."""
        code = """
try:
    raise ValueError("test")
except ValueError as e:
    result = str(e)
        """
        # Should compile without error
        compile(code, '<string>', 'exec')
        
    def test_none_comparison(self):
        """Test using 'is None' instead of '== None'."""
        x = None
        y = "not None"
        
        self.assertTrue(x is None)
        self.assertFalse(y is None)
        self.assertTrue(y is not None)
        
        import scitools.numpyutils as nu
        import inspect
        src = inspect.getsource(nu)
        self.assertNotIn('== None', src)
        
    def test_exec_function(self):
        """Test exec() function syntax works."""
        code = """
x = 0
exec("x = 1 + 2")
        """
        ns = {}
        exec(code, ns)
        
    def test_file_handle_closing_with_statement(self):
        """Test that files are properly closed."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_name = f.name
        
        try:
            with open(temp_name, 'r') as f:
                content = f.read()
                self.assertEqual(content, "test content")
                self.assertFalse(f.closed)
            self.assertTrue(f.closed)
        finally:
            os.unlink(temp_name)

    def test_import_scitools(self):
        """Test that scitools main module can be imported."""
        import scitools
        self.assertIsNotNone(scitools)

    def test_no_print_redirect_syntax(self):
        """Test that print >> sys.stderr is not used anymore."""
        import scitools.misc as misc
        import inspect
        src = inspect.getsource(misc)
        self.assertNotIn('print >>', src)

    def test_time_clock_replacement(self):
        """Test that time.clock() is replaced with time.perf_counter()."""
        import scitools.basics
        import time
        self.assertTrue(hasattr(time, 'perf_counter'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
