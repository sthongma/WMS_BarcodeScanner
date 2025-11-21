# การเข้าถึง Web App จากเครือข่ายภายนอก

## ภาพรวม
Web application WMS Barcode Scanner ถูกตั้งค่าให้รับการเชื่อมต่อจากเครือข่ายภายนอกได้โดยค่าเริ่มต้น

## การตั้งค่าปัจจุบัน

### Network Configuration
- **Host**: `0.0.0.0` (รับการเชื่อมต่อจากทุก network interface)
- **Port**: `5000` (configurable via `FLASK_PORT`)
- **CORS**: อนุญาตทุก origins โดยค่าเริ่มต้น

### Environment Variables
```bash
FLASK_HOST=0.0.0.0        # Host to bind to
FLASK_PORT=5000           # Port to listen on
CORS_ORIGINS=*            # CORS allowed origins
FLASK_ENV=development     # Environment mode
FLASK_DEBUG=0             # Debug mode
```

## วิธีเข้าถึงจากเครือข่ายภายนอก

### 1. หา IP Address ของเครื่อง Server

#### Linux/Mac:
```bash
# หา IP ของ network interface
ip addr show

# หรือ
ifconfig

# หรือ
hostname -I
```

#### Windows:
```cmd
ipconfig
```

### 2. URL สำหรับเข้าถึง

#### จาก Local Network (LAN):
```
http://<IP-ADDRESS>:5000
```

ตัวอย่าง:
```
http://192.168.1.100:5000
http://10.0.0.50:5000
```

#### จาก Internet (WAN):
```
http://<PUBLIC-IP>:5000
```

**หมายเหตุ**: ต้องทำ Port Forwarding ที่ Router ก่อน

### 3. ตรวจสอบว่า Server กำลังฟัง

```bash
# ตรวจสอบว่า port 5000 เปิดอยู่
sudo netstat -tulpn | grep :5000

# หรือ
sudo ss -tulpn | grep :5000

# หรือ
sudo lsof -i :5000
```

ผลลัพธ์ที่ต้องการ:
```
tcp  0  0  0.0.0.0:5000  0.0.0.0:*  LISTEN  12345/python
```

## การแก้ปัญหา

### ปัญหา 1: ไม่สามารถเข้าถึงจาก External Network

#### สาเหตุและวิธีแก้:

#### A. Firewall บล็อก Port 5000

**Linux (UFW):**
```bash
# เปิด port 5000
sudo ufw allow 5000/tcp

# ตรวจสอบ status
sudo ufw status
```

**Linux (iptables):**
```bash
# เพิ่ม rule
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT

# บันทึก rules
sudo iptables-save
```

**Windows:**
```powershell
# เปิด PowerShell as Administrator
New-NetFirewallRule -DisplayName "WMS Web App" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

#### B. Docker Networking Issues

ตรวจสอบว่า Docker expose port ถูกต้อง:

```bash
# ดู ports ที่ container ใช้
docker ps

# ควรเห็น: 0.0.0.0:5000->5000/tcp
```

ถ้าไม่เห็น ให้แก้ไข `docker-compose.yml`:
```yaml
services:
  web:
    ports:
      - "0.0.0.0:5000:5000"  # Explicitly bind to all interfaces
```

#### C. Router/Network Configuration

สำหรับการเข้าถึงจาก Internet:

1. **Port Forwarding** ที่ Router:
   - External Port: 5000 (หรือ port อื่นตามต้องการ)
   - Internal Port: 5000
   - Internal IP: IP ของเครื่อง Server

2. **Dynamic DNS** (ถ้า Public IP เปลี่ยนบ่อย):
   - ใช้บริการ No-IP, DuckDNS, หรือ DynDNS

### ปัญหา 2: CORS Errors

ถ้าได้ CORS errors ในการเรียก API:

#### แก้ไขใน `.env`:
```bash
# อนุญาตทุก origins (development)
CORS_ORIGINS=*

# หรือกำหนด origins เฉพาะ (production)
CORS_ORIGINS=http://192.168.1.100:5000,http://example.com
```

### ปัญหา 3: Connection Refused

#### ตรวจสอบว่า application กำลังทำงาน:

```bash
# ตรวจสอบ container status
docker-compose ps

# ดู logs
docker-compose logs -f web

# ตรวจสอบ health check
curl http://localhost:5000/health
```

## Security Considerations (สำคัญ!)

### 1. Production Environment

เมื่อ deploy production **ต้อง**:

#### A. ปิด Debug Mode:
```bash
FLASK_ENV=production
FLASK_DEBUG=0
```

#### B. จำกัด CORS Origins:
```bash
# เปลี่ยนจาก * เป็น domains เฉพาะ
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

#### C. ใช้ HTTPS:
```bash
# ใช้ reverse proxy (Nginx/Apache) กับ SSL certificate
# หรือใช้ Cloudflare
```

### 2. Firewall Rules

อนุญาตเฉพาะ IPs ที่ต้องการ:

```bash
# UFW - อนุญาตเฉพาะ subnet เฉพาะ
sudo ufw allow from 192.168.1.0/24 to any port 5000

# iptables - อนุญาตเฉพาะ IP เฉพาะ
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 5000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5000 -j DROP
```

### 3. Reverse Proxy (แนะนำสำหรับ Production)

ใช้ Nginx หรือ Apache เป็น reverse proxy:

#### ตัวอย่าง Nginx Config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Rate Limiting

ป้องกัน abuse โดยใช้ rate limiting:

```python
# ใน app.py อาจเพิ่ม Flask-Limiter
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)
```

## การใช้งานกับ Docker

### Development:
```bash
# Start services
docker-compose up -d

# Check logs
docker-compose logs -f web

# Access at: http://<your-ip>:5000
```

### Production:
```bash
# Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Ensure environment variables are set
# FLASK_ENV=production
# FLASK_DEBUG=0
# CORS_ORIGINS=<your-domains>
```

## ทดสอบการเชื่อมต่อ

### จาก Server เครื่องเดียวกัน:
```bash
curl http://localhost:5000/health
```

### จากเครื่องอื่นใน LAN:
```bash
curl http://<server-ip>:5000/health
```

### จาก Internet (ถ้าทำ port forwarding แล้ว):
```bash
curl http://<public-ip>:5000/health
```

ผลลัพธ์ที่คาดหวัง:
```json
{
  "status": "healthy",
  "service": "wms-barcode-scanner-web",
  "timestamp": "2025-11-21T10:30:00.123456"
}
```

## Quick Reference

### URLs to Access:
| Location | URL |
|----------|-----|
| Localhost | `http://localhost:5000` |
| LAN | `http://<local-ip>:5000` |
| WAN | `http://<public-ip>:5000` (requires port forwarding) |

### Important Ports:
- **5000**: Flask web application (default)

### Key Files:
- `src/web/app.py`: Main application file
- `.env`: Environment variables configuration
- `docker-compose.yml`: Docker services configuration
- `Dockerfile`: Container build configuration

### Useful Commands:
```bash
# Get local IP
hostname -I

# Check if port is listening
sudo netstat -tulpn | grep :5000

# Test local access
curl http://localhost:5000/health

# Test external access
curl http://<ip-address>:5000/health

# View logs
docker-compose logs -f web

# Restart services
docker-compose restart web
```

## ติดต่อสอบถาม

หากมีปัญหาหรือข้อสงสัย กรุณาตรวจสอบ:
1. Logs: `docker-compose logs web`
2. Network connectivity: `ping <server-ip>`
3. Port availability: `telnet <server-ip> 5000`
4. Firewall rules: `sudo ufw status` หรือ `sudo iptables -L`
