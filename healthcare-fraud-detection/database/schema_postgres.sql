-- PostgreSQL / Supabase Schema for Healthcare Fraud Detection System

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'employee',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Policyholders
CREATE TABLE IF NOT EXISTS policyholders (
    policyholder_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(50),
    phone VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Insurance Policies
CREATE TABLE IF NOT EXISTS insurance_policies (
    policy_id SERIAL PRIMARY KEY,
    policy_number VARCHAR(50) UNIQUE NOT NULL,
    policyholder_id INTEGER NOT NULL REFERENCES policyholders(policyholder_id) ON DELETE CASCADE,
    insurance_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    premium_amount NUMERIC(15, 2),
    coverage_amount NUMERIC(15, 2),
    policy_status VARCHAR(50) DEFAULT 'active'
);

-- 4. Insurance Claims
CREATE TABLE IF NOT EXISTS insurance_claims (
    claim_id SERIAL PRIMARY KEY,
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    policy_id INTEGER NOT NULL REFERENCES insurance_policies(policy_id) ON DELETE CASCADE,
    claim_date DATE NOT NULL,
    incident_date DATE,
    claim_type VARCHAR(50),
    claim_amount NUMERIC(15, 2) NOT NULL,
    incident_location VARCHAR(150),
    incident_description TEXT,
    police_report_available INTEGER DEFAULT 0,
    witnesses_count INTEGER DEFAULT 0,
    claim_status VARCHAR(50) DEFAULT 'submitted',
    submitted_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Fraud Predictions
CREATE TABLE IF NOT EXISTS fraud_predictions (
    prediction_id SERIAL PRIMARY KEY,
    claim_id INTEGER NOT NULL REFERENCES insurance_claims(claim_id) ON DELETE CASCADE,
    predicted_label VARCHAR(50) NOT NULL CHECK (predicted_label IN ('Fraud', 'Not Fraud')),
    fraud_probability DOUBLE PRECISION NOT NULL CHECK (fraud_probability >= 0 AND fraud_probability <= 1),
    risk_level VARCHAR(20) CHECK (risk_level IN ('Low', 'Medium', 'High')),
    model_version VARCHAR(50),
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT
);

-- 6. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    claim_id INTEGER REFERENCES insurance_claims(claim_id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Helpful indexes for faster lookup
CREATE INDEX IF NOT EXISTS idx_claim_policy_id ON insurance_claims(policy_id);
CREATE INDEX IF NOT EXISTS idx_prediction_claim_id ON fraud_predictions(claim_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
