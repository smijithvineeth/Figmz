@echo off
REM Face Recognition AI - Automated Setup Script for Windows
REM This script sets up the virtual environment and installs all dependencies

echo.
echo ================================================================================
echo   FACE RECOGNITION AI - AUTOMATED SETUP
echo ================================================================================
echo.

REM Check if Python 3.13 is installed
echo Checking for Python 3.13...
python3.13 --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python 3.13 is not installed or not in PATH
    echo.
    echo SOLUTION:
    echo 1. Download Python 3.13 from: https://www.python.org/downloads/release/python-3137/
    echo 2. Run the installer with "Add Python 3.13 to PATH" CHECKED
    echo 3. Restart this script
    echo.
    pause
    exit /b 1
)

python3.13 --version
echo Python 3.13 found! Proceeding...
echo.

REM Set the base directory
set BASEDIR=%~dp0
cd /d "%BASEDIR%"

REM Step 1: Remove old virtual environment if it exists
echo [1/5] Cleaning up old installation...
if exist venv (
    echo Removing old venv...
    rmdir /s /q venv 2>nul
)
echo.

REM Step 2: Create virtual environment
echo [2/5] Creating virtual environment...
python3.13 -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created!
echo.

REM Step 3: Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

REM Step 4: Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo WARNING: pip upgrade had issues, continuing anyway...
)
echo.

REM Step 5: Install dependencies
echo [5/5] Installing dependencies (this may take 5-10 minutes)...
echo Installing FastAPI, OpenCV, face-recognition, and other packages...
echo.
cd backend
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   SETUP COMPLETE!
echo ================================================================================
echo.
echo Your Face Recognition AI is ready to use!
echo.
echo Next steps:
echo 1. Run the server: python run.py
echo 2. Open browser: http://localhost:8000
echo.
echo The virtual environment will stay activated in this window.
echo.
pause
