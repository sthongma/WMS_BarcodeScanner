"""
WMS Barcode Scanner - Constants
Central repository for all hard-coded values used throughout the application.
"""

# ============================================================================
# WINDOW & DIALOG SIZES
# ============================================================================

# Main Application Windows
WINDOW_MAIN_SIZE = "1200x900"
WINDOW_LOGIN_SIZE = "550x550"

# Dialog Windows
DIALOG_DUPLICATE_WARNING_SIZE = "500x200"
DIALOG_DUPLICATE_INFO_SIZE = "500x300"
DIALOG_EDIT_SCAN_SIZE = "600x400"
DIALOG_EDIT_HISTORY_SIZE = "400x300"
DIALOG_STATISTICS_SIZE = "500x400"
DIALOG_SUB_JOB_EDIT_SIZE = "400x220"

# ============================================================================
# UI COMPONENT SIZES
# ============================================================================

# Entry Field & Combobox Widths
ENTRY_FIELD_WIDTH = 40
ENTRY_FIELD_LOGIN_WIDTH = 35
COMBOBOX_WIDTH = 30
FILTER_FIELD_WIDTH = 20
JOB_LIST_WIDTH = 25

# Treeview Heights
TREEVIEW_HEIGHT_SMALL = 6
TREEVIEW_HEIGHT_MEDIUM = 8
TREEVIEW_HEIGHT_STANDARD = 10
TREEVIEW_HEIGHT_LARGE = 15
TREEVIEW_HEIGHT_XL = 20

# Column Widths for Treeviews
COLUMN_WIDTH_SMALL = 100
COLUMN_WIDTH_DEFAULT = 120
COLUMN_WIDTH_WIDE = 150
COLUMN_WIDTH_EXTRA_WIDE = 200

# ============================================================================
# SPACING & PADDING
# ============================================================================

# Standard Padding (padx, pady)
PADDING_STANDARD = {"padx": 10, "pady": 10}
PADDING_SMALL = {"padx": 5, "pady": 5}
PADDING_LARGE = {"padx": 10, "pady": 20}

# Specific Padding for Sections
PADDING_SECTION_TOP = {"pady": (0, 20)}
PADDING_SECTION_VERTICAL = {"pady": (0, 10)}

# ============================================================================
# FONTS
# ============================================================================

FONT_TITLE = ("Arial", 14, "bold")
FONT_HEADING = ("Arial", 12, "bold")
FONT_HEADING_SMALL = ("Arial", 10, "bold")
FONT_REGULAR = ("Arial", 12)
FONT_REGULAR_SMALL = ("Arial", 11)

# ============================================================================
# TIME & DATE SETTINGS
# ============================================================================

# Time Windows (in hours)
DUPLICATE_CHECK_HOURS_FULL_HISTORY = 24 * 365  # Check entire year's history
DEFAULT_DATE_RANGE_DAYS = 7  # Default date range for filters

# Auto-close Timers (in milliseconds)
DUPLICATE_WARNING_AUTO_CLOSE_MS = 3000  # 3 seconds

# Date/Time Formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
FILENAME_DATE_FORMAT = "%Y%m%d"

# ============================================================================
# DATA LIMITS
# ============================================================================

RECENT_SCANS_LIMIT = 50
HISTORY_SCANS_LIMIT = 10000
IMPORT_PREVIEW_LIMIT = 20
IMPORT_ERRORS_DISPLAY_LIMIT = 10

# ============================================================================
# FILE EXTENSIONS
# ============================================================================

FILE_EXTENSION_EXCEL_XLSX = ".xlsx"
FILE_EXTENSION_EXCEL_XLS = ".xls"
FILE_EXTENSION_CSV = ".csv"

FILE_EXTENSIONS_EXCEL = (".xlsx", ".xls")
FILE_EXTENSIONS_IMPORT = (".xlsx", ".xls", ".csv")

# ============================================================================
# DATABASE COLUMN NAMES
# ============================================================================

# Primary Columns
COL_ID = "id"
COL_NAME = "name"
COL_DESCRIPTION = "description"
COL_STATUS = "status"
COL_IS_ACTIVE = "is_active"

# Job Related Columns
COL_JOB_ID = "job_id"
COL_MAIN_JOB_ID = "main_job_id"
COL_SUB_JOB_ID = "sub_job_id"
COL_JOB_TYPE = "job_type"
COL_JOB_TYPE_NAME = "job_type_name"
COL_SUB_JOB_TYPE_NAME = "sub_job_type_name"

# Scan Related Columns
COL_BARCODE = "barcode"
COL_SCAN_DATE = "scan_date"
COL_USER_ID = "user_id"
COL_SCANNED_BY = "scanned_by"
COL_NOTES = "notes"

# Import Required Columns
REQUIRED_IMPORT_COLUMNS = ["barcode", "main_job_id", "sub_job_id"]
OPTIONAL_IMPORT_COLUMNS = ["notes"]

# ============================================================================
# UI TEXT - TAB NAMES (THAI)
# ============================================================================

TAB_SCANNING = "หน้าจอหลัก"
TAB_HISTORY = "ประวัติการสแกน"
TAB_REPORTS = "รายงาน"
TAB_IMPORT = "นำเข้าข้อมูล"
TAB_JOB_SETTINGS = "จัดการประเภทงานหลัก"
TAB_SUB_JOB_SETTINGS = "จัดการประเภทงานย่อย"
TAB_DATABASE_SETTINGS = "ตั้งค่าฐานข้อมูล"

# ============================================================================
# UI TEXT - SECTION TITLES (THAI)
# ============================================================================

SECTION_SCANNING = "การสแกน"
SECTION_SCAN_HISTORY = "ประวัติการสแกนล่าสุด"
SECTION_FILTER = "ตัวกรอง"
SECTION_RESULTS = "ผลลัพธ์"
SECTION_REPORT_CONDITIONS = "เลือกเงื่อนไขรายงาน"
SECTION_REPORT_RESULTS = "ผลลัพธ์รายงาน"
SECTION_FILE_SELECT = "เลือกไฟล์"
SECTION_DATA_VALIDATION = "ตรวจสอบข้อมูล"

# ============================================================================
# UI TEXT - LABELS (THAI)
# ============================================================================

LABEL_BARCODE = "Barcode:"
LABEL_JOB_TYPE = "Job Type:"
LABEL_SUB_JOB_TYPE = "Sub Job Type:"
LABEL_MAIN_JOB = "งานหลัก:"
LABEL_SUB_JOB = "งานรอง:"
LABEL_DATE = "วันที่:"
LABEL_DATE_START = "วันที่เริ่มต้น:"
LABEL_DATE_END = "วันที่สิ้นสุด:"
LABEL_NOTES = "หมายเหตุ:"
LABEL_FILTER_NOTES = "กรองหมายเหตุ:"
LABEL_ALL = "ทั้งหมด"
LABEL_USER = "ผู้ใช้:"
LABEL_STATUS = "สถานะ:"

# ============================================================================
# UI TEXT - BUTTONS (THAI)
# ============================================================================

BUTTON_SCAN = "สแกน"
BUTTON_CLEAR = "ล้างข้อมูล"
BUTTON_REFRESH = "รีเฟรช"
BUTTON_SEARCH = "ค้นหา"
BUTTON_CLEAR_FILTER = "ล้างตัวกรอง"
BUTTON_EDIT = "แก้ไข"
BUTTON_DELETE = "ลบ"
BUTTON_EXPORT = "ส่งออก"
BUTTON_EXPORT_EXCEL = "ส่งออก Excel"
BUTTON_IMPORT = "นำเข้าข้อมูล"
BUTTON_VALIDATE = "ตรวจสอบข้อมูล"
BUTTON_ADD = "เพิ่ม"
BUTTON_SAVE = "บันทึก"
BUTTON_CANCEL = "ยกเลิก"
BUTTON_VIEW_REPORT = "ดูรายงาน"
BUTTON_DOWNLOAD_TEMPLATE = "ดาวน์โหลด Template"
BUTTON_SELECT_FILE = "เลือกไฟล์ Excel/CSV"
BUTTON_STATISTICS = "สถิติ"
BUTTON_CONTINUE = "ดำเนินการต่อ"

# ============================================================================
# UI TEXT - MENU ITEMS (THAI)
# ============================================================================

MENU_EXPORT = "ส่งออก"
MENU_EDIT = "แก้ไข"
MENU_DELETE = "ลบ"

# ============================================================================
# UI TEXT - STATUS MESSAGES (THAI)
# ============================================================================

STATUS_SUCCESS = "สำเร็จ"
STATUS_PASS = "ผ่าน"
STATUS_FAIL = "ไม่ผ่าน"
STATUS_PENDING = "รอตรวจสอบ"
STATUS_ACTIVE = "เปิดใช้งาน"
STATUS_INACTIVE = "ปิดใช้งาน"

# ============================================================================
# UI TEXT - INFO MESSAGES (THAI)
# ============================================================================

INFO_NO_FILE_SELECTED = "ยังไม่ได้เลือกไฟล์"
INFO_FILE_SELECTED = "ไฟล์: {}"
INFO_NO_DATA_FOUND = "ไม่พบข้อมูลในวันที่ที่เลือก"
INFO_DATA_FOUND = "พบข้อมูล {} รายการ"
INFO_SCAN_SUCCESS = "สแกนสำเร็จ"
INFO_DUPLICATE_BARCODE = "บาร์โค้ด {} ถูกสแกนแล้ว"
INFO_REPORT_SUCCESS = "รันรายงานสำเร็จ พบข้อมูล {} รายการ"

# ============================================================================
# ERROR MESSAGES - INPUT VALIDATION (THAI)
# ============================================================================

ERROR_EMPTY_BARCODE = "กรุณาใส่บาร์โค้ด"
ERROR_NO_JOB_TYPE = "กรุณาเลือกประเภทงานหลักก่อน"
ERROR_NO_SUB_JOB_TYPE = "กรุณาเลือกประเภทงานย่อยก่อน"
ERROR_INVALID_SUB_JOB = "ไม่พบประเภทงานย่อยที่เลือก"
ERROR_NO_DATE = "กรุณาระบุวันที่"
ERROR_INVALID_DATE_FORMAT = "รูปแบบวันที่ไม่ถูกต้อง (ต้องเป็น YYYY-MM-DD)"
ERROR_DATE_RANGE_INVALID = "วันที่เริ่มต้นต้องไม่เกินวันที่สิ้นสุด"

# ============================================================================
# ERROR MESSAGES - DATA OPERATIONS (THAI)
# ============================================================================

ERROR_DUPLICATE_BARCODE = "พบข้อมูลซ้ำ"
ERROR_SAVE_DATA = "ไม่สามารถบันทึกข้อมูลได้: {}"
ERROR_CHECK_DUPLICATE = "ไม่สามารถตรวจสอบข้อมูลซ้ำได้: {}"
ERROR_CHECK_DEPENDENCIES = "ไม่สามารถตรวจสอบ dependencies ได้: {}"
ERROR_CREATE_REPORT = "ไม่สามารถสร้างรายงานได้: {}"
ERROR_READ_FILE = "ไม่สามารถอ่านไฟล์ได้หรือไฟล์ว่างเปล่า"
ERROR_LOAD_FILE = "เกิดข้อผิดพลาดในการโหลดไฟล์: {}"

# ============================================================================
# ERROR MESSAGES - MISSING DATA (THAI)
# ============================================================================

ERROR_JOB_NOT_FOUND = "ไม่พบงานหลักที่มี ID {}"
ERROR_SUB_JOB_NOT_FOUND = "ไม่พบงานย่อยที่มี ID {}"
ERROR_SUB_JOB_MISMATCH = "งานย่อยไม่ตรงกับงานหลักที่เลือก"
ERROR_MISSING_DEPENDENCIES = "ไม่มีงาน {}"  # Followed by list of missing jobs
ERROR_NO_IMPORT_DATA = "ไม่มีข้อมูลให้นำเข้า"
ERROR_NO_VALID_DATA = "ไม่มีข้อมูลที่ถูกต้องให้นำเข้า"

# ============================================================================
# SUCCESS MESSAGES (THAI)
# ============================================================================

SUCCESS_SCAN = "สแกนสำเร็จ"
SUCCESS_VALIDATION_COMPLETE = "ตรวจสอบข้อมูลเสร็จสิ้น: ถูกต้อง {} แถว, ผิดพลาด {} แถว"
SUCCESS_IMPORT_COMPLETE = "นำเข้าข้อมูลเสร็จสิ้น: สำเร็จ {} แถว, ล้มเหลว {} แถว"

# ============================================================================
# DISPLAY TEXT - MORE ERRORS (THAI)
# ============================================================================

TEXT_MORE_ERRORS = "... และอีก {} ข้อผิดพลาด"
TEXT_ERROR_DETAILS = "ข้อผิดพลาดในข้อมูล:"

# ============================================================================
# COLUMN HEADERS - TREEVIEW DISPLAYS (THAI/ENGLISH)
# ============================================================================

# Scanning Tab History Columns
COLUMNS_SCANNING_HISTORY = ("เวลา", "Barcode", "Job Type", "Sub Job Type", "สถานะ")

# History Tab Columns
COLUMNS_HISTORY = (
    "ID",
    "วันที่สแกน",
    "Barcode",
    "Job Type",
    "Sub Job Type",
    "ผู้สแกน",
    "สถานะ",
    "หมายเหตุ",
)

# Import Tab Preview Columns
COLUMNS_IMPORT_PREVIEW = (
    "แถว",
    "Barcode",
    "Job Type",
    "Sub Job Type",
    "หมายเหตุ",
    "สถานะ",
)

# Reports Tab Columns
COLUMNS_REPORT = (
    "barcode",
    "scan_date",
    "job_type_name",
    "sub_job_type_name",
    "user_id",
    "notes",
)

# Settings Tab - Job Types Columns
COLUMNS_JOB_TYPES = ("ID", "Name", "Description", "Status")

# Settings Tab - Dependencies Columns
COLUMNS_DEPENDENCIES = ("Job Type", "Dependent Job", "Order", "Required")

# Statistics Dialog Columns
COLUMNS_STATISTICS = ("Job Type", "จำนวนการสแกน")

# ============================================================================
# TEMPLATE COLUMN DEFINITIONS (For Import/Export)
# ============================================================================

TEMPLATE_COLUMNS = [
    {"name": "barcode", "thai_name": "บาร์โค้ด", "required": True},
    {"name": "main_job_id", "thai_name": "ID_ประเภทงานหลัก", "required": True},
    {"name": "sub_job_id", "thai_name": "ID_ประเภทงานย่อย", "required": True},
    {"name": "notes", "thai_name": "หมายเหตุ", "required": False},
]

# ============================================================================
# DEFAULT VALUES
# ============================================================================

# Authentication
DEFAULT_AUTH_TYPE = "SQL"
AUTH_TYPE_WINDOWS = "Windows"
AUTH_TYPE_SQL = "SQL"

# Widget States
WIDGET_STATE_READONLY = "readonly"
WIDGET_STATE_NORMAL = "normal"
WIDGET_STATE_DISABLED = "disabled"

# Default Boolean Values
DEFAULT_CHECKBOX_STATE = True
DEFAULT_ACTIVE_ONLY = True

# ============================================================================
# APPLICATION METADATA
# ============================================================================

APP_NAME = "WMS Barcode Scanner"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Development Team"
