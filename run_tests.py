"""Test runner script"""
import sys
import unittest
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests(verbose=True):
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_unit_tests():
    """Run only unit tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromName('tests.test_models'))
    suite.addTests(loader.loadTestsFromName('tests.test_analyzers'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_integration_tests():
    """Run only integration tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_integration')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_performance_tests():
    """Run performance tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_performance')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--performance', action='store_true', help='Run performance tests only')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    success = True
    
    if args.unit:
        print("Running unit tests...")
        success = run_unit_tests()
    elif args.integration:
        print("Running integration tests...")
        success = run_integration_tests()
    elif args.performance:
        print("Running performance tests...")
        success = run_performance_tests()
    else:
        print("Running all tests...")
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
