-- =====================================================
-- สร้างตาราง audit_logs สำหรับบันทึกประวัติการเปลี่ยนแปลง
-- สำหรับ WMS Barcode Scanner System
-- =====================================================

-- สร้างตาราง audit_logs (บันทึกประวัติการลบและแก้ไขข้อมูลการสแกน)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='audit_logs' AND xtype='U')
BEGIN
    CREATE TABLE audit_logs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        scan_record_id INT NOT NULL,                    -- ID ของข้อมูลสแกนที่ถูกเปลี่ยนแปลง
        action_type NVARCHAR(10) NOT NULL,              -- 'UPDATE' หรือ 'DELETE'
        old_values NVARCHAR(MAX) NULL,                  -- ข้อมูลเดิมในรูปแบบ JSON
        new_values NVARCHAR(MAX) NULL,                  -- ข้อมูลใหม่ในรูปแบบ JSON (NULL สำหรับ DELETE)
        changed_by NVARCHAR(100) NOT NULL,              -- ผู้ที่ทำการเปลี่ยนแปลง
        change_date DATETIME NOT NULL DEFAULT GETDATE(), -- วันที่และเวลาที่เปลี่ยนแปลง
        notes NVARCHAR(500) NULL,                       -- หมายเหตุเพิ่มเติม
        
        -- Constraints
        CONSTRAINT CK_audit_logs_action_type 
            CHECK (action_type IN ('UPDATE', 'DELETE'))
    );
    
    -- สร้าง indexes สำหรับประสิทธิภาพ
    CREATE INDEX IX_audit_logs_scan_record_id ON audit_logs (scan_record_id);
    CREATE INDEX IX_audit_logs_change_date ON audit_logs (change_date);
    CREATE INDEX IX_audit_logs_changed_by ON audit_logs (changed_by);
    CREATE INDEX IX_audit_logs_action_type ON audit_logs (action_type);
    CREATE INDEX IX_audit_logs_scan_record_action ON audit_logs (scan_record_id, action_type);
    
    PRINT 'Table audit_logs created successfully with indexes.';
END
ELSE
BEGIN
    PRINT 'Table audit_logs already exists.';
END

-- สร้างตัวอย่างข้อมูลและการใช้งาน (comment ไว้)
/*
-- ตัวอย่างการใช้งาน:

-- บันทึกการแก้ไขข้อมูล
INSERT INTO audit_logs (scan_record_id, action_type, old_values, new_values, changed_by, notes)
VALUES (
    12345, 
    'UPDATE',
    '{"barcode":"ABC123","notes":"เก่า","job_type":"ตรวจสอบ"}',
    '{"barcode":"ABC123","notes":"ใหม่","job_type":"ตรวจสอบ"}',
    'user123',
    'แก้ไขหมายเหตุ'
);

-- บันทึกการลบข้อมูล
INSERT INTO audit_logs (scan_record_id, action_type, old_values, new_values, changed_by, notes)
VALUES (
    12345, 
    'DELETE',
    '{"barcode":"ABC123","scan_date":"2024-01-01 10:00:00","job_type":"ตรวจสอบ","user_id":"user123"}',
    NULL,
    'admin',
    'ลบข้อมูลผิดพลาด'
);

-- ดูประวัติการเปลี่ยนแปลงของข้อมูลสแกนหนึ่ง record
SELECT 
    al.id,
    al.scan_record_id,
    al.action_type,
    al.old_values,
    al.new_values,
    al.changed_by,
    al.change_date,
    al.notes
FROM audit_logs al
WHERE al.scan_record_id = 12345
ORDER BY al.change_date DESC;

-- ดูประวัติการเปลี่ยนแปลงทั้งหมดของวันนี้
SELECT 
    al.id,
    al.scan_record_id,
    al.action_type,
    al.changed_by,
    al.change_date,
    al.notes
FROM audit_logs al
WHERE CAST(al.change_date AS DATE) = CAST(GETDATE() AS DATE)
ORDER BY al.change_date DESC;
*/

PRINT 'Audit logs table setup completed.';
PRINT '';
PRINT 'Table structure:';
PRINT '- id: Primary key';
PRINT '- scan_record_id: ID ของข้อมูลสแกนที่ถูกเปลี่ยนแปลง';
PRINT '- action_type: UPDATE หรือ DELETE';
PRINT '- old_values: ข้อมูลเดิม (JSON)';
PRINT '- new_values: ข้อมูลใหม่ (JSON)';
PRINT '- changed_by: ผู้ทำการเปลี่ยนแปลง';
PRINT '- change_date: วันที่เปลี่ยนแปลง';
PRINT '- notes: หมายเหตุ';
PRINT '=====================================================';