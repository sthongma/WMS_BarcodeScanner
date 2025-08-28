#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WMS Barcode Scanner Application
Entry point for running the application
"""

import sys
import os

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import main

if __name__ == "__main__":
    main() 