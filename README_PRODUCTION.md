# WMS Barcode Scanner - Production Deployment Guide

## การปรับปรุงสำหรับใช้งานพร้อมกัน

### ✅ การปรับปรุงที่ทำแล้ว

1. **Thread-Safe Database Management**
   - ใช้ `threading.local()` สำหรับ database connection แต่ละ thread
   - แต่ละผู้ใช้จะมี database connection ของตัวเอง

2. **Rate Limiting**
   - `/api/login`: จำกัด 5 ครั้งต่อ 5 นาที
   - `/api/scan`: จำกัด 120 ครั้งต่อนาที (2 scans/วินาที)
   - `/api/init`: จำกัด 10 ครั้งต่อนาที
   - API อื่นๆ: จำกัด 30 ครั้งต่อนาที

3. **Session Management**
   - Session timeout: 8 ชั่วโมง
   - Secure cookie settings
   - Auto-cleanup expired sessions

4. **Improved Logging**
   - RotatingFileHandler (max 10MB per file)
   - แยกระดับ log: INFO, WARNING, ERROR
   - Log ทั้งไฟล์และ console

5. **Production Configuration**
   - แยกไฟล์ config สำหรับ production/development
   - Environment-based settings
   - Security improvements

## 🚀 การใช้งาน Production

### วิธีการ 1: ใช้ Batch File (แนะนำ)
```bash
# Double-click หรือรันคำสั่ง
start_production.bat
```

### วิธีการ 2: ใช้ Python Script
```bash
python run_production.py
```

### วิธีการ 3: ใช้ Environment Variable
```bash
set FLASK_ENV=production
python web_app.py
```

## ⚙️ การตั้งค่า

### 1. Production Config (`config/production.json`)
- Database connection pooling
- Rate limiting settings
- Security configurations
- Logging settings

### 2. Development Config (`config/development.json`)
- สำหรับการทดสอบ
- Rate limit ที่หลวมกว่า
- Detailed logging

## 📊 ประสิทธิภาพ

### รองรับผู้ใช้งาน
- **Concurrent Users**: 10-15 คน
- **Peak Performance**: 120 scans/minute
- **Thread-Safe**: ✅ ปลอดภัยสำหรับ multi-user

### Database Performance
- Connection pooling
- Per-thread connections
- Optimized queries
- Proper indexing

## 🔒 Security Features

1. **Rate Limiting**: ป้องกัน abuse และ DDoS
2. **Session Security**: Secure cookies, timeout
3. **Input Validation**: ตรวจสอบข้อมูลนำเข้า
4. **Error Handling**: ไม่เปิดเผยข้อมูลระบบ
5. **Logging**: บันทึกการเข้าถึงและข้อผิดพลาด

## 📝 Monitoring

### Log Files
- `logs/web_app.log`: Production logs
- `logs/web_app_dev.log`: Development logs

### การตรวจสอบ
```bash
# ดู log แบบ real-time
tail -f logs/web_app.log

# ตรวจสอบ error
grep "ERROR" logs/web_app.log

# ตรวจสอบ rate limiting
grep "Rate limit" logs/web_app.log
```

## 🛠️ Troubleshooting

### ปัญหาที่อาจพบ

1. **Database Connection Issues**
   - ตรวจสอบ `config/sql_config.json`
   - ตรวจสอบ network connectivity
   - ดู logs สำหรับ connection errors

2. **Rate Limiting**
   - ลด frequency ของ requests
   - ตรวจสอบ IP address ที่ถูก limit

3. **Session Timeout**
   - Login ใหม่หลังจาก 8 ชั่วโมง
   - ตรวจสอบ browser cookies

4. **High Memory Usage**
   - Restart application ทุก 24 ชั่วโมง
   - ตรวจสอบ database connections

## 🔧 Advanced Configuration

### สำหรับ Production Server จริง

1. **ใช้ WSGI Server**
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

2. **Reverse Proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **SSL/HTTPS**
```python
# ใน production.json
"security": {
    "https_only": true,
    "cookie_secure": true
}
```

## 📈 Performance Tuning

### Database
- เพิ่ม connection pool size
- ใช้ database clustering
- Optimize queries และ indexes

### Application
- เพิ่มจำนวน worker processes
- ใช้ Redis สำหรับ session storage
- Implement caching

### Infrastructure
- Load balancer
- Database replication
- CDN สำหรับ static files

## 🎯 Recommendations

1. **สำหรับ 10-15 users**: Configuration ปัจจุบันเพียงพอ
2. **สำหรับ 20+ users**: ใช้ Gunicorn + Nginx
3. **สำหรับ 50+ users**: ใช้ load balancing + database clustering

## 📞 Support

หากพบปัญหาหรือต้องการปรับปรุงเพิ่มเติม:

1. ตรวจสอบ logs ก่อน
2. ดู configuration files
3. Test ใน development mode ก่อน
4. Backup database ก่อนทำการเปลี่ยนแปลง