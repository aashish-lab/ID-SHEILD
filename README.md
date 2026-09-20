# ID SHIELD - AI Identity Fraud & Border Checkpoint Travel Document Screening Platform

ID SHIELD is an enterprise-grade AI-powered identity fraud investigation and border screening platform. It automatically inspects travel credentials (passports, visas, national IDs, driver licenses, and permits), detects physical and digital tampering, validates rules against border watchlists, and performs 1:1 facial biometric matching to assist immigration officers and security investigators under high passenger volume.

---

## ⚡ Quick Start

### How to Run:

#### On Windows:
Double-click `run.bat` or run:
```bash
python start.py
```

#### On Terminal:
```bash
pip install -r requirements.txt
python app.py
```

Then open your browser at:
👉 **http://127.0.0.1:5050**

*(Note: Configured on port **5050** to allow parallel execution with other local projects).*

---

## 🛡️ Key Platform Capabilities

### 1. Border Checkpoint Challenges Addressed
- **Fake Passports and Visas**: Counterfeit credentials with non-conforming substrates.
- **Altered Photographs**: Photo replacement, facial contour splicing, and head-swaps.
- **Modified Dates of Birth (DOB)**: Text manipulation to bypass age requirements or quotas.
- **Tampered Visa Stamps**: Forged consular seals, irregular geometry, and ink bleed anomalies.
- **Identity Impersonation**: Impostors presenting genuine stolen travel credentials belonging to look-alikes.
- **Multiple Identities**: Cross-border aliases and conflicting travel documents.
- **Expired / Blacklisted Documents**: Interpol SLTD (Stolen & Lost Travel Documents) hits and border watchlists.
- **High Passenger Volume Delays**: Accelerated automated triage assisting immigration personnel (3-second e-Gate decision support).

---

## 🧩 The 4 Core Screening Modules

### Module 1: OCR Extraction
- **Passport**: Document Number, Full Name, DOB, Expiry Date, Nationality, Gender, and ICAO 9303 Machine Readable Zone (MRZ Lines 1 & 2).
- **Visa**: Visa Number, Category (B1/B2, Work, Transit, Diplomatic), Issue & Expiration Dates, Sponsoring Country, and Visa Stamp Status.
- **National ID**: ID Number, Full Name, DOB, Address, Citizen Category, Expiry Date.
- **Driving License**: License Number, Full Name, DOB, Address, License Class, Expiry Date.
- **Travel Permit**: Permit ID, Holder Name, Authorized Border Port, Validity Window, Sponsoring Authority.

### Module 2: Document Validation (Rules & Watchlists)
- **Expiration Verification**: Real-time legal validity window calculation.
- **DOB & Age Plausibility**: Algorithmic consistency check to detect modified birth dates.
- **ICAO 9303 MRZ Checksums**: 7-3-1 weighting algorithm verification on document serial, birth date, and expiry.
- **Border Watchlist & Interpol SLTD Database Lookup**: Automated cross-referencing against blacklisted stolen credentials.
- **Travel Authorization Status**: Issues `APPROVED`, `SUSPENDED`, or `REVOKED (SECURITY HOLD)`.

### Module 3: Tampering Detection (Image Forensics)
- **Laplacian Variance**: Sharpness, recapture artifact, and blur detection.
- **Edge Density Variation**: 4x4 block-based Canny contour analysis for copy-move splicing detection.
- **Modified DOB Forensics**: Font weight, kerning, and localized pixel compression anomalies.
- **Visa Stamp Analysis**: Stamp boundary geometry, ink bleed, and seal deformation detection.

### Module 4: Face Detection & 1:1 Biometric Comparison
- **OpenCV Facial Cascade**: Fast CPU-accelerated facial portrait extraction.
- **1:1 Biometric Matching**: Cosine similarity and histogram feature correlation comparing credential portrait photo to live traveler camera capture.
- **Impersonation Prevention**: Detects when an impostor attempts to cross using a genuine document.

---

## 🚦 Border Security Personnel Assist Mode

- **CLEAR FOR ENTRY** (Green / Score 0-30): Valid MRZ checksum, zero watchlist hits, authentic visa stamps, and confirmed 1:1 facial biometric match.
- **SECONDARY INSPECTION** (Amber / Score 31-70): Route to Border Control Officer Desk for manual interview or high-resolution scan.
- **DETAIN & INVESTIGATE** (Red / Score 71-100): Critical security alert (Interpol hit, tampered stamp, modified DOB, or identity impersonation).

---

## 🧪 Interactive Screening Scenarios

1. **Border Case A: Genuine Passport with MRZ** (`case_border_passport.jpg`): ICAO 9303 valid, Watchlist clear, Biometrics 96.8% match → **CLEAR FOR ENTRY** (Score: 6/100).
2. **Border Case B: Tampered Visa Stamp & Modified DOB** (`case_border_tampered_visa.jpg`): Forged stamp geometry and spliced DOB detected → **DETAIN & INVESTIGATE** (Score: 84/100).
3. **Border Case C: Stolen / Blacklisted Credential** (`case_border_blacklist.jpg`): Interpol SLTD stolen document hit → **DETAIN & INVESTIGATE** (Score: 96/100).
4. **Case 1: Genuine Citizen Identity**: Cross-field consistency 100% verified → **LOW RISK** (Score: 6/100).
5. **Case 2: Tampered Document**: Localized text splicing highlighted in red box → **HIGH RISK** (Score: 84/100).
6. **Case 3: Identity Mismatch**: Live selfie does not match document portrait (38.4%) → **HIGH RISK** (Score: 92/100).

---

## 🤖 Ask the AI Investigation Assistant

Investigators can query the embedded explainability engine using natural language:
- *"Why was this identity flagged?"*
- *"Verify ICAO 9303 MRZ lines and checksums"*
- *"Check Border Watchlist and Interpol database status"*
- *"Check visa stamp authenticity and altered DOB"*
- *"Explain traveler face match confidence"*
- *"What are the recommended next steps?"*

---

## 📁 Repository Structure

```
id-shield/
├── app.py                  # Flask server & REST API (Port 5050)
├── analyzer.py             # 4-Module Screening Engine (OCR, Rules/MRZ, Tampering, Face Biometrics)
├── database.py             # SQLite database manager (id_shield.db)
├── generate_samples.py     # Test document generator for Border & KYC cases
├── test_system.py          # 5-Suite automated testing framework
├── start.py                # Cross-platform Python launcher
├── run.bat                 # 1-Click Windows batch launcher
├── requirements.txt        # Python dependencies
├── README.md               # Complete platform guide
├── templates/
│   └── index.html          # Dark glassmorphism border screening & KYC dashboard
└── static/
    ├── css/style.css       # Custom cyber glow & border control styling
    ├── js/app.js           # Interactive triage, MRZ viewer, and AI assistant logic
    ├── auth-bg.png         # Cyber shield wallpaper
    └── uploads/            # Document storage & OpenCV annotated outputs
```
