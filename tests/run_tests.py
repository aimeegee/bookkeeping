#!/usr/bin/env python3
"""
Test runner for the bookkeeping system
Run all tests with: python -m pytest tests/
Run specific test: python -m pytest tests/test_data_processor.py
Run with coverage: python -m pytest tests/ --cov=src --cov-report=html
"""

import unittest
import sys
from pathlib import Path

def discover_and_run_tests():
    """Discover and run all tests"""
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Discover tests
    loader = unittest.TestLoader()
    test_dir = Path(__file__).parent
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()

if __name__ == '__main__':
    success = discover_and_run_tests()
    sys.exit(0 if success else 1)
