#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Barcode Generator GUI
Simple standalone GUI for generating random barcodes with configurable settings
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import random
from datetime import datetime
import pyperclip
import pyautogui


class BarcodeGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📦 Barcode Generator - Standalone Tool")
        self.root.geometry("600x500")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.is_running = False
        self.generator_thread = None
        self.stats = {'generated': 0}
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="📦 Random Barcode Generator", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=15)
        
        # Settings frame
        settings_frame = tk.LabelFrame(self.root, text="⚙️ Generator Settings", 
                                      bg='#f0f0f0', font=('Arial', 10, 'bold'))
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        # Count setting
        count_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        count_frame.pack(fill='x', padx=10, pady=8)
        tk.Label(count_frame, text="จำนวนบาร์โค้ด:", bg='#f0f0f0', width=15, anchor='w', font=('Arial', 10)).pack(side='left')
        self.count_var = tk.StringVar(value="10")
        count_spin = tk.Spinbox(count_frame, from_=1, to=1000, textvariable=self.count_var, width=10, font=('Arial', 10))
        count_spin.pack(side='left', padx=5)
        
        # Interval setting
        interval_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        interval_frame.pack(fill='x', padx=10, pady=8)
        tk.Label(interval_frame, text="ช่วงเวลา (ms):", bg='#f0f0f0', width=15, anchor='w', font=('Arial', 10)).pack(side='left')
        self.interval_var = tk.StringVar(value="500")
        interval_spin = tk.Spinbox(interval_frame, from_=10, to=5000, textvariable=self.interval_var, width=10, font=('Arial', 10))
        interval_spin.pack(side='left', padx=5)
        
        # Speed info
        speed_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        speed_frame.pack(fill='x', padx=10, pady=8)
        tk.Label(speed_frame, text="ความเร็ว:", bg='#f0f0f0', width=15, anchor='w', font=('Arial', 10)).pack(side='left')
        self.speed_label = tk.Label(speed_frame, text="2.0 codes/second", bg='#f0f0f0', fg='#666', font=('Arial', 10))
        self.speed_label.pack(side='left')
        
        # Update speed calculation when interval changes
        self.interval_var.trace('w', self.update_speed_label)
        
        # Barcode format settings
        format_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        format_frame.pack(fill='x', padx=10, pady=8)
        tk.Label(format_frame, text="รูปแบบบาร์โค้ด:", bg='#f0f0f0', width=15, anchor='w', font=('Arial', 10)).pack(side='left')
        
        self.format_var = tk.StringVar(value="random_16")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, width=20, font=('Arial', 10))
        format_combo['values'] = (
            'random_16',        # 16 digit random
            'random_13',        # 13 digit random  
            'sequential_16',    # 16 digit sequential
            'sequential_13',    # 13 digit sequential
            'timestamp_based'   # based on timestamp
        )
        format_combo.pack(side='left', padx=5)
        
        # Start delay setting
        delay_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        delay_frame.pack(fill='x', padx=10, pady=8)
        tk.Label(delay_frame, text="หน่วงเวลาเริ่มต้น (วินาที):", bg='#f0f0f0', width=18, anchor='w', font=('Arial', 10)).pack(side='left')
        self.start_delay_var = tk.StringVar(value="3")
        delay_spin = tk.Spinbox(delay_frame, from_=0, to=10, textvariable=self.start_delay_var, width=10, font=('Arial', 10))
        delay_spin.pack(side='left', padx=5)
        tk.Label(delay_frame, text="(เวลาให้คลิกช่องพิมพ์)", bg='#f0f0f0', fg='#888', font=('Arial', 9)).pack(side='left', padx=(10,0))
        
        # Auto typing option
        typing_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        typing_frame.pack(fill='x', padx=10, pady=8)
        self.auto_type_var = tk.BooleanVar(value=True)
        auto_type_check = tk.Checkbutton(typing_frame, text="พิมพ์บาร์โค้ดอัตโนมัติ (ลงในช่องที่คลิก)", 
                                    variable=self.auto_type_var, bg='#f0f0f0', font=('Arial', 10))
        auto_type_check.pack(side='left')
        
        # Enter after typing option
        enter_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        enter_frame.pack(fill='x', padx=10, pady=8)
        self.auto_enter_var = tk.BooleanVar(value=True)
        auto_enter_check = tk.Checkbutton(enter_frame, text="กด Enter หลังพิมพ์แต่ละบาร์โค้ด", 
                                     variable=self.auto_enter_var, bg='#f0f0f0', font=('Arial', 10))
        auto_enter_check.pack(side='left')
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(fill='x', padx=20, pady=15)
        
        self.start_btn = tk.Button(control_frame, text="▶️ Start Generate", 
                                  command=self.start_generation, bg='#28a745', fg='white',
                                  font=('Arial', 12, 'bold'), width=15)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Stop", 
                                 command=self.stop_generation, bg='#dc3545', fg='white',
                                 font=('Arial', 12, 'bold'), width=15, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        self.clear_btn = tk.Button(control_frame, text="🗑️ Clear", 
                                  command=self.clear_output, bg='#6c757d', fg='white',
                                  font=('Arial', 12, 'bold'), width=15)
        self.clear_btn.pack(side='left', padx=5)
        
        # Stats frame
        stats_frame = tk.Frame(self.root, bg='#f0f0f0')
        stats_frame.pack(fill='x', padx=20, pady=5)
        
        self.stats_label = tk.Label(stats_frame, text="พร้อมสร้างบาร์โค้ด...", 
                                   bg='#f0f0f0', font=('Arial', 11, 'bold'), fg='#333')
        self.stats_label.pack()
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(stats_frame, variable=self.progress_var, 
                                       maximum=100, length=500)
        self.progress.pack(pady=5)
        
        # Output frame
        output_frame = tk.LabelFrame(self.root, text="📋 Generated Barcodes", 
                                    bg='#f0f0f0', font=('Arial', 10, 'bold'))
        output_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Output text with copy functionality
        text_frame = tk.Frame(output_frame, bg='#f0f0f0')
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(text_frame, height=12, font=('Consolas', 10))
        self.output_text.pack(side='left', fill='both', expand=True)
        
        # Copy button frame
        copy_frame = tk.Frame(text_frame, bg='#f0f0f0')
        copy_frame.pack(side='right', fill='y', padx=(5, 0))
        
        copy_all_btn = tk.Button(copy_frame, text="📋\nCopy All", 
                               command=self.copy_all_barcodes, bg='#17a2b8', fg='white',
                               font=('Arial', 9, 'bold'), width=8)
        copy_all_btn.pack(pady=5)
        
        copy_last_btn = tk.Button(copy_frame, text="📄\nCopy Last", 
                                command=self.copy_last_barcode, bg='#ffc107', fg='black',
                                font=('Arial', 9, 'bold'), width=8)
        copy_last_btn.pack(pady=5)
        
        # Configure text tags for colored output
        self.output_text.tag_config('barcode', foreground='#0066cc', font=('Consolas', 11, 'bold'))
        self.output_text.tag_config('info', foreground='#666666')
        self.output_text.tag_config('counter', foreground='#28a745', font=('Consolas', 10, 'bold'))
        self.output_text.tag_config('success', foreground='#28a745')
        self.output_text.tag_config('error', foreground='#dc3545')
        
        # Variables for sequential mode
        self.sequential_counter = 1000000000000000  # 16-digit start
        self.sequential_counter_13 = 1000000000000  # 13-digit start
        self.all_generated_barcodes = []
    
    def update_speed_label(self, *args):
        try:
            interval = int(self.interval_var.get())
            speed = round(1000 / interval, 1)
            self.speed_label.config(text=f"{speed} codes/second")
        except:
            self.speed_label.config(text="Invalid interval")
    
    def generate_barcode(self, format_type):
        """Generate barcode based on format type"""
        if format_type == "random_16":
            return str(random.randint(1000000000000000, 9999999999999999))
        elif format_type == "random_13":
            return str(random.randint(1000000000000, 9999999999999))
        elif format_type == "sequential_16":
            barcode = str(self.sequential_counter)
            self.sequential_counter += 1
            return barcode
        elif format_type == "sequential_13":
            barcode = str(self.sequential_counter_13)
            self.sequential_counter_13 += 1
            return barcode
        elif format_type == "timestamp_based":
            timestamp = str(int(time.time() * 1000))[-13:]  # Last 13 digits of timestamp
            random_suffix = str(random.randint(100, 999))
            return timestamp + random_suffix
        else:
            return str(random.randint(1000000000000000, 9999999999999999))
    
    def output_barcode(self, barcode, counter):
        """Output barcode to text widget and optionally type it"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Auto type the barcode if enabled
        if self.auto_type_var.get():
            try:
                # Type the barcode
                pyautogui.write(barcode)
                
                # Press Enter if enabled
                if self.auto_enter_var.get():
                    pyautogui.press('enter')
                
                # Add to display with typing indicator
                self.output_text.insert(tk.END, f"[{counter:04d}] ", 'counter')
                self.output_text.insert(tk.END, f"{timestamp} - ", 'info')
                self.output_text.insert(tk.END, f"{barcode} ", 'barcode')
                self.output_text.insert(tk.END, "✅ พิมพ์แล้ว\n", 'success')
                
            except Exception as e:
                # Add to display with error indicator
                self.output_text.insert(tk.END, f"[{counter:04d}] ", 'counter')
                self.output_text.insert(tk.END, f"{timestamp} - ", 'info')
                self.output_text.insert(tk.END, f"{barcode} ", 'barcode')
                self.output_text.insert(tk.END, f"❌ พิมพ์ไม่ได้: {str(e)}\n", 'error')
        else:
            # Just display without typing
            self.output_text.insert(tk.END, f"[{counter:04d}] ", 'counter')
            self.output_text.insert(tk.END, f"{timestamp} - ", 'info')
            self.output_text.insert(tk.END, f"{barcode}\n", 'barcode')
        
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
        # Store for copying
        self.all_generated_barcodes.append(barcode)
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.stats = {'generated': 0}
        self.all_generated_barcodes = []
        self.update_stats_display()
        self.progress_var.set(0)
        
        # Add welcome message
        welcome_msg = "✨ Ready to generate barcodes!\n"
        welcome_msg += "Choose your settings and click 'Start Generate'\n"
        welcome_msg += "=" * 50 + "\n"
        self.output_text.insert(tk.END, welcome_msg, 'info')
    
    def update_stats_display(self):
        generated = self.stats['generated']
        self.stats_label.config(text=f"สร้างบาร์โค้ดแล้ว: {generated} รายการ")
    
    def copy_all_barcodes(self):
        if self.all_generated_barcodes:
            clipboard_text = '\n'.join(self.all_generated_barcodes)
            try:
                pyperclip.copy(clipboard_text)
                self.output_text.insert(tk.END, f"\n✅ Copied {len(self.all_generated_barcodes)} barcodes to clipboard!\n", 'info')
            except:
                # Fallback to tkinter clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(clipboard_text)
                self.output_text.insert(tk.END, f"\n✅ Copied {len(self.all_generated_barcodes)} barcodes to clipboard!\n", 'info')
            self.output_text.see(tk.END)
    
    def copy_last_barcode(self):
        if self.all_generated_barcodes:
            last_barcode = self.all_generated_barcodes[-1]
            try:
                pyperclip.copy(last_barcode)
                self.output_text.insert(tk.END, f"\n📄 Copied last barcode: {last_barcode}\n", 'info')
            except:
                # Fallback to tkinter clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(last_barcode)
                self.output_text.insert(tk.END, f"\n📄 Copied last barcode: {last_barcode}\n", 'info')
            self.output_text.see(tk.END)
    
    def start_generation(self):
        if self.is_running:
            return
        
        try:
            count = int(self.count_var.get())
            interval = int(self.interval_var.get())
            start_delay = int(self.start_delay_var.get())
        except ValueError:
            tk.messagebox.showerror("Input Error", "กรุณาป้อนตัวเลขที่ถูกต้อง")
            return
        
        if count <= 0 or interval <= 0:
            tk.messagebox.showerror("Input Error", "ค่าต้องมากกว่า 0")
            return
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        # Reset stats
        self.stats = {'generated': 0}
        self.progress_var.set(0)
        
        format_type = self.format_var.get()
        speed = round(1000 / interval, 1)
        
        # Add start message with countdown
        start_msg = f"\n🚀 เตรียมสร้างบาร์โค้ด: {count} รายการ\n"
        start_msg += f"📊 ความเร็ว: {speed} codes/second\n"
        start_msg += f"📋 รูปแบบ: {format_type}\n"
        if start_delay > 0:
            start_msg += f"⏰ หน่วงเวลา: {start_delay} วินาที (เวลาสำหรับคลิกช่องพิมพ์)\n"
        start_msg += "=" * 50 + "\n"
        self.output_text.insert(tk.END, start_msg, 'info')
        self.output_text.see(tk.END)
        
        # Start generation in separate thread with delay
        self.generator_thread = threading.Thread(
            target=self.run_generation_with_delay,
            args=(count, interval, format_type, start_delay)
        )
        self.generator_thread.daemon = True
        self.generator_thread.start()
    
    def stop_generation(self):
        if self.is_running:
            self.is_running = False
            self.output_text.insert(tk.END, "\n⏹️ การสร้างบาร์โค้ดถูกหยุดโดยผู้ใช้\n", 'info')
            self.output_text.see(tk.END)
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
    
    def run_generation_with_delay(self, count, interval, format_type, start_delay):
        """Run generation with initial countdown delay"""
        # Countdown delay
        if start_delay > 0:
            for i in range(start_delay, 0, -1):
                if not self.is_running:
                    return
                
                countdown_msg = f"⏰ เริ่มใน {i} วินาที... (คลิกช่องพิมพ์ได้แล้ว!)\n"
                self.output_text.insert(tk.END, countdown_msg, 'info')
                self.output_text.see(tk.END)
                time.sleep(1)
            
            if not self.is_running:
                return
            
            # Start message
            self.output_text.insert(tk.END, "🚀 เริ่มสร้างบาร์โค้ด!\n\n", 'info')
            self.output_text.see(tk.END)
        
        # Run the actual generation
        self.run_generation(count, interval, format_type)
    
    def run_generation(self, count, interval, format_type):
        interval_seconds = interval / 1000.0
        
        for i in range(count):
            if not self.is_running:
                break
            
            # Generate barcode
            barcode = self.generate_barcode(format_type)
            self.stats['generated'] += 1
            
            # Output barcode
            self.output_barcode(barcode, i + 1)
            
            # Update progress and stats
            progress = ((i + 1) / count) * 100
            self.progress_var.set(progress)
            self.update_stats_display()
            
            # Wait before next generation
            if i < count - 1 and self.is_running:
                time.sleep(interval_seconds)
        
        # Generation completed
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        completion_msg = f"\n🏁 เสร็จสิ้น! สร้างบาร์โค้ดทั้งหมด: {self.stats['generated']} รายการ\n"
        completion_msg += f"⏰ เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        completion_msg += "=" * 50 + "\n"
        self.output_text.insert(tk.END, completion_msg, 'info')
        self.output_text.see(tk.END)


def main():
    # Check if required modules are available
    try:
        import pyperclip
    except ImportError:
        print("Note: pyperclip not installed. Using tkinter clipboard fallback.")
        import sys
        class MockPyperclip:
            @staticmethod
            def copy(text):
                raise ImportError("pyperclip not available")
        sys.modules['pyperclip'] = MockPyperclip()
        import pyperclip
    
    try:
        import pyautogui
        # Set pyautogui safety settings
        pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort
        pyautogui.PAUSE = 0.1  # Small pause between actions
    except ImportError:
        print("Error: pyautogui is required for auto-typing functionality.")
        print("Please install it with: pip install pyautogui")
        return
    
    root = tk.Tk()
    app = BarcodeGeneratorGUI(root)
    
    # Initialize with welcome message
    app.clear_output()
    
    root.mainloop()


if __name__ == "__main__":
    main()