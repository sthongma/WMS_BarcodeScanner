-- WMS Barcode Scanner - SQL Server User Creation Script
-- สคริปสำหรับสร้างผู้ใช้ SQL Server สำหรับระบบ WMS Barcode Scanner
-- วันที่: 2025-08-31

USE master;
GO

-- =============================================================================
-- สร้าง SQL Server Logins
-- =============================================================================

-- 1. สร้าง Login สำหรับ Admin (ตัวพิมพ์ใหญ่เพื่อให้เข้ากับ SQL Server)
IF NOT EXISTS (SELECT name FROM sys.sql_logins WHERE name = 'WMS_ADMIN')
BEGIN
    CREATE LOGIN [WMS_ADMIN] WITH PASSWORD = 'Admin@123!WMS';
    PRINT 'Created login: WMS_ADMIN';
END
ELSE
    PRINT 'Login WMS_ADMIN already exists';

-- 2. สร้าง Login สำหรับ User (ตัวพิมพ์ใหญ่เพื่อให้เข้ากับ SQL Server)
IF NOT EXISTS (SELECT name FROM sys.sql_logins WHERE name = 'WMS_USER')
BEGIN
    CREATE LOGIN [WMS_USER] WITH PASSWORD = 'User@456!WMS';
    PRINT 'Created login: WMS_USER';
END
ELSE
    PRINT 'Login WMS_USER already exists';

-- =============================================================================
-- สร้าง Database Users และกำหนดสิทธิ์
-- =============================================================================

USE WMS_EP;
GO

-- 1. สร้าง User สำหรับ Admin
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'WMS_ADMIN')
BEGIN
    CREATE USER [WMS_ADMIN] FOR LOGIN [WMS_ADMIN];
    PRINT 'Created database user: WMS_ADMIN';
END
ELSE
    PRINT 'Database user WMS_ADMIN already exists';

-- 2. สร้าง User สำหรับ User
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'WMS_USER')
BEGIN
    CREATE USER [WMS_USER] FOR LOGIN [WMS_USER];
    PRINT 'Created database user: WMS_USER';
END
ELSE
    PRINT 'Database user WMS_USER already exists';

-- =============================================================================
-- กำหนดสิทธิ์สำหรับ Admin (Full Access)
-- =============================================================================

-- เพิ่ม Admin เป็น db_owner (สิทธิ์เต็ม)
IF IS_ROLEMEMBER('db_owner', 'WMS_ADMIN') = 0
BEGIN
    ALTER ROLE db_owner ADD MEMBER [WMS_ADMIN];
    PRINT 'Added WMS_ADMIN to db_owner role';
END
ELSE
    PRINT 'WMS_ADMIN is already a member of db_owner role';

-- =============================================================================
-- กำหนดสิทธิ์สำหรับ User (Limited Access)
-- =============================================================================

-- เพิ่ม User เป็น db_datareader และ db_datawriter
IF IS_ROLEMEMBER('db_datareader', 'wms_user') = 0
BEGIN
    ALTER ROLE db_datareader ADD MEMBER wms_user;
    PRINT 'Added wms_user to db_datareader role';
END
ELSE
    PRINT 'wms_user is already a member of db_datareader role';

IF IS_ROLEMEMBER('db_datawriter', 'wms_user') = 0
BEGIN
    ALTER ROLE db_datawriter ADD MEMBER wms_user;
    PRINT 'Added wms_user to db_datawriter role';
END
ELSE
    PRINT 'wms_user is already a member of db_datawriter role';

-- กำหนดสิทธิ์เพิ่มเติมสำหรับ User (EXECUTE stored procedures)
GRANT EXECUTE ON SCHEMA::dbo TO wms_user;
PRINT 'Granted EXECUTE permission on dbo schema to wms_user';

-- =============================================================================
-- แสดงข้อมูลผู้ใช้ที่สร้างเสร็จแล้ว
-- =============================================================================

PRINT '';
PRINT '=== WMS Barcode Scanner Users Created Successfully ===';
PRINT '';
PRINT 'Admin User:';
PRINT '  Username: wms_admin';
PRINT '  Password: Admin@123!WMS';
PRINT '  Permissions: Full access (db_owner)';
PRINT '';
PRINT 'Standard User:';
PRINT '  Username: wms_user';
PRINT '  Password: User@456!WMS';
PRINT '  Permissions: Read/Write data + Execute procedures';
PRINT '';
PRINT '=== Security Recommendations ===';
PRINT '1. เปลี่ยนรหัสผ่านหลังจากการติดตั้งครั้งแรก';
PRINT '2. สร้างผู้ใช้เพิ่มเติมตามความต้องการ';
PRINT '3. ทบทวนสิทธิ์การเข้าถึงเป็นประจำ';
PRINT '4. เก็บข้อมูลผู้ใช้ไว้ในที่ปลอดภัย';
PRINT '';

-- =============================================================================
-- ตรวจสอบผู้ใช้ที่สร้างแล้ว
-- =============================================================================

PRINT '=== Current Database Users ===';
SELECT 
    dp.name AS principal_name,
    dp.type_desc AS principal_type,
    r.name AS role_name
FROM sys.database_principals dp
LEFT JOIN sys.database_role_members rm ON dp.principal_id = rm.member_principal_id
LEFT JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
WHERE dp.name IN ('wms_admin', 'wms_user')
ORDER BY dp.name, r.name;

GO