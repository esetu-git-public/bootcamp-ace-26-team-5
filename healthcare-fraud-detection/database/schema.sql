PRAGMA foreign_keys = ON;

-- 1. Users who access the system
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'employee',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Insurance customers
CREATE TABLE IF NOT EXISTS policyholders (
    policyholder_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    gender TEXT,
    phone TEXT,
    email TEXT UNIQUE,
    address TEXT,
    city TEXT,
    state TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Insurance policy details
CREATE TABLE IF NOT EXISTS insurance_policies (
    policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_number TEXT UNIQUE NOT NULL,
    policyholder_id INTEGER NOT NULL,
    insurance_type TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    premium_amount REAL,
    coverage_amount REAL,
    policy_status TEXT DEFAULT 'active',

    FOREIGN KEY (policyholder_id)
        REFERENCES policyholders(policyholder_id)
        ON DELETE CASCADE
);

-- 4. Claim details submitted for fraud analysis
CREATE TABLE IF NOT EXISTS insurance_claims (
    claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_number TEXT UNIQUE NOT NULL,
    policy_id INTEGER NOT NULL,
    claim_date DATE NOT NULL,
    incident_date DATE,
    claim_type TEXT,
    claim_amount REAL NOT NULL,
    incident_location TEXT,
    incident_description TEXT,
    police_report_available INTEGER DEFAULT 0,
    witnesses_count INTEGER DEFAULT 0,
    claim_status TEXT DEFAULT 'submitted',
    submitted_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (policy_id)
        REFERENCES insurance_policies(policy_id)
        ON DELETE CASCADE,

    FOREIGN KEY (submitted_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL
);

-- 5. ML model fraud prediction output
CREATE TABLE IF NOT EXISTS fraud_predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    predicted_label TEXT NOT NULL CHECK (predicted_label IN ('Fraud', 'Not Fraud')),
    fraud_probability REAL NOT NULL CHECK (fraud_probability >= 0 AND fraud_probability <= 1),
    risk_level TEXT CHECK (risk_level IN ('Low', 'Medium', 'High')),
    model_version TEXT,
    prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,

    FOREIGN KEY (claim_id)
        REFERENCES insurance_claims(claim_id)
        ON DELETE CASCADE
);

-- Helpful indexes for faster claim and prediction lookup
CREATE INDEX IF NOT EXISTS idx_claim_policy_id
ON insurance_claims(policy_id);

CREATE INDEX IF NOT EXISTS idx_prediction_claim_id
ON fraud_predictions(claim_id);

-- 6. Notifications for in-app messaging
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    severity TEXT DEFAULT 'info',
    is_read INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipient_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications(recipient_id);

-- 7. Audit logs for logging user actions
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    claim_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (claim_id) REFERENCES insurance_claims(claim_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_claim ON audit_logs(claim_id);