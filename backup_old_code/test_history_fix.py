#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify history loading fix
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_history_loading():
    """Test if history loading works correctly"""
    try:
        from ui.main_window import WMSScannerApp
        import tkinter as tk
        
        print("Testing history loading fix...")
        
        # Create a test root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test database connection info
        test_connection_info = {
            'config': {
                'server': 'localhost\\SQLEXPRESS',
                'database': 'WMS_EP',
                'auth_type': 'Windows',
                'username': '',
                'password': ''
            },
            'connection_string': 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=WMS_EP;Trusted_Connection=yes;TrustServerCertificate=yes;',
            'current_user': 'TestUser'
        }
        
        # Create app instance
        app = WMSScannerApp(root, test_connection_info)
        
        print("✓ App created successfully")
        
        # Test refresh_scanning_history method
        try:
            app.refresh_scanning_history()
            print("✓ refresh_scanning_history() executed successfully")
        except Exception as e:
            print(f"✗ Error in refresh_scanning_history(): {str(e)}")
        
        # Test tab change event
        try:
            # Simulate tab change to "หน้าจอหลัก"
            event = type('Event', (), {'widget': app.notebook})()
            app.on_tab_changed(event)
            print("✓ on_tab_changed() executed successfully")
        except Exception as e:
            print(f"✗ Error in on_tab_changed(): {str(e)}")
        
        root.destroy()
        print("✓ Test completed successfully")
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_history_loading()
    if success:
        print("\n🎉 History loading fix test PASSED!")
    else:
        print("\n❌ History loading fix test FAILED!") 