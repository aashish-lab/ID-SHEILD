@echo off
title ID SHIELD - Any Network & Device Launcher
cls
echo =======================================================================
echo    ID SHIELD - Border Checkpoint & Identity Fraud Screening
echo               Running on ANY NETWORK on ANY DEVICE
echo =======================================================================
echo.
cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Error: Python is not found in PATH.
    pause
    exit /b
)

echo [2/3] Checking dependencies...
python -c "import flask, cv2, PIL, pytesseract" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install flask werkzeug pillow opencv-python pytesseract
)

echo [3/3] Starting ID SHIELD on Port 5050 with Global Tunnel...
echo.
python app.py
pause
