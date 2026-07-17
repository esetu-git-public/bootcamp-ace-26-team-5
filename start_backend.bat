@echo off
cd /d "%~dp0"
echo ==================================================
echo Starting Flask Backend Server...
echo ==================================================
cd healthcare-fraud-detection
call .venv\Scripts\activate
python backend\app.py
pause
