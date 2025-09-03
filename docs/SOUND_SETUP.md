# การตั้งค่าเสียงสำหรับ WMS Barcode Scanner

## การติดตั้ง pygame

เพื่อให้ระบบเสียงทำงานได้ คุณต้องติดตั้ง pygame:

```bash
pip install pygame>=2.1.0
```

หรือใช้ requirements.txt:

```bash
pip install -r requirements.txt
```

## ไฟล์เสียง

ระบบจะใช้ไฟล์เสียงจากโฟลเดอร์ `static/`:

- `error_2.mp3` - เสียงเตือนเมื่อสแกนซ้ำ
- `error_3.mp3` - เสียงเตือนเมื่องานก่อนหน้านี้ไม่มี
- `error_4.mp3` - เสียงข้อมูลทั่วไป

## การปรับแต่งเสียง

คุณสามารถเปลี่ยนไฟล์เสียงได้โดยแก้ไขใน `src/ui/main_window.py`:

```python
sound_files = {
    "error": "static/error_2.mp3",      # สำหรับสแกนซ้ำ
    "warning": "static/error_3.mp3",    # สำหรับงานก่อนหน้านี้ไม่มี
    "info": "static/error_4.mp3"        # สำหรับข้อมูลทั่วไป
}
```

## การปิดเสียง

หากต้องการปิดเสียง สามารถแก้ไขใน `src/ui/main_window.py`:

```python
# เปลี่ยนจาก
self.sound_enabled = True
# เป็น
self.sound_enabled = False
```

## หมายเหตุ

- ระบบจะแสดง warning หากไม่สามารถ initialize pygame ได้
- ไฟล์เสียงต้องเป็นรูปแบบ MP3
- หากไฟล์เสียงไม่พบ ระบบจะแสดงข้อความใน console แต่จะไม่หยุดการทำงาน
