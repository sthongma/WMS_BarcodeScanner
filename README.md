# WMS Barcode Scanner Application

ระบบสแกนบาร์โค้ดสำหรับระบบจัดการคลังสินค้า (Warehouse Management System)

## 🚀 ฟีเจอร์หลัก

- 📱 **Desktop Application** - แอปพลิเคชันสำหรับคอมพิวเตอร์
- 🌐 **Web Application** - แอปพลิเคชันสำหรับ Android ผ่านเว็บเบราว์เซอร์
- 📷 **การสแกนบาร์โค้ด**: สแกนและบันทึกข้อมูลบาร์โค้ด
- 📊 **การจัดการ Job Types**: จัดการประเภทงานหลักและงานย่อย
- 📋 **การนำเข้าข้อมูล**: นำเข้าข้อมูลจากไฟล์ Excel/CSV
- 📈 **รายงาน**: สร้างรายงานการสแกนและสถิติ
- ⚙️ **การตั้งค่าฐานข้อมูล**: จัดการการเชื่อมต่อฐานข้อมูล SQL Server

## 📱 การใช้งานบน Android

### วิธีที่ง่ายที่สุด:

1. **รัน Web Server:**
   ```bash
   # Windows
   start_android_server.bat
   
   # Linux/Mac
   ./start_android_server.sh
   ```

2. **สร้าง QR Code (ไม่บังคับ):**
   ```bash
   # Windows
   generate_qr.bat
   
   # Linux/Mac
   python generate_qr.py
   ```

3. **เข้าถึงจาก Android:**
   - เปิดเว็บเบราว์เซอร์บน Android
   - ไปที่ URL ที่แสดงในหน้าต่าง Terminal
   - หรือสแกน QR Code ที่สร้างขึ้น

### ฟีเจอร์สำหรับ Android:

- ✅ **Responsive Design** - ใช้งานได้ดีบนมือถือ
- ✅ **Camera Access** - ใช้กล้องมือถือสแกนบาร์โค้ด
- ✅ **Touch-friendly UI** - UI ที่เหมาะสำหรับการสัมผัส
- ✅ **Offline Support** - ทำงานได้ในเครือข่ายท้องถิ่น

## โครงสร้างโปรแกรม

```
WMS_BarcodeScanner/
├── src/                          # โค้ดหลักของโปรแกรม
│   ├── main.py                   # จุดเริ่มต้นของโปรแกรม
│   ├── database/                 # โมดูลจัดการฐานข้อมูล
│   │   ├── database_manager.py   # จัดการการเชื่อมต่อและ query
│   │   └── connection_config.py  # การตั้งค่าการเชื่อมต่อ
│   ├── ui/                       # ส่วนติดต่อผู้ใช้
│   │   ├── login_window.py       # หน้าต่างเข้าสู่ระบบ
│   │   ├── main_window.py        # หน้าต่างหลัก
│   │   └── components/           # องค์ประกอบ UI ย่อย
│   ├── utils/                    # ฟังก์ชันช่วยเหลือ
│   │   ├── file_utils.py         # จัดการไฟล์
│   │   └── validation_utils.py   # ตรวจสอบความถูกต้อง
│   └── models/                   # โมเดลข้อมูล
│       └── data_models.py        # โครงสร้างข้อมูล
├── config/                       # ไฟล์การตั้งค่า
│   └── sql_config.json          # การตั้งค่าฐานข้อมูล
├── requirements.txt              # Dependencies
├── README.md                     # เอกสารนี้
└── run.py                       # จุดเริ่มต้นโปรแกรม
```

## การติดตั้ง

1. **ติดตั้ง Python 3.8+**
2. **ติดตั้ง Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **ติดตั้ง ODBC Driver for SQL Server**
4. **ตั้งค่าฐานข้อมูล**:
   - แก้ไขไฟล์ `config/sql_config.json`
   - ระบุ Server, Database, และข้อมูลการเข้าสู่ระบบ

## การใช้งาน

### 🖥️ Desktop Application
```bash
python run.py
```

### 📱 Web Application (สำหรับ Android)
```bash
python web_app.py
```

### การสแกนบาร์โค้ด
1. เลือกแท็บ "สแกนบาร์โค้ด"
2. เลือกประเภทงาน
3. สแกนบาร์โค้ด
4. ระบบจะบันทึกข้อมูลอัตโนมัติ

### การนำเข้าข้อมูล
1. เลือกแท็บ "นำเข้าข้อมูล"
2. ดาวน์โหลด template
3. กรอกข้อมูลในไฟล์ Excel
4. อัปโหลดไฟล์และตรวจสอบ
5. นำเข้าข้อมูล

### การสร้างรายงาน
1. เลือกแท็บ "รายงาน"
2. เลือก stored procedure
3. กำหนดพารามิเตอร์
4. สร้างรายงานและส่งออก

## การตั้งค่าฐานข้อมูล

### Windows Authentication
```json
{
    "server": "localhost\\SQLEXPRESS",
    "database": "WMS_EP",
    "auth_type": "Windows",
    "username": "",
    "password": ""
}
```

### SQL Authentication
```json
{
    "server": "localhost\\SQLEXPRESS",
    "database": "WMS_EP",
    "auth_type": "SQL",
    "username": "your_username",
    "password": "your_password"
}
```

## การพัฒนา

### โครงสร้างโค้ด
- **Database Layer**: จัดการการเชื่อมต่อและ query
- **UI Layer**: ส่วนติดต่อผู้ใช้
- **Business Logic**: ตรรกะทางธุรกิจ
- **Data Models**: โครงสร้างข้อมูล

### การเพิ่มฟีเจอร์ใหม่
1. สร้างโมดูลใหม่ใน `src/`
2. เพิ่ม UI components ใน `src/ui/components/`
3. อัปเดต `__init__.py` files
4. ทดสอบและตรวจสอบ

## การแก้ไขปัญหา

### ปัญหาการเชื่อมต่อฐานข้อมูล
- ตรวจสอบ ODBC Driver
- ตรวจสอบการตั้งค่า Server
- ตรวจสอบสิทธิ์การเข้าถึง

### ปัญหาการนำเข้าข้อมูล
- ตรวจสอบรูปแบบไฟล์
- ตรวจสอบคอลัมน์ที่จำเป็น
- ตรวจสอบข้อมูลในไฟล์

## 📖 เอกสารเพิ่มเติม

- [คู่มือการใช้งานบน Android](README_ANDROID.md)
- [การตั้งค่าฐานข้อมูล](docs/database_setup.md)
- [การแก้ไขปัญหา](docs/troubleshooting.md)

## 🤝 การสนับสนุน

สำหรับคำถามหรือปัญหาการใช้งาน กรุณาติดต่อทีมพัฒนา

## ใบอนุญาต

โปรแกรมนี้เป็นส่วนหนึ่งของระบบ WMS และสงวนลิขสิทธิ์

---

**🎉 ตอนนี้คุณสามารถใช้ WMS Barcode Scanner ได้ทั้งบน Desktop และ Android แล้ว!** 