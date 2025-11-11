#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Dialog Components
Modal and Toast notification dialogs for displaying popup notifications
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class ModalNotificationDialog(tk.Toplevel):
    """Modal dialog สำหรับแสดงแจ้งเตือนแบบ modal (ต้องกดปิด)"""

    # สี/ไอคอนสำหรับแต่ละ event_type
    EVENT_COLORS = {
        'success': {'bg': '#d4edda', 'fg': '#155724', 'icon': '✓', 'border': '#c3e6cb'},
        'error': {'bg': '#f8d7da', 'fg': '#721c24', 'icon': '✗', 'border': '#f5c6cb'},
        'duplicate': {'bg': '#fff3cd', 'fg': '#856404', 'icon': '⚠', 'border': '#ffeaa7'},
        'warning': {'bg': '#fff3cd', 'fg': '#856404', 'icon': '⚠', 'border': '#ffeaa7'},
        'info': {'bg': '#d1ecf1', 'fg': '#0c5460', 'icon': 'ℹ', 'border': '#bee5eb'}
    }

    def __init__(self, parent, notification: Dict[str, Any]):
        super().__init__(parent)

        self.notification = notification
        self.event_type = notification.get('event_type', 'info')

        # Configure window
        self.title("แจ้งเตือน")
        self.transient(parent)
        self.grab_set()

        # Remove window decorations for custom style
        self.overrideredirect(False)

        # Get colors for event type
        colors = self.EVENT_COLORS.get(self.event_type, self.EVENT_COLORS['info'])

        # Configure window size and position
        window_width = 500
        window_height = 250
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Main container with border
        main_frame = tk.Frame(self, bg=colors['border'], padx=3, pady=3)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Content frame
        content_frame = tk.Frame(main_frame, bg=colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Icon and title frame
        header_frame = tk.Frame(content_frame, bg=colors['bg'])
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        # Icon
        icon_label = tk.Label(
            header_frame,
            text=colors['icon'],
            font=('Arial', 36, 'bold'),
            fg=colors['fg'],
            bg=colors['bg']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 15))

        # Title and Barcode container
        title_container = tk.Frame(header_frame, bg=colors['bg'])
        title_container.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Barcode (if available)
        if notification.get('barcode'):
            barcode_label = tk.Label(
                title_container,
                text=f"Barcode: {notification.get('barcode')}",
                font=('Courier New', 13, 'bold'),
                fg=colors['fg'],
                bg=colors['bg'],
                anchor=tk.W
            )
            barcode_label.pack(fill=tk.X)

        # Title
        title_label = tk.Label(
            title_container,
            text=notification.get('title', 'แจ้งเตือน'),
            font=('Arial', 16, 'bold'),
            fg=colors['fg'],
            bg=colors['bg'],
            anchor=tk.W
        )
        title_label.pack(fill=tk.X, pady=(5, 0) if notification.get('barcode') else (0, 0))

        # Message frame with scrollbar
        message_frame = tk.Frame(content_frame, bg=colors['bg'])
        message_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Message text with scrollbar
        text_frame = tk.Frame(message_frame, bg=colors['bg'])
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        message_text = tk.Text(
            text_frame,
            font=('Arial', 12),
            fg=colors['fg'],
            bg=colors['bg'],
            wrap=tk.WORD,
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set,
            height=4
        )
        message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=message_text.yview)

        # Insert message
        message_text.insert('1.0', notification.get('message', ''))
        message_text.config(state=tk.DISABLED)

        # Button frame
        button_frame = tk.Frame(content_frame, bg=colors['bg'])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Close button
        close_btn = tk.Button(
            button_frame,
            text="ตรวจสอบแล้ว",
            font=('Arial', 11, 'bold'),
            bg=colors['fg'],
            fg='white',
            activebackground=colors['border'],
            activeforeground=colors['fg'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=10,
            command=self.close_dialog
        )
        close_btn.pack(side=tk.RIGHT)

        # Bind ESC key to close
        self.bind('<Escape>', lambda e: self.close_dialog())

        # Focus on button
        close_btn.focus_set()

    def close_dialog(self):
        """ปิด dialog"""
        self.grab_release()
        self.destroy()


class ToastNotification(tk.Toplevel):
    """Toast notification สำหรับแสดงแจ้งเตือนแบบ toast (หายอัตโนมัติ)"""

    # สี/ไอคอนสำหรับแต่ละ event_type
    EVENT_COLORS = {
        'success': {'bg': '#28a745', 'fg': 'white', 'icon': '✓'},
        'error': {'bg': '#dc3545', 'fg': 'white', 'icon': '✗'},
        'duplicate': {'bg': '#ffc107', 'fg': '#212529', 'icon': '⚠'},
        'warning': {'bg': '#ffc107', 'fg': '#212529', 'icon': '⚠'},
        'info': {'bg': '#17a2b8', 'fg': 'white', 'icon': 'ℹ'}
    }

    def __init__(self, parent, notification: Dict[str, Any], duration: int = 5000):
        super().__init__(parent)

        self.notification = notification
        self.event_type = notification.get('event_type', 'info')
        self.duration = duration
        self.closing = False

        # Configure window
        self.overrideredirect(True)

        # Get colors for event type
        colors = self.EVENT_COLORS.get(self.event_type, self.EVENT_COLORS['info'])

        # Configure window size and position (bottom-right corner)
        window_width = 400
        window_height = 120
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = screen_width - window_width - 20
        y = screen_height - window_height - 60
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Configure transparency (if supported)
        try:
            self.attributes('-alpha', 0.95)
        except:
            pass

        # Main frame with shadow effect
        main_frame = tk.Frame(self, bg='#2c3e50', padx=2, pady=2)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Content frame
        content_frame = tk.Frame(main_frame, bg=colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Header frame (icon + title + barcode)
        header_frame = tk.Frame(content_frame, bg=colors['bg'])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 5))

        # Icon
        icon_label = tk.Label(
            header_frame,
            text=colors['icon'],
            font=('Arial', 20, 'bold'),
            fg=colors['fg'],
            bg=colors['bg']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # Title and Barcode container
        title_container = tk.Frame(header_frame, bg=colors['bg'])
        title_container.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Barcode (if available)
        if notification.get('barcode'):
            barcode_label = tk.Label(
                title_container,
                text=f"Barcode: {notification.get('barcode')}",
                font=('Courier New', 10, 'bold'),
                fg=colors['fg'],
                bg=colors['bg'],
                anchor=tk.W
            )
            barcode_label.pack(fill=tk.X)

        # Title
        title_label = tk.Label(
            title_container,
            text=notification.get('title', 'แจ้งเตือน'),
            font=('Arial', 12, 'bold'),
            fg=colors['fg'],
            bg=colors['bg'],
            anchor=tk.W
        )
        title_label.pack(fill=tk.X, pady=(3, 0) if notification.get('barcode') else (0, 0))

        # Message
        message_label = tk.Label(
            content_frame,
            text=notification.get('message', '')[:150] + ('...' if len(notification.get('message', '')) > 150 else ''),
            font=('Arial', 10),
            fg=colors['fg'],
            bg=colors['bg'],
            wraplength=360,
            justify=tk.LEFT,
            anchor=tk.W
        )
        message_label.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Progress bar (countdown)
        self.progress_frame = tk.Frame(content_frame, bg=colors['fg'], height=3)
        self.progress_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.progress_bar = tk.Frame(self.progress_frame, bg='white', height=3)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.Y)

        # Bind click to close
        content_frame.bind('<Button-1>', lambda e: self.close_toast())

        # Slide in animation
        self.slide_in()

        # Auto close after duration
        if duration > 0:
            self.animate_progress()

    def slide_in(self):
        """Animation slide in จากขวา"""
        screen_width = self.winfo_screenwidth()
        start_x = screen_width
        end_x = screen_width - 400 - 20

        def animate(current_x):
            if current_x > end_x:
                next_x = current_x - 20
                self.geometry(f"400x120+{next_x}+{self.winfo_y()}")
                self.after(10, lambda: animate(next_x))

        self.geometry(f"400x120+{start_x}+{self.winfo_y()}")
        animate(start_x)

    def animate_progress(self):
        """Animation progress bar countdown"""
        steps = 100
        step_duration = self.duration // steps
        current_width = 400

        def update_progress(step):
            if step > 0 and not self.closing:
                width = int((step / steps) * 400)
                self.progress_bar.config(width=width)
                self.after(step_duration, lambda: update_progress(step - 1))
            elif not self.closing:
                self.close_toast()

        update_progress(steps)

    def close_toast(self):
        """ปิด toast notification"""
        if self.closing:
            return

        self.closing = True

        # Slide out animation
        def slide_out(current_x):
            if current_x < self.winfo_screenwidth():
                next_x = current_x + 20
                try:
                    self.geometry(f"400x120+{next_x}+{self.winfo_y()}")
                    self.after(10, lambda: slide_out(next_x))
                except:
                    self.destroy()
            else:
                self.destroy()

        slide_out(self.winfo_x())


def show_notification(parent, notification: Dict[str, Any], popup_type: str = None):
    """
    แสดง notification popup ตามประเภท

    Args:
        parent: parent window
        notification: notification dict ที่มี title, message, event_type, popup_type
        popup_type: บังคับประเภท popup ('modal' หรือ 'toast'), ถ้าไม่ระบุจะใช้ค่าจาก notification
    """
    if not popup_type:
        popup_type = notification.get('popup_type', 'toast')

    if popup_type == 'modal':
        dialog = ModalNotificationDialog(parent, notification)
    else:
        dialog = ToastNotification(parent, notification)

    return dialog
