import os
import unittest
import database
import analyzer
from app import app

class TestIDShieldSystem(unittest.TestCase):
    def setUp(self):
        database.init_db()
        self.client = app.test_client()
        self.client.testing = True

    def test_01_user_authentication(self):
        email = f"user_{os.urandom(4).hex()}@idshield.dev"
        ok, user = database.register_user("Investigator", email, "securepass")
        self.assertTrue(ok)
        
        auth_ok, auth_user = database.authenticate_user(email, "securepass")
        self.assertTrue(auth_ok)
        self.assertEqual(auth_user["id"], user["id"])

    def test_02_three_general_demo_cases(self):
        upload_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
        
        # Case 1: Genuine Identity
        c1 = analyzer.run_document_pipeline(
            os.path.join(upload_dir, "case1_doc.jpg"),
            "case1_doc.jpg",
            1,
            selfie_path=os.path.join(upload_dir, "case1_selfie.jpg")
        )
        self.assertEqual(c1["risk_level"], "Low Risk")
        self.assertLessEqual(c1["risk_score"], 30.0)
        self.assertEqual(c1["border_triage"], "CLEAR FOR ENTRY")
        self.assertEqual(c1["attack_type"], "None / Genuine Identity")
        self.assertEqual(c1["cross_field_status"], "PASS")

        # Case 2: Tampered Document
        c2 = analyzer.run_document_pipeline(
            os.path.join(upload_dir, "case2_doc.jpg"),
            "case2_doc.jpg",
            1
        )
        self.assertEqual(c2["risk_level"], "High Risk")
        self.assertGreater(c2["risk_score"], 70.0)
        self.assertEqual(c2["border_triage"], "DETAIN & INVESTIGATE")
        self.assertTrue(c2["tamper_signals"]["tamper_edge_splicing_detected"])

        # Case 3: Identity Mismatch
        c3 = analyzer.run_document_pipeline(
            os.path.join(upload_dir, "case3_doc.jpg"),
            "case3_doc.jpg",
            1,
            selfie_path=os.path.join(upload_dir, "case3_selfie.jpg")
        )
        self.assertEqual(c3["risk_level"], "High Risk")
        self.assertGreater(c3["risk_score"], 70.0)
        self.assertEqual(c3["border_triage"], "DETAIN & INVESTIGATE")
        self.assertEqual(c3["attack_type"], "Identity Impersonation")

    def test_03_border_checkpoint_modules(self):
        upload_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")

        # Border Case A: Genuine Travel Passport with MRZ
        c_pass = analyzer.run_document_pipeline(
            os.path.join(upload_dir, "case_border_passport.jpg"),
            "case_border_passport.jpg",
            1,
            selfie_path=os.path.join(upload_dir, "case_border_passport_selfie.jpg"),
            explicit_type="Passport"
        )
        self.assertEqual(c_pass["extracted_text"]["document_type"], "Passport")
        self.assertIn("mrz_line1", c_pass["extracted_text"])
        self.assertEqual(c_pass["border_triage"], "CLEAR FOR ENTRY")
        self.assertEqual(c_pass["validation_results"]["travel_authorization"], "APPROVED (AUTOMATED CLEARANCE)")
        self.assertFalse(c_pass["validation_results"]["is_blacklisted"])

        # Border Case B: Tampered Visa Stamp & Modified DOB
        c_visa = analyzer.run_document_pipeline(
            os.path.join(upload_dir, "case_border_tampered_visa.jpg"),
            "case_border_tampered_visa.jpg",
            1,
            explicit_type="Passport"
        )
        self.assertTrue(c_visa["tamper_signals"]["tampered_visa_stamp_detected"])
        self.assertTrue(c_visa["tamper_signals"]["modified_dob_detected"])
        self.assertEqual(c_visa["border_triage"], "DETAIN & INVESTIGATE")

        # Border Case C: Blacklisted / Stolen Credential (Interpol SLTD)
        c_bl = analyzer.run_document_pipeline(
            os.path.join(upload_dir, "case_border_blacklist.jpg"),
            "case_border_blacklist.jpg",
            1,
            explicit_type="Passport"
        )
        self.assertTrue(c_bl["validation_results"]["is_blacklisted"])
        self.assertIn("SLTD", c_bl["validation_results"]["blacklist_reason"])
        self.assertEqual(c_bl["border_triage"], "DETAIN & INVESTIGATE")

    def test_04_ask_ai_assistant(self):
        upload_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
        res = analyzer.run_document_pipeline(
            os.path.join(upload_dir, "case_border_passport.jpg"),
            "case_border_passport.jpg",
            1,
            explicit_type="Passport"
        )
        doc_id = database.save_document(res)
        doc = database.get_document_by_id(doc_id, 1)
        
        # Query MRZ
        answer_mrz = analyzer.answer_ai_query("Verify MRZ lines and checksums", doc)
        self.assertIn("MRZ Line", answer_mrz)
        
        # Query Watchlist
        answer_wl = analyzer.answer_ai_query("Check Watchlist status", doc)
        self.assertIn("CLEAR", answer_wl)

    def test_05_api_demo_cases(self):
        signup_res = self.client.post("/api/signup", json={
            "name": "API Tester",
            "email": f"api_{os.urandom(4).hex()}@idshield.dev",
            "password": "pass"
        })
        self.assertEqual(signup_res.status_code, 200)

        # Upload border demo case 1
        upload_res = self.client.post("/api/upload", data={"sample_case": "border_case1"})
        self.assertEqual(upload_res.status_code, 200)
        data = upload_res.get_json()["data"]
        self.assertEqual(data["border_triage"], "CLEAR FOR ENTRY")
        self.assertIn("mrz_line1", data["extracted_text"])

if __name__ == "__main__":
    unittest.main()
