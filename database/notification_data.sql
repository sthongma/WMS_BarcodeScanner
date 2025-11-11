-- ===========================================
-- Notification Data Table
-- สำหรับเก็บข้อมูล popup แจ้งเตือนที่แสดงเมื่อสแกนบาร์โค้ด
-- ===========================================

-- สร้างตาราง notification_data
CREATE TABLE notification_data (
    id INT IDENTITY(1,1) PRIMARY KEY,
    barcode NVARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- success, error, duplicate, warning
    popup_type VARCHAR(20) NOT NULL,   -- modal, toast
    title NVARCHAR(255) NOT NULL,
    message NVARCHAR(MAX) NOT NULL,
    is_enabled BIT DEFAULT 1,
    created_date DATETIME2 DEFAULT GETDATE(),
    created_by NVARCHAR(50) NOT NULL,

    -- Constraints
    CONSTRAINT CK_notification_event_type CHECK (event_type IN ('success', 'error', 'duplicate', 'warning')),
    CONSTRAINT CK_notification_popup_type CHECK (popup_type IN ('modal', 'toast'))
);

-- สร้าง indexes สำหรับการค้นหาเร็ว
CREATE INDEX IX_notification_data_barcode ON notification_data(barcode)
    WHERE is_enabled = 1;

CREATE INDEX IX_notification_data_enabled ON notification_data(is_enabled)
    WHERE is_enabled = 1;

-- Comment อธิบายตาราง
EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'เก็บข้อมูล popup notification ที่แสดงเมื่อสแกนบาร์โค้ด',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'notification_data';

-- Comment สำหรับ columns
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'รหัสบาร์โค้ดที่ต้องการแจ้งเตือน', @level0type = N'SCHEMA', @level0name = N'dbo', @level1type = N'TABLE', @level1name = N'notification_data', @level2type = N'COLUMN', @level2name = N'barcode';
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'ประเภทเหตุการณ์ (เชื่อมกับ sound_settings): success, error, duplicate, warning', @level0type = N'SCHEMA', @level0name = N'dbo', @level1type = N'TABLE', @level1name = N'notification_data', @level2type = N'COLUMN', @level2name = N'event_type';
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'รูปแบบ popup: modal (ต้องกดปิด), toast (หายอัตโนมัติ)', @level0type = N'SCHEMA', @level0name = N'dbo', @level1type = N'TABLE', @level1name = N'notification_data', @level2type = N'COLUMN', @level2name = N'popup_type';
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'หัวข้อแจ้งเตือน', @level0type = N'SCHEMA', @level0name = N'dbo', @level1type = N'TABLE', @level1name = N'notification_data', @level2type = N'COLUMN', @level2name = N'title';
EXEC sp_addextendedproperty @name = N'MS_Description', @value = N'ข้อความแจ้งเตือน', @level0type = N'SCHEMA', @level0name = N'dbo', @level1type = N'TABLE', @level1name = N'notification_data', @level2type = N'COLUMN', @level2name = N'message';

-- ข้อมูลตัวอย่าง (สำหรับทดสอบ)
INSERT INTO notification_data (barcode, event_type, popup_type, title, message, created_by)
VALUES
    ('TEST001', 'warning', 'modal', 'สินค้าใกล้หมดอายุ', 'สินค้านี้จะหมดอายุภายใน 7 วัน กรุณาตรวจสอบ', 'system'),
    ('TEST002', 'error', 'modal', 'สินค้าหมดอายุแล้ว', 'สินค้านี้หมดอายุแล้ว ห้ามจัดส่ง!', 'system'),
    ('TEST003', 'warning', 'toast', 'แจ้งเตือนทั่วไป', 'สินค้านี้ต้องเก็บในอุณหภูมิต่ำ', 'system');

GO

-- สคริปต์สำหรับลบตาราง (ใช้เมื่อต้องการ reset)
-- DROP TABLE IF EXISTS notification_data;
