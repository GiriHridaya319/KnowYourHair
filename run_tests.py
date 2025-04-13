import unittest
import sys
import os

# Add the project root to the path if needed
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_hairfall_predictor import TestHairfallPredictor
from test_product_recommender import TestProductRecommender


def run_tests():
    """Run all test suites and print comprehensive results"""
    print("=" * 80)
    print("RUNNING WHITE BOX TESTS FOR HAIRFALL PREDICTION MODELS")
    print("=" * 80)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add all tests from both test classes
    test_suite.addTest(unittest.makeSuite(TestHairfallPredictor))
    test_suite.addTest(unittest.makeSuite(TestProductRecommender))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Ran {result.testsRun} tests")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    # Return success/failure
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)