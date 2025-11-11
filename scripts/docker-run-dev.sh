#!/bin/bash
# ===================================================================
# WMS Barcode Scanner - Docker Run Development (Linux/Mac)
# ===================================================================

set -e

echo "========================================"
echo "WMS Barcode Scanner - Development Mode"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found"
    echo ""
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "[IMPORTANT] Please edit .env file with your database configuration"
    echo "Then run this script again."
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "[ERROR] Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "[INFO] Starting development environment..."
echo ""
echo "Features:"
echo "  - Hot-reload enabled"
echo "  - Debug mode ON"
echo "  - Source code mounted for live editing"
echo "  - Logs persisted to ./logs"
echo ""

# Run docker-compose (automatically uses docker-compose.override.yml)
docker-compose up

# Note: docker-compose up will run in foreground
# Press Ctrl+C to stop
