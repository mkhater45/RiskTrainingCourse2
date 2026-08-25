"""Discovers and runs tests from the current directory using pytest's default conventions.

Recursively scans subdirectories to execute all functions/classes named test_* or *_test.
The '-v' flag enables verbose output to print individual test names at runtime.
"""

import pytest
pytest.main(["-v"])
