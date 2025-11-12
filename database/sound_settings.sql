-- =====================================================
-- Sound Settings Table Creation Script
-- =====================================================
-- คำอธิบาย: สคริปต์นี้ใช้สำหรับสร้างตารางการตั้งค่าเสียง
-- วันที่สร้าง: 2025-11-11
-- เวอร์ชัน: 1.0
-- =====================================================

-- =====================================================
-- สร้างตาราง sound_settings (การตั้งค่าเสียง)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sound_settings')
BEGIN
    CREATE TABLE sound_settings (
        id INT IDENTITY(1,1) PRIMARY KEY,
        job_id INT NULL,                        -- NULL = default sound สำหรับทุก job
        sub_job_id INT NULL,                    -- NULL = ใช้เสียงของ main job
        event_type VARCHAR(50) NOT NULL,        -- 'success', 'error', 'duplicate', 'warning'
        sound_file NVARCHAR(255) NOT NULL,      -- ชื่อไฟล์เสียง หรือ path
        is_enabled BIT DEFAULT 1,               -- เปิด/ปิดการใช้งาน
        volume DECIMAL(3,2) DEFAULT 1.00,       -- ระดับเสียง 0.00 - 1.00
        created_date DATETIME2 DEFAULT GETDATE(),
        modified_date DATETIME2 DEFAULT GETDATE(),

        -- Foreign Keys
        CONSTRAINT FK_sound_job_id
            FOREIGN KEY (job_id) REFERENCES job_types(id)
            ON DELETE CASCADE,
        CONSTRAINT FK_sound_sub_job_id
            FOREIGN KEY (sub_job_id) REFERENCES sub_job_types(id)
            ON DELETE NO ACTION,

        -- Constraints
        CONSTRAINT CK_volume_range CHECK (volume >= 0.00 AND volume <= 1.00),
        CONSTRAINT CK_event_type CHECK (event_type IN ('success', 'error', 'duplicate', 'warning')),

        -- ป้องกันการตั้งค่าซ้ำสำหรับ job/sub-job/event เดียวกัน
        CONSTRAINT UQ_sound_settings_per_event
            UNIQUE (job_id, sub_job_id, event_type)
    );

    -- สร้าง Indexes สำหรับการค้นหาเร็ว
    CREATE INDEX IX_sound_settings_job_event
        ON sound_settings(job_id, event_type);
    CREATE INDEX IX_sound_settings_sub_job_event
        ON sound_settings(sub_job_id, event_type);
    CREATE INDEX IX_sound_settings_enabled
        ON sound_settings(is_enabled)
        WHERE is_enabled = 1;

    -- เพิ่มข้อมูลเริ่มต้น (Default sounds)
    INSERT INTO sound_settings (job_id, sub_job_id, event_type, sound_file, is_enabled, volume)
    VALUES
        (NULL, NULL, 'success', '/static/sounds/success.mp3', 1, 0.80),
        (NULL, NULL, 'error', '/static/error_2.mp3', 1, 0.80),
        (NULL, NULL, 'duplicate', '/static/sounds/duplicate.mp3', 1, 0.80),
        (NULL, NULL, 'warning', '/static/sounds/warning.mp3', 1, 0.80);

    PRINT 'Table sound_settings created successfully with default data.';
    PRINT 'Indexes created for better performance.';
END
ELSE
BEGIN
    PRINT 'Table sound_settings already exists.';
END
GO

-- =====================================================
-- สรุปการติดตั้ง
-- =====================================================

PRINT '=====================================================';
PRINT 'Sound Settings Table Setup Completed!';
PRINT '=====================================================';
PRINT 'Features:';
PRINT '- Default sounds for all events (success, error, duplicate, warning)';
PRINT '- Job-specific sounds override';
PRINT '- Sub-job-specific sounds override';
PRINT '- Volume control (0.00-1.00)';
PRINT '- Enable/Disable toggle';
PRINT '';
PRINT 'System is ready for sound configuration!';
PRINT '=====================================================';
GO
