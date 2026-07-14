# Healthcare Insurance Claim Fraud Detection System
## Teammate Setup & Deployment Guide

This guide details the steps required to configure, connect, and run both the Backend (Flask API + ML Pipeline) and Frontend (React + Vite) services.

---

## 🔑 1. Seeded Verification Credentials

For validation testing, the database contains the following pre-configured user credentials:

| Role | Username / Email | Password | Allowed Access |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@fraudshield.com` | `admin123` | Full analytics, user controls, and reports. |
| **Claims Officer** | `officer@fraudshield.com` | `officer123` | Pending claims queue, approval/rejection actions. |
| **Policyholder** | *(Register new account)* | *(At least 6 chars)* | Submit claim, view own claim history. |

---

## 🛠️ 2. Prerequisites
Before getting started, make sure your system has the following installed:
*   **Python:** Version `3.10` or `3.11`
*   **Node.js:** Version `18` or higher
*   **Supabase Client:** Access to a Supabase project

---

## 💾 3. Database Schema & Role Constraint Patch

To prevent signup errors, the database check constraints must allow the `'customer'` role.

### SQL Patch Execution
1. Open your [Supabase Console](https://supabase.com/dashboard).
2. Open your project and select **SQL Editor** on the left menu.
3. Open a **New Query** window, ensure it is completely empty, paste the following SQL block, and click **Run**:

```sql
-- 1. Correct user role constraints
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('customer', 'employee', 'admin'));
ALTER TABLE users ALTER COLUMN role SET DEFAULT 'customer';

-- 2. Optional: Create notifications table if missing
CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    recipient_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Optional: Create audit logs table if missing
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    claim_id INTEGER REFERENCES insurance_claims(claim_id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🐍 4. Backend Setup (Flask + Deep Learning)

1. Open your terminal in the backend directory:
   ```bash
   cd healthcare-fraud-detection/backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables. Copy `.env.example` to `.env` and fill in your keys:
   ```ini
   FLASK_APP=app.py
   FLASK_ENV=development
   JWT_SECRET_KEY=healthcare_fraud_secret_key
   
   # Supabase REST Credentials
   SUPABASE_URL=https://<your-project-id>.supabase.co
   SUPABASE_KEY=<your-service-role-key>
   ```
5. Start the backend:
   ```bash
   python app.py
   ```
   *The singleton model loader will initialize the Keras neural network model and PyTorch backend on port `5000`.*

---

## ⚛️ 5. Frontend Setup (React + Vite)

1. Open a new terminal in the frontend directory:
   ```bash
   cd healthcare-fraud-detection/frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Configure environment variables. Copy `.env.example` to `.env`:
   ```ini
   VITE_API_BASE_URL=http://localhost:5000/api
   VITE_USE_MOCK=false
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```
5. Open your browser and navigate to **`http://localhost:5173`**.

---

## 🔍 6. Troubleshooting

*   **Vite Resolve Errors (`@mui/material`):** Ensure you have run `npm install` to load the newly added Material-UI packages.
*   **Database Constraints (400 Bad Request):** If user signup returns a constraint validation error, make sure the `fix_users_role_check.sql` patch was executed in the Supabase SQL editor.
*   **REST Connection Failures:** Verify that `SUPABASE_URL` and `SUPABASE_KEY` in `backend/.env` contain correct keys matching your Supabase project.
