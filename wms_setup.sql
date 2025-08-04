-- =====================================================
-- WMS Barcode Scanner Database Setup Script
-- =====================================================
-- คำอธิบาย: สคริปต์นี้ใช้สำหรับสร้างและตั้งค่าฐานข้อมูล WMS
-- วันที่สร้าง: 2024
-- เวอร์ชัน: 1.0
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
        job_name VARCHAR(100) NOT NULL UNIQUE
    );
    
    -- เพิ่มข้อมูลตัวอย่างประเภทงาน
    INSERT INTO job_types (job_name) VALUES 
    ('1.Release'),
    ('2.Inprocess'),
    ('3.Outbound'),
    ('4.Loading'),
    ('5.Return'),
    ('6.Repack');
    
    PRINT 'Table job_types created successfully with sample data.';
END
ELSE
BEGIN
    -- จัดการตารางที่มีอยู่แล้ว
    PRINT 'Table job_types already exists. Checking for updates...';
    
    -- เพิ่มคอลัมน์ id ถ้ายังไม่มี (สำหรับตารางที่มีอยู่)
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE TABLE_NAME = 'job_types' AND COLUMN_NAME = 'id')
    BEGIN
        ALTER TABLE job_types ADD id INT IDENTITY(1,1);
        PRINT 'Added id column to existing job_types table.';
    END
    
    -- เพิ่ม unique constraint สำหรับ job_name ถ้ายังไม่มี
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('job_types') AND name = 'UQ_job_types_job_name')
    BEGIN
        ALTER TABLE job_types ADD CONSTRAINT UQ_job_types_job_name UNIQUE (job_name);
        PRINT 'Added unique constraint for job_name.';
    END
    
    -- ลบคอลัมน์ priority_order ถ้ามี (ระบบเก่า)
    IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'job_types' AND COLUMN_NAME = 'priority_order')
    BEGIN
        ALTER TABLE job_types DROP COLUMN priority_order;
        PRINT 'Removed old priority_order column.';
    END
END

-- 1.2 สร้างตาราง job_dependencies (ความสัมพันธ์ระหว่างงาน)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='job_dependencies' AND xtype='U')
BEGIN
    CREATE TABLE job_dependencies (
        id INT IDENTITY(1,1) PRIMARY KEY,
        job_id INT NOT NULL,
        required_job_id INT NOT NULL,
        
        -- Foreign key constraints
        CONSTRAINT FK_job_dependencies_job_id 
            FOREIGN KEY (job_id) REFERENCES job_types(id) ON DELETE CASCADE,
        CONSTRAINT FK_job_dependencies_required_job_id 
            FOREIGN KEY (required_job_id) REFERENCES job_types(id) ON DELETE NO ACTION,
        
        -- ป้องกันการอ้างอิงตัวเองและความซ้ำซ้อน
        CONSTRAINT CK_job_dependencies_no_self CHECK (job_id != required_job_id),
        CONSTRAINT UQ_job_dependencies UNIQUE (job_id, required_job_id)
    );
    
    -- สร้าง indexes สำหรับประสิทธิภาพ
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_job_dependencies_job_id')
        CREATE INDEX IX_job_dependencies_job_id ON job_dependencies (job_id);
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_job_dependencies_required_job_id')
        CREATE INDEX IX_job_dependencies_required_job_id ON job_dependencies (required_job_id);
    
    -- เพิ่มข้อมูลตัวอย่างความสัมพันธ์
    INSERT INTO job_dependencies (job_id, required_job_id) 
    SELECT j1.id, j2.id 
    FROM job_types j1, job_types j2 
    WHERE j1.job_name = 'ตรวจนับ' AND j2.job_name = 'รับของ';
    
    INSERT INTO job_dependencies (job_id, required_job_id) 
    SELECT j1.id, j2.id 
    FROM job_types j1, job_types j2 
    WHERE j1.job_name = 'โอนย้าย' AND j2.job_name = 'ตรวจนับ';
    
    PRINT 'Table job_dependencies created successfully with sample dependencies.';
END
ELSE
BEGIN
    PRINT 'Table job_dependencies already exists.';
END

-- 1.3 สร้างตาราง scan_logs (บันทึกการสแกน)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='scan_logs' AND xtype='U')
BEGIN
    CREATE TABLE scan_logs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        barcode VARCHAR(100) NOT NULL,
        scan_date DATETIME NOT NULL DEFAULT GETDATE(),
        job_type VARCHAR(100) NOT NULL,
        user_id VARCHAR(50) NOT NULL,
        job_id INT NULL,
        
        -- Foreign key to job_types
        CONSTRAINT FK_scan_logs_job_id 
            FOREIGN KEY (job_id) REFERENCES job_types(id)
    );
    
    -- สร้าง indexes สำหรับประสิทธิภาพ
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_scan_logs_barcode')
        CREATE INDEX IX_scan_logs_barcode ON scan_logs (barcode);
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_scan_logs_scan_date')
        CREATE INDEX IX_scan_logs_scan_date ON scan_logs (scan_date);
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_scan_logs_job_type')
        CREATE INDEX IX_scan_logs_job_type ON scan_logs (job_type);
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_scan_logs_user_id')
        CREATE INDEX IX_scan_logs_user_id ON scan_logs (user_id);
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_scan_logs_job_id')
        CREATE INDEX IX_scan_logs_job_id ON scan_logs (job_id);
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_scan_logs_barcode_job_id')
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
        
        -- เพิ่ม foreign key constraint
        ALTER TABLE scan_logs ADD CONSTRAINT FK_scan_logs_job_id 
        FOREIGN KEY (job_id) REFERENCES job_types(id);
        
        -- สร้าง indexes สำหรับ job_id
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_scan_logs_job_id')
            CREATE INDEX IX_scan_logs_job_id ON scan_logs (job_id);
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_scan_logs_barcode_job_id')
            CREATE INDEX IX_scan_logs_barcode_job_id ON scan_logs (barcode, job_id);
        
        -- อัปเดตข้อมูลที่มีอยู่ให้ตรงกับ job_id
        UPDATE sl SET job_id = jt.id 
        FROM scan_logs sl 
        INNER JOIN job_types jt ON sl.job_type = jt.job_name
        WHERE sl.job_id IS NULL;
        
        PRINT 'Added job_id column and updated existing records.';
    END
    
    -- ลบคอลัมน์ priority_order ถ้ามี (ระบบเก่า)
    IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'scan_logs' AND COLUMN_NAME = 'priority_order')
    BEGIN
        DROP INDEX IF EXISTS IX_scan_logs_priority_order ON scan_logs;
        ALTER TABLE scan_logs DROP COLUMN priority_order;
        PRINT 'Removed old priority_order column from scan_logs.';
    END
END

-- =====================================================
-- ส่วนที่ 2: ระบบประเภทงานย่อย (Sub Job Types System)
-- =====================================================

-- 2.1 สร้างตาราง sub_job_types
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sub_job_types')
BEGIN
    CREATE TABLE sub_job_types (
        id INT IDENTITY(1,1) PRIMARY KEY,
        main_job_id INT NOT NULL,
        sub_job_name NVARCHAR(255) NOT NULL,
        description NVARCHAR(500) NULL,
        created_date DATETIME2 DEFAULT GETDATE(),
        updated_date DATETIME2 DEFAULT GETDATE(),
        is_active BIT DEFAULT 1,
        
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

-- 2.2 เพิ่มคอลัมน์ใน scan_logs สำหรับประเภทงานย่อยและหมายเหตุ
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('scan_logs') AND name = 'sub_job_id')
BEGIN
    ALTER TABLE scan_logs 
    ADD sub_job_id INT NULL,
        notes NVARCHAR(1000) NULL;
    
    PRINT 'Added sub_job_id and notes columns to scan_logs.';
END
ELSE
BEGIN
    PRINT 'Columns sub_job_id and notes already exist in scan_logs.';
END

-- 2.3 เพิ่ม Foreign Key สำหรับ sub_job_id
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_scan_logs_sub_job')
BEGIN
    ALTER TABLE scan_logs
    ADD CONSTRAINT FK_scan_logs_sub_job 
        FOREIGN KEY (sub_job_id) REFERENCES sub_job_types(id);
    
    PRINT 'Foreign key FK_scan_logs_sub_job added.';
END
ELSE
BEGIN
    PRINT 'Foreign key FK_scan_logs_sub_job already exists.';
END

-- 2.4 สร้าง Index สำหรับ sub_job_id
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_scan_logs_sub_job_id')
BEGIN
    CREATE INDEX IX_scan_logs_sub_job_id ON scan_logs(sub_job_id);
    PRINT 'Index IX_scan_logs_sub_job_id created.';
END

-- =====================================================
-- ส่วนที่ 3: Stored Procedures สำหรับรายงาน
-- =====================================================

-- 3.1 Stored Procedure สำหรับประวัติการสแกน
-- =====================================================
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetScanHistory')
    DROP PROCEDURE sp_GetScanHistory;
GO

CREATE PROCEDURE sp_GetScanHistory
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        sl.id,
        sl.barcode,
        sl.scan_date,
        sl.job_type,
        sl.user_id,
        jt.id as job_id,
        COUNT(*) OVER() as total_records
    FROM scan_logs sl
    LEFT JOIN job_types jt ON sl.job_type = jt.job_name
    WHERE sl.scan_date >= DATEADD(day, -30, GETDATE())
    ORDER BY sl.scan_date DESC;
END
GO

-- 3.2 Stored Procedure สำหรับความสัมพันธ์ระหว่างงาน
-- =====================================================
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetJobDependencies')
    DROP PROCEDURE sp_GetJobDependencies;
GO

CREATE PROCEDURE sp_GetJobDependencies
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        jt1.job_name as job_name,
        jt1.id as job_id,
        jt2.job_name as required_job_name,
        jt2.id as required_job_id
    FROM job_dependencies jd
    INNER JOIN job_types jt1 ON jd.job_id = jt1.id
    INNER JOIN job_types jt2 ON jd.required_job_id = jt2.id
    ORDER BY jt1.job_name, jt2.job_name;
END
GO

-- 3.3 Stored Procedure สำหรับสรุปรายวัน
-- =====================================================
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetDailySummary')
    DROP PROCEDURE sp_GetDailySummary;
GO

CREATE PROCEDURE sp_GetDailySummary
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        CAST(sl.scan_date AS DATE) as scan_date,
        jt.job_name as job_main,
        ISNULL(sjt.sub_job_name, 'ไม่มี') as job_sub,
        COUNT(*) as scan_count
    FROM scan_logs sl
    LEFT JOIN job_types jt ON sl.job_type = jt.job_name
    LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
    WHERE sl.scan_date >= DATEADD(day, -7, GETDATE())
    GROUP BY CAST(sl.scan_date AS DATE), jt.job_name, sjt.sub_job_name
    ORDER BY scan_date DESC, jt.job_name, sjt.sub_job_name;
END
GO

-- 3.4 Stored Procedure สำหรับความถี่ของบาร์โค้ด
-- =====================================================
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetBarcodeFrequency')
    DROP PROCEDURE sp_GetBarcodeFrequency;
GO

CREATE PROCEDURE sp_GetBarcodeFrequency
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        sl.barcode,
        COUNT(*) as scan_count,
        MIN(sl.scan_date) as first_scan,
        MAX(sl.scan_date) as last_scan,
        COUNT(DISTINCT sl.job_type) as job_types_used,
        COUNT(DISTINCT jt.id) as job_ids_used,
        COUNT(DISTINCT sl.user_id) as users_scanned
    FROM scan_logs sl
    LEFT JOIN job_types jt ON sl.job_type = jt.job_name
    WHERE sl.scan_date >= DATEADD(day, -30, GETDATE())
    GROUP BY sl.barcode
    HAVING COUNT(*) > 1  -- แสดงเฉพาะบาร์โค้ดที่สแกนมากกว่า 1 ครั้ง
    ORDER BY scan_count DESC;
END
GO

-- 3.5 Stored Procedure สำหรับตรวจสอบความสอดคล้องของความสัมพันธ์
-- =====================================================
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetDependencyCompliance')
    DROP PROCEDURE sp_GetDependencyCompliance;
GO

CREATE PROCEDURE sp_GetDependencyCompliance
    @barcode VARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    -- ตรวจสอบความสอดคล้องของความสัมพันธ์สำหรับบาร์โค้ด
    WITH BarcodeDependencies AS (
        SELECT DISTINCT
            sl.barcode,
            jt.id as job_id,
            jt.job_name,
            jd.required_job_id,
            rjt.job_name as required_job_name
        FROM scan_logs sl
        INNER JOIN job_types jt ON sl.job_type = jt.job_name
        LEFT JOIN job_dependencies jd ON jt.id = jd.job_id
        LEFT JOIN job_types rjt ON jd.required_job_id = rjt.id
        WHERE (@barcode IS NULL OR sl.barcode = @barcode)
    ),
    ComplianceCheck AS (
        SELECT 
            bd.barcode,
            bd.job_name,
            bd.required_job_name,
            CASE 
                WHEN bd.required_job_id IS NULL THEN 'No Dependencies'
                WHEN EXISTS (
                    SELECT 1 FROM scan_logs sl2 
                    INNER JOIN job_types jt2 ON sl2.job_type = jt2.job_name
                    WHERE sl2.barcode = bd.barcode AND jt2.id = bd.required_job_id
                ) THEN 'Compliant'
                ELSE 'Missing Dependency'
            END as compliance_status
        FROM BarcodeDependencies bd
    )
    SELECT 
        barcode,
        job_name,
        required_job_name,
        compliance_status,
        COUNT(*) OVER (PARTITION BY barcode, compliance_status) as status_count
    FROM ComplianceCheck
    ORDER BY barcode, job_name;
END
GO

-- 3.6 Stored Procedure สำหรับจัดการประเภทงานย่อย
-- =====================================================
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetSubJobTypes')
    DROP PROCEDURE sp_GetSubJobTypes;
GO

CREATE PROCEDURE sp_GetSubJobTypes
    @MainJobId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        sjt.id,
        sjt.main_job_id,
        sjt.sub_job_name,
        sjt.description,
        sjt.is_active,
        jt.job_name as main_job_name
    FROM sub_job_types sjt
    INNER JOIN job_types jt ON sjt.main_job_id = jt.id
    WHERE (@MainJobId IS NULL OR sjt.main_job_id = @MainJobId)
        AND sjt.is_active = 1
    ORDER BY jt.job_name, sjt.sub_job_name;
END
GO

-- 3.7 Stored Procedure สำหรับรายงานที่รวมประเภทงานย่อย
-- =====================================================
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetScanLogsWithSubJobs')
    DROP PROCEDURE sp_GetScanLogsWithSubJobs;
GO

CREATE PROCEDURE sp_GetScanLogsWithSubJobs
    @StartDate DATE = NULL,
    @EndDate DATE = NULL,
    @MainJobId INT = NULL,
    @SubJobId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        sl.id,
        sl.barcode,
        sl.scan_date,
        sl.job_type as main_job_name,
        sjt.sub_job_name,
        sl.notes,
        sl.user_id
    FROM scan_logs sl
    LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
    LEFT JOIN job_types jt ON sl.job_id = jt.id
    WHERE (@StartDate IS NULL OR CAST(sl.scan_date AS DATE) >= @StartDate)
        AND (@EndDate IS NULL OR CAST(sl.scan_date AS DATE) <= @EndDate)
        AND (@MainJobId IS NULL OR sl.job_id = @MainJobId)
        AND (@SubJobId IS NULL OR sl.sub_job_id = @SubJobId)
    ORDER BY sl.scan_date DESC;
END
GO

-- =====================================================
-- ส่วนที่ 4: การตั้งค่าสิทธิ์ (Permissions)
-- =====================================================

-- หมายเหตุ: ปรับแต่งตามสภาพแวดล้อมของคุณ
-- GRANT SELECT, INSERT, UPDATE, DELETE ON scan_logs TO [your_user];
-- GRANT SELECT, INSERT, UPDATE, DELETE ON job_types TO [your_user];
-- GRANT SELECT, INSERT, UPDATE, DELETE ON job_dependencies TO [your_user];
-- GRANT SELECT, INSERT, UPDATE, DELETE ON sub_job_types TO [your_user];
-- GRANT EXECUTE ON sp_GetScanHistory TO [your_user];
-- GRANT EXECUTE ON sp_GetJobDependencies TO [your_user];
-- GRANT EXECUTE ON sp_GetDailySummary TO [your_user];
-- GRANT EXECUTE ON sp_GetBarcodeFrequency TO [your_user];
-- GRANT EXECUTE ON sp_GetDependencyCompliance TO [your_user];
-- GRANT EXECUTE ON sp_GetSubJobTypes TO [your_user];
-- GRANT EXECUTE ON sp_GetScanLogsWithSubJobs TO [your_user];

-- =====================================================
-- ส่วนที่ 5: ข้อมูลตัวอย่าง (Sample Data)
-- =====================================================

-- หมายเหตุ: เปิดใช้งานส่วนนี้ถ้าต้องการเพิ่มข้อมูลตัวอย่าง
-- INSERT INTO sub_job_types (main_job_id, sub_job_name, description) VALUES
-- (1, 'รับสินค้าปกติ', 'การรับสินค้าแบบปกติ'),
-- (1, 'รับสินค้าด่วน', 'การรับสินค้าที่ต้องรีบ'),
-- (2, 'จัดส่งภายในประเทศ', 'จัดส่งสินค้าภายในประเทศ'),
-- (2, 'จัดส่งต่างประเทศ', 'จัดส่งสินค้าไปต่างประเทศ');

-- =====================================================
-- สรุปการติดตั้งทั้งหมด
-- =====================================================

PRINT '=====================================================';
PRINT 'WMS Database Setup Completed Successfully!';
PRINT '=====================================================';
PRINT 'Tables created/updated:';
PRINT '- job_types (ประเภทงานหลัก)';
PRINT '- job_dependencies (ความสัมพันธ์ระหว่างงาน)';
PRINT '- scan_logs (บันทึกการสแกน)';
PRINT '- sub_job_types (ประเภทงานย่อย)';
PRINT '';
PRINT 'Stored Procedures created:';
PRINT '- sp_GetScanHistory (ประวัติการสแกน)';
PRINT '- sp_GetJobDependencies (ความสัมพันธ์ระหว่างงาน)';
PRINT '- sp_GetDailySummary (สรุปรายวัน)';
PRINT '- sp_GetBarcodeFrequency (ความถี่บาร์โค้ด)';
PRINT '- sp_GetDependencyCompliance (ตรวจสอบความสอดคล้อง)';
PRINT '- sp_GetSubJobTypes (จัดการประเภทงานย่อย)';
PRINT '- sp_GetScanLogsWithSubJobs (รายงานรวมประเภทงานย่อย)';
PRINT '';
PRINT 'System is ready to use!';
PRINT '=====================================================';
