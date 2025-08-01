#!/usr/bin/env python3
"""Simple test runner for proxy-reader tests"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        import pytest

        # Run the tests
        pytest.main(["-v", "tests/"])
    except ImportError:
        print("pytest not found. Please install it with: pip install pytest")
        sys.exit(1)
