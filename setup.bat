@echo off
REM Quick setup script for Twitter News Curator
REM Run this to set up the project quickly

echo ================================
echo Twitter News Curator - Setup
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Creating .env file from template...
if not exist .env (
    copy .env.template .env
    echo Created .env file. IMPORTANT: Edit .env and add your API keys!
) else (
    echo .env file already exists - skipping
)

echo [5/5] Creating data directory...
if not exist data mkdir data

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API credentials
echo 2. Run: python run.py
echo.
echo For help, see README.md
echo.
pause
