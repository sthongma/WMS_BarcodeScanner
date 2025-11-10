#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WMS Barcode Scanner Application
Main application file with multi-tab interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from typing import Dict, Optional, Any

# Import constants
from .. import constants

# Import database manager and repositories
from ..database.database_manager import DatabaseManager
from ..database import (
    JobTypeRepository,
    SubJobRepository,
    ScanLogRepository,
    DependencyRepository
)

# Import services
from ..services import (
    ScanService,
    DependencyService,
    ReportService,
    ImportService
)

# Import UI tabs
from .tabs import (
    DatabaseSettingsTab,
    ScanningTab,
    ImportTab,
    HistoryTab,
    SettingsTab,
    ReportsTab,
    SubJobSettingsTab
)

# Import login window
try:
    from .login_window import LoginWindow
except ImportError:
    print("Error: login_window.py not found")
    sys.exit(1)


class WMSScannerApp:
    """Main WMS Scanner Application"""

    def __init__(self, root, connection_info: Optional[Dict[str, Any]] = None):
        self.root = root
        self.root.title("WMS EP Asia Group Co., Ltd.")
        self.root.geometry(constants.WINDOW_MAIN_SIZE)
        self.root.resizable(False, False)

        # Initialize database manager with connection info
        self.db = DatabaseManager(connection_info)

        # Test database connection on startup (only if not using login)
        if not connection_info:
            if not self.db.test_connection():
                messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถเชื่อมต่อฐานข้อมูลได้")

        # Initialize repositories
        self.job_type_repo = JobTypeRepository(self.db)
        self.sub_job_repo = SubJobRepository(self.db)
        self.scan_log_repo = ScanLogRepository(self.db)
        self.dependency_repo = DependencyRepository(self.db)

        # Initialize services
        self.scan_service = ScanService(
            scan_log_repo=self.scan_log_repo,
            sub_job_repo=self.sub_job_repo,
            dependency_repo=self.dependency_repo
        )
        self.dependency_service = DependencyService(
            dependency_repo=self.dependency_repo,
            job_type_repo=self.job_type_repo
        )
        self.report_service = ReportService(
            scan_log_repo=self.scan_log_repo,
            job_type_repo=self.job_type_repo,
            sub_job_repo=self.sub_job_repo
        )
        self.import_service = ImportService(
            job_type_repo=self.job_type_repo,
            sub_job_repo=self.sub_job_repo,
            scan_log_repo=self.scan_log_repo
        )

        # Initialize UI with component-based tabs
        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI with component-based tabs"""
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Prepare repositories and services for dependency injection
        repositories = {
            'job_type_repo': self.job_type_repo,
            'sub_job_repo': self.sub_job_repo,
            'scan_log_repo': self.scan_log_repo,
            'dependency_repo': self.dependency_repo
        }

        services = {
            'scan_service': self.scan_service,
            'dependency_service': self.dependency_service,
            'report_service': self.report_service,
            'import_service': self.import_service
        }

        # Create tab components with dependency injection
        # Tab 1: Scanning (Main Screen)
        self.scanning_tab = ScanningTab(
            parent=self.notebook,
            db_manager=self.db,
            repositories=repositories,
            services=services,
            on_scan_completed=self.on_scan_completed
        )
        self.notebook.add(self.scanning_tab.frame, text=constants.TAB_SCANNING)

        # Tab 2: History
        self.history_tab = HistoryTab(
            parent=self.notebook,
            db_manager=self.db,
            repositories=repositories,
            services=services,
            on_history_updated=None
        )
        self.notebook.add(self.history_tab.frame, text=constants.TAB_HISTORY)

        # Tab 3: Reports
        self.reports_tab = ReportsTab(
            parent=self.notebook,
            db_manager=self.db,
            repositories=repositories,
            services=services,
            on_report_generated=None
        )
        self.notebook.add(self.reports_tab.frame, text=constants.TAB_REPORTS)

        # Tab 4: Import
        self.import_tab = ImportTab(
            parent=self.notebook,
            db_manager=self.db,
            repositories=repositories,
            services=services,
            on_import_completed=self.on_import_completed
        )
        self.notebook.add(self.import_tab.frame, text=constants.TAB_IMPORT)

        # Tab 5: Settings (Job Types Management)
        self.settings_tab = SettingsTab(
            parent=self.notebook,
            db_manager=self.db,
            repositories=repositories,
            services=services,
            on_settings_changed=self.on_settings_changed
        )
        self.notebook.add(self.settings_tab.frame, text=constants.TAB_JOB_SETTINGS)

        # Tab 6: Sub Job Settings
        self.sub_job_settings_tab = SubJobSettingsTab(
            parent=self.notebook,
            db_manager=self.db,
            repositories=repositories,
            services=services,
            on_sub_job_updated=self.on_sub_job_updated
        )
        self.notebook.add(self.sub_job_settings_tab.frame, text=constants.TAB_SUB_JOB_SETTINGS)

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        """Handle tab change events"""
        try:
            selected_tab = event.widget.tab('current')['text']

            # Refresh scanning tab when selected
            if selected_tab == constants.TAB_SCANNING:
                self.root.after(100, self.scanning_tab.refresh_history)

            # Refresh history tab when selected
            elif selected_tab == constants.TAB_HISTORY:
                self.root.after(100, self.history_tab.refresh_history)

        except Exception as e:
            print(f"Error in on_tab_changed: {str(e)}")

    # Callback methods for inter-component communication
    def on_scan_completed(self):
        """Called when a scan is completed successfully"""
        # Refresh history tab if it exists
        if hasattr(self, 'history_tab'):
            self.history_tab.refresh_history()

    def on_import_completed(self):
        """Called when import is completed successfully"""
        # Refresh relevant tabs
        if hasattr(self, 'history_tab'):
            self.history_tab.refresh_history()
        if hasattr(self, 'scanning_tab'):
            self.scanning_tab.refresh_history()

    def on_settings_changed(self):
        """Called when job type settings are changed"""
        # Refresh job types in scanning tab
        if hasattr(self, 'scanning_tab'):
            self.scanning_tab.refresh_job_types()
        # Refresh job types in reports tab
        if hasattr(self, 'reports_tab'):
            self.reports_tab.refresh_job_types()
        # Refresh main job list in sub job settings tab
        if hasattr(self, 'sub_job_settings_tab'):
            self.sub_job_settings_tab.refresh_main_job_list()

    def on_sub_job_updated(self):
        """Called when sub job settings are changed"""
        # Refresh sub job types in scanning tab if a main job is selected
        if hasattr(self, 'scanning_tab'):
            # Trigger refresh by simulating job type change
            self.scanning_tab.on_job_type_change()


def main():
    """Main entry point for the application"""
    root = tk.Tk()

    # Show login window first
    login_window = LoginWindow(root)
    root.wait_window(login_window.window)

    # Check if login was successful
    if login_window.connection_info:
        app = WMSScannerApp(root, login_window.connection_info)
        root.mainloop()
    else:
        root.destroy()


if __name__ == "__main__":
    main()
