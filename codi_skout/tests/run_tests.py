import unittest
import sys
import os
import logging
from typing import List, Optional

def run_tests(test_modules: Optional[List[str]] = None):
    """Run the specified test modules or all tests if none specified"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Discover and run tests
    if test_modules:
        # Run specific test modules
        suite = unittest.TestSuite()
        
        for module_name in test_modules:
            try:
                module = __import__(f"tests.{module_name}", fromlist=["*"])
                suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(module))
            except ImportError as e:
                print(f"Error importing test module {module_name}: {str(e)}")
                return 1
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
    else:
        # Run all tests
        test_dir = os.path.dirname(os.path.abspath(__file__))
        suite = unittest.defaultTestLoader.discover(test_dir, pattern="test_*.py")
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    # Get test modules from command line arguments
    test_modules = sys.argv[1:] if len(sys.argv) > 1 else None
    
    # Run tests
    sys.exit(run_tests(test_modules))