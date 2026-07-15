#!/bin/bash
cd "$(dirname "$0")"

echo "=================================================="
echo "Starting Healthcare Fraud Detection System Setup..."
echo "=================================================="

# 1. Copy env files if they do not exist
if [ ! -f "healthcare-fraud-detection/backend/.env" ]; then
    echo "[Backend] Creating .env file from .env.example..."
    cp healthcare-fraud-detection/backend/.env.example healthcare-fraud-detection/backend/.env
fi

if [ ! -f "healthcare-fraud-detection/frontend/.env" ]; then
    echo "[Frontend] Creating .env file from .env.example..."
    cp healthcare-fraud-detection/frontend/.env.example healthcare-fraud-detection/frontend/.env
fi

# 2. Initialize SQLite Database
echo "[Database] Initializing and seeding SQLite database..."
python3 healthcare-fraud-detection/database/init_db.py
python3 healthcare-fraud-detection/database/seed_data.py

# 3. Backend Setup
echo "[Backend] Preparing Virtual Environment..."
cd healthcare-fraud-detection/backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
echo "[Backend] Installing dependencies..."
pip install -r ../requirements.txt
cd ../..

# 4. Frontend Setup
echo "[Frontend] Installing dependencies..."
cd healthcare-fraud-detection/frontend
npm install
cd ../..

# 5. Run Backend and Frontend concurrently
echo "=================================================="
echo "Starting Backend and Frontend Servers..."
echo "=================================================="

# Start backend in background
cd healthcare-fraud-detection/backend
source .venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ../..

# Start frontend
cd healthcare-fraud-detection/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

wait
