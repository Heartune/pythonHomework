#!/usr/bin/env python3
"""
Test runner for Library Management System.
"""

import unittest
import sys
import os

def run_tests():
    """Run all tests for the Library Management System."""
    # Add project root to path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Create test loader
    loader = unittest.TestLoader()
    
    # Discover tests
    test_suite = loader.discover('tests', pattern='test_*.py')
    
    # Create test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run tests
    result = runner.run(test_suite)
    
    # Return exit code based on test result
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
