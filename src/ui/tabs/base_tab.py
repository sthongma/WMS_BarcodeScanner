#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Tab Class
Provides common functionality for all tab components
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional


class BaseTab:
    """
    Base class for all tab components in the WMS Scanner application

    This class provides common functionality and dependencies that all tabs need,
    including access to the database manager, repositories, and services.

    All tab subclasses should:
    1. Call super().__init__() in their __init__ method
    2. Implement build_ui() to create their specific UI
    3. Use the provided repositories and services for data operations
    """

    def __init__(
        self,
        parent: tk.Widget,
        db_manager: Any,
        repositories: Dict[str, Any],
        services: Dict[str, Any]
    ):
        """
        Initialize the base tab

        Args:
            parent: Parent widget (usually a ttk.Notebook)
            db_manager: DatabaseManager instance
            repositories: Dictionary of repository instances
                - job_type_repo: JobTypeRepository
                - sub_job_repo: SubJobRepository
                - scan_log_repo: ScanLogRepository
                - dependency_repo: DependencyRepository
            services: Dictionary of service instances
                - scan_service: ScanService
                - dependency_service: DependencyService
                - report_service: ReportService
                - import_service: ImportService
        """
        self.parent = parent
        self.db = db_manager

        # Store repositories
        self.job_type_repo = repositories.get('job_type_repo')
        self.sub_job_repo = repositories.get('sub_job_repo')
        self.scan_log_repo = repositories.get('scan_log_repo')
        self.dependency_repo = repositories.get('dependency_repo')

        # Store services
        self.scan_service = services.get('scan_service')
        self.dependency_service = services.get('dependency_service')
        self.report_service = services.get('report_service')
        self.import_service = services.get('import_service')

        # Create main frame for this tab
        self.frame = ttk.Frame(parent)

        # Build UI (to be implemented by subclass)
        self.build_ui()

    def build_ui(self):
        """
        Build the tab UI

        This method should be overridden by subclasses to create their specific UI.
        The UI should be built inside self.frame.

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclass must implement build_ui() method")

    def get_frame(self) -> ttk.Frame:
        """
        Get the tab frame

        Returns:
            ttk.Frame: The main frame for this tab
        """
        return self.frame

    def refresh(self):
        """
        Refresh the tab data

        This method can be overridden by subclasses to refresh their data
        when the tab becomes visible or when data changes.

        Default implementation does nothing.
        """
        pass

    def on_show(self):
        """
        Called when the tab becomes visible

        This method can be overridden by subclasses to perform actions
        when the tab is selected by the user.

        Default implementation calls refresh().
        """
        self.refresh()

    def cleanup(self):
        """
        Cleanup resources when tab is destroyed

        This method can be overridden by subclasses to cleanup any resources
        (e.g., close files, cancel pending operations, etc.)

        Default implementation does nothing.
        """
        pass
