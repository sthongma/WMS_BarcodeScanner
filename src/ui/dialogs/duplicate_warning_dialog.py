#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duplicate Warning Dialog
Displays a warning when a duplicate barcode is detected
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable
from ... import constants


class DuplicateWarningDialog:
    """
    Dialog to display duplicate barcode warning

    This dialog shows when a barcode has already been scanned for the
    same job type and sub job type. It displays the existing scan details
    and auto-closes after 3 seconds.
    """

    def __init__(
        self,
        parent: tk.Widget,
        barcode: str,
        job_type: str,
        sub_job_type: str,
        existing_record: Dict[str, Any],
        on_close_callback: Optional[Callable] = None
    ):
        """
        Initialize duplicate warning dialog

        Args:
            parent: Parent window
            barcode: The duplicate barcode
            job_type: Main job type name
            sub_job_type: Sub job type name
            existing_record: Dictionary with existing scan details:
                - scan_date: datetime object of when it was scanned
                - user_id: User who performed the scan
            on_close_callback: Optional callback to execute when dialog closes
        """
        self.parent = parent
        self.barcode = barcode
        self.job_type = job_type
        self.sub_job_type = sub_job_type
        self.existing_record = existing_record
        self.on_close_callback = on_close_callback

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("ไม่อนุญาตให้สแกนซ้ำ")
        self.dialog.geometry(constants.DIALOG_DUPLICATE_WARNING_SIZE)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.center_dialog()

        # Build UI
        self.build_ui()

        # Setup auto-close
        self.setup_auto_close()

    def center_dialog(self):
        """Center dialog relative to parent window"""
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))

    def build_ui(self):
        """Build dialog UI"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Format scan date
        scan_date = self.existing_record.get('scan_date')
        if scan_date:
            try:
                formatted_date = scan_date.strftime(constants.DATETIME_FORMAT)
            except AttributeError:
                # If scan_date is already a string
                formatted_date = str(scan_date)
        else:
            formatted_date = "ไม่ทราบ"

        # Warning message with details
        warning_text = f"⚠️ ไม่อนุญาตให้สแกนซ้ำ ⚠️\n\n"
        warning_text += f"เลขพัสดุ: {self.barcode}\n"
        warning_text += f"ประเภทงานหลัก: {self.job_type}\n"
        warning_text += f"ประเภทงานย่อย: {self.sub_job_type}\n"
        warning_text += f"สแกนไปแล้วเมื่อ: {formatted_date}\n"
        warning_text += f"โดยผู้ใช้: {self.existing_record.get('user_id', 'ไม่ทราบ')}\n\n"
        warning_text += "กรุณาตรวจสอบเลขพัสดุอีกครั้ง"

        message_label = ttk.Label(
            main_frame,
            text=warning_text,
            justify=tk.CENTER,
            font=constants.FONT_REGULAR_SMALL
        )
        message_label.pack(pady=20)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        # Close button
        close_btn = ttk.Button(
            button_frame,
            text="ปิด (Enter)",
            command=self.close
        )
        close_btn.pack()
        close_btn.focus_set()  # Set focus for Enter key

        # Bind keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self.close())
        self.dialog.bind('<Escape>', lambda e: self.close())

    def setup_auto_close(self):
        """Setup auto-close after 3 seconds"""
        self.dialog.after(constants.DUPLICATE_WARNING_AUTO_CLOSE_MS, self.close)

        # Setup close callback
        self.dialog.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        """Close the dialog"""
        try:
            self.dialog.destroy()
        except:
            pass  # Dialog already destroyed

        # Execute callback if provided
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except:
                pass

    def show(self):
        """Show the dialog and wait for it to close"""
        self.parent.wait_window(self.dialog)
