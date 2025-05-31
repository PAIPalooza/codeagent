"""
This file is automatically loaded by pytest and allows us to configure the test environment.
"""
import os
import sys

# Add the project root directory to the Python path
# This allows imports to work properly for both app modules and tests
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
