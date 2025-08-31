# WMS Barcode Scanner - User Management

## 📋 คำแนะนำการสร้างผู้ใช้

### 🎯 วิธีการรัน SQL Script

1. **เปิด SQL Server Management Studio (SSMS)**
2. **เชื่อมต่อไปยัง SQL Server Instance**
3. **เปิดไฟล์ `create_users.sql`**
4. **รันสคริป (F5 หรือ Execute)**

### 👥 ผู้ใช้ที่จะถูกสร้าง

#### 🔑 Admin User
```
Username: WMS_ADMIN
Password: Admin@123!WMS
Permissions: db_owner (เข้าถึงได้ทุกอย่าง)
```

#### 👤 Standard User  
```
Username: WMS_USER
Password: User@456!WMS
Permissions: db_datareader + db_datawriter + EXECUTE
```

### 🛡️ ความปลอดภัย

#### ⚠️ สิ่งที่ควรทำหลังการติดตั้ง:

1. **เปลี่ยนรหัสผ่าน** - ใช้คำสั่ง SQL:
```sql
ALTER LOGIN [WMS_ADMIN] WITH PASSWORD = 'YourNewStrongPassword';
ALTER LOGIN [WMS_USER] WITH PASSWORD = 'YourNewStrongPassword';
```

2. **อัปเดต Config Files**:
   - `config/sql_config.json`
   - เปลี่ยน username/password ให้ตรงกับที่ตั้งใหม่

3. **สำรองข้อมูลผู้ใช้** - เก็บข้อมูลไว้ในที่ปลอดภัย

### 🔍 การตรวจสอบผู้ใช้

```sql
-- ดูผู้ใช้ทั้งหมดในฐานข้อมูล
SELECT name, type_desc FROM sys.database_principals 
WHERE name IN ('WMS_ADMIN', 'WMS_USER');

-- ดูสิทธิ์ของผู้ใช้
SELECT 
    dp.name AS user_name,
    r.name AS role_name
FROM sys.database_principals dp
JOIN sys.database_role_members rm ON dp.principal_id = rm.member_principal_id
JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
WHERE dp.name IN ('WMS_ADMIN', 'WMS_USER');
```

### 🚀 การทดสอบ Login

#### สำหรับ Web App:
1. ไปที่ http://localhost:5003/login
2. ลองใช้: `WMS_ADMIN` / `Admin@123!WMS` หรือ `WMS_USER` / `User@456!WMS`

#### สำหรับ Desktop App:
1. รัน `python run_desktop.py`
2. กรอกข้อมูลใน Login Window

### 📝 การสร้างผู้ใช้เพิ่มเติม

```sql
-- Template สำหรับสร้างผู้ใช้ใหม่
CREATE LOGIN your_username WITH PASSWORD = 'YourPassword';
USE WMS_EP;
CREATE USER your_username FOR LOGIN your_username;
ALTER ROLE db_datareader ADD MEMBER your_username;
ALTER ROLE db_datawriter ADD MEMBER your_username;
GRANT EXECUTE ON SCHEMA::dbo TO your_username;
```

### ❌ การลบผู้ใช้

```sql
USE WMS_EP;
DROP USER wms_user;
USE master;
DROP LOGIN wms_user;
```

---

**⚠️ หมายเหตุ**: รหัสผ่านที่ให้มาเป็นเพียงตัวอย่าง กรุณาเปลี่ยนรหัสผ่านในการใช้งานจริง!