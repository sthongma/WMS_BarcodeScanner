# คู่มือการตั้งค่า Cloudflare Tunnel สำหรับ WMS Barcode Scanner

คู่มือนี้จะแนะนำวิธีการตั้งค่า Cloudflare Tunnel เพื่อให้คนอื่นเข้าถึง WMS Web App จากภายนอกได้ โดยไม่ต้องเปิด port หรือตั้งค่า router

## 📋 สิ่งที่ต้องเตรียม

1. ✅ Cloudflare Account (สมัครฟรีที่ https://dash.cloudflare.com/sign-up)
2. ✅ Domain name (ไม่บังคับ - Cloudflare จะให้ subdomain ฟรี)
3. ✅ Windows OS (คู่มือนี้สำหรับ Windows)
4. ✅ WMS Web App ต้องรันอยู่ที่ port 5003

---

## 🚀 ขั้นตอนที่ 1: ติดตั้ง cloudflared

### วิธีที่ 1: ดาวน์โหลดแบบง่าย (แนะนำ)

1. ดาวน์โหลด cloudflared สำหรับ Windows:
   - 64-bit: https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
   - 32-bit: https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-386.exe

2. เปลี่ยนชื่อไฟล์เป็น `cloudflared.exe`

3. วางไฟล์ไว้ที่หนึ่งในตำแหน่งนี้:
   - `C:\Windows\System32\` (ต้องใช้สิทธิ์ Administrator)
   - หรือ สร้างโฟลเดอร์ `C:\cloudflared\` แล้วเพิ่ม path เข้า Environment Variables

### วิธีที่ 2: ใช้ Chocolatey (ถ้ามี)

```powershell
choco install cloudflared
```

### วิธีที่ 3: ใช้ winget (Windows 10/11)

```powershell
winget install --id Cloudflare.cloudflared
```

### ตรวจสอบการติดตั้ง

เปิด Command Prompt แล้วพิมพ์:

```cmd
cloudflared --version
```

ถ้าติดตั้งสำเร็จจะแสดงเวอร์ชันของ cloudflared

---

## 🔐 ขั้นตอนที่ 2: Login เข้า Cloudflare

เปิด Command Prompt ในโฟลเดอร์ WMS_BarcodeScanner แล้วรัน:

```cmd
cloudflared tunnel login
```

- เบราว์เซอร์จะเปิดขึ้นมาอัตโนมัติ
- เลือก domain ที่ต้องการใช้ (หรือข้ามไปถ้าไม่มี domain)
- อนุญาตการเชื่อมต่อ
- ไฟล์ `cert.pem` จะถูกสร้างขึ้นที่ `C:\Users\YOUR_USERNAME\.cloudflared\`

---

## 🌐 ขั้นตอนที่ 3: สร้าง Tunnel

สร้าง tunnel ชื่อ `wms-barcode-scanner`:

```cmd
cloudflared tunnel create wms-barcode-scanner
```

คำสั่งนี้จะ:
- สร้าง Tunnel ID (UUID แบบยาวๆ เช่น `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)
- สร้างไฟล์ credentials ที่ `C:\Users\YOUR_USERNAME\.cloudflared\a1b2c3d4-e5f6-7890-abcd-ef1234567890.json`

**⚠️ สำคัญ:** บันทึก Tunnel ID ที่ได้ ต้องใช้ในขั้นตอนถัดไป!

---

## ⚙️ ขั้นตอนที่ 4: แก้ไขไฟล์ Config

### 4.1 คัดลอกไฟล์ credentials

คัดลอกไฟล์ credentials จาก:
```
C:\Users\YOUR_USERNAME\.cloudflared\YOUR_TUNNEL_ID.json
```

ไปยัง:
```
WMS_BarcodeScanner\cloudflare\credentials.json
```

### 4.2 แก้ไขไฟล์ config.yml

เปิดไฟล์ `WMS_BarcodeScanner\cloudflare\config.yml` แล้วแก้ไข:

```yaml
tunnel: YOUR_TUNNEL_ID  # <-- ใส่ Tunnel ID ที่ได้จากขั้นตอนที่ 3
credentials-file: C:\Users\shins\OneDrive\Desktop\GitHub\WMS_BarcodeScanner\cloudflare\credentials.json

ingress:
  # WMS Barcode Scanner Web App
  - hostname: YOUR_DOMAIN.com  # <-- ใส่ domain หรือ subdomain ของคุณ
    service: http://localhost:5003

  # Catch-all rule (required)
  - service: http_status:404
```

**ตัวอย่าง:**

```yaml
tunnel: a1b2c3d4-e5f6-7890-abcd-ef1234567890
credentials-file: C:\Users\shins\OneDrive\Desktop\GitHub\WMS_BarcodeScanner\cloudflare\credentials.json

ingress:
  - hostname: wms.example.com
    service: http://localhost:5003

  - service: http_status:404
```

---

## 🔗 ขั้นตอนที่ 5: กำหนด DNS Route

สร้าง DNS record ที่เชื่อม domain กับ tunnel:

```cmd
cloudflared tunnel route dns wms-barcode-scanner wms.example.com
```

เปลี่ยน `wms.example.com` เป็น domain/subdomain ที่ต้องการใช้

### ถ้าไม่มี Domain ของตัวเอง

Cloudflare จะให้ subdomain ฟรีในรูปแบบ:
```
https://YOUR_TUNNEL_ID.cfargotunnel.com
```

ใช้ได้เลยโดยไม่ต้องกำหนด DNS route

---

## 🎯 ขั้นตอนที่ 6: รัน Tunnel

### วิธีที่ 1: รัน Tunnel อย่างเดียว

ถ้า WMS Web App รันอยู่แล้วที่ port 5003:

```cmd
run_tunnel.bat
```

### วิธีที่ 2: รัน WMS App + Tunnel พร้อมกัน (แนะนำ)

```cmd
run_wms_with_tunnel.bat
```

Script นี้จะ:
1. เปิด WMS Web App ในหน้าต่างใหม่
2. เปิด Cloudflare Tunnel ในหน้าต่างปัจจุบัน

### วิธีที่ 3: รันด้วย Command Line โดยตรง

```cmd
cloudflared tunnel --config cloudflare\config.yml run
```

---

## ✅ ทดสอบการเชื่อมต่อ

1. รัน WMS Web App + Tunnel
2. เปิดเบราว์เซอร์แล้วไปที่ URL ของคุณ:
   - ถ้ามี domain: `https://wms.example.com`
   - ถ้าไม่มี domain: `https://YOUR_TUNNEL_ID.cfargotunnel.com`
3. ควรเห็นหน้า WMS Barcode Scanner

---

## 🔄 ตั้งค่าให้ Tunnel รันอัตโนมัติ (Optional)

### วิธีที่ 1: ติดตั้งเป็น Windows Service (แนะนำ)

1. เปิด Command Prompt แบบ Administrator
2. ไปที่โฟลเดอร์ WMS_BarcodeScanner
3. รันคำสั่ง:

```cmd
cloudflared service install
```

4. Start service:

```cmd
cloudflared service start
```

5. ตรวจสอบสถานะ:

```cmd
cloudflared service status
```

### วิธีที่ 2: เพิ่มเข้า Startup

1. กด `Win + R` แล้วพิมพ์ `shell:startup`
2. สร้าง shortcut ของ `run_tunnel.bat` ในโฟลเดอร์ Startup

---

## 🛠️ คำสั่งที่มีประโยชน์

### ดู Tunnel ทั้งหมด

```cmd
cloudflared tunnel list
```

### ดูข้อมูล Tunnel

```cmd
cloudflared tunnel info wms-barcode-scanner
```

### ลบ Tunnel

```cmd
cloudflared tunnel delete wms-barcode-scanner
```

### ดู Logs

```cmd
cloudflared tunnel --config cloudflare\config.yml run --loglevel debug
```

---

## 🔒 ความปลอดภัย

### เพิ่ม Access Policy (แนะนำ)

ถ้าต้องการจำกัดคนที่เข้าถึง:

1. ไปที่ Cloudflare Dashboard: https://one.dash.cloudflare.com/
2. เลือก **Access** > **Applications**
3. คลิก **Add an application**
4. ตั้งค่า authentication (Email OTP, Google, etc.)
5. กำหนดว่าใครสามารถเข้าถึงได้

### ตัวอย่าง Access Rules:

- อนุญาตเฉพาะ email จากบริษัท: `*@company.com`
- อนุญาตเฉพาะ IP range: `192.168.1.0/24`
- ใช้ One-Time PIN ผ่าน Email

---

## 🐛 แก้ไขปัญหา

### ปัญหา: cloudflared not found

**วิธีแก้:**
- ตรวจสอบว่าติดตั้ง cloudflared แล้ว
- ตรวจสอบ PATH environment variable
- ลองรันด้วย full path: `C:\cloudflared\cloudflared.exe`

### ปัญหา: Connection refused

**วิธีแก้:**
- ตรวจสอบว่า WMS Web App รันอยู่ที่ port 5003
- รัน `netstat -ano | findstr :5003` เพื่อดูว่า port 5003 เปิดอยู่หรือไม่
- ลองรัน WMS App ก่อนแล้วค่อยรัน Tunnel

### ปัญหา: 404 Error

**วิธีแก้:**
- ตรวจสอบว่า DNS route ถูกต้อง
- ตรวจสอบ hostname ใน config.yml
- รอ 1-2 นาทีให้ DNS propagate

### ปัญหา: Credentials file not found

**วิธีแก้:**
- ตรวจสอบว่าคัดลอกไฟล์ credentials.json ไปที่ `cloudflare\credentials.json` แล้ว
- ตรวจสอบ path ใน config.yml ว่าถูกต้อง

---

## 📊 ตรวจสอบสถานะและ Traffic

ดู traffic และสถานะได้ที่:
- Cloudflare Dashboard: https://dash.cloudflare.com/
- Zero Trust Dashboard: https://one.dash.cloudflare.com/
- Analytics: ดู requests, bandwidth, errors

---

## 💡 เคล็ดลับ

1. **ใช้ชื่อ tunnel ที่เข้าใจง่าย** เพื่อจัดการภายหลัง
2. **เก็บ Tunnel ID และ credentials ไว้อย่างปลอดภัย** อย่าเผยแพร่สู่สาธารณะ
3. **ใช้ Access Policy** ถ้าต้องการความปลอดภัยสูง
4. **ติดตั้งเป็น Service** ถ้าต้องการให้รันตลอดเวลา
5. **ตรวจสอบ Logs** เป็นระยะเพื่อดูปัญหา

---

## 📚 ข้อมูลเพิ่มเติม

- Cloudflare Tunnel Docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- Cloudflare Zero Trust: https://www.cloudflare.com/products/zero-trust/
- Community Forum: https://community.cloudflare.com/

---

## ✨ ทดสอบแล้วเรียบร้อย!

เมื่อตั้งค่าเสร็จแล้ว คนอื่นสามารถเข้าถึง WMS Web App ได้จาก:

```
https://YOUR_DOMAIN.com
```

หรือ

```
https://YOUR_TUNNEL_ID.cfargotunnel.com
```

โดยไม่ต้องเปิด port บน router หรือตั้งค่า port forwarding!

---

**หมายเหตุ:** ใช้งานฟรีสำหรับ Cloudflare Tunnel (ไม่จำกัด bandwidth)
