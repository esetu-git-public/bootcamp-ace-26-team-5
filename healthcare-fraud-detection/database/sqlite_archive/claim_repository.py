from database.db_connection import get_db_connection


def add_policyholder(
    full_name,
    date_of_birth,
    gender,
    phone,
    email,
    address,
    city,
    state
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO policyholders
        (full_name, date_of_birth, gender, phone, email, address, city, state)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        full_name,
        date_of_birth,
        gender,
        phone,
        email,
        address,
        city,
        state
    ))

    policyholder_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return policyholder_id


def add_policy(
    policy_number,
    policyholder_id,
    insurance_type,
    start_date,
    end_date,
    premium_amount,
    coverage_amount,
    policy_status="active"
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO insurance_policies
        (policy_number, policyholder_id, insurance_type, start_date, end_date,
         premium_amount, coverage_amount, policy_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        policy_number,
        policyholder_id,
        insurance_type,
        start_date,
        end_date,
        premium_amount,
        coverage_amount,
        policy_status
    ))

    policy_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return policy_id

def add_claim(
    claim_number,
    policy_id,
    claim_date,
    incident_date,
    claim_type,
    claim_amount,
    incident_location,
    incident_description,
    police_report_available,
    witnesses_count,
    submitted_by=None
):
    if not claim_number or not claim_number.strip():
        raise ValueError("Claim number is required.")

    if claim_amount is None or float(claim_amount) <= 0:
        raise ValueError("Claim amount must be greater than 0.")

    if witnesses_count is None or int(witnesses_count) < 0:
        raise ValueError("Witness count cannot be negative.")

    if police_report_available not in [0, 1, True, False]:
        raise ValueError("Police report value must be 0 or 1.")

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO insurance_claims
            (claim_number, policy_id, claim_date, incident_date, claim_type,
             claim_amount, incident_location, incident_description,
             police_report_available, witnesses_count, claim_status, submitted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'submitted', ?)
        """, (
            claim_number.strip(),
            policy_id,
            claim_date,
            incident_date,
            claim_type,
            float(claim_amount),
            incident_location,
            incident_description,
            int(police_report_available),
            int(witnesses_count),
            submitted_by
        ))

        claim_id = cursor.lastrowid
        connection.commit()
        return claim_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
def save_prediction(
    claim_id,
    predicted_label,
    fraud_probability,
    risk_level,
    model_version="v1.0",
    remarks=None
):
    allowed_labels = ["Fraud", "Not Fraud"]
    allowed_risk_levels = ["Low", "Medium", "High"]

    if predicted_label not in allowed_labels:
        raise ValueError("Prediction must be either Fraud or Not Fraud.")

    if risk_level not in allowed_risk_levels:
        raise ValueError("Risk level must be Low, Medium, or High.")

    if fraud_probability is None or not 0 <= float(fraud_probability) <= 1:
        raise ValueError("Fraud probability must be between 0 and 1.")

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT claim_id
            FROM insurance_claims
            WHERE claim_id = ?
        """, (claim_id,))

        if cursor.fetchone() is None:
            raise ValueError(f"Claim ID {claim_id} does not exist.")

        cursor.execute("""
            SELECT prediction_id
            FROM fraud_predictions
            WHERE claim_id = ?
        """, (claim_id,))

        existing_prediction = cursor.fetchone()

        if existing_prediction:
            cursor.execute("""
                UPDATE fraud_predictions
                SET
                    predicted_label = ?,
                    fraud_probability = ?,
                    risk_level = ?,
                    model_version = ?,
                    prediction_date = CURRENT_TIMESTAMP,
                    remarks = ?
                WHERE claim_id = ?
            """, (
                predicted_label,
                float(fraud_probability),
                risk_level,
                model_version,
                remarks,
                claim_id
            ))

            prediction_id = existing_prediction["prediction_id"]

        else:
            cursor.execute("""
                INSERT INTO fraud_predictions
                (claim_id, predicted_label, fraud_probability, risk_level,
                 model_version, remarks)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                claim_id,
                predicted_label,
                float(fraud_probability),
                risk_level,
                model_version,
                remarks
            ))

            prediction_id = cursor.lastrowid

        connection.commit()
        return prediction_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
        
def get_claim_by_id(claim_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            c.claim_id,
            c.claim_number,
            c.claim_date,
            c.incident_date,
            c.claim_type,
            c.claim_amount,
            c.incident_location,
            c.incident_description,
            c.police_report_available,
            c.witnesses_count,
            c.claim_status,

            p.policy_number,
            p.insurance_type,
            p.premium_amount,
            p.coverage_amount,
            p.policy_status,

            ph.full_name AS policyholder_name,
            ph.date_of_birth,
            ph.gender,
            ph.city,
            ph.state

        FROM insurance_claims AS c
        JOIN insurance_policies AS p
            ON c.policy_id = p.policy_id
        JOIN policyholders AS ph
            ON p.policyholder_id = ph.policyholder_id
        WHERE c.claim_id = ?
    """, (claim_id,))

    claim = cursor.fetchone()
    connection.close()

    return dict(claim) if claim else None

def get_all_claims_with_predictions():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            c.claim_id,
            c.claim_number,
            c.claim_date,
            c.claim_type,
            c.claim_amount,
            c.claim_status,

            ph.full_name AS policyholder_name,
            p.policy_number,
            p.insurance_type,

            fp.predicted_label,
            fp.fraud_probability,
            fp.risk_level,
            fp.model_version,
            fp.prediction_date,
            fp.remarks

        FROM insurance_claims AS c
        JOIN insurance_policies AS p
            ON c.policy_id = p.policy_id
        JOIN policyholders AS ph
            ON p.policyholder_id = ph.policyholder_id
        LEFT JOIN fraud_predictions AS fp
            ON c.claim_id = fp.claim_id

        ORDER BY c.claim_id DESC
    """)

    claims = cursor.fetchall()
    connection.close()

    return [dict(claim) for claim in claims]

def update_claim_status(claim_id, new_status):
    allowed_statuses = ["submitted", "under_review", "approved", "rejected"]

    if new_status not in allowed_statuses:
        raise ValueError(
            "Invalid status. Use: submitted, under_review, approved, or rejected."
        )

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE insurance_claims
        SET claim_status = ?
        WHERE claim_id = ?
    """, (new_status, claim_id))

    connection.commit()

    updated_rows = cursor.rowcount
    connection.close()

    return updated_rows > 0