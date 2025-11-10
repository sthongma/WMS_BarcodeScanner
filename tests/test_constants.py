"""
Tests for constants module
Verifies that all constants are properly defined and have expected values
"""

import pytest
from src import constants


class TestWindowSizes:
    """Test window and dialog size constants"""

    def test_main_window_size(self):
        assert constants.WINDOW_MAIN_SIZE == "1200x900"

    def test_login_window_size(self):
        assert constants.WINDOW_LOGIN_SIZE == "550x550"

    def test_dialog_sizes_defined(self):
        """Test that all dialog sizes are defined"""
        assert hasattr(constants, "DIALOG_DUPLICATE_WARNING_SIZE")
        assert hasattr(constants, "DIALOG_DUPLICATE_INFO_SIZE")
        assert hasattr(constants, "DIALOG_EDIT_SCAN_SIZE")
        assert hasattr(constants, "DIALOG_EDIT_HISTORY_SIZE")


class TestUIComponentSizes:
    """Test UI component size constants"""

    def test_entry_field_widths(self):
        assert constants.ENTRY_FIELD_WIDTH == 40
        assert constants.COMBOBOX_WIDTH == 30

    def test_treeview_heights(self):
        """Test treeview height constants"""
        assert constants.TREEVIEW_HEIGHT_SMALL == 6
        assert constants.TREEVIEW_HEIGHT_MEDIUM == 8
        assert constants.TREEVIEW_HEIGHT_STANDARD == 10
        assert constants.TREEVIEW_HEIGHT_LARGE == 15

    def test_column_widths(self):
        """Test column width constants"""
        assert constants.COLUMN_WIDTH_DEFAULT == 120
        assert constants.COLUMN_WIDTH_WIDE == 150
        assert constants.COLUMN_WIDTH_EXTRA_WIDE == 200


class TestTimeSettings:
    """Test time and date related constants"""

    def test_duplicate_check_hours(self):
        assert constants.DUPLICATE_CHECK_HOURS_FULL_HISTORY == 24 * 365

    def test_date_formats(self):
        assert constants.DATE_FORMAT == "%Y-%m-%d"
        assert constants.DATETIME_FORMAT == "%Y-%m-%d %H:%M:%S"
        assert constants.FILENAME_DATE_FORMAT == "%Y%m%d"

    def test_default_date_range(self):
        assert constants.DEFAULT_DATE_RANGE_DAYS == 7


class TestDataLimits:
    """Test data limit constants"""

    def test_scan_limits(self):
        assert constants.RECENT_SCANS_LIMIT == 50
        assert constants.HISTORY_SCANS_LIMIT == 10000

    def test_import_limits(self):
        assert constants.IMPORT_PREVIEW_LIMIT == 20
        assert constants.IMPORT_ERRORS_DISPLAY_LIMIT == 10


class TestFileExtensions:
    """Test file extension constants"""

    def test_excel_extensions(self):
        assert constants.FILE_EXTENSION_EXCEL_XLSX == ".xlsx"
        assert constants.FILE_EXTENSION_EXCEL_XLS == ".xls"
        assert constants.FILE_EXTENSIONS_EXCEL == (".xlsx", ".xls")

    def test_csv_extension(self):
        assert constants.FILE_EXTENSION_CSV == ".csv"

    def test_import_extensions(self):
        assert constants.FILE_EXTENSIONS_IMPORT == (".xlsx", ".xls", ".csv")


class TestDatabaseColumns:
    """Test database column name constants"""

    def test_primary_columns(self):
        assert constants.COL_ID == "id"
        assert constants.COL_NAME == "name"
        assert constants.COL_STATUS == "status"

    def test_job_columns(self):
        assert constants.COL_MAIN_JOB_ID == "main_job_id"
        assert constants.COL_SUB_JOB_ID == "sub_job_id"
        assert constants.COL_JOB_TYPE_NAME == "job_type_name"

    def test_scan_columns(self):
        assert constants.COL_BARCODE == "barcode"
        assert constants.COL_SCAN_DATE == "scan_date"
        assert constants.COL_USER_ID == "user_id"
        assert constants.COL_NOTES == "notes"

    def test_required_import_columns(self):
        assert constants.REQUIRED_IMPORT_COLUMNS == [
            "barcode",
            "main_job_id",
            "sub_job_id",
        ]


class TestUITextThai:
    """Test Thai language UI text constants"""

    def test_tab_names(self):
        """Test tab name constants"""
        assert constants.TAB_SCANNING == "หน้าจอหลัก"
        assert constants.TAB_HISTORY == "ประวัติการสแกน"
        assert constants.TAB_REPORTS == "รายงาน"

    def test_button_labels(self):
        """Test button label constants"""
        assert constants.BUTTON_SCAN == "สแกน"
        assert constants.BUTTON_CLEAR == "ล้างข้อมูล"
        assert constants.BUTTON_REFRESH == "รีเฟรช"
        assert constants.BUTTON_SEARCH == "ค้นหา"

    def test_status_messages(self):
        """Test status message constants"""
        assert constants.STATUS_SUCCESS == "สำเร็จ"
        assert constants.STATUS_PASS == "ผ่าน"
        assert constants.STATUS_FAIL == "ไม่ผ่าน"


class TestErrorMessages:
    """Test error message constants"""

    def test_validation_errors(self):
        """Test input validation error messages"""
        assert constants.ERROR_EMPTY_BARCODE == "กรุณาใส่บาร์โค้ด"
        assert constants.ERROR_NO_JOB_TYPE == "กรุณาเลือกประเภทงานหลักก่อน"
        assert constants.ERROR_NO_SUB_JOB_TYPE == "กรุณาเลือกประเภทงานย่อยก่อน"

    def test_data_operation_errors(self):
        """Test data operation error messages"""
        assert constants.ERROR_DUPLICATE_BARCODE == "พบข้อมูลซ้ำ"
        # Error messages with placeholders
        assert "{}" in constants.ERROR_SAVE_DATA
        assert "{}" in constants.ERROR_CHECK_DUPLICATE

    def test_missing_data_errors(self):
        """Test missing data error messages"""
        assert "{}" in constants.ERROR_JOB_NOT_FOUND
        assert "{}" in constants.ERROR_SUB_JOB_NOT_FOUND


class TestColumnHeaders:
    """Test column header constants"""

    def test_scanning_history_columns(self):
        assert len(constants.COLUMNS_SCANNING_HISTORY) == 5
        assert "Barcode" in constants.COLUMNS_SCANNING_HISTORY

    def test_history_columns(self):
        assert len(constants.COLUMNS_HISTORY) == 8
        assert "Barcode" in constants.COLUMNS_HISTORY
        assert "หมายเหตุ" in constants.COLUMNS_HISTORY

    def test_import_preview_columns(self):
        assert len(constants.COLUMNS_IMPORT_PREVIEW) == 6

    def test_report_columns(self):
        assert len(constants.COLUMNS_REPORT) == 6
        assert "barcode" in constants.COLUMNS_REPORT


class TestTemplateColumns:
    """Test template column definitions"""

    def test_template_columns_structure(self):
        """Test template columns are properly defined"""
        assert isinstance(constants.TEMPLATE_COLUMNS, list)
        assert len(constants.TEMPLATE_COLUMNS) == 4

    def test_template_columns_have_required_fields(self):
        """Test each template column has required fields"""
        for col in constants.TEMPLATE_COLUMNS:
            assert "name" in col
            assert "thai_name" in col
            assert "required" in col

    def test_required_columns_marked_correctly(self):
        """Test that barcode, main_job_id, sub_job_id are marked required"""
        required_count = sum(1 for col in constants.TEMPLATE_COLUMNS if col["required"])
        assert required_count == 3  # barcode, main_job_id, sub_job_id


class TestDefaultValues:
    """Test default value constants"""

    def test_auth_defaults(self):
        assert constants.DEFAULT_AUTH_TYPE == "SQL"
        assert constants.AUTH_TYPE_WINDOWS == "Windows"
        assert constants.AUTH_TYPE_SQL == "SQL"

    def test_widget_states(self):
        assert constants.WIDGET_STATE_READONLY == "readonly"
        assert constants.WIDGET_STATE_NORMAL == "normal"
        assert constants.WIDGET_STATE_DISABLED == "disabled"

    def test_boolean_defaults(self):
        assert constants.DEFAULT_CHECKBOX_STATE is True
        assert constants.DEFAULT_ACTIVE_ONLY is True


class TestPaddingConstants:
    """Test padding and spacing constants"""

    def test_standard_padding(self):
        assert constants.PADDING_STANDARD == {"padx": 10, "pady": 10}
        assert constants.PADDING_SMALL == {"padx": 5, "pady": 5}
        assert constants.PADDING_LARGE == {"padx": 10, "pady": 20}

    def test_section_padding(self):
        assert constants.PADDING_SECTION_TOP == {"pady": (0, 20)}
        assert constants.PADDING_SECTION_VERTICAL == {"pady": (0, 10)}


class TestFonts:
    """Test font constants"""

    def test_font_definitions(self):
        assert constants.FONT_TITLE == ("Arial", 14, "bold")
        assert constants.FONT_HEADING == ("Arial", 12, "bold")
        assert constants.FONT_REGULAR == ("Arial", 12)


class TestAppMetadata:
    """Test application metadata constants"""

    def test_app_metadata_exists(self):
        assert hasattr(constants, "APP_NAME")
        assert hasattr(constants, "APP_VERSION")
        assert isinstance(constants.APP_NAME, str)
        assert isinstance(constants.APP_VERSION, str)


class TestConstantsIntegrity:
    """Test overall constants integrity"""

    def test_no_duplicate_values_for_unique_keys(self):
        """Test that certain key constants have unique values"""
        # Tab names should all be unique
        tab_names = [
            constants.TAB_SCANNING,
            constants.TAB_HISTORY,
            constants.TAB_REPORTS,
            constants.TAB_IMPORT,
            constants.TAB_JOB_SETTINGS,
            constants.TAB_SUB_JOB_SETTINGS,
        ]
        assert len(tab_names) == len(set(tab_names))

    def test_column_names_consistency(self):
        """Test that column names used in multiple places are consistent"""
        # Barcode column should be consistent
        assert constants.COL_BARCODE == "barcode"
        assert "barcode" in constants.REQUIRED_IMPORT_COLUMNS

    def test_no_empty_strings(self):
        """Test that important constants are not empty strings"""
        assert constants.ERROR_EMPTY_BARCODE != ""
        assert constants.TAB_SCANNING != ""
        assert constants.BUTTON_SCAN != ""
