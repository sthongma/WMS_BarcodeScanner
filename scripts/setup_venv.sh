#!/bin/bash
# ===================================================================
# WMS Barcode Scanner - Virtual Environment Setup (Linux/Mac)
# ===================================================================
# This script creates and configures a Python virtual environment
# for the Desktop application.
# ===================================================================

set -e  # Exit on error

echo "========================================"
echo "WMS Barcode Scanner - Virtual Environment Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from your package manager or https://www.python.org/"
    exit 1
fi

echo "[1/5] Checking Python version..."
python3 --version

# Check if .venv already exists
if [ -d ".venv" ]; then
    echo ""
    echo "[WARNING] Virtual environment already exists at .venv"
    echo ""
    read -p "Do you want to recreate it? (y/N): " RECREATE
    if [[ ! "$RECREATE" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

echo ""
echo "[2/5] Creating virtual environment at .venv..."
python3 -m venv .venv

echo ""
echo "[3/5] Activating virtual environment..."
source .venv/bin/activate

echo ""
echo "[4/5] Upgrading pip..."
python -m pip install --upgrade pip || echo "[WARNING] Failed to upgrade pip, continuing anyway..."

echo ""
echo "[5/5] Installing production dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "Or use the convenience script:"
echo "  source scripts/activate_dev.sh"
echo ""
echo "To install development dependencies:"
echo "  pip install -r requirements-dev.txt"
echo ""
echo "To run the Desktop application:"
echo "  python run.py"
echo ""
