import unittest

from main import read_args, main

class TestProgram(unittest.TestCase):
    def setUp(self):
        print("\n=================================")
    
    def test_read_args_no_filepath(self):
        print("Executing test: test_read_args_no_filepath")
        try:
            args = ["main.py"]
            expected_output = {}
            self.assertEqual(read_args(args), expected_output)
            print("test_read_args_no_filepath: OK")
        except Exception as e:
            print("test_read_args_no_filepath: ERROR ({0})".format(e))

    def test_read_args_filepath_found(self):
        print("Executing test: test_read_args_filepath_found")
        try:
            args = ["main.py", "-f", "/path/to/image.png"]
            expected_output = {"filepath": "/path/to/image.png"}
            self.assertEqual(read_args(args), expected_output)
            print("test_read_args_filepath_found: OK")
        except Exception as e:
            print("test_read_args_filepath_found: ERROR ({0})".format(e))