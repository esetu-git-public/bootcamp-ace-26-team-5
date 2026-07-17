@echo off
cd /d "%~dp0"
echo ==================================================
echo Starting Healthcare Fraud Detection System...
echo ==================================================

start cmd /k "echo Starting Flask Backend... & cd healthcare-fraud-detection & call .venv\Scripts\activate & python backend\app.py"
start cmd /k "echo Starting React Frontend... & cd healthcare-fraud-detection\frontend & npm run dev"

echo Servers started successfully in separate windows!
