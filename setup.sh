#!/bin/bash
# Quick setup script for Twitter News Curator (Linux/macOS)

echo "================================"
echo "Twitter News Curator - Setup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv || { echo "[ERROR] Failed to create venv"; exit 1; }

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt || { echo "[ERROR] Failed to install dependencies"; exit 1; }

echo "[4/5] Creating .env file from template..."
if [ ! -f .env ]; then
    cp .env.template .env
    echo "Created .env file. IMPORTANT: Edit .env and add your API keys!"
else
    echo ".env file already exists - skipping"
fi

echo "[5/5] Creating data directory..."
mkdir -p data

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API credentials"
echo "2. Run: python run.py"
echo ""
echo "For help, see README.md"
echo ""
