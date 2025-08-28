-- =====================================================
-- WMS Barcode Scanner Database Setup Script (Clean Version)
-- =====================================================
-- คำอธิบาย: สคริปต์นี้ใช้สำหรับสร้างและตั้งค่าฐานข้อมูล WMS (เฉพาะที่จำเป็น)
-- วันที่อัปเดต: 2024
-- เวอร์ชัน: 2.0 - Clean
-- =====================================================

USE WMS_EP;
GO

-- =====================================================
-- ส่วนที่ 1: สร้างตารางหลัก (Core Tables)
-- =====================================================

-- 1.1 สร้างตาราง job_types (ประเภทงานหลัก)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='job_types' AND xtype='U')
BEGIN
    CREATE TABLE job_types (
        id INT IDENTITY(1,1) PRIMARY KEY,
        job_name NVARCHAR(100) NOT NULL UNIQUE,
        
        -- ID Range: 1-99 (จำกัดไว้ให้ปลอดภัย)
        CONSTRAINT CK_job_types_id_range CHECK (id < 100)
    );
    
    -- เพิ่มข้อมูลตัวอย่างประเภทงาน
    INSERT INTO job_types (job_name) VALUES 
    ('1-RELEASE'),
    ('2-INPROCESS'),
    ('3-OUTBOUND'),
    ('4-LOADING'),
    ('5-RETURN'),
    ('6-REPACK');

    PRINT 'Table job_types created successfully with sample data.';
END
ELSE
BEGIN
    PRINT 'Table job_types already exists.';
END

-- 1.2 สร้างตาราง sub_job_types (ประเภทงานย่อย)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sub_job_types')
BEGIN
    CREATE TABLE sub_job_types (
        id INT IDENTITY(100,1) PRIMARY KEY,
        main_job_id INT NOT NULL,
        sub_job_name NVARCHAR(255) NOT NULL,
        description NVARCHAR(500) NULL,
        created_date DATETIME2 DEFAULT GETDATE(),
        is_active BIT DEFAULT 1,
        
        -- ID Range: 100-9999 (จำกัดไว้ให้ปลอดภัย)
        CONSTRAINT CK_sub_job_types_id_range CHECK (id >= 100 AND id < 10000),
        
        -- Foreign Key
        CONSTRAINT FK_sub_job_types_main_job 
            FOREIGN KEY (main_job_id) REFERENCES job_types(id) 
            ON DELETE CASCADE,
        
        -- Unique constraint
        CONSTRAINT UQ_sub_job_types_name_per_main 
            UNIQUE (main_job_id, sub_job_name)
    );
    
    -- สร้าง Index สำหรับการค้นหาที่เร็วขึ้น
    CREATE INDEX IX_sub_job_types_main_job_id ON sub_job_types(main_job_id);
    
    PRINT 'Table sub_job_types created successfully.';
END
ELSE
BEGIN
    PRINT 'Table sub_job_types already exists.';
END

-- 1.3 สร้างตาราง scan_logs (บันทึกการสแกน)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='scan_logs' AND xtype='U')
BEGIN
    CREATE TABLE scan_logs (
        id INT IDENTITY(10000,1) PRIMARY KEY,
        barcode NVARCHAR(100) NOT NULL,
        scan_date DATETIME NOT NULL DEFAULT GETDATE(),
        job_type NVARCHAR(100) NOT NULL,
        user_id NVARCHAR(50) NOT NULL,
        job_id INT NULL,
        sub_job_id INT NULL,
        notes NVARCHAR(1000) NULL,
        
        -- Foreign keys
        CONSTRAINT FK_scan_logs_job_id 
            FOREIGN KEY (job_id) REFERENCES job_types(id),
        CONSTRAINT FK_scan_logs_sub_job 
            FOREIGN KEY (sub_job_id) REFERENCES sub_job_types(id)
    );
    
    -- สร้าง indexes สำหรับประสิทธิภาพ
    CREATE INDEX IX_scan_logs_barcode ON scan_logs (barcode);
    CREATE INDEX IX_scan_logs_scan_date ON scan_logs (scan_date);
    CREATE INDEX IX_scan_logs_job_type ON scan_logs (job_type);
    CREATE INDEX IX_scan_logs_user_id ON scan_logs (user_id);
    CREATE INDEX IX_scan_logs_job_id ON scan_logs (job_id);
    CREATE INDEX IX_scan_logs_sub_job_id ON scan_logs(sub_job_id);
    CREATE INDEX IX_scan_logs_barcode_job_id ON scan_logs (barcode, job_id);
    
    PRINT 'Table scan_logs created successfully with indexes.';
END
ELSE
BEGIN
    PRINT 'Table scan_logs already exists. Checking for updates...';
    
    -- เพิ่มคอลัมน์ job_id ถ้ายังไม่มี
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE TABLE_NAME = 'scan_logs' AND COLUMN_NAME = 'job_id')
    BEGIN
        ALTER TABLE scan_logs ADD job_id INT NULL;
        ALTER TABLE scan_logs ADD CONSTRAINT FK_scan_logs_job_id 
        FOREIGN KEY (job_id) REFERENCES job_types(id);
        PRINT 'Added job_id column.';
    END
    
    -- เพิ่มคอลัมน์ sub_job_id และ notes ถ้ายังไม่มี
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('scan_logs') AND name = 'sub_job_id')
    BEGIN
        ALTER TABLE scan_logs ADD 
            sub_job_id INT NULL,
            notes NVARCHAR(1000) NULL;
        
        ALTER TABLE scan_logs ADD CONSTRAINT FK_scan_logs_sub_job 
        FOREIGN KEY (sub_job_id) REFERENCES sub_job_types(id);
        
        PRINT 'Added sub_job_id and notes columns.';
    END
END

-- =====================================================
-- สรุปการติดตั้งทั้งหมด
-- =====================================================

PRINT '=====================================================';
PRINT 'WMS Database Setup Completed Successfully! (Clean Version)';
PRINT '=====================================================';
PRINT 'Tables created/updated:';
PRINT '- job_types (ประเภทงานหลัก)';
PRINT '- sub_job_types (ประเภทงานย่อย)';
PRINT '- scan_logs (บันทึกการสแกน)';
PRINT '';
PRINT 'System is ready to use!';
PRINT '=====================================================';