"""Pytest configuration for VeriClip AI tests."""
import sys
import os

# Add the backend directory to Python path so 'app' module resolves correctly
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
