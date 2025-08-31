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
from flask_session import Session

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

# Import web services
from web.database_service import initialize_database
from src.session.redis_session import configure_flask_redis_sessions, get_redis_session_manager


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
    
    # Configure Redis sessions with fallback (Phase 1 Complete)
    redis_url = app_config.get('redis_url', 'redis://localhost:6379/0')
    logger = logging.getLogger(__name__)
    
    try:
        if configure_flask_redis_sessions(app, redis_url):
            logger.info("🚀 Redis sessions configured successfully")
        else:
            logger.info("📁 Using filesystem sessions as fallback")
    except Exception as e:
        logger.warning(f"⚠️ Session configuration failed: {e}, using default Flask sessions")
    
    # Configure logging
    setup_logging(app_config['debug'])
    
    # Register blueprints
    register_blueprints(app)
    
    # Register main routes
    register_main_routes(app)
    
    return app


def setup_logging(debug_mode: bool = False):
    """Setup application logging with daily rotation"""
    from logging.handlers import TimedRotatingFileHandler
    import glob
    from datetime import datetime
    
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Use today's date in filename
    today = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'logs/web_app_{today}.log'
    
    # Create daily rotating file handler
    file_handler = TimedRotatingFileHandler(
        log_filename,
        when='midnight',        # Rotate at midnight
        interval=1,            # Every 1 day
        backupCount=30,        # Keep 30 days
        encoding='utf-8'
    )
    file_handler.suffix = '%Y-%m-%d'  # Format for rotated files
    
    # Cleanup old logs beyond 30 days
    def cleanup_old_logs():
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=30)
            log_files = glob.glob('logs/web_app_*.log*')
            for log_file in log_files:
                try:
                    # Extract date from filename (web_app_2025-08-31.log)
                    filename = os.path.basename(log_file)
                    if 'web_app_' in filename:
                        date_part = filename.replace('web_app_', '').split('.')[0]
                        if len(date_part) == 10 and date_part.count('-') == 2:  # YYYY-MM-DD format
                            file_date = datetime.strptime(date_part, '%Y-%m-%d')
                            if file_date < cutoff_date:
                                os.remove(log_file)
                                print(f"🗑️ Cleaned old log: {log_file}")
                except:
                    pass
        except:
            pass
    
    # Run cleanup on startup
    cleanup_old_logs()
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            file_handler,
            logging.StreamHandler()
        ]
    )
    
    # Configure console handler encoding for Windows
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