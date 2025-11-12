#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WMS Barcode Scanner - Web Application Entry Point
เรียกใช้แอปพลิเคชันแบบ Web (Flask Server)
สำหรับใช้งานบน Android ผ่านเว็บเบราว์เซอร์
"""

import os
import sys
import logging
from datetime import timedelta
from flask import Flask, render_template, session, redirect
from flask_cors import CORS
from dotenv import load_dotenv

# Disable Windows QuickEdit to prevent console freeze on accidental clicks
try:
    from src.utils.console_utils import disable_quick_edit  # type: ignore
    disable_quick_edit()
except Exception:
    # Fail silently – console tweak should not break app
    pass

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import configuration and middleware
from config_utils.config_manager import config_manager
from middleware.rate_limiter import clear_expired_requests, rate_limit

# Import route blueprints
from routes.auth_routes import auth_bp
from routes.job_routes import job_bp
from routes.scan_routes import scan_bp
from routes.report_routes import report_bp
from routes.sound_routes import sound_bp
from routes.notification_routes import notification_bp

# Import web services
from web.database_service import initialize_database


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load application configuration
    app_config = config_manager.get_app_config()
    
    # Configure Flask app
    app.secret_key = app_config['secret_key']
    app.config.update(
        PERMANENT_SESSION_LIFETIME=timedelta(hours=app_config['session_timeout_hours']),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,  # ใส่ True ถ้าใช้ HTTPS
        SESSION_COOKIE_SAMESITE='Lax'
    )
    
    # Enable CORS
    CORS(app)
    
    # Configure logging
    setup_logging(app_config['debug'])
    
    # Register blueprints
    register_blueprints(app)
    
    # Register main routes
    register_main_routes(app)
    
    return app


def setup_logging(debug_mode: bool = False):
    """Setup application logging with daily rotation"""
    from src.utils.log_manager import setup_daily_rotating_logging
    setup_daily_rotating_logging(debug_mode, 'logs')


def register_blueprints(app: Flask):
    """Register all route blueprints"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(sound_bp)
    app.register_blueprint(notification_bp)


def register_main_routes(app: Flask):
    """Register main application routes"""
    
    @app.route('/')
    @rate_limit(max_requests=100, per_seconds=60, show_page=True)  # จำกัด 100 ครั้งต่อนาที
    def index():
        """หน้าแรกของแอปพลิเคชัน"""
        # Check if user is authenticated
        if 'db_config' not in session:
            return redirect('/login')
        return render_template('index.html')
    
    @app.route('/login')
    @rate_limit(max_requests=100, per_seconds=60, show_page=True)
    def login_page():
        """หน้าล็อกอิน"""
        # If already logged in, redirect to main app
        if 'db_config' in session:
            return redirect('/')
        return render_template('login.html')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        from web.database_service import get_connection_status
        
        db_status = get_connection_status()
        
        return {
            'status': 'healthy' if db_status['connected'] else 'unhealthy',
            'database': db_status,
            'version': '2.0.0'
        }
    
    @app.route('/api/logs/status')
    @rate_limit(max_requests=10, per_seconds=60)
    def log_status():
        """ดูสถานะของระบบ log"""
        from src.utils.log_manager import get_log_status
        return get_log_status()
    
    @app.route('/api/logs/cleanup')
    @rate_limit(max_requests=1, per_seconds=300)  # จำกัด 1 ครั้งต่อ 5 นาที
    def force_log_cleanup():
        """บังคับลบไฟล์ log เก่า"""
        from src.utils.log_manager import log_manager
        log_manager.cleanup_old_logs()
        return {'success': True, 'message': 'Log cleanup completed'}
    
    @app.route('/api/logs/rotate')
    @rate_limit(max_requests=1, per_seconds=300)  # จำกัด 1 ครั้งต่อ 5 นาที
    def force_log_rotation():
        """บังคับหมุนเวียน log ทันที"""
        from src.utils.log_manager import force_log_rotation
        force_log_rotation()
        return {'success': True, 'message': 'Log rotation completed'}
    
    @app.before_request
    def cleanup_background_tasks():
        """Clean up expired requests periodically"""
        import random
        # Run cleanup 1% of the time to avoid performance impact
        if random.random() < 0.01:
            clear_expired_requests()


def initialize_app():
    """Initialize application components"""
    try:
        # Create necessary directories
        os.makedirs('templates', exist_ok=True)
        os.makedirs('static', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        logger = logging.getLogger(__name__)
        logger.info("START: เริ่มต้น WMS Barcode Scanner Web Application")
        logger.info("URL: สามารถเข้าถึงได้ที่ http://localhost:5003")
        logger.info("MOBILE: สำหรับ Android http://[IP_ADDRESS]:5003")
        logger.info("TIP: ใช้ IP Address ของเครื่องนี้แทน [IP_ADDRESS]")
        
        # ไม่เชื่อมต่อฐานข้อมูลอัตโนมัติ - บังคับให้ login ก่อน
        logger.info("AUTH: แอปพลิเคชันพร้อมใช้งาน - ต้อง Login ก่อนใช้งาน")
        logger.info("LOGIN: ไปที่ http://localhost:5003/login เพื่อเข้าสู่ระบบ")
        
        return True
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"ERROR: เกิดข้อผิดพลาดในการเริ่มต้นแอป: {e}")
        return False


def main():
    """Main application entry point"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Create Flask application
    app = create_app()
    
    # Initialize application
    if not initialize_app():
        logger = logging.getLogger(__name__)
        logger.error("ERROR: Unable to initialize application")
        return
    
    # Get application configuration
    app_config = config_manager.get_app_config()
    
    # Run application
    logger = logging.getLogger(__name__)
    
    if not app_config['debug']:
        logger.info("PRODUCTION: Running in PRODUCTION mode")
        app.run(
            host=app_config['host'],
            port=app_config['port'],
            debug=False,
            threaded=True,
            use_reloader=False
        )
    else:
        logger.info("DEVELOPMENT: Running in DEVELOPMENT mode")
        app.run(
            host=app_config['host'],
            port=app_config['port'],
            debug=False,  # Keep False for better performance
            threaded=True
        )


if __name__ == '__main__':
    main()