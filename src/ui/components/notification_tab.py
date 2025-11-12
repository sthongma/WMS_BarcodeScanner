#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Tab Component
UI component for notification data management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Callable, List
import pandas as pd
from services.notification_service import NotificationService
from utils.file_utils import create_template_excel
import logging


class NotificationTab:
    """แท็บการจัดการ notification popup"""

    def __init__(self, parent: ttk.Frame, db_manager, current_user: str = "system"):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.notification_service = NotificationService("UI: NotificationTab", db_manager)
        self.import_data = None
        # module logger - UI components use module logger
        self.logger = logging.getLogger(__name__)

        self.setup_ui()
        self.load_notifications()

    def setup_ui(self):
        """สร้าง UI"""
        # สร้าง frame หลัก
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # หัวข้อ
        title_label = ttk.Label(main_frame, text="จัดการแจ้งเตือน Popup", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # Frame สำหรับปุ่มบน
        top_button_frame = ttk.LabelFrame(main_frame, text="จัดการข้อมูล")
        top_button_frame.pack(fill=tk.X, pady=(0, 20))

        # ปุ่มนำเข้า Excel
        ttk.Button(
            top_button_frame,
            text="นำเข้าจาก Excel",
            command=self.import_excel
        ).pack(side=tk.LEFT, padx=5, pady=10)

        # ปุ่มดาวน์โหลด template
        ttk.Button(
            top_button_frame,
            text="ดาวน์โหลด Template",
            command=self.download_template
        ).pack(side=tk.LEFT, padx=5, pady=10)

        # Info label
        info_text = "รูปแบบ Excel: barcode | event_type (success/error/duplicate/warning) | popup_type (modal/toast) | title | message"
        info_label = ttk.Label(top_button_frame, text=info_text, foreground="gray")
        info_label.pack(side=tk.LEFT, padx=10)

        # Frame สำหรับตาราง
        list_frame = ttk.LabelFrame(main_frame, text="รายการแจ้งเตือน")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Treeview สำหรับแสดงรายการ
        columns = ("ID", "Barcode", "Event Type", "Popup Type", "Title", "Message", "สถานะ", "วันที่สร้าง")
        self.notification_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        # กำหนดหัวข้อ
        column_widths = {
            "ID": 50,
            "Barcode": 120,
            "Event Type": 100,
            "Popup Type": 80,
            "Title": 200,
            "Message": 300,
            "สถานะ": 80,
            "วันที่สร้าง": 150
        }

        for col in columns:
            self.notification_tree.heading(col, text=col)
            self.notification_tree.column(col, width=column_widths.get(col, 100))

        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.notification_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.notification_tree.xview)
        self.notification_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Pack scrollbars and treeview
        self.notification_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Context menu สำหรับตาราง
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="แก้ไข", command=self.edit_notification)
        self.context_menu.add_command(label="ทดสอบแจ้งเตือน", command=self.test_notification)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="ลบ", command=self.delete_selected)

        # Bind right-click context menu
        self.notification_tree.bind("<Button-3>", self.show_context_menu)

    def load_notifications(self):
        """โหลดรายการ notification"""
        # ล้างข้อมูลเก่า
        for item in self.notification_tree.get_children():
            self.notification_tree.delete(item)

        # ดึงข้อมูลจาก service
        notifications = self.notification_service.get_all_notifications()
        self.logger.debug(f"[NotificationTab] โหลดข้อมูล: พบ {len(notifications)} รายการ")

        # แสดงข้อมูลใน treeview
        for notif in notifications:
            status = "เปิดใช้งาน" if notif['is_enabled'] else "ปิดใช้งาน"
            created_date = notif['created_date'].strftime('%Y-%m-%d %H:%M') if notif['created_date'] else ''

            # Truncate message if too long
            message = notif['message']
            if len(message) > 50:
                message = message[:50] + '...'

            self.notification_tree.insert("", tk.END, values=(
                notif['id'],
                notif['barcode'],
                notif['event_type'],
                notif['popup_type'],
                notif['title'],
                message,
                status,
                created_date
            ), tags=(notif['event_type'],))

        # Add tag colors
        self.notification_tree.tag_configure('success', foreground='green')
        self.notification_tree.tag_configure('error', foreground='red')
        self.notification_tree.tag_configure('warning', foreground='orange')
        self.notification_tree.tag_configure('duplicate', foreground='orange')

    def import_excel(self):
        """นำเข้าข้อมูลจาก Excel"""
        self.logger.info("[NotificationTab] เริ่มกระบวนการนำเข้า Excel")

        file_path = filedialog.askopenfilename(
            title="เลือกไฟล์ Excel",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            self.logger.debug("[NotificationTab] ผู้ใช้ยกเลิกการเลือกไฟล์")
            return

        self.logger.info(f"[NotificationTab] เลือกไฟล์: {file_path}")

        # ยืนยันการนำเข้า (จะล้างข้อมูลเก่าทั้งหมด)
        confirm = messagebox.askyesno(
            "ยืนยันการนำเข้า",
            "การนำเข้าจะล้างข้อมูล notification เก่าทั้งหมด\n\nต้องการดำเนินการต่อหรือไม่?"
        )

        if not confirm:
            self.logger.debug("[NotificationTab] ผู้ใช้ยกเลิกการนำเข้า")
            return

        try:
            self.logger.debug("[NotificationTab] เรียก import_notifications...")
            # นำเข้าผ่าน service
            result = self.notification_service.import_notifications(file_path, self.current_user)
            self.logger.info(f"[NotificationTab] ผลลัพธ์การนำเข้า: success={result.get('success')} message={result.get('message')}")

            if result['success']:
                self.logger.info("[NotificationTab] นำเข้าสำเร็จ - กำลังรีเฟรชตาราง...")
                self.load_notifications()
                self.logger.debug("[NotificationTab] รีเฟรชตารางเสร็จสิ้น")

                # Force UI update
                self.notification_tree.update_idletasks()
                self.parent.update_idletasks()

                messagebox.showinfo("สำเร็จ", result['message'])
            else:
                self.logger.warning(f"[NotificationTab] นำเข้าไม่สำเร็จ: {result.get('message')}")
                error_msg = result['message']
                if 'errors' in result:
                    error_msg += "\n\nข้อผิดพลาด:\n" + "\n".join(result['errors'][:5])
                    if len(result['errors']) > 5:
                        error_msg += f"\n... และอีก {len(result['errors']) - 5} รายการ"
                messagebox.showerror("ผิดพลาด", error_msg)

        except Exception as e:
            self.logger.exception(f"[NotificationTab] Exception during import: {e}")
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

    def download_template(self):
        """ดาวน์โหลด template"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="บันทึก Template",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )

            if file_path:
                columns = ["barcode", "event_type", "popup_type", "title", "message"]
                sample_data = [
                    ["TEST001", "warning", "modal", "สินค้าใกล้หมดอายุ", "สินค้านี้จะหมดอายุภายใน 7 วัน กรุณาตรวจสอบ"],
                    ["TEST002", "error", "modal", "สินค้าหมดอายุ", "สินค้านี้หมดอายุแล้ว ห้ามจัดส่ง!"],
                    ["TEST003", "warning", "toast", "แจ้งเตือนทั่วไป", "สินค้านี้ต้องเก็บในอุณหภูมิต่ำ"]
                ]

                if create_template_excel(file_path, columns, sample_data):
                    messagebox.showinfo("สำเร็จ", f"บันทึก template เรียบร้อยแล้วที่: {file_path}")
                else:
                    messagebox.showerror("ผิดพลาด", "ไม่สามารถสร้าง template ได้")

        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

    def show_context_menu(self, event):
        """แสดง context menu เมื่อคลิกขวา"""
        # Select the item under cursor
        item = self.notification_tree.identify_row(event.y)
        if item:
            self.notification_tree.selection_set(item)
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def edit_notification(self):
        """แก้ไขรายการ notification"""
        self.logger.debug("[NotificationTab] เริ่มกระบวนการแก้ไข")
        selected = self.notification_tree.selection()

        if not selected:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกรายการที่ต้องการแก้ไข")
            return

        # ดึงข้อมูลที่เลือก
        item = self.notification_tree.item(selected[0])
        values = item['values']
        notification_id = values[0]
        self.logger.debug(f"[NotificationTab] แก้ไข notification ID: {notification_id}")

        # แสดง dialog สำหรับแก้ไข
        self.show_edit_dialog(notification_id, values)

    def show_edit_dialog(self, notification_id: int, current_values: tuple):
        """แสดง dialog สำหรับแก้ไข notification"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("แก้ไขการแจ้งเตือน")
        dialog.geometry("500x450")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Main frame with padding
        main_dialog_frame = ttk.Frame(dialog, padding=20)
        main_dialog_frame.pack(fill=tk.BOTH, expand=True)

        # Barcode
        ttk.Label(main_dialog_frame, text="Barcode:").grid(row=0, column=0, sticky=tk.W, pady=5)
        barcode_entry = ttk.Entry(main_dialog_frame, width=40)
        barcode_entry.insert(0, current_values[1])  # barcode
        barcode_entry.grid(row=0, column=1, pady=5, padx=5)

        # Event Type
        ttk.Label(main_dialog_frame, text="Event Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        event_type_var = tk.StringVar(value=current_values[2])  # event_type
        event_type_combo = ttk.Combobox(main_dialog_frame, textvariable=event_type_var, width=37, state='readonly')
        event_type_combo['values'] = ('success', 'error', 'duplicate', 'warning')
        event_type_combo.grid(row=1, column=1, pady=5, padx=5)

        # Popup Type
        ttk.Label(main_dialog_frame, text="Popup Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        popup_type_var = tk.StringVar(value=current_values[3])  # popup_type
        popup_type_combo = ttk.Combobox(main_dialog_frame, textvariable=popup_type_var, width=37, state='readonly')
        popup_type_combo['values'] = ('modal', 'toast')
        popup_type_combo.grid(row=2, column=1, pady=5, padx=5)

        # Title
        ttk.Label(main_dialog_frame, text="Title:").grid(row=3, column=0, sticky=tk.W, pady=5)
        title_entry = ttk.Entry(main_dialog_frame, width=40)
        title_entry.insert(0, current_values[4])  # title
        title_entry.grid(row=3, column=1, pady=5, padx=5)

        # Message
        ttk.Label(main_dialog_frame, text="Message:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        message_text = tk.Text(main_dialog_frame, width=40, height=8, wrap=tk.WORD)
        # Get full message from service
        notifications = self.notification_service.get_all_notifications()
        full_message = ""
        for notif in notifications:
            if notif['id'] == notification_id:
                full_message = notif['message']
                break
        message_text.insert('1.0', full_message)
        message_text.grid(row=4, column=1, pady=5, padx=5)

        def save_changes():
            barcode = barcode_entry.get().strip()
            event_type = event_type_var.get().strip()
            popup_type = popup_type_var.get().strip()
            title = title_entry.get().strip()
            message = message_text.get('1.0', tk.END).strip()

            if not barcode or not event_type or not popup_type or not title or not message:
                messagebox.showerror("ผิดพลาด", "กรุณากรอกข้อมูลให้ครบถ้วน")
                return

            if len(title) > 255:
                messagebox.showerror("ผิดพลาด", "Title ต้องไม่เกิน 255 ตัวอักษร")
                return

            try:
                self.logger.info(f"[NotificationTab] บันทึกการแก้ไข ID: {notification_id}")

                # Update notification
                update_query = """
                    UPDATE notification_data
                    SET barcode = ?, event_type = ?, popup_type = ?,
                        title = ?, message = ?
                    WHERE id = ?
                """
                self.db_manager.execute_non_query(
                    update_query,
                    (barcode, event_type, popup_type, title, message, notification_id)
                )

                messagebox.showinfo("สำเร็จ", "แก้ไขรายการเรียบร้อยแล้ว")
                dialog.destroy()
                self.load_notifications()

            except Exception as e:
                self.logger.exception(f"[NotificationTab] ข้อผิดพลาดในการแก้ไข: {e}")
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถแก้ไขรายการได้: {str(e)}")

        # Buttons
        button_frame = ttk.Frame(main_dialog_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="บันทึก", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ยกเลิก", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_selected(self):
        """ลบรายการที่เลือก"""
        self.logger.info("[NotificationTab] เริ่มกระบวนการลบรายการ")
        selected_items = self.notification_tree.selection()

        if not selected_items:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกรายการที่ต้องการลบ")
            return

        self.logger.debug(f"[NotificationTab] เลือกรายการ: {len(selected_items)} รายการ")

        # ยืนยันการลบ
        confirm = messagebox.askyesno(
            "ยืนยันการลบ",
            f"ต้องการลบรายการที่เลือก {len(selected_items)} รายการหรือไม่?"
        )

        if not confirm:
            self.logger.debug("[NotificationTab] ผู้ใช้ยกเลิกการลบ")
            return

        # ลบรายการ
        deleted_count = 0
        errors = []

        for item in selected_items:
            values = self.notification_tree.item(item, 'values')
            notification_id = int(values[0])
            self.logger.debug(f"[NotificationTab] กำลังลบ ID: {notification_id}")

            result = self.notification_service.delete_notification(notification_id)

            if result['success']:
                deleted_count += 1
            else:
                errors.append(f"ID {notification_id}: {result['message']}")

        self.logger.info(f"[NotificationTab] ลบเสร็จสิ้น: {deleted_count} รายการ")

        # รีเฟรชรายการ
        self.logger.debug("[NotificationTab] กำลังรีเฟรชตาราง...")
        self.load_notifications()

        # Force UI update
        self.notification_tree.update_idletasks()
        self.parent.update_idletasks()

        # แสดงผลลัพธ์
        if errors:
            messagebox.showwarning(
                "ลบบางรายการไม่สำเร็จ",
                f"ลบสำเร็จ {deleted_count} รายการ\n\nข้อผิดพลาด:\n" + "\n".join(errors[:5])
            )
        else:
            messagebox.showinfo("สำเร็จ", f"ลบรายการสำเร็จ {deleted_count} รายการ")

    def clear_all_notifications(self):
        """ล้าง notification ทั้งหมด"""
        self.logger.info("[NotificationTab] เริ่มกระบวนการล้างข้อมูลทั้งหมด")

        # ยืนยันการลบ
        confirm = messagebox.askyesno(
            "ยืนยันการล้างข้อมูล",
            "ต้องการล้างข้อมูล notification ทั้งหมดหรือไม่?\n\nการดำเนินการนี้ไม่สามารถยกเลิกได้!"
        )

        if not confirm:
            self.logger.debug("[NotificationTab] ผู้ใช้ยกเลิกการล้างข้อมูล")
            return

        # ล้างข้อมูล
        result = self.notification_service.clear_all_notifications()
        self.logger.info(f"[NotificationTab] ผลลัพธ์การล้างข้อมูล: success={result.get('success')} message={result.get('message')}")

        if result['success']:
            self.logger.info("[NotificationTab] ล้างข้อมูลสำเร็จ - กำลังรีเฟรชตาราง...")
            self.load_notifications()

            # Force UI update
            self.notification_tree.update_idletasks()
            self.parent.update_idletasks()

            messagebox.showinfo("สำเร็จ", result['message'])
        else:
            messagebox.showerror("ผิดพลาด", result.get('message'))

    def test_notification(self):
        """ทดสอบแจ้งเตือน"""
        self.logger.info("[NotificationTab] เริ่มทดสอบแจ้งเตือน")
        selected_items = self.notification_tree.selection()

        if not selected_items:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกรายการที่ต้องการทดสอบ")
            return

        # ดึงข้อมูลรายการที่เลือก
        values = self.notification_tree.item(selected_items[0], 'values')
        notification_id = values[0]
        self.logger.debug(f"[NotificationTab] ทดสอบ notification ID: {notification_id}")

        # Get full message from service
        notifications = self.notification_service.get_all_notifications()
        full_message = ""
        for notif in notifications:
            if notif['id'] == notification_id:
                full_message = notif['message']
                break

        notification_data = {
            'barcode': values[1],  # barcode
            'title': values[4],
            'message': full_message,
            'event_type': values[2],
            'popup_type': values[3]
        }

        # แสดง notification dialog
        from ui.components.notification_dialog import show_notification
        show_notification(self.parent, notification_data)
        self.logger.debug("[NotificationTab] แสดง notification dialog สำเร็จ")