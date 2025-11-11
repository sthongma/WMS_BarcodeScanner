#!/bin/bash
# ===================================================================
# WMS Barcode Scanner - Activate Development Environment (Linux/Mac)
# ===================================================================
# This script activates the virtual environment and optionally
# installs development dependencies.
# ===================================================================
# Usage: source scripts/activate_dev.sh
# ===================================================================

echo "========================================"
echo "WMS Barcode Scanner - Development Environment"
echo "========================================"
echo ""

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "[ERROR] Virtual environment not found at .venv"
    echo ""
    echo "Please run setup first:"
    echo "  bash scripts/setup_venv.sh"
    echo ""
    return 1 2>/dev/null || exit 1
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo ""
echo "Virtual environment activated!"
echo "Python location: $(which python)"
echo ""

# Check if dev dependencies are installed
if ! python -c "import pytest" &> /dev/null; then
    echo "[INFO] Development dependencies not found."
    read -p "Install development dependencies? (Y/n): " INSTALL_DEV
    if [[ ! "$INSTALL_DEV" =~ ^[Nn]$ ]]; then
        echo ""
        echo "Installing development dependencies..."
        pip install -r requirements-dev.txt
        echo ""
        echo "Development dependencies installed!"
    fi
fi

echo ""
echo "========================================"
echo "Ready for development!"
echo "========================================"
echo ""
echo "Available commands:"
echo "  python run.py              - Run Desktop App"
echo "  pytest                     - Run tests"
echo "  pytest --cov=src           - Run tests with coverage"
echo "  black src/ tests/          - Format code"
echo "  flake8 src/ tests/         - Lint code"
echo "  mypy src/                  - Type check"
echo ""
echo "To deactivate: deactivate"
echo ""
