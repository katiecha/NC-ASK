"""
Pytest configuration for NC-ASK tests.
"""
import sys
from pathlib import Path

# Add backend directory to Python path so imports work
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
