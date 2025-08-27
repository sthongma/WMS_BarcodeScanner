#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager
Centralizes configuration management for the WMS application
"""

import json
import os
import logging
from typing import Dict, Any, Optional


class ConfigManager:
    """จัดการการตั้งค่าของแอปพลิเคชัน"""
    
    def __init__(self):
        self.config_file = "config/sql_config.json"
        self._config_cache = None
        self.logger = logging.getLogger(__name__)
    
    def load_database_config(self) -> Optional[Dict[str, Any]]:
        """โหลดการตั้งค่าฐานข้อมูล"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # ตรวจสอบว่ามีข้อมูลที่จำเป็นครบหรือไม่
                required_fields = ['server', 'database']
                for field in required_fields:
                    if field not in config:
                        self.logger.error(f"ERROR: Missing field {field} in config file")
                        return None
                
                self._config_cache = config
                self.logger.info(f"OK: Config loaded successfully {config['server']}/{config['database']}")
                return config
            else:
                self.logger.warning(f"WARNING: Config file not found {self.config_file}")
                return None
        except Exception as e:
            self.logger.error(f"ERROR: Error loading config {e}")
            return None
    
    def create_connection_string(self, config: Dict[str, Any]) -> Optional[str]:
        """สร้าง connection string จาก config"""
        try:
            server = config.get('server', '')
            database = config.get('database', '')
            auth_type = config.get('auth_type', 'SQL')
            
            if auth_type == 'Windows':
                return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
            else:
                username = config.get('username', '')
                password = config.get('password', '')
                return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        except Exception as e:
            self.logger.error(f"ERROR: Error creating connection string {e}")
            return None
    
    def get_app_config(self) -> Dict[str, Any]:
        """ดึงการตั้งค่าแอปพลิเคชัน"""
        return {
            'app_name': 'WMS Barcode Scanner',
            'version': '1.0.0',
            'debug': os.environ.get('FLASK_ENV') != 'production',
            'host': '0.0.0.0',
            'port': int(os.environ.get('PORT', 5000)),
            'secret_key': 'wms_scanner_secret_key_2024',
            'session_timeout_hours': 8
        }
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """ดึงการตั้งค่า rate limiting"""
        return {
            'default': {'max_requests': 200, 'per_seconds': 60},
            'login': {'max_requests': 20, 'per_seconds': 60},
            'init': {'max_requests': 50, 'per_seconds': 60},
            'scan': {'max_requests': 120, 'per_seconds': 60},
            'api': {'max_requests': 100, 'per_seconds': 60},
            'report': {'max_requests': 50, 'per_seconds': 60}
        }
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """บันทึกการตั้งค่า"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self._config_cache = config
            return True
        except Exception as e:
            self.logger.error(f"ERROR: Error saving config {e}")
            return False
    
    def get_cached_config(self) -> Optional[Dict[str, Any]]:
        """ดึง config ที่ cache ไว้"""
        if self._config_cache is None:
            return self.load_database_config()
        return self._config_cache
    
    def create_connection_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """สร้าง connection info object"""
        connection_string = self.create_connection_string(config)
        return {
            'config': config,
            'connection_string': connection_string,
            'current_user': config.get('username', 'system')
        }


# Global instance
config_manager = ConfigManager()