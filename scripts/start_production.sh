#!/bin/bash
# WMS Barcode Scanner - Production Startup Script (Linux/Unix)
# Phase 1 Production-Ready Configuration

echo "========================================"
echo " WMS Barcode Scanner - Production Mode"
echo "========================================"

# Change to project root directory
cd "$(dirname "$0")/.."

# Create logs directory
mkdir -p logs

# Set environment variables
export FLASK_ENV=production
export WMS_ENV=production
export PYTHONPATH="$(pwd)/src"

echo "[1/3] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[2/3] Starting Redis server (if not running)..."
# Check if Redis is running
if ! pgrep redis-server > /dev/null; then
    echo "Starting Redis server..."
    redis-server --daemonize yes
    sleep 2
else
    echo "Redis server already running"
fi

echo "[3/3] Starting WMS application with Gunicorn..."
echo
echo "Server will be available at:"
echo "  http://localhost:5003"
echo "  http://[YOUR_IP]:5003"
echo
echo "Press Ctrl+C to stop the server"
echo

# Start with Gunicorn using configuration file
gunicorn -c gunicorn.conf.py run_web:app

echo
echo "Server stopped."