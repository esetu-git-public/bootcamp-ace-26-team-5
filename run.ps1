Write-Host "==================================================" -ForegroundColor Green
Write-Host "Starting Healthcare Fraud Detection System Setup..." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Change directory to the script's location
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($ScriptDir) {
    Set-Location $ScriptDir
}

# 1. Copy env files if they do not exist
if (-not (Test-Path "healthcare-fraud-detection\backend\.env")) {
    Write-Host "[Backend] Creating .env file from .env.example..." -ForegroundColor Cyan
    Copy-Item "healthcare-fraud-detection\backend\.env.example" "healthcare-fraud-detection\backend\.env"
}
if (-not (Test-Path "healthcare-fraud-detection\frontend\.env")) {
    Write-Host "[Frontend] Creating .env file from .env.example..." -ForegroundColor Cyan
    Copy-Item "healthcare-fraud-detection\frontend\.env.example" "healthcare-fraud-detection\frontend\.env"
}

# 2. Initialize SQLite Database
Write-Host "[Database] Initializing and seeding SQLite database..." -ForegroundColor Cyan
python healthcare-fraud-detection\database\init_db.py
python healthcare-fraud-detection\database\seed_data.py

# 3. Backend Setup
Write-Host "[Backend] Preparing Virtual Environment..." -ForegroundColor Cyan
Set-Location healthcare-fraud-detection\backend
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
# Install packages using the venv pip directly (safer than activating first in scripts)
Write-Host "[Backend] Installing dependencies..." -ForegroundColor Cyan
& .venv\Scripts\pip.exe install -r ..\requirements.txt
Set-Location ..\..

# 4. Frontend Setup
Write-Host "[Frontend] Installing dependencies..." -ForegroundColor Cyan
Set-Location healthcare-fraud-detection\frontend
npm install
Set-Location ..\..

# 5. Run Backend and Frontend concurrently
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Starting Backend and Frontend Servers..." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting Flask Backend...'; cd healthcare-fraud-detection\backend; .venv\Scripts\activate.ps1; python app.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting React Frontend...'; cd healthcare-fraud-detection\frontend; npm run dev"

Write-Host "System started successfully! Check the newly opened terminal windows." -ForegroundColor Green
