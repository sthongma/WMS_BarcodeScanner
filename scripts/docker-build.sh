#!/bin/bash
# ===================================================================
# WMS Barcode Scanner - Docker Build Script (Linux/Mac)
# ===================================================================

set -e

echo "========================================"
echo "WMS Barcode Scanner - Docker Build"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "[ERROR] Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "[INFO] Building Docker image..."
echo ""

# Build the image
docker build -t wms-barcode-scanner-web:latest .

echo ""
echo "========================================"
echo "Build completed successfully!"
echo "========================================"
echo ""
echo "Image: wms-barcode-scanner-web:latest"
echo ""
echo "Next steps:"
echo "  Development: bash scripts/docker-run-dev.sh"
echo "  Production:  bash scripts/docker-run-prod.sh"
echo ""
