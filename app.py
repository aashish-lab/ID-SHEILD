import os
import secrets
import shutil
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
import database
import analyzer

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "id-shield-secret-" + secrets.token_hex(16))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf", "bmp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
database.init_db()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure samples exist
try:
    from generate_samples import generate_test_samples
    if not os.path.exists(os.path.join(UPLOAD_FOLDER, "case1_doc.jpg")):
        generate_test_samples(UPLOAD_FOLDER)
except Exception as e:
    print(f"Sample generation note: {e}")

# ----------------- PAGE ROUTES -----------------

@app.route("/")
def index():
    return render_template("index.html")

# ----------------- AUTHENTICATION API -----------------

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not name or not email or not password:
        return jsonify({"success": False, "message": "All fields (Name, Email, Password) are required."}), 400

    if len(password) < 4:
        return jsonify({"success": False, "message": "Password should be at least 4 characters long."}), 400

    success, result = database.register_user(name, email, password)
    if not success:
        return jsonify({"success": False, "message": result}), 400

    session["user_id"] = result["id"]
    return jsonify({
        "success": True,
        "message": "Account created successfully! Welcome to ID Shield.",
        "user": result
    })

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    success, result = database.authenticate_user(email, password)
    if not success:
        return jsonify({"success": False, "message": result}), 401

    session["user_id"] = result["id"]
    return jsonify({
        "success": True,
        "message": "Login successful! Welcome back.",
        "user": result
    })

@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    new_password = data.get("new_password", "").strip()

    if not email or not new_password:
        return jsonify({"success": False, "message": "Email and new password are required."}), 400

    if len(new_password) < 4:
        return jsonify({"success": False, "message": "Password should be at least 4 characters long."}), 400

    success, message = database.reset_user_password(email, new_password)
    if not success:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({"success": True, "message": message})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route("/api/me", methods=["GET"])
def get_me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False}), 200
    user = database.get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({"authenticated": False}), 200
    return jsonify({"authenticated": True, "user": user})

# ----------------- MULTI-MODAL DOCUMENT & INVESTIGATION API -----------------

@app.route("/api/upload", methods=["POST"])
def upload_document():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Authentication required. Please sign in."}), 401

    sample_case = request.form.get("sample_case")
    selfie_path = None
    supporting_path = None
    explicit_doc_type = request.form.get("doc_type")

    if sample_case:
        # Pre-packaged case execution
        case_id = sample_case.strip().lower()
        if case_id in ["case1", "case 1", "genuine"]:
            doc_name = "case1_doc.jpg"
            orig_title = "CITIZEN IDENTITY CARD (CASE 1 - GENUINE)"
            selfie_name = "case1_selfie.jpg"
            explicit_doc_type = "National ID"
            entered_info = {"name": "CITIZEN HOLDER", "dob": "1992-06-18", "id_number": "ID-90214812"}
        elif case_id in ["case2", "case 2", "tampered"]:
            doc_name = "case2_doc.jpg"
            orig_title = "NATIONAL ID CARD (CASE 2 - TAMPERED)"
            selfie_name = None
            explicit_doc_type = "National ID"
            entered_info = {"name": "ALTERED / FORGED USER", "dob": "1988-03-22", "id_number": "ID-99482-INVALID"}
        elif case_id in ["case3", "case 3", "mismatch"]:
            doc_name = "case3_doc.jpg"
            orig_title = "DRIVER LICENSE (CASE 3 - IDENTITY MISMATCH)"
            selfie_name = "case3_selfie.jpg"
            explicit_doc_type = "Driving License"
            entered_info = {"name": "VERIFIED CITIZEN", "dob": "1991-04-12", "id_number": "DL-88219044"}
        elif case_id in ["border_case1", "border_passport", "border_genuine"]:
            doc_name = "case_border_passport.jpg"
            orig_title = "TRAVEL PASSPORT (BORDER SCREENING - GENUINE WITH MRZ)"
            selfie_name = "case_border_passport_selfie.jpg"
            explicit_doc_type = "Passport"
            entered_info = {"name": "ALEXANDER CHEN", "dob": "1994-08-14", "id_number": "P98421074"}
        elif case_id in ["border_case2", "border_tampered_visa", "tampered_stamp"]:
            doc_name = "case_border_tampered_visa.jpg"
            orig_title = "TRAVEL PASSPORT & VISA (BORDER SCREENING - TAMPERED STAMP & MODIFIED DOB)"
            selfie_name = None
            explicit_doc_type = "Passport"
            entered_info = {"name": "ALTERED / FORGED USER", "dob": "1988-03-22", "id_number": "P984210-FORGED"}
        elif case_id in ["border_case3", "border_blacklist", "watchlist_hit"]:
            doc_name = "case_border_blacklist.jpg"
            orig_title = "TRAVEL PASSPORT (BORDER SCREENING - WATCHLIST / BLACKLIST HIT)"
            selfie_name = None
            explicit_doc_type = "Passport"
            entered_info = {"name": "SANCTIONED TRAVELER", "dob": "1990-01-01", "id_number": "P-BLOCKED-902"}
        else:
            doc_name = "case1_doc.jpg"
            orig_title = "CITIZEN IDENTITY CARD (CASE 1 - GENUINE)"
            selfie_name = "case1_selfie.jpg"
            explicit_doc_type = "National ID"
            entered_info = {"name": "CITIZEN HOLDER", "dob": "1992-06-18", "id_number": "ID-90214812"}

        src_doc = os.path.join(UPLOAD_FOLDER, doc_name)
        if not os.path.exists(src_doc):
            generate_test_samples(UPLOAD_FOLDER)

        unique_token = secrets.token_hex(4)
        target_filename = f"{unique_token}_{doc_name}"
        target_path = os.path.join(UPLOAD_FOLDER, target_filename)
        shutil.copyfile(src_doc, target_path)
        original_name = orig_title

        if selfie_name:
            src_selfie = os.path.join(UPLOAD_FOLDER, selfie_name)
            target_selfie_name = f"{unique_token}_{selfie_name}"
            selfie_path = os.path.join(UPLOAD_FOLDER, target_selfie_name)
            shutil.copyfile(src_selfie, selfie_path)
    else:
        # Custom Multi-Modal Upload
        if "document" not in request.files:
            return jsonify({"success": False, "message": "No identity document file provided."}), 400
        
        file = request.files["document"]
        if file.filename == "":
            return jsonify({"success": False, "message": "No document file selected."}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"success": False, "message": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

        orig_clean = secure_filename(file.filename) or f"doc_{secrets.token_hex(4)}.jpg"
        unique_token = secrets.token_hex(6)
        target_filename = f"{unique_token}_{orig_clean}"
        target_path = os.path.join(UPLOAD_FOLDER, target_filename)
        file.save(target_path)
        original_name = file.filename

        # Optional Live Selfie
        if "selfie" in request.files and request.files["selfie"].filename != "":
            s_file = request.files["selfie"]
            s_clean = secure_filename(s_file.filename)
            s_target = f"{unique_token}_selfie_{s_clean}"
            selfie_path = os.path.join(UPLOAD_FOLDER, s_target)
            s_file.save(selfie_path)

        # Optional Supporting Document
        if "supporting_doc" in request.files and request.files["supporting_doc"].filename != "":
            sup_file = request.files["supporting_doc"]
            sup_clean = secure_filename(sup_file.filename)
            sup_target = f"{unique_token}_sup_{sup_clean}"
            supporting_path = os.path.join(UPLOAD_FOLDER, sup_target)
            sup_file.save(supporting_path)

        entered_info = {
            "name": request.form.get("entered_name", "").strip(),
            "dob": request.form.get("entered_dob", "").strip(),
            "id_number": request.form.get("entered_id", "").strip()
        }

    # Execute ID Shield 4-Module Screening Pipeline
    try:
        pipeline_result = analyzer.run_document_pipeline(
            target_path,
            original_name,
            user_id,
            selfie_path=selfie_path,
            supporting_path=supporting_path,
            entered_info=entered_info,
            explicit_type=explicit_doc_type
        )
        
        doc_id = database.save_document(pipeline_result)
        pipeline_result["id"] = doc_id
        
        return jsonify({
            "success": True,
            "message": "Fraud investigation pipeline completed and saved to SQLite.",
            "data": pipeline_result
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Pipeline execution error: {str(e)}"}), 500

# ----------------- ASK THE AI INVESTIGATION ASSISTANT -----------------

@app.route("/api/ask-ai", methods=["POST"])
def ask_ai():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Authentication required."}), 401

    data = request.get_json() or {}
    query = data.get("query", "").strip()
    doc_id = data.get("doc_id")

    if not query:
        return jsonify({"success": False, "message": "Query cannot be empty."}), 400

    if not doc_id:
        return jsonify({"success": False, "message": "Document reference ID is required."}), 400

    doc = database.get_document_by_id(doc_id, user_id)
    if not doc:
        return jsonify({"success": False, "message": "Document not found."}), 404

    answer = analyzer.answer_ai_query(query, doc)
    return jsonify({"success": True, "answer": answer})

@app.route("/api/documents", methods=["GET"])
def list_documents():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Authentication required."}), 401
    docs = database.get_user_documents(user_id)
    return jsonify({"success": True, "documents": docs})

@app.route("/api/documents/<int:doc_id>", methods=["GET"])
def get_document(doc_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Authentication required."}), 401
    doc = database.get_document_by_id(doc_id, user_id)
    if not doc:
        return jsonify({"success": False, "message": "Document not found."}), 404
    return jsonify({"success": True, "document": doc})

@app.route("/api/documents/<int:doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Authentication required."}), 401
    doc = database.get_document_by_id(doc_id, user_id)
    if not doc:
        return jsonify({"success": False, "message": "Document not found."}), 404
    
    try:
        f1 = os.path.join(UPLOAD_FOLDER, doc["filename"])
        if os.path.exists(f1): os.remove(f1)
        if doc.get("annotated_filename"):
            f2 = os.path.join(UPLOAD_FOLDER, doc["annotated_filename"])
            if os.path.exists(f2): os.remove(f2)
        if doc.get("selfie_filename"):
            f3 = os.path.join(UPLOAD_FOLDER, doc["selfie_filename"])
            if os.path.exists(f3): os.remove(f3)
    except Exception as e:
        print(f"File cleanup error: {e}")

    deleted = database.delete_document(doc_id, user_id)
    return jsonify({"success": deleted, "message": "Document record deleted."})

@app.route("/api/demo-cases", methods=["GET"])
def get_demo_cases():
    cases = [
        {
            "id": "case1",
            "category": "Identity Fraud",
            "title": "Case 1: Genuine Identity",
            "risk_label": "LOW RISK",
            "score": "6/100",
            "badges": {"Document": "PASS", "OCR": "PASS", "Face": "PASS", "Liveness": "PASS", "Consistency": "PASS"},
            "description": "Authentic citizen identity card with verified biometric facial match and 100% cross-field consistency.",
            "preview": "/static/uploads/case1_doc.jpg"
        },
        {
            "id": "case2",
            "category": "Identity Fraud",
            "title": "Case 2: Tampered Document",
            "risk_label": "HIGH RISK",
            "score": "84/100",
            "badges": {"Document": "FAIL", "OCR": "PASS", "Face": "PASS", "Tampering": "FAIL", "Consistency": "REVIEW"},
            "description": "Localized text manipulation and edge splicing detected around document number and name field.",
            "preview": "/static/uploads/case2_doc.jpg"
        },
        {
            "id": "case3",
            "category": "Identity Fraud",
            "title": "Case 3: Identity Mismatch",
            "risk_label": "HIGH RISK",
            "score": "92/100",
            "badges": {"Document": "PASS", "Face Match": "FAILED", "Similarity": "38.4%", "Consistency": "FAILED"},
            "description": "Document Photo ≠ Live Photo. Facial similarity failed threshold, indicating synthetic or impersonation attempt.",
            "preview": "/static/uploads/case3_doc.jpg"
        },
        {
            "id": "border_case1",
            "category": "Border Checkpoint",
            "title": "Border Case A: Genuine Passport with MRZ",
            "risk_label": "CLEAR FOR ENTRY",
            "score": "6/100",
            "badges": {"MRZ": "VALID", "Watchlist": "CLEAR", "Visa Stamp": "AUTHENTIC", "Face Biometrics": "PASS (96.8%)"},
            "description": "Valid Machine Readable Zone (ICAO 9303), zero watchlist hits, and verified traveler biometric match.",
            "preview": "/static/uploads/case_border_passport.jpg"
        },
        {
            "id": "border_case2",
            "category": "Border Checkpoint",
            "title": "Border Case B: Tampered Visa Stamp & Modified DOB",
            "risk_label": "DETAIN & INVESTIGATE",
            "score": "84/100",
            "badges": {"MRZ": "CHECKSUM ALERT", "Visa Stamp": "TAMPERED", "DOB": "MODIFIED", "Triage": "DETAIN"},
            "description": "Forged visa endorsement stamp geometry, ink bleed, and spliced date of birth field detected.",
            "preview": "/static/uploads/case_border_tampered_visa.jpg"
        },
        {
            "id": "border_case3",
            "category": "Border Checkpoint",
            "title": "Border Case C: Stolen Credential / Watchlist Hit",
            "risk_label": "DETAIN & INVESTIGATE",
            "score": "96/100",
            "badges": {"Watchlist": "HIT (INTERPOL)", "Status": "STOLEN DOC", "Travel Auth": "REVOKED", "Triage": "DETAIN"},
            "description": "Stolen passport match against Interpol SLTD database. Travel authorization permanently revoked.",
            "preview": "/static/uploads/case_border_blacklist.jpg"
        }
    ]
    return jsonify({"success": True, "cases": cases})

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/api/network-info", methods=["GET"])
def get_network_info():
    # Detect single permanent cloud URL or local host
    app_url = os.environ.get("APP_URL")
    if not app_url:
        app_url = request.host_url.rstrip("/")

    is_cloud = "onrender.com" in app_url or bool(os.environ.get("RENDER")) or bool(os.environ.get("PORT"))

    return jsonify({
        "success": True,
        "network": {
            "is_cloud": is_cloud,
            "permanent_url": app_url,
            "database_type": "Cloud PostgreSQL" if database.IS_POSTGRES else "Persistent SQLite",
            "status": "online"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print("=" * 70)
    print("  ID SHIELD - 24/7 CLOUD-READY PERSISTENCE SERVER")
    print(f"  * Listening Port      : {port}")
    print(f"  * Database Engine     : {'Cloud PostgreSQL' if database.IS_POSTGRES else 'SQLite (id_shield.db)'}")
    print(f"  * Deployment Mode     : {'Production Cloud' if os.environ.get('PORT') else 'Local Workstation'}")
    print("=" * 70)

    # Bind to 0.0.0.0 so all network interfaces can connect
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

