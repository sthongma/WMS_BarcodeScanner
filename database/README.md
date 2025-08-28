# Database Scripts

## Files

### Core Scripts
- **`wms_setup_db_clean.sql`** - สคริปต์หลักสำหรับสร้างฐานข้อมูล (เฉพาะที่จำเป็น)
- **`wms_user_setup.sql`** - สร้าง user และกำหนดสิทธิ์

### Legacy
- **`wms_setup_db.sql`** - สคริปต์เก่าที่มีส่วนที่ไม่ใช้ (สำหรับอ้างอิง)

## Tables Used by Application

### job_types
- `id` - Primary key
- `job_name` - ชื่อประเภทงาน

### sub_job_types  
- `id` - Primary key
- `main_job_id` - Foreign key to job_types
- `sub_job_name` - ชื่อประเภทงานย่อย
- `is_active` - สถานะใช้งาน

### scan_logs
- `id` - Primary key
- `barcode` - รหัสบาร์โค้ด
- `scan_date` - วันที่สแกน
- `job_type` - ประเภทงาน (string)
- `user_id` - ผู้ใช้
- `job_id` - Foreign key to job_types
- `sub_job_id` - Foreign key to sub_job_types
- `notes` - หมายเหตุ

## Usage

1. รัน `wms_setup_db_clean.sql` เพื่อสร้างตารางหลัก
2. รัน `wms_user_setup.sql` เพื่อสร้าง user และกำหนดสิทธิ์