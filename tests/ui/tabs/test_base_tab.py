#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for BaseTab class
"""

import pytest
import tkinter as tk
from unittest.mock import MagicMock
from src.ui.tabs.base_tab import BaseTab


class ConcreteTab(BaseTab):
    """Concrete implementation of BaseTab for testing"""

    def build_ui(self):
        """Override to create simple UI"""
        self.label = tk.Label(self.frame, text="Test Tab")
        self.label.pack()


@pytest.fixture
def mock_repositories():
    """Mock repositories for testing"""
    return {
        'job_type_repo': MagicMock(),
        'sub_job_repo': MagicMock(),
        'scan_log_repo': MagicMock(),
        'dependency_repo': MagicMock()
    }


@pytest.fixture
def mock_services():
    """Mock services for testing"""
    return {
        'scan_service': MagicMock(),
        'dependency_service': MagicMock(),
        'report_service': MagicMock(),
        'import_service': MagicMock()
    }


@pytest.fixture
def root_window():
    """Create root window for testing"""
    root = tk.Tk()
    yield root
    root.destroy()


@pytest.fixture
def mock_db_manager():
    """Mock database manager"""
    return MagicMock()


@pytest.mark.unit
@pytest.mark.ui
class TestBaseTab:
    """Test BaseTab class"""

    def test_init(self, root_window, mock_db_manager, mock_repositories, mock_services):
        """Test that BaseTab initializes correctly"""
        tab = ConcreteTab(root_window, mock_db_manager, mock_repositories, mock_services)

        assert tab.parent == root_window
        assert tab.db == mock_db_manager
        assert tab.job_type_repo == mock_repositories['job_type_repo']
        assert tab.sub_job_repo == mock_repositories['sub_job_repo']
        assert tab.scan_log_repo == mock_repositories['scan_log_repo']
        assert tab.dependency_repo == mock_repositories['dependency_repo']
        assert tab.scan_service == mock_services['scan_service']
        assert tab.dependency_service == mock_services['dependency_service']
        assert tab.report_service == mock_services['report_service']
        assert tab.import_service == mock_services['import_service']

    def test_build_ui_called(self, root_window, mock_db_manager, mock_repositories, mock_services):
        """Test that build_ui is called during initialization"""
        tab = ConcreteTab(root_window, mock_db_manager, mock_repositories, mock_services)

        # Check that UI was built
        assert hasattr(tab, 'label')
        assert tab.label.winfo_exists()

    def test_get_frame(self, root_window, mock_db_manager, mock_repositories, mock_services):
        """Test get_frame returns the tab frame"""
        tab = ConcreteTab(root_window, mock_db_manager, mock_repositories, mock_services)

        frame = tab.get_frame()
        assert frame == tab.frame
        assert isinstance(frame, (tk.Frame, tk.ttk.Frame))

    def test_refresh_default(self, root_window, mock_db_manager, mock_repositories, mock_services):
        """Test refresh does nothing by default"""
        tab = ConcreteTab(root_window, mock_db_manager, mock_repositories, mock_services)

        # Should not raise any errors
        tab.refresh()

    def test_on_show_calls_refresh(self, root_window, mock_db_manager, mock_repositories, mock_services):
        """Test on_show calls refresh"""
        tab = ConcreteTab(root_window, mock_db_manager, mock_repositories, mock_services)

        # Mock refresh to track calls
        tab.refresh = MagicMock()

        tab.on_show()
        tab.refresh.assert_called_once()

    def test_cleanup_default(self, root_window, mock_db_manager, mock_repositories, mock_services):
        """Test cleanup does nothing by default"""
        tab = ConcreteTab(root_window, mock_db_manager, mock_repositories, mock_services)

        # Should not raise any errors
        tab.cleanup()

    def test_base_tab_build_ui_not_implemented(self, root_window, mock_db_manager, mock_repositories, mock_services):
        """Test that BaseTab.build_ui raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            BaseTab(root_window, mock_db_manager, mock_repositories, mock_services)
