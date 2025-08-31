#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gunicorn Configuration for WMS Barcode Scanner
Optimized for 20-30 concurrent users
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5003"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Usually 4-8 workers
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Preload application for better memory usage
preload_app = True

# Logging
loglevel = "info"
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'wms_barcode_scanner'

# Server mechanics
daemon = False
pidfile = 'logs/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment if needed)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

# Performance tuning
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else None

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("🚀 WMS Barcode Scanner ready to serve requests")
    server.log.info(f"👥 Workers: {workers}")
    server.log.info(f"🔗 Listening on: {bind}")

def worker_int(worker):
    """Called when worker receives INT signal."""
    worker.log.info(f"Worker {worker.pid} received INT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"🔄 Forking worker {worker.age}")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"✅ Worker {worker.pid} spawned")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("🔄 Forked child, re-executing")

def on_exit(server):
    """Called just before exiting."""
    server.log.info("👋 WMS Barcode Scanner shutting down")