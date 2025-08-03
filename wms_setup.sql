-- WMS Barcode Scanner Database Setup
-- Execute these scripts in your SQL Server database

-- Create job_types table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='job_types' AND xtype='U')
BEGIN
    CREATE TABLE job_types (
        id INT IDENTITY(1,1) PRIMARY KEY,
        job_name VARCHAR(100) NOT NULL UNIQUE
    );
    
    -- Insert sample job types
    INSERT INTO job_types (job_name) VALUES 
    ('1.Release'),
    ('2.Inprocess'),
    ('3.Outbound'),
    ('4.Loading'),
    ('5.Return'),
    ('6.Repack');
END
ELSE
BEGIN
    -- Add id column if it doesn't exist (for existing tables)
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE TABLE_NAME = 'job_types' AND COLUMN_NAME = 'id')
    BEGIN
        -- Add identity column
        ALTER TABLE job_types ADD id INT IDENTITY(1,1);
        
        -- Make job_name unique if not already
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('job_types') AND name = 'UQ_job_types_job_name')
        BEGIN
            ALTER TABLE job_types ADD CONSTRAINT UQ_job_types_job_name UNIQUE (job_name);
        END
    END
    
    -- Remove priority_order column if it exists (old system)
    IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'job_types' AND COLUMN_NAME = 'priority_order')
    BEGIN
        ALTER TABLE job_types DROP COLUMN priority_order;
    END
END

-- Create job_dependencies table for the new dependency system
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='job_dependencies' AND xtype='U')
BEGIN
    CREATE TABLE job_dependencies (
        id INT IDENTITY(1,1) PRIMARY KEY,
        job_id INT NOT NULL,
        required_job_id INT NOT NULL,
        
        -- Foreign key constraints
        CONSTRAINT FK_job_dependencies_job_id FOREIGN KEY (job_id) REFERENCES job_types(id) ON DELETE CASCADE,
        CONSTRAINT FK_job_dependencies_required_job_id FOREIGN KEY (required_job_id) REFERENCES job_types(id) ON DELETE NO ACTION,
        
        -- Prevent self-dependency and duplicate dependencies
        CONSTRAINT CK_job_dependencies_no_self CHECK (job_id != required_job_id),
        CONSTRAINT UQ_job_dependencies UNIQUE (job_id, required_job_id),
        
        -- Indexes for better performance
        INDEX IX_job_dependencies_job_id (job_id),
        INDEX IX_job_dependencies_required_job_id (required_job_id)
    );
    
    -- Insert sample dependencies (ตรวจนับ ต้องมี รับของ ก่อน, โอนย้าย ต้องมี ตรวจนับ ก่อน)
    INSERT INTO job_dependencies (job_id, required_job_id) 
    SELECT j1.id, j2.id 
    FROM job_types j1, job_types j2 
    WHERE j1.job_name = 'ตรวจนับ' AND j2.job_name = 'รับของ';
    
    INSERT INTO job_dependencies (job_id, required_job_id) 
    SELECT j1.id, j2.id 
    FROM job_types j1, job_types j2 
    WHERE j1.job_name = 'โอนย้าย' AND j2.job_name = 'ตรวจนับ';
END

-- Create scan_logs table  
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
        CONSTRAINT FK_scan_logs_job_id FOREIGN KEY (job_id) REFERENCES job_types(id),
        
        -- Add indexes for better performance
        INDEX IX_scan_logs_barcode (barcode),
        INDEX IX_scan_logs_scan_date (scan_date),
        INDEX IX_scan_logs_job_type (job_type),
        INDEX IX_scan_logs_user_id (user_id),
        INDEX IX_scan_logs_job_id (job_id),
        INDEX IX_scan_logs_barcode_job_id (barcode, job_id)
    );
END
ELSE
BEGIN
    -- Add job_id column if it doesn't exist
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE TABLE_NAME = 'scan_logs' AND COLUMN_NAME = 'job_id')
    BEGIN
        ALTER TABLE scan_logs ADD job_id INT NULL;
        
        -- Add foreign key constraint
        ALTER TABLE scan_logs ADD CONSTRAINT FK_scan_logs_job_id 
        FOREIGN KEY (job_id) REFERENCES job_types(id);
        
        -- Create indexes for job_id
        CREATE INDEX IX_scan_logs_job_id ON scan_logs (job_id);
        CREATE INDEX IX_scan_logs_barcode_job_id ON scan_logs (barcode, job_id);
        
        -- Update existing records to set job_id based on job_type
        UPDATE sl SET job_id = jt.id 
        FROM scan_logs sl 
        INNER JOIN job_types jt ON sl.job_type = jt.job_name
        WHERE sl.job_id IS NULL;
    END
    
    -- Remove priority_order column if it exists (old system)
    IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'scan_logs' AND COLUMN_NAME = 'priority_order')
    BEGIN
        DROP INDEX IF EXISTS IX_scan_logs_priority_order ON scan_logs;
        ALTER TABLE scan_logs DROP COLUMN priority_order;
    END
END

-- Sample stored procedure for history report
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

-- Sample stored procedure for dependency validation report
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

-- Sample stored procedure for daily summary report
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetDailySummary')
    DROP PROCEDURE sp_GetDailySummary;
GO

CREATE PROCEDURE sp_GetDailySummary
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        CAST(sl.scan_date AS DATE) as scan_date,
        sl.job_type,
        jt.id as job_id,
        sl.user_id,
        COUNT(*) as scan_count,
        COUNT(DISTINCT sl.barcode) as unique_barcodes
    FROM scan_logs sl
    LEFT JOIN job_types jt ON sl.job_type = jt.job_name
    WHERE sl.scan_date >= DATEADD(day, -7, GETDATE())
    GROUP BY CAST(sl.scan_date AS DATE), sl.job_type, jt.id, sl.user_id
    ORDER BY scan_date DESC, sl.job_type, sl.user_id;
END
GO

-- Sample stored procedure for barcode frequency report
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
    HAVING COUNT(*) > 1  -- Only show barcodes scanned more than once
    ORDER BY scan_count DESC;
END
GO

-- Sample stored procedure for dependency compliance report
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GetDependencyCompliance')
    DROP PROCEDURE sp_GetDependencyCompliance;
GO

CREATE PROCEDURE sp_GetDependencyCompliance
    @barcode VARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check dependency compliance for barcodes
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

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON scan_logs TO [your_user];
-- GRANT SELECT, INSERT, UPDATE, DELETE ON job_types TO [your_user];
-- GRANT SELECT, INSERT, UPDATE, DELETE ON job_dependencies TO [your_user];
-- GRANT EXECUTE ON sp_GetScanHistory TO [your_user];
-- GRANT EXECUTE ON sp_GetJobDependencies TO [your_user];
-- GRANT EXECUTE ON sp_GetDailySummary TO [your_user];
-- GRANT EXECUTE ON sp_GetBarcodeFrequency TO [your_user];
-- GRANT EXECUTE ON sp_GetDependencyCompliance TO [your_user];

-- Migration Script for Sub Job Types System
-- สร้างตารางประเภทงานย่อยและปรับปรุงตาราง scan_logs

USE WMS_EP;
GO

-- 1. สร้างตาราง sub_job_types
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
    
    PRINT 'Table sub_job_types created successfully.';
END
ELSE
BEGIN
    PRINT 'Table sub_job_types already exists.';
END

-- 2. เพิ่มคอลัมน์ใน scan_logs สำหรับประเภทงานย่อยและหมายเหตุ
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

-- 3. เพิ่ม Foreign Key สำหรับ sub_job_id
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

-- 4. สร้าง Index สำหรับการค้นหาที่เร็วขึ้น
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_sub_job_types_main_job_id')
BEGIN
    CREATE INDEX IX_sub_job_types_main_job_id ON sub_job_types(main_job_id);
    PRINT 'Index IX_sub_job_types_main_job_id created.';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_scan_logs_sub_job_id')
BEGIN
    CREATE INDEX IX_scan_logs_sub_job_id ON scan_logs(sub_job_id);
    PRINT 'Index IX_scan_logs_sub_job_id created.';
END

-- 5. เพิ่มข้อมูลตัวอย่าง (ถ้าต้องการ)
-- INSERT INTO sub_job_types (main_job_id, sub_job_name, description) VALUES
-- (1, 'รับสินค้าปกติ', 'การรับสินค้าแบบปกติ'),
-- (1, 'รับสินค้าด่วน', 'การรับสินค้าที่ต้องรีบ'),
-- (2, 'จัดส่งภายในประเทศ', 'จัดส่งสินค้าภายในประเทศ'),
-- (2, 'จัดส่งต่างประเทศ', 'จัดส่งสินค้าไปต่างประเทศ');

-- 6. สร้าง Stored Procedure สำหรับการจัดการประเภทงานย่อย
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

-- 7. สร้าง Stored Procedure สำหรับการรายงานที่รวมประเภทงานย่อย
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

PRINT 'Migration completed successfully!';
PRINT 'Sub job types system is ready to use.';
