# Main Window Breakdown Plan

## Current Status
- **File:** `src/ui/main_window.py`
- **Lines:** 2,652 lines
- **Methods:** 55 methods
- **Target:** < 300 lines (orchestrator only)

## Component Analysis

### 1. Scanning Tab (Lines ~280-405)
**Methods (11):**
- `create_scanning_tab()` - UI creation
- `create_scanning_history_table()` - Table creation
- `refresh_scanning_history()` - Data loading
- `on_main_job_change()` - Event handler
- `on_sub_job_change()` - Event handler
- `on_notes_change()` - Event handler
- `on_notes_var_change()` - Variable change handler
- `process_barcode()` - Core scanning logic ⭐ CRITICAL
- `check_dependencies()` - Dependency validation
- `show_duplicate_info()` - Dialog display
- `load_today_summary()` - Summary display

**State Variables:**
- `current_job_type`
- `current_sub_job_type`
- `notes_var`
- `barcode_entry_var`
- `job_types_data`
- `sub_job_types_data`

**Dependencies:**
- ScanService
- ScanLogRepository
- SubJobRepository
- DependencyRepository

### 2. History Tab (Lines ~487-524)
**Methods (7):**
- `create_history_tab()` - UI creation
- `create_history_table()` - Table creation
- `search_history()` - Search functionality
- `show_scan_context_menu()` - Context menu
- `edit_scan_record()` - Edit dialog trigger
- `delete_scan_record()` - Delete operation
- `show_edit_dialog()` - Edit dialog ⭐ CAN BE EXTRACTED

**State Variables:**
- None (uses history tree)

**Dependencies:**
- ScanLogRepository
- SubJobRepository

### 3. Reports Tab (Lines ~551-607)
**Methods (5):**
- `create_reports_tab()` - UI creation
- `create_report_table()` - Table creation
- `refresh_report_job_types()` - Data loading
- `on_report_job_type_change()` - Event handler
- `run_report()` - Report generation ⭐ CRITICAL
- `export_report()` - Export to Excel

**State Variables:**
- `report_date_var`
- `report_job_type_var`
- `report_sub_job_type_var`
- `report_note_filter_var`
- `report_job_types_data`
- `report_sub_job_types_data`
- `last_report_data` (for export)

**Dependencies:**
- ReportService
- ScanLogRepository
- JobTypeRepository
- SubJobRepository

### 4. Import Tab (Lines ~405-487)
**Methods (8):**
- `create_import_tab()` - UI creation
- `create_import_preview_table()` - Table creation
- `download_template()` - Template generation
- `show_sample_data()` - Sample data display
- `select_import_file()` - File selection
- `clear_import_data()` - Clear data
- `clear_import_preview()` - Clear preview
- `validate_import_data()` - Validation
- `import_data()` - Import operation

**State Variables:**
- `import_file_path`
- `validated_import_data`

**Dependencies:**
- ImportService
- JobTypeRepository
- SubJobRepository
- ScanLogRepository

### 5. Settings Tab (Lines ~123-192)
**Methods (6):**
- `create_settings_tab()` - UI creation
- `refresh_job_types()` - Data loading
- `on_job_select()` - Event handler
- `refresh_dependencies_display()` - Dependencies display
- `save_dependencies()` - Save dependencies
- `add_job_type()` - Add job type
- `delete_job_type()` - Delete job type

**State Variables:**
- `current_selected_job`
- `dependencies_vars`
- `job_types_data`

**Dependencies:**
- DependencyService
- JobTypeRepository
- DependencyRepository

### 6. Sub Job Settings Tab (Lines ~192-280)
**Methods (8):**
- `create_sub_job_settings_tab()` - UI creation
- `refresh_main_job_list_for_sub()` - Data loading
- `on_main_job_select_for_sub()` - Event handler
- `refresh_sub_job_list()` - Data loading
- `on_sub_job_select()` - Event handler
- `add_sub_job_type()` - Add sub job
- `edit_sub_job_type()` - Edit dialog trigger
- `delete_sub_job_type()` - Delete operation
- `show_sub_job_edit_dialog()` - Edit dialog ⭐ CAN BE EXTRACTED

**State Variables:**
- `current_selected_sub_job`
- `sub_job_types_data`

**Dependencies:**
- SubJobRepository
- JobTypeRepository

## Extraction Strategy

### Phase 4.1: Create Infrastructure
1. Create `src/ui/tabs/` directory
2. Create `src/ui/dialogs/` directory
3. Create `src/ui/tabs/base_tab.py` - Base class for all tabs
4. Create tests directory structure

### Phase 4.2: Extract Dialogs (Smallest components first)
1. Extract `EditScanDialog` from `show_edit_dialog()` → `src/ui/dialogs/edit_scan_dialog.py`
2. Extract `DuplicateWarningDialog` from `show_duplicate_info()` → `src/ui/dialogs/duplicate_warning_dialog.py`
3. Extract `SubJobEditDialog` from `show_sub_job_edit_dialog()` → `src/ui/dialogs/sub_job_edit_dialog.py`

### Phase 4.3: Extract Tabs (In order of independence)
1. **ImportTab** (Most independent) → `src/ui/tabs/import_tab.py`
   - Least dependencies on other tabs
   - Self-contained functionality

2. **ReportsTab** → `src/ui/tabs/reports_tab.py`
   - Uses ReportService
   - Independent of other tabs

3. **HistoryTab** → `src/ui/tabs/history_tab.py`
   - Uses dialogs
   - Independent search/edit functionality

4. **ScanningTab** → `src/ui/tabs/scanning_tab.py`
   - Core functionality
   - Uses ScanService

5. **SettingsTab** → `src/ui/tabs/settings_tab.py`
   - Job type management
   - Dependency configuration

6. **SubJobSettingsTab** → `src/ui/tabs/sub_job_settings_tab.py`
   - Sub job management
   - Uses dialogs

### Phase 4.4: Refactor main_window.py
- Keep only orchestration logic
- Tab initialization
- Service initialization
- Menu bar (if any)
- Window configuration

## Base Tab Class Design

```python
class BaseTab:
    """Base class for all tabs"""

    def __init__(self, parent, db_manager, repositories, services):
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

        # Create tab frame
        self.frame = ttk.Frame(parent)

        # Build UI
        self.build_ui()

    def build_ui(self):
        """Override in subclass to build UI"""
        raise NotImplementedError()

    def get_frame(self):
        """Return the tab frame"""
        return self.frame
```

## Expected Results
- **main_window.py:** 2,652 → ~250 lines (-90%)
- **New Files:** 9 files (6 tabs + 3 dialogs)
- **Tests:** Add tab-specific tests
- **Maintainability:** Each component < 500 lines
- **Reusability:** Tabs can be reused/tested independently

## Testing Strategy
1. Test each tab component independently
2. Test dialogs independently
3. Integration test with main_window
4. Verify all 190 existing tests still pass
5. Add new tab-specific tests

## Rollback Plan
- Keep original main_window.py as main_window_backup.py
- Commit each extraction separately
- If issues arise, can revert individual commits
