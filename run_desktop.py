#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WMS Barcode Scanner - Desktop Application Entry Point
เรียกใช้แอปพลิเคชันแบบ Desktop (Tkinter GUI)
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.main import main

if __name__ == "__main__":
    main()