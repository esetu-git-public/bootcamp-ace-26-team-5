import os
import sys
import unittest
import json
from dotenv import load_dotenv

# Add paths
base_path = "d:/ML bootcamp project/bootcamp-ace-26-team-5/healthcare-fraud-detection"
sys.path.append(os.path.join(base_path, "backend"))

# Load env variables
load_dotenv(os.path.join(base_path, "backend/.env"))

from app import app
from utils.supabase_client import supabase

class TestIntegrationSuite(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.supabase = supabase
        
        # Test emails
        self.cust_email = "test_cust_999@fraudshield.com"
        self.emp_email = "test_emp_999@fraudshield.com"
        self.pwd = "testPass123"

        # Cleanup prior test data to ensure isolation
        if os.getenv("DB_PROVIDER") == "sqlite":
            from utils.sqlite_client import get_sqlite_conn
            try:
                with get_sqlite_conn() as conn:
                    conn.execute("DELETE FROM users WHERE email IN (?, ?)", (self.cust_email, self.emp_email))
                    conn.commit()
            except Exception:
                pass
        else:
            try:
                self.supabase.table("users").delete().eq("email", self.cust_email).execute()
                self.supabase.table("users").delete().eq("email", self.emp_email).execute()
            except Exception:
                pass

    def tearDown(self):
        # Cleanup test accounts from database if they exist
        if os.getenv("DB_PROVIDER") == "sqlite":
            from utils.sqlite_client import get_sqlite_conn
            try:
                with get_sqlite_conn() as conn:
                    conn.execute("DELETE FROM users WHERE email IN (?, ?)", (self.cust_email, self.emp_email))
                    conn.commit()
            except Exception:
                pass
        else:
            try:
                self.supabase.table("users").delete().eq("email", self.cust_email).execute()
                self.supabase.table("users").delete().eq("email", self.emp_email).execute()
            except Exception:
                pass

    def test_01_public_signup_enforces_customer(self):
        # Public signup payload trying to sneak in employee role
        payload = {
            "fullName": "Test Customer Sneak",
            "email": self.cust_email,
            "password": self.pwd,
            "role": "employee" # Should be overwritten to customer
        }
        res = self.app.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 201)
        
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        
        # Retrieve user and assert role is customer
        if os.getenv("DB_PROVIDER") == "sqlite":
            from utils.sqlite_client import get_sqlite_conn
            with get_sqlite_conn() as conn:
                user = conn.execute("SELECT * FROM users WHERE email = ?", (self.cust_email,)).fetchone()
                self.assertIsNotNone(user)
                self.assertEqual(user["role"], "customer")
        else:
            db_res = self.supabase.table("users").select("*").eq("email", self.cust_email).execute()
            self.assertTrue(len(db_res.data) > 0)
            user = db_res.data[0]
            self.assertEqual(user["role"], "customer")

    def test_02_login_and_jwt_authentication(self):
        # Register a valid customer
        reg_payload = {
            "fullName": "Test Customer Auth",
            "email": self.cust_email,
            "password": self.pwd
        }
        self.app.post("/api/auth/register", json=reg_payload)
        
        # Perform login
        login_payload = {
            "email": self.cust_email,
            "password": self.pwd
        }
        res = self.app.post("/api/auth/login", json=login_payload)
        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        
        tokens = data["data"]
        self.assertIn("access_token", tokens)
        self.assertIn("refresh_token", tokens)
        
        user_info = data["data"]["user"]
        self.assertEqual(user_info["role"], "customer")

        # Test JWT role guards (Customer calling Admin reports should be 403 Forbidden)
        headers = {
            "Authorization": f"Bearer {tokens['access_token']}"
        }
        res_reports = self.app.get("/api/reports", headers=headers)
        self.assertEqual(res_reports.status_code, 403)

    def test_03_claim_submission_and_prediction(self):
        # Register and Login customer
        reg_payload = {
            "fullName": "Test Customer Claims",
            "email": self.cust_email,
            "password": self.pwd
        }
        self.app.post("/api/auth/register", json=reg_payload)
        
        login_payload = {"email": self.cust_email, "password": self.pwd}
        log_res = self.app.post("/api/auth/login", json=login_payload)
        tokens = json.loads(log_res.data)["data"]
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Submit a low amount claim (typically low risk) using frontend form format
        claim_payload = {
            "patientName": "Ravi Kumar",
            "claimAmount": 150.0,
            "gender": "Male",
            "age": 30,
            "diagnosis": "I10",
            "hospital": "City Health Center"
        }

        res = self.app.post("/api/claims", json=claim_payload, headers=headers)
        self.assertEqual(res.status_code, 201)
        
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        
        claim_data = data["data"]
        self.assertIn("claim_id", claim_data)
        self.assertIn("claim_status", claim_data)
        
        # Verify entries in database
        if os.getenv("DB_PROVIDER") == "sqlite":
            from utils.sqlite_client import get_sqlite_conn
            with get_sqlite_conn() as conn:
                pred = conn.execute("SELECT * FROM fraud_predictions WHERE claim_id = ?", (claim_data["claim_id"],)).fetchone()
                self.assertIsNotNone(pred)
                
                notif = conn.execute("SELECT * FROM notifications WHERE recipient_id = ?", (claim_data["submitted_by"],)).fetchone()
                self.assertIsNotNone(notif)
                
                audit = conn.execute("SELECT * FROM audit_logs WHERE claim_id = ?", (claim_data["claim_id"],)).fetchone()
                self.assertIsNotNone(audit)
        else:
            # Verify prediction entry
            pred_res = self.supabase.table("fraud_predictions").select("*").eq("claim_id", claim_data["claim_id"]).execute()
            self.assertTrue(len(pred_res.data) > 0)
            
            # Verify notification entry
            notif_res = self.supabase.table("notifications").select("*").eq("recipient_id", claim_data["submitted_by"]).execute()
            self.assertTrue(len(notif_res.data) > 0)
            
            # Verify audit log entry
            audit_res = self.supabase.table("audit_logs").select("*").eq("claim_id", claim_data["claim_id"]).execute()
            self.assertTrue(len(audit_res.data) > 0)

    def test_model_feedback(self):
        # 1. Create a Claims Officer (employee) account
        signup_payload = {
            "fullName": "Test Employee",
            "email": self.emp_email,
            "password": self.pwd,
            "role": "employee"
        }
        self.app.post("/api/auth/register", json=signup_payload)
        
        # Force the database role to 'employee' (bypassing the public registration customer role lock)
        if os.getenv("DB_PROVIDER") == "sqlite":
            from utils.sqlite_client import get_sqlite_conn
            with get_sqlite_conn() as conn:
                conn.execute("UPDATE users SET role = 'employee' WHERE email = ?", (self.emp_email,))
                conn.commit()
        else:
            try:
                self.supabase.table("users").update({"role": "employee"}).eq("email", self.emp_email).execute()
            except Exception:
                pass
        
        # 2. Login employeet access token
        login_payload = {"email": self.emp_email, "password": self.pwd}
        log_res = self.app.post("/api/auth/login", json=login_payload)
        tokens = json.loads(log_res.data)["data"]
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # 3. Submit feedback for claim ID 1 (which always exists in seeded database)
        feedback_payload = {
            "claim_id": 1,
            "is_incorrect": True,
            "actual_label": "Fraud",
            "feedback_text": "Model predicted Not Fraud but medical records indicate potential duplicate claims",
            "model_version": "v1.0"
        }
        
        # Cleanup any pre-existing feedback for claim 1 to prevent unique constraint failures
        if os.getenv("DB_PROVIDER") == "sqlite":
            from utils.sqlite_client import get_sqlite_conn
            with get_sqlite_conn() as conn:
                conn.execute("DELETE FROM model_feedback WHERE claim_id = 1")
                conn.commit()
        else:
            try:
                self.supabase.table("model_feedback").delete().eq("claim_id", 1).execute()
            except Exception as e:
                # If the table is missing in Supabase, skip this test gracefully
                if "PGRST205" in str(e) or "schema cache" in str(e):
                    print("\n[WARNING] Skipping model_feedback integration test because the model_feedback table does not exist in the configured Supabase database. Run database/patches/create_model_feedback.sql in your Supabase editor to resolve.")
                    return
                raise e

        # Submit
        res = self.app.post("/api/feedback", json=feedback_payload, headers=headers)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        self.assertEqual(data["data"]["feedback_text"], feedback_payload["feedback_text"])

        # 4. Try submitting again for the same claim (should fail with 400 bad request)
        res_fail = self.app.post("/api/feedback", json=feedback_payload, headers=headers)
        self.assertEqual(res_fail.status_code, 400)

        # 5. Fetch feedback for claim 1
        res_get = self.app.get("/api/feedback/claim/1", headers=headers)
        self.assertEqual(res_get.status_code, 200)
        data_get = json.loads(res_get.data)
        self.assertIsNotNone(data_get["data"])
        self.assertEqual(data_get["data"]["claim_id"], 1)

        # 6. Fetch stats
        res_stats = self.app.get("/api/feedback/stats", headers=headers)
        self.assertEqual(res_stats.status_code, 200)
        data_stats = json.loads(res_stats.data)
        self.assertIn("accuracy", data_stats["data"])
        self.assertIn("disagreementRate", data_stats["data"])

        # 7. Fetch all feedback list
        res_list = self.app.get("/api/feedback", headers=headers)
        self.assertEqual(res_list.status_code, 200)
        data_list = json.loads(res_list.data)
        self.assertTrue(len(data_list["data"]) > 0)
        
        # Cleanup
        if os.getenv("DB_PROVIDER") == "sqlite":
            from utils.sqlite_client import get_sqlite_conn
            with get_sqlite_conn() as conn:
                conn.execute("DELETE FROM model_feedback WHERE claim_id = 1")
                conn.commit()
        else:
            try:
                self.supabase.table("model_feedback").delete().eq("claim_id", 1).execute()
            except Exception:
                pass

if __name__ == "__main__":
    unittest.main()
