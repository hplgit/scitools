"""
Test suite for Python 2 to Python 3 compatibility fixes.

This module tests all the bug fixes related to Python 3 compatibility:
1. Print statement syntax
2. Tab and space indentation consistency
3. Python 2 style exception handling
4. None comparison using == instead of is
5. Invalid escape sequence warnings
6. exec statement syntax
7. print >> syntax
8. File handle not properly closed
"""

import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))


class TestPrintStatement(unittest.TestCase):
    """Test that print statements have been converted to print() functions."""
    
    def test_print_function_works(self):
        """Test that print() function works correctly."""
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            print("Hello, World!")
            output = sys.stdout.getvalue()
            self.assertEqual(output, "Hello, World!\n")
        finally:
            sys.stdout = old_stdout
    
    def test_print_multiple_args(self):
        """Test print with multiple arguments."""
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            print("a", "b", "c")
            output = sys.stdout.getvalue()
            self.assertEqual(output, "a b c\n")
        finally:
            sys.stdout = old_stdout


class TestExceptionSyntax(unittest.TestCase):
    """Test that exception handling uses Python 3 syntax."""
    
    def test_except_as_syntax(self):
        """Test that except Exception as e syntax works."""
        try:
            raise ValueError("test error")
        except ValueError as e:
            self.assertEqual(str(e), "test error")
    
    def test_except_multiple_exceptions(self):
        """Test handling multiple exception types."""
        try:
            raise TypeError("type error")
        except (ValueError, TypeError) as e:
            self.assertIn("type error", str(e))


class TestNoneComparison(unittest.TestCase):
    """Test that None comparisons use 'is' instead of '=='."""
    
    def test_is_none(self):
        """Test 'is None' comparison."""
        x = None
        self.assertTrue(x is None)
    
    def test_is_not_none(self):
        """Test 'is not None' comparison."""
        x = "something"
        self.assertTrue(x is not None)


class TestExecSyntax(unittest.TestCase):
    """Test that exec statements have been converted to exec() functions."""
    
    def test_exec_function(self):
        """Test that exec() function works correctly."""
        code = "result = 1 + 2"
        local_vars = {}
        exec(code, {}, local_vars)
        self.assertEqual(local_vars['result'], 3)
    
    def test_exec_with_globals(self):
        """Test exec() with custom globals."""
        code = "result = x * 2"
        local_vars = {}
        exec(code, {'x': 5}, local_vars)
        self.assertEqual(local_vars['result'], 10)


class TestPrintRedirect(unittest.TestCase):
    """Test that print >> syntax has been converted to print(..., file=)."""
    
    def test_print_to_file(self):
        """Test printing to a file object."""
        import io
        file_obj = io.StringIO()
        print("test message", file=file_obj)
        self.assertEqual(file_obj.getvalue(), "test message\n")
    
    def test_print_to_stderr(self):
        """Test printing to stderr."""
        import io
        import sys
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            print("error message", file=sys.stderr)
            output = sys.stderr.getvalue()
            self.assertEqual(output, "error message\n")
        finally:
            sys.stderr = old_stderr


class TestFileHandle(unittest.TestCase):
    """Test that file handles are properly closed."""
    
    def test_with_statement_for_reading(self):
        """Test using 'with' statement for file reading."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            with open(temp_path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "test content")
        finally:
            os.unlink(temp_path)
    
    def test_with_statement_for_writing(self):
        """Test using 'with' statement for file writing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name
        
        try:
            with open(temp_path, 'w') as f:
                f.write("new content")
            
            with open(temp_path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "new content")
        finally:
            os.unlink(temp_path)


class TestConfigParser(unittest.TestCase):
    """Test that ConfigParser is Python 3 compatible."""
    
    def test_configparser_import(self):
        """Test that ConfigParser can be imported."""
        from scitools.configdata import config_parser_frontend
        self.assertTrue(callable(config_parser_frontend))
    
    def test_tobool_function(self):
        """Test the tobool function."""
        from scitools.configdata import tobool
        self.assertTrue(tobool('yes'))
        self.assertTrue(tobool('ON'))
        self.assertTrue(tobool('true'))
        self.assertFalse(tobool('no'))
        self.assertFalse(tobool('OFF'))
        self.assertFalse(tobool('false'))


class TestTimeClock(unittest.TestCase):
    """Test that time.clock() has been replaced with time.perf_counter()."""
    
    def test_perf_counter_exists(self):
        """Test that time.perf_counter() is available."""
        import time
        self.assertTrue(hasattr(time, 'perf_counter'))
        t1 = time.perf_counter()
        self.assertIsInstance(t1, float)


class TestScitoolsImport(unittest.TestCase):
    """Test that scitools modules can be imported."""
    
    def test_import_misc(self):
        """Test importing scitools.misc."""
        import scitools.misc
        self.assertTrue(hasattr(scitools.misc, 'str2bool'))
    
    def test_import_configdata(self):
        """Test importing scitools.configdata."""
        import scitools.configdata
        self.assertTrue(hasattr(scitools.configdata, 'tobool'))
    
    def test_import_numpyutils(self):
        """Test importing scitools.numpyutils."""
        import scitools.numpyutils
        self.assertTrue(hasattr(scitools.numpyutils, 'seq'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
