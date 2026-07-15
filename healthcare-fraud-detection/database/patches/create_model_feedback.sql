-- SQL patch to create model_feedback table for Supabase / Postgres

CREATE TABLE IF NOT EXISTS model_feedback (
    feedback_id SERIAL PRIMARY KEY,
    claim_id INTEGER NOT NULL UNIQUE,
    user_id INTEGER,
    is_incorrect BOOLEAN DEFAULT FALSE,
    actual_label VARCHAR(50),
    feedback_text TEXT,
    model_version VARCHAR(50) DEFAULT 'v1.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_claim FOREIGN KEY (claim_id) REFERENCES insurance_claims(claim_id) ON DELETE CASCADE,
    CONSTRAINT fk_feedback_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_model_feedback_claim ON model_feedback(claim_id);
