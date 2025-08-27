#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production Runner for WMS Barcode Scanner
ใช้สำหรับรันแอปในโหมด production
"""

import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler

def load_config(config_file='config/production.json'):
    """โหลดการตั้งค่าจากไฟล์ config"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ ไม่สามารถโหลด config ได้: {e}")
        return None

def setup_logging(config):
    """ตั้งค่า logging สำหรับ production"""
    log_config = config.get('logging', {})
    
    # สร้าง logs directory
    os.makedirs('logs', exist_ok=True)
    
    # ตั้งค่า RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_config.get('file_path', 'logs/web_app_production.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # ตั้งค่า format
    formatter = logging.Formatter(
        log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    file_handler.setFormatter(formatter)
    
    # ตั้งค่า console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # ตั้งค่า root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def main():
    """Main function สำหรับ production"""
    print("🏭 Starting WMS Barcode Scanner in PRODUCTION mode")
    
    # โหลด config
    config = load_config()
    if not config:
        print("❌ ไม่สามารถโหลด production config ได้")
        sys.exit(1)
    
    # ตั้งค่า environment variables
    os.environ['FLASK_ENV'] = 'production'
    os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
    
    # ตั้งค่า logging
    setup_logging(config)
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting production server...")
    logger.info(f"📊 Config loaded: {config['app']['name']} v{config['app']['version']}")
    
    # Import และรัน app
    try:
        from web_app import app
        
        app_config = config['app']
        perf_config = config['performance']
        
        # อัพเดต Flask config
        app.config.update({
            'MAX_CONTENT_LENGTH': perf_config.get('max_content_length', '16MB'),
            'SEND_FILE_MAX_AGE_DEFAULT': perf_config.get('send_file_max_age', 43200)
        })
        
        # รันเซิร์ฟเวอร์
        app.run(
            host=app_config.get('host', '0.0.0.0'),
            port=int(os.environ.get('PORT', app_config.get('port', 5000))),
            debug=app_config.get('debug', False),
            threaded=perf_config.get('threaded', True),
            processes=perf_config.get('processes', 1),
            use_reloader=False
        )
        
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดในการเริ่มเซิร์ฟเวอร์: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()