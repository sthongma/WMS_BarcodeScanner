#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tab Configuration Loader
อ่านการตั้งค่าการแสดงแท็บจากไฟล์ JSON
"""

import json
import os
import logging

logger = logging.getLogger(__name__)


class TabConfigLoader:
    """คลาสง่ายๆ สำหรับอ่านการตั้งค่าแท็บจากไฟล์ JSON"""
    
    def __init__(self, config_path=None):
        """
        Initialize TabConfigLoader
        
        Args:
            config_path (str, optional): Path to config file. 
                                       Defaults to 'config/tab_settings.json'
        """
        if config_path is None:
            # Default path relative to project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(project_root, 'config', 'tab_settings.json')
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """โหลดการตั้งค่าจากไฟล์ JSON"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Config file not found: {self.config_path}. Creating default config.")
                return self._create_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
                logger.info(f"Loaded tab config from: {self.config_path}")
                return config
                
        except Exception as e:
            logger.error(f"Error loading tab config: {str(e)}. Using default config.")
            return self._create_default_config()
    
    def _create_default_config(self):
        """สร้างการตั้งค่าเริ่มต้น"""
        default_config = {
            "tabs": {
                "tabs_scan": True,
                "tabs_history": True,
                "tabs_reports": True,
                "tabs_import": False,
                "tabs_settings": True,
                "tabs_sub_job_settings": False
            },
            "tab_names": {
                "tabs_scan": "หน้าจอหลัก",
                "tabs_history": "ประวัติ",
                "tabs_reports": "รายงาน",
                "tabs_import": "นำเข้าข้อมูล",
                "tabs_settings": "จัดการประเภทงานหลัก",
                "tabs_sub_job_settings": "จัดการประเภทงานย่อย"
            },
            "metadata": {
                "version": "1.0.0",
                "description": "การตั้งค่าการแสดงแท็บต่างๆ ในระบบ WMS Barcode Scanner"
            }
        }
        
        # Save default config to file
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config):
        """บันทึกการตั้งค่าลงไฟล์"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=2, ensure_ascii=False)
            
            logger.info(f"Tab config saved to: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving tab config: {str(e)}")
    
    def is_tab_enabled(self, tab_name):
        """
        ตรวจสอบว่าแท็บนั้นควรแสดงหรือไม่
        
        Args:
            tab_name (str): ชื่อแท็บ เช่น 'tabs_scan', 'tabs_history'
            
        Returns:
            bool: True ถ้าควรแสดง, False ถ้าไม่ควรแสดง
        """
        try:
            return self.config.get("tabs", {}).get(tab_name, True)
        except Exception as e:
            logger.error(f"Error checking tab status for {tab_name}: {str(e)}")
            return True  # Default to enabled if error
    
    def get_tab_name(self, tab_key):
        """
        ได้รับชื่อที่แสดงของแท็บ
        
        Args:
            tab_key (str): คีย์ของแท็บ เช่น 'tabs_scan'
            
        Returns:
            str: ชื่อที่แสดงของแท็บ
        """
        try:
            return self.config.get("tab_names", {}).get(tab_key, tab_key)
        except Exception as e:
            logger.error(f"Error getting tab name for {tab_key}: {str(e)}")
            return tab_key
    
    def get_all_enabled_tabs(self):
        """
        ได้รับรายการแท็บทั้งหมดที่เปิดใช้งาน
        
        Returns:
            list: รายการ tuple ของ (tab_key, tab_name) ที่เปิดใช้งาน
        """
        enabled_tabs = []
        try:
            tabs = self.config.get("tabs", {})
            tab_names = self.config.get("tab_names", {})
            
            for tab_key, enabled in tabs.items():
                if enabled:
                    tab_name = tab_names.get(tab_key, tab_key)
                    enabled_tabs.append((tab_key, tab_name))
            
            return enabled_tabs
        except Exception as e:
            logger.error(f"Error getting enabled tabs: {str(e)}")
            return []
    
    def reload_config(self):
        """โหลดการตั้งค่าใหม่จากไฟล์"""
        try:
            self.config = self._load_config()
            logger.info("Tab config reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error reloading config: {str(e)}")
            return False