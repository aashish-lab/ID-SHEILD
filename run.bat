@echo off
title ID Shield - AI Anti-Fraud Identity Verification Portal
echo ======================================================================
echo           ID SHIELD - AI Anti-Fraud Identity Verification Portal
echo ======================================================================
echo.
cd /d "%~dp0"

echo [1/2] Checking and installing Python dependencies...
python -m pip install -r requirements.txt
echo.
echo [2/2] Starting Flask server on http://127.0.0.1:5050 ...
echo.
echo ======================================================================
echo  Open your browser at: http://127.0.0.1:5050
echo  Press Ctrl+C in this terminal window to stop the server.
echo ======================================================================
echo.
python app.py
pause
