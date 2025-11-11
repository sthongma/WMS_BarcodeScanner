#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WMS Barcode Scanner Application
Entry point for running the application
"""

import sys
import os

# Ensure the project root is in Python path (not src/)
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.main import main

if __name__ == "__main__":
    main() 