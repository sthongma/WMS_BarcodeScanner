#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sound Manager
จัดการระบบเสียงสำหรับ Desktop Application (Tkinter)
"""

import os
import threading
from typing import Optional, Dict, Any
from pathlib import Path


class SoundManager:
    """
    จัดการระบบเสียงสำหรับ Desktop App
    รองรับการเล่นเสียงผ่าน pygame.mixer
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern - มี instance เดียวในระบบ"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize sound manager"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.pygame_available = False
            self.mixer = None
            self.current_sound = None
            self.sound_enabled = True
            self.default_volume = 0.8

            # พยายาม import pygame
            self._init_pygame()

    def _init_pygame(self):
        """Initialize pygame mixer"""
        try:
            import pygame
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.pygame_available = True
            self.mixer = pygame.mixer
            print("✅ Sound Manager: pygame.mixer initialized successfully")
        except ImportError:
            print("⚠️ Sound Manager: pygame not installed. Sound will be disabled.")
            print("   To enable sound, run: pip install pygame")
            self.pygame_available = False
        except Exception as e:
            print(f"⚠️ Sound Manager: Failed to initialize pygame.mixer: {e}")
            self.pygame_available = False

    def play_sound(self, sound_obj: Optional[Dict[str, Any]]) -> bool:
        """
        เล่นเสียงจาก sound object ที่ได้จาก SoundService

        Args:
            sound_obj: Dict containing sound_file, volume, is_enabled

        Returns:
            bool: True if sound played successfully, False otherwise
        """
        if not self.pygame_available or not self.sound_enabled:
            return False

        if not sound_obj or not sound_obj.get('sound_file') or not sound_obj.get('is_enabled'):
            return False

        sound_file = sound_obj.get('sound_file', '')
        volume = sound_obj.get('volume', self.default_volume)

        return self.play_sound_file(sound_file, volume)

    def play_sound_file(self, sound_path: str, volume: float = None) -> bool:
        """
        เล่นเสียงจากไฟล์โดยตรง

        Args:
            sound_path: path ของไฟล์เสียง (เช่น /static/sounds/success.mp3)
            volume: ระดับเสียง (0.0-1.0)

        Returns:
            bool: True if sound played successfully, False otherwise
        """
        if not self.pygame_available or not self.sound_enabled:
            return False

        try:
            # แปลง web path เป็น file path
            file_path = self._convert_web_path_to_file(sound_path)

            if not os.path.exists(file_path):
                print(f"⚠️ Sound file not found: {file_path}")
                return False

            # หยุดเสียงเดิม (ถ้ามี)
            if self.current_sound:
                self.current_sound.stop()

            # โหลดและเล่นเสียง
            self.current_sound = self.mixer.Sound(file_path)

            # ตั้งค่า volume
            if volume is None:
                volume = self.default_volume
            volume = max(0.0, min(1.0, volume))  # clamp to 0.0-1.0
            self.current_sound.set_volume(volume)

            # เล่นเสียง
            self.current_sound.play()

            return True

        except Exception as e:
            print(f"❌ Error playing sound: {e}")
            return False

    def _convert_web_path_to_file(self, web_path: str) -> str:
        """
        แปลง web path เป็น file path
        เช่น /static/sounds/success.mp3 -> C:/path/to/project/static/sounds/success.mp3

        Args:
            web_path: path แบบ web (เช่น /static/sounds/success.mp3)

        Returns:
            str: absolute file path
        """
        # ลบ leading slash
        if web_path.startswith('/'):
            web_path = web_path[1:]

        # แปลง forward slash เป็น path separator ของ OS
        web_path = web_path.replace('/', os.sep)

        # หา project root (ตำแหน่งที่มี static folder)
        current_dir = Path(__file__).resolve().parent.parent.parent
        file_path = current_dir / web_path

        return str(file_path)

    def play_success_sound(self, sound_obj: Optional[Dict[str, Any]] = None) -> bool:
        """เล่นเสียง success"""
        return self.play_sound(sound_obj)

    def play_error_sound(self, sound_obj: Optional[Dict[str, Any]] = None) -> bool:
        """เล่นเสียง error"""
        return self.play_sound(sound_obj)

    def play_duplicate_sound(self, sound_obj: Optional[Dict[str, Any]] = None) -> bool:
        """เล่นเสียง duplicate"""
        return self.play_sound(sound_obj)

    def play_warning_sound(self, sound_obj: Optional[Dict[str, Any]] = None) -> bool:
        """เล่นเสียง warning"""
        return self.play_sound(sound_obj)

    def stop(self):
        """หยุดเสียงที่กำลังเล่นอยู่"""
        if self.pygame_available and self.current_sound:
            try:
                self.current_sound.stop()
            except Exception as e:
                print(f"Error stopping sound: {e}")

    def set_enabled(self, enabled: bool):
        """เปิด/ปิดเสียงทั้งหมด"""
        self.sound_enabled = enabled
        if not enabled:
            self.stop()

    def is_enabled(self) -> bool:
        """ตรวจสอบว่าเสียงเปิดอยู่หรือไม่"""
        return self.sound_enabled

    def set_volume(self, volume: float):
        """ตั้งค่า default volume"""
        self.default_volume = max(0.0, min(1.0, volume))

    def is_available(self) -> bool:
        """ตรวจสอบว่าระบบเสียงพร้อมใช้งานหรือไม่"""
        return self.pygame_available

    def test_sound(self, sound_path: str) -> bool:
        """
        ทดสอบเสียง

        Args:
            sound_path: path ของไฟล์เสียงที่ต้องการทดสอบ

        Returns:
            bool: True if test successful
        """
        return self.play_sound_file(sound_path, self.default_volume)


# Global instance
_sound_manager = None


def get_sound_manager() -> SoundManager:
    """
    ดึง SoundManager instance (Singleton)

    Returns:
        SoundManager: sound manager instance
    """
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager
