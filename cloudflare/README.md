# Cloudflare Tunnel Configuration

โฟลเดอร์นี้เก็บไฟล์ configuration สำหรับ Cloudflare Tunnel

## ไฟล์ในโฟลเดอร์

### config.yml
ไฟล์ configuration หลักสำหรับ Cloudflare Tunnel
- ต้องแก้ไข `YOUR_TUNNEL_ID` และ `YOUR_DOMAIN.com` ก่อนใช้งาน

### credentials.json (ไม่มีใน git)
ไฟล์ credentials ที่ได้จาก Cloudflare
- **ห้ามแชร์หรือ commit ไฟล์นี้!**
- คัดลอกจาก `C:\Users\YOUR_USERNAME\.cloudflared\YOUR_TUNNEL_ID.json`

### credentials.json.example
ตัวอย่างโครงสร้างไฟล์ credentials

### .gitignore
ป้องกันไม่ให้ไฟล์ sensitive ถูก commit เข้า git

## วิธีใช้

ดูคู่มือฉบับเต็มที่: [CLOUDFLARE_TUNNEL_SETUP.md](../CLOUDFLARE_TUNNEL_SETUP.md)

## Quick Start

1. ติดตั้ง cloudflared
2. Login: `cloudflared tunnel login`
3. สร้าง tunnel: `cloudflared tunnel create wms-barcode-scanner`
4. คัดลอก credentials.json มาที่โฟลเดอร์นี้
5. แก้ไข config.yml
6. รัน: `cloudflared tunnel --config cloudflare\config.yml run`
