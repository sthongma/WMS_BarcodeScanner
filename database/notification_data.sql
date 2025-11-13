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
    job_id INT NULL,          -- งานหลัก (อ้างอิง job_types.id) ถ้า NULL = ใช้ได้ทุกงาน
    sub_job_id INT NULL,      -- งานย่อย (อ้างอิง sub_job_types.id) ถ้า NULL = ใช้ได้ทุกงานย่อยของงานหลักนั้น
    created_date DATETIME2 DEFAULT GETDATE(),
    created_by NVARCHAR(50) NOT NULL,

    -- Constraints
    CONSTRAINT CK_notification_event_type CHECK (event_type IN ('success', 'error', 'duplicate', 'warning')),
    CONSTRAINT CK_notification_popup_type CHECK (popup_type IN ('modal', 'toast'))
    -- หมายเหตุ: ไม่ใส่ FK constraints เพื่อให้นำเข้าข้อมูลได้ง่าย หากต้องการบังคับ referential integrity สามารถเพิ่ม FK ภายหลัง
);

-- สร้าง indexes สำหรับการค้นหาเร็ว
CREATE INDEX IX_notification_data_barcode ON notification_data(barcode)
    WHERE is_enabled = 1;

CREATE INDEX IX_notification_data_enabled ON notification_data(is_enabled)
    WHERE is_enabled = 1;

-- Indexes สำหรับ job_id / sub_job_id เพื่อให้ค้นหาเร็ว
CREATE INDEX IX_notification_data_job ON notification_data(job_id)
    WHERE job_id IS NOT NULL;

CREATE INDEX IX_notification_data_sub_job ON notification_data(sub_job_id)
    WHERE sub_job_id IS NOT NULL;

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
INSERT INTO notification_data (barcode, event_type, popup_type, title, message, is_enabled, job_id, sub_job_id, created_by)
VALUES
    ('TEST001', 'warning', 'modal', 'สินค้าใกล้หมดอายุ', 'สินค้านี้จะหมดอายุภายใน 7 วัน กรุณาตรวจสอบ', 1, NULL, NULL, 'system'),
    ('TEST002', 'error', 'modal', 'สินค้าหมดอายุแล้ว', 'สินค้านี้หมดอายุแล้ว ห้ามจัดส่ง!', 1, NULL, NULL, 'system'),
    ('TEST003', 'warning', 'toast', 'แจ้งเตือนทั่วไป', 'สินค้านี้ต้องเก็บในอุณหภูมิต่ำ', 1, NULL, NULL, 'system');

GO

-- สคริปต์สำหรับลบตาราง (ใช้เมื่อต้องการ reset)
-- DROP TABLE IF EXISTS notification_data;
