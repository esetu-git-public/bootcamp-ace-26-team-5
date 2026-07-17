@echo off
cd /d "%~dp0"
echo ==================================================
echo Setting Up Healthcare Fraud Detection System...
echo ==================================================

:: 1. Copy env files if they do not exist
if not exist "healthcare-fraud-detection\backend\.env" (
    echo [Backend] Creating .env file from .env.example...
    copy "healthcare-fraud-detection\backend\.env.example" "healthcare-fraud-detection\backend\.env"
)
if not exist "healthcare-fraud-detection\frontend\.env" (
    echo [Frontend] Creating .env file from .env.example...
    copy "healthcare-fraud-detection\frontend\.env.example" "healthcare-fraud-detection\frontend\.env"
)

:: 2. Backend Setup (Virtual Environment at project root)
echo [Backend] Preparing Virtual Environment...
cd healthcare-fraud-detection
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate
echo [Backend] Installing Python dependencies...
pip install -r requirements.txt

:: 3. Initialize SQLite Database
echo [Database] Initializing and seeding SQLite database...
python database\init_db.py
python database\seed_data.py
cd ..

:: 4. Frontend Setup
echo [Frontend] Installing Node dependencies...
cd healthcare-fraud-detection\frontend
call npm install
cd ..\..

echo ==================================================
echo Setup completed successfully!
echo Run 'run_project.bat' to start the application.
echo ==================================================
pause
