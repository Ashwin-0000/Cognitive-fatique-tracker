"""Tests package initialization"""
import unittest

# Test discovery
def load_tests(loader, tests, pattern):
    """Load all tests"""
    return loader.discover('tests', pattern='test_*.py')


if __name__ == '__main__':
    unittest.main()
