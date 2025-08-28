# การแก้ไขปัญหาประวัติการสแกน

## ปัญหาที่พบ
เมื่อ login เข้าโปรแกรมแล้ว ประวัติการสแกนไม่แสดงในแท็บ "หน้าจอหลัก" ต้องสแกนบาร์โค้ดก่อนถึงจะขึ้นประวัติ

## สาเหตุของปัญหา
1. **ชื่อแท็บไม่ตรงกัน**: ในฟังก์ชัน `on_tab_changed()` มีการตรวจสอบ `if selected_tab == "สแกน":` แต่ชื่อแท็บจริงๆ คือ "หน้าจอหลัก"
2. **Index แท็บไม่ถูกต้อง**: ในฟังก์ชัน `main()` มีการเรียก `app.notebook.select(3)` แต่แท็บ "หน้าจอหลัก" คือ index 0
3. **ไม่มีการโหลดประวัติเริ่มต้น**: ไม่มีการเรียก `refresh_scanning_history()` เมื่อเริ่มโปรแกรม

## การแก้ไขที่ทำ

### 1. แก้ไขชื่อแท็บใน on_tab_changed()
```python
# เดิม
if selected_tab == "สแกน":

# ใหม่  
if selected_tab == "หน้าจอหลัก":
```

### 2. แก้ไข index แท็บใน main()
```python
# เดิม
root.after(100, lambda: app.notebook.select(3))

# ใหม่
root.after(100, lambda: app.notebook.select(0))
```

### 3. เพิ่มการโหลดประวัติเริ่มต้นใน __init__()
```python
# เพิ่มบรรทัดนี้ใน __init__()
self.root.after(1000, self.refresh_scanning_history)  # Load initial history data
```

### 4. เพิ่ม debug messages ใน refresh_scanning_history()
```python
def refresh_scanning_history(self):
    try:
        print("Refreshing scanning history...")  # Debug message
        # ... existing code ...
        print(f"Found {len(results)} records")  # Debug message
        # ... existing code ...
        print("Scanning history refreshed successfully")  # Debug message
    except Exception as e:
        print(f"Error refreshing scanning history: {str(e)}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
```

## ผลลัพธ์ที่คาดหวัง
- เมื่อ login เข้าโปรแกรม ประวัติการสแกนจะแสดงทันทีในแท็บ "หน้าจอหลัก"
- เมื่อเปลี่ยนไปยังแท็บ "หน้าจอหลัก" ประวัติจะถูก refresh อัตโนมัติ
- เมื่อสแกนบาร์โค้ดใหม่ ประวัติจะอัพเดททันที

## การทดสอบ
รันไฟล์ `test_history_fix.py` เพื่อทดสอบการแก้ไข:

```bash
python test_history_fix.py
```

## หมายเหตุ
- การแก้ไขนี้จะทำให้ประวัติแสดงทันทีเมื่อเริ่มโปรแกรม
- Debug messages จะแสดงใน console เพื่อช่วยในการ troubleshoot
- ประวัติจะถูก refresh อัตโนมัติเมื่อมีการสแกนใหม่ 