# This file acts as a passthrough to the main app.py
# Streamlit Cloud is configured to look for this file,
# but the actual app logic is in the root app.py

import sys
import os

# Add parent directory to path so we can import the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and run the main app
from app import *
