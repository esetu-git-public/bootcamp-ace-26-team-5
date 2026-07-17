@echo off
cd /d "%~dp0"
echo ==================================================
echo Starting React Frontend Server...
echo ==================================================
cd healthcare-fraud-detection\frontend
npm run dev
pause
