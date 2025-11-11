#!/bin/bash
# ===================================================================
# WMS Barcode Scanner - Docker Run Production (Linux/Mac)
# ===================================================================

set -e

echo "========================================"
echo "WMS Barcode Scanner - Production Mode"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[ERROR] .env file not found"
    echo "Please create .env file from .env.example"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "[ERROR] Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "[INFO] Starting production environment..."
echo ""
echo "Features:"
echo "  - Optimized build"
echo "  - Debug mode OFF"
echo "  - Resource limits enabled"
echo "  - Auto-restart on failure"
echo "  - Logs persisted to ./logs"
echo ""

read -p "Are you sure you want to run in PRODUCTION mode? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Starting containers..."

# Run docker-compose with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo ""
echo "========================================"
echo "Production environment started!"
echo "========================================"
echo ""
echo "Access the application at:"
echo "  http://localhost:5000"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f wms-web"
echo ""
echo "To stop:"
echo "  bash scripts/docker-stop.sh"
echo ""
