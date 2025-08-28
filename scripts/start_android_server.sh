#!/bin/bash

echo "========================================"
echo "   WMS Barcode Scanner สำหรับ Android"
echo "========================================"
echo

# ตรวจสอบ Python
echo "🔍 กำลังตรวจสอบ Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ ไม่พบ Python กรุณาติดตั้ง Python ก่อน"
    exit 1
fi

echo "✅ พบ Python แล้ว"
echo

# ติดตั้ง Dependencies
echo "📦 กำลังติดตั้ง Dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ เกิดข้อผิดพลาดในการติดตั้ง Dependencies"
    exit 1
fi

echo "✅ ติดตั้ง Dependencies สำเร็จ"
echo

# แสดง IP Address
echo "🌐 กำลังแสดง IP Address ของเครื่อง..."
if command -v ip &> /dev/null; then
    # สำหรับระบบที่ใช้ ip command
    IP=$(ip route get 1.1.1.1 | awk '{print $7}' | head -n1)
else
    # สำหรับระบบที่ใช้ ifconfig
    IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
fi

echo "📱 IP Address: $IP"
echo "📱 URL สำหรับ Android: http://$IP:5000"
echo

echo "🚀 กำลังเริ่มต้น Web Server..."
echo "📱 สามารถเข้าถึงได้ที่: http://localhost:5000"
echo "📱 สำหรับ Android: http://$IP:5000"
echo
echo "💡 กด Ctrl+C เพื่อหยุดการทำงาน"
echo

python3 web_app.py 