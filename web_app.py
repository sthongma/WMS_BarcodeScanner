#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WMS Barcode Scanner Web Application - Refactored Version
สำหรับใช้งานบน Android ผ่านเว็บเบราว์เซอร์
"""

import os
import logging
from datetime import timedelta
from flask import Flask, render_template, session
from flask_cors import CORS

# Import configuration and middleware
from config_utils.config_manager import config_manager
from middleware.rate_limiter import clear_expired_requests

# Import route blueprints
from routes.auth_routes import auth_bp
from routes.job_routes import job_bp
from routes.scan_routes import scan_bp
from routes.report_routes import report_bp

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
    """Setup application logging"""
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/web_app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Configure console handler encoding for Windows
    import sys
    if sys.platform == 'win32':
        for handler in logging.root.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stderr:
                try:
                    handler.stream.reconfigure(encoding='utf-8')
                except:
                    pass
    
    # Set specific logger levels
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def register_blueprints(app: Flask):
    """Register all route blueprints"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(report_bp)


def register_main_routes(app: Flask):
    """Register main application routes"""
    
    @app.route('/')
    def index():
        """หน้าแรกของแอปพลิเคชัน"""
        return render_template('index.html')
    
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
        logger.info("URL: สามารถเข้าถึงได้ที่ http://localhost:5000")
        logger.info("MOBILE: สำหรับ Android http://[IP_ADDRESS]:5000")
        logger.info("TIP: ใช้ IP Address ของเครื่องนี้แทน [IP_ADDRESS]")
        
        # เริ่มต้นการเชื่อมต่อฐานข้อมูล
        logger.info("DB: กำลังเชื่อมต่อฐานข้อมูล...")
        if initialize_database():
            logger.info("OK: พร้อมใช้งาน - ฐานข้อมูลเชื่อมต่อสำเร็จ")
        else:
            logger.warning("WARNING: แอปพลิเคชันจะทำงานในโหมด Offline")
        
        return True
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"ERROR: เกิดข้อผิดพลาดในการเริ่มต้นแอป: {e}")
        return False


def main():
    """Main application entry point"""
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