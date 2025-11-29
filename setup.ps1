# Face Recognition AI - PowerShell Setup Script

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "   FACE RECOGNITION AI - AUTOMATED SETUP" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3.12 is installed
Write-Host "Checking for Python 3.13..." -ForegroundColor Yellow
try {
    $pythonVersion = & python3.13 --version 2>&1
    Write-Host "✓ $pythonVersion found!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "ERROR: Python 3.13 is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "SOLUTION:" -ForegroundColor Yellow
    Write-Host "1. Download Python 3.13 from: https://www.python.org/downloads/release/python-3137/" -ForegroundColor Cyan
    Write-Host "2. Run the installer with 'Add Python 3.13 to PATH' CHECKED" -ForegroundColor Cyan
    Write-Host "3. Restart this script" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
$basePath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $basePath

# Step 1: Remove old virtual environment
Write-Host "[1/5] Cleaning up old installation..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Removing old venv..."
    Remove-Item -Recurse -Force "venv" -ErrorAction SilentlyContinue
}
Write-Host ""

# Step 2: Create virtual environment
Write-Host "[2/5] Creating virtual environment..." -ForegroundColor Yellow
& python3.13 -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Virtual environment created!" -ForegroundColor Green
Write-Host ""

# Step 3: Activate virtual environment
Write-Host "[3/5] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Step 4: Upgrade pip
Write-Host "[4/5] Upgrading pip..." -ForegroundColor Yellow
& python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: pip upgrade had issues, continuing anyway..." -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Install dependencies
Write-Host "[5/5] Installing dependencies (this may take 5-10 minutes)..." -ForegroundColor Yellow
Write-Host "Installing FastAPI, OpenCV, face-recognition, and other packages..." -ForegroundColor Cyan
Write-Host ""

Set-Location "backend"
& pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "   SETUP COMPLETE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your Face Recognition AI is ready to use!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run the server: python run.py" -ForegroundColor Cyan
Write-Host "2. Open browser: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "The virtual environment will stay activated in this window." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue"
