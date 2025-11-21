# WMS Barcode Scanner

ระบบสแกนบาร์โค้ดสำหรับ Warehouse Management System (WMS) รองรับทั้งการใช้งานแบบ Desktop และ Web Application

## 🚀 เริ่มต้นใช้งาน

### วิธีการรัน

```bash
# รันแบบ Desktop (GUI)
python run.py desktop

# รันแบบ Web Server (สำหรับ Android/Mobile)
python run.py web

# ดูตัวเลือกทั้งหมด
python run.py --help
```

### วิธีการรันแบบเก่า (ยังใช้ได้)

```bash
# Desktop Application
python run_desktop.py

# Web Application  
python run_web.py
```

## 📱 โหมดการใช้งาน

### Desktop Mode
- **Interface:** Tkinter GUI
- **เหมาะสำหรับ:** การจัดการข้อมูลครบครัน
- **คุณสมบัติ:** 
  - การจัดการประเภทงาน
  - รายงานและสถิติ
  - การนำเข้าข้อมูล
  - การตั้งค่าระบบ

### Web Mode
- **Interface:** Web Browser
- **เหมาะสำหรับ:** การใช้งานบนมือถือ Android
- **URL:**
  - Local: http://localhost:5003
  - Mobile: http://[YOUR_IP]:5003
- **คุณสมบัติ:**
  - สแกนบาร์โค้ด
  - ดูประวัติ
  - รายงานพื้นฐาน

### 🌐 Cloudflare Tunnel (สำหรับเข้าถึงจากภายนอก)
เปิดให้คนอื่นเข้าถึง Web App จากภายนอกโดยไม่ต้องเปิด port หรือตั้งค่า router

**วิธีรัน:**
```bash
# รัน WMS + Cloudflare Tunnel พร้อมกัน
run_wms_with_tunnel.bat

# รัน Tunnel เพียงอย่างเดียว (ถ้า WMS รันอยู่แล้ว)
run_tunnel.bat
```

**ดูคู่มือฉบับเต็ม:** [CLOUDFLARE_TUNNEL_SETUP.md](CLOUDFLARE_TUNNEL_SETUP.md)

## 📂 โครงสร้างโปรเจค

```
WMS_BarcodeScanner/
├── run.py              # Main launcher
├── run_desktop.py      # Desktop entry point
├── run_web.py         # Web entry point
├── src/               # Core application code
│   ├── database/      # Database management
│   ├── services/      # Business logic
│   ├── ui/            # Desktop UI components
│   └── utils/         # Utility functions
├── routes/            # Web API routes
├── web/               # Web services
├── config/            # Configuration files
├── templates/         # Web templates
├── static/           # Web static files
└── archive/          # Old backup files
```

## 🔧 การตั้งค่า

### ฐานข้อมูล
1. รันสคริปต์สร้างฐานข้อมูล: `database/wms_setup_db_clean.sql`
2. แก้ไขการเชื่อมต่อใน: `config/sql_config.json`

### การกำหนดค่า
- **Development:** `config/development.json`
- **Production:** `config/production.json`

## 🔍 การแก้ไขปัญหา

### Desktop App ไม่รัน
```bash
# ตรวจสอบ Python path
python run.py desktop
```

### Web App ไม่รัน
```bash  
# ตรวจสอบ port และการเชื่อมต่อฐานข้อมูล
python run.py web
```

### การเชื่อมต่อฐานข้อมูล
- ตรวจสอบ SQL Server ทำงาน
- ตรวจสอบการตั้งค่าใน `config/sql_config.json`
- รันสคริปต์ `database/wms_setup_db_clean.sql`

## 📚 เอกสารเพิ่มเติม

- [Android Setup](docs/README_ANDROID.md)
- [Production Deployment](docs/README_PRODUCTION.md)
- [History Management](docs/HISTORY_FIX_README.md)
- [Reports](docs/README_REPORT.md)

## 🏗️ สถาปัตยกรรม

- **Frontend:** Tkinter (Desktop), HTML/CSS/JS (Web)
- **Backend:** Python Flask (Web API)
- **Database:** Microsoft SQL Server
- **ORM:** Raw SQL with pyodbc

---
*เวอร์ชัน 0.3.5 - โครงสร้างใหม่ ใช้งานง่ายขึ้น*