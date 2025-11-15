-- ===========================================
-- Migration: Add note_fill column to notification_data
-- Date: 2025-11-15
-- Description: เพิ่ม column note_fill เพื่อเก็บข้อความที่จะเติมลงใน notes อัตโนมัติเมื่อสแกนเจอ notification
-- ===========================================

-- ตรวจสอบว่า column note_fill มีอยู่แล้วหรือไม่
IF NOT EXISTS (
    SELECT 1
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'notification_data'
    AND COLUMN_NAME = 'note_fill'
)
BEGIN
    -- เพิ่ม column note_fill
    ALTER TABLE notification_data
    ADD note_fill NVARCHAR(1000) NULL;

    -- เพิ่ม comment อธิบาย column
    EXEC sp_addextendedproperty
        @name = N'MS_Description',
        @value = N'ข้อความที่จะเติมลงใน notes อัตโนมัติเมื่อสแกนเจอ notification นี้ (คั่นด้วย comma ถ้ามีหลายหัวข้อ)',
        @level0type = N'SCHEMA', @level0name = N'dbo',
        @level1type = N'TABLE', @level1name = N'notification_data',
        @level2type = N'COLUMN', @level2name = N'note_fill';

    PRINT 'Column note_fill has been added to notification_data table successfully.';
END
ELSE
BEGIN
    PRINT 'Column note_fill already exists in notification_data table.';
END

GO

-- อัปเดตข้อมูลตัวอย่างให้มี note_fill (optional)
UPDATE notification_data
SET note_fill = 'ตรวจสอบวันหมดอายุแล้ว,ใกล้หมดอายุ'
WHERE barcode = '1' AND note_fill IS NULL;

UPDATE notification_data
SET note_fill = 'สินค้าหมดอายุ,ห้ามจัดส่ง'
WHERE barcode = '2' AND note_fill IS NULL;

UPDATE notification_data
SET note_fill = 'เก็บในอุณหภูมิต่ำ'
WHERE barcode = '3' AND note_fill IS NULL;

PRINT 'Sample data updated with note_fill values.';

GO
