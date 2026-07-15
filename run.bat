@echo off
cd /d "%~dp0"
echo ==================================================
echo Starting Healthcare Fraud Detection System Setup...
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

:: 2. Initialize SQLite Database
echo [Database] Initializing and seeding SQLite database...
python healthcare-fraud-detection\database\init_db.py
python healthcare-fraud-detection\database\seed_data.py

:: 3. Backend Setup
echo [Backend] Preparing Virtual Environment...
cd healthcare-fraud-detection\backend
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate
echo [Backend] Installing dependencies...
pip install -r ..\requirements.txt
cd ..\..

:: 4. Frontend Setup
echo [Frontend] Installing dependencies...
cd healthcare-fraud-detection\frontend
call npm install
cd ..\..

:: 5. Run Backend and Frontend concurrently
echo ==================================================
echo Starting Backend and Frontend Servers...
echo ==================================================

start cmd /k "echo Starting Flask Backend... & cd healthcare-fraud-detection\backend & call .venv\Scripts\activate & python app.py"
start cmd /k "echo Starting React Frontend... & cd healthcare-fraud-detection\frontend & npm run dev"

echo System started successfully! Check the newly opened terminal windows.
