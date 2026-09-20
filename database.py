"""
ID SHIELD - Cloud-Ready Persistent Database Engine
Supports:
  1. Cloud PostgreSQL (via DATABASE_URL from Neon, Supabase, Render, etc.)
  2. Local Persistent SQLite (fallback when DATABASE_URL is not set)
"""

import os
import json
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "id_shield.db")

IS_POSTGRES = False
if DATABASE_URL and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")):
    # Fix Render's legacy postgres:// prefix for SQLAlchemy / psycopg2
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    IS_POSTGRES = True

def get_db():
    """Returns database connection based on active engine."""
    if IS_POSTGRES:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def _format_query(query):
    """Adapts query parameter placeholders (? for SQLite, %s for PostgreSQL)."""
    if IS_POSTGRES:
        return query.replace("?", "%s")
    return query

def init_db():
    """Initializes schema on whichever database is active."""
    conn = get_db()
    cursor = conn.cursor()

    if IS_POSTGRES:
        # PostgreSQL Schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                selfie_filename TEXT,
                supporting_doc_filename TEXT,
                entered_info TEXT,
                file_type TEXT,
                file_size INTEGER,
                sha256_hash TEXT,
                extracted_text TEXT,
                face_detected INTEGER DEFAULT 0,
                face_count INTEGER DEFAULT 0,
                face_boxes TEXT,
                face_similarity_score REAL DEFAULT 0.0,
                liveness_status TEXT DEFAULT 'PASS',
                tamper_signals TEXT,
                cross_field_status TEXT DEFAULT 'PASS',
                attack_type TEXT DEFAULT 'None / Genuine',
                risk_level TEXT NOT NULL,
                risk_score REAL NOT NULL,
                border_triage TEXT DEFAULT 'CLEAR FOR ENTRY',
                validation_results TEXT,
                risk_reasons TEXT,
                ai_investigation_log TEXT,
                annotated_filename TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    else:
        # SQLite Schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                selfie_filename TEXT,
                supporting_doc_filename TEXT,
                entered_info TEXT,
                file_type TEXT,
                file_size INTEGER,
                sha256_hash TEXT,
                extracted_text TEXT,
                face_detected INTEGER DEFAULT 0,
                face_count INTEGER DEFAULT 0,
                face_boxes TEXT,
                face_similarity_score REAL DEFAULT 0.0,
                liveness_status TEXT DEFAULT 'PASS',
                tamper_signals TEXT,
                cross_field_status TEXT DEFAULT 'PASS',
                attack_type TEXT DEFAULT 'None / Genuine',
                risk_level TEXT NOT NULL,
                risk_score REAL NOT NULL,
                border_triage TEXT DEFAULT 'CLEAR FOR ENTRY',
                validation_results TEXT,
                risk_reasons TEXT,
                ai_investigation_log TEXT,
                annotated_filename TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

        # Backwards compatibility migration check
        cursor.execute("PRAGMA table_info(documents)")
        existing_cols = {row["name"] for row in cursor.fetchall()}
        new_cols = {
            "selfie_filename": "TEXT",
            "supporting_doc_filename": "TEXT",
            "entered_info": "TEXT",
            "face_similarity_score": "REAL DEFAULT 0.0",
            "liveness_status": "TEXT DEFAULT 'PASS'",
            "cross_field_status": "TEXT DEFAULT 'PASS'",
            "attack_type": "TEXT DEFAULT 'None / Genuine'",
            "ai_investigation_log": "TEXT",
            "border_triage": "TEXT DEFAULT 'CLEAR FOR ENTRY'",
            "validation_results": "TEXT"
        }
        for col_name, col_type in new_cols.items():
            if col_name not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE documents ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"Column add notice: {e}")

    conn.commit()
    conn.close()

def register_user(name, email, password):
    email = email.strip().lower()
    name = name.strip()
    if not name or not email or not password:
        return False, "All fields are required."

    password_hash = generate_password_hash(password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        q = _format_query("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)")
        cursor.execute(q, (name, email, password_hash))
        conn.commit()
        if IS_POSTGRES:
            cursor.execute(_format_query("SELECT id FROM users WHERE email = ?"), (email,))
            user_id = cursor.fetchone()[0]
        else:
            user_id = cursor.lastrowid
        return True, {"id": user_id, "name": name, "email": email}
    except Exception as e:
        conn.rollback() if IS_POSTGRES else None
        return False, "An account with this email already exists."
    finally:
        conn.close()

def authenticate_user(email, password):
    email = email.strip().lower()
    conn = get_db()
    cursor = conn.cursor()
    q = _format_query("SELECT id, name, email, password_hash FROM users WHERE email = ?")
    cursor.execute(q, (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password_hash"], password):
        return True, {"id": user["id"], "name": user["name"], "email": user["email"]}
    return False, "Invalid email or password."

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    q = _format_query("SELECT id, name, email, created_at FROM users WHERE id = ?")
    cursor.execute(q, (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def save_document(doc_data):
    conn = get_db()
    cursor = conn.cursor()

    fields = [
        "user_id", "filename", "original_name", "selfie_filename", "supporting_doc_filename",
        "entered_info", "file_type", "file_size", "sha256_hash",
        "extracted_text", "face_detected", "face_count", "face_boxes", "face_similarity_score",
        "liveness_status", "tamper_signals", "cross_field_status", "attack_type",
        "risk_level", "risk_score", "border_triage", "validation_results", "risk_reasons", "ai_investigation_log", "annotated_filename"
    ]
    placeholders = ", ".join(["?" for _ in fields])
    q = f"INSERT INTO documents ({', '.join(fields)}) VALUES ({placeholders})"
    if IS_POSTGRES:
        q += " RETURNING id"
    q = _format_query(q)

    values = (
        doc_data["user_id"],
        doc_data["filename"],
        doc_data["original_name"],
        doc_data.get("selfie_filename", ""),
        doc_data.get("supporting_doc_filename", ""),
        json.dumps(doc_data.get("entered_info", {})),
        doc_data.get("file_type", "unknown"),
        doc_data.get("file_size", 0),
        doc_data.get("sha256_hash", ""),
        json.dumps(doc_data.get("extracted_text", {})),
        1 if doc_data.get("face_detected") else 0,
        doc_data.get("face_count", 0),
        json.dumps(doc_data.get("face_boxes", [])),
        doc_data.get("face_similarity_score", 0.0),
        doc_data.get("liveness_status", "PASS"),
        json.dumps(doc_data.get("tamper_signals", {})),
        doc_data.get("cross_field_status", "PASS"),
        doc_data.get("attack_type", "None / Genuine"),
        doc_data.get("risk_level", "Review"),
        doc_data.get("risk_score", 50.0),
        doc_data.get("border_triage", "CLEAR FOR ENTRY"),
        json.dumps(doc_data.get("validation_results", {})),
        json.dumps(doc_data.get("risk_reasons", [])),
        json.dumps(doc_data.get("ai_investigation_log", {})),
        doc_data.get("annotated_filename", "")
    )

    cursor.execute(q, values)
    conn.commit()
    if IS_POSTGRES:
        doc_id = cursor.fetchone()[0]
    else:
        doc_id = cursor.lastrowid
    conn.close()
    return doc_id

def get_user_documents(user_id):
    conn = get_db()
    cursor = conn.cursor()
    q = _format_query("SELECT * FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC")
    cursor.execute(q, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    docs = []
    for r in rows:
        d = dict(r)
        d["extracted_text"] = json.loads(d["extracted_text"]) if d.get("extracted_text") else {}
        d["face_boxes"] = json.loads(d["face_boxes"]) if d.get("face_boxes") else []
        d["tamper_signals"] = json.loads(d["tamper_signals"]) if d.get("tamper_signals") else {}
        d["risk_reasons"] = json.loads(d["risk_reasons"]) if d.get("risk_reasons") else []
        d["entered_info"] = json.loads(d["entered_info"]) if d.get("entered_info") else {}
        d["ai_investigation_log"] = json.loads(d["ai_investigation_log"]) if d.get("ai_investigation_log") else {}
        d["validation_results"] = json.loads(d["validation_results"]) if d.get("validation_results") else {}
        docs.append(d)
    return docs

def get_document_by_id(doc_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    q = _format_query("SELECT * FROM documents WHERE id = ? AND user_id = ?")
    cursor.execute(q, (doc_id, user_id))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    d = dict(r)
    d["extracted_text"] = json.loads(d["extracted_text"]) if d.get("extracted_text") else {}
    d["face_boxes"] = json.loads(d["face_boxes"]) if d.get("face_boxes") else []
    d["tamper_signals"] = json.loads(d["tamper_signals"]) if d.get("tamper_signals") else {}
    d["risk_reasons"] = json.loads(d["risk_reasons"]) if d.get("risk_reasons") else []
    d["entered_info"] = json.loads(d["entered_info"]) if d.get("entered_info") else {}
    d["ai_investigation_log"] = json.loads(d["ai_investigation_log"]) if d.get("ai_investigation_log") else {}
    d["validation_results"] = json.loads(d["validation_results"]) if d.get("validation_results") else {}
    return d

def delete_document(doc_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    q = _format_query("DELETE FROM documents WHERE id = ? AND user_id = ?")
    cursor.execute(q, (doc_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0
