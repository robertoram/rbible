#!/usr/bin/env python3
import unittest
import sys
import os

# Add the parent directory to the path so we can import the rbible package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all test modules
from tests.test_bible_data import TestBibleData
from tests.test_verse_operations import TestVerseOperations
from tests.test_user_data import TestUserData
from tests.test_formatters import TestFormatters

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestBibleData))
    test_suite.addTest(unittest.makeSuite(TestVerseOperations))
    test_suite.addTest(unittest.makeSuite(TestUserData))
    test_suite.addTest(unittest.makeSuite(TestFormatters))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())