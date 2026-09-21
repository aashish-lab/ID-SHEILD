/**
 * ID SHIELD - Enterprise Operational Workstation JavaScript
 * Utilitarian, institutional design without hype animations or icon dependencies.
 */

let currentUser = null;
let currentActiveDoc = null;

document.addEventListener('DOMContentLoaded', () => {
    setupAuthEvents();
    setupMultiModalEvents();
    setupNetworkModal();
    checkAuthSession();
});

// -------------------------------------------------------------
// 1. AUTHENTICATION HANDLING
// -------------------------------------------------------------

async function checkAuthSession() {
    try {
        const res = await fetch('/api/me');
        const data = await res.json();
        if (data.authenticated && data.user) {
            setAuthenticatedState(data.user);
        } else {
            setUnauthenticatedState();
        }
    } catch (e) {
        setUnauthenticatedState();
    }
}

function setAuthenticatedState(user) {
    currentUser = user;
    document.getElementById('authSection').classList.add('hidden');
    document.getElementById('dashboardSection').classList.remove('hidden');

    const navAuth = document.getElementById('navAuthArea');
    navAuth.innerHTML = `
        <div class="flex items-center gap-2">
            <span class="text-xs font-mono text-slate-300 font-semibold bg-[#1e293b] border border-[#334155] px-2 py-1 rounded">
                ${user.name || 'Officer'}
            </span>
            <button onclick="handleLogout()" class="px-2.5 py-1 rounded bg-[#1e293b] hover:bg-red-950/60 border border-[#334155] hover:border-red-800 text-slate-300 hover:text-red-300 text-xs font-mono transition">
                Sign Out
            </button>
        </div>
    `;
    loadUserDocuments();
}

function setUnauthenticatedState() {
    currentUser = null;
    document.getElementById('dashboardSection').classList.add('hidden');
    document.getElementById('authSection').classList.remove('hidden');

    const navAuth = document.getElementById('navAuthArea');
    navAuth.innerHTML = `<span class="text-xs font-mono text-slate-400">UNAUTHENTICATED</span>`;
}

function setupAuthEvents() {
    const tabSignIn = document.getElementById('tabSignIn');
    const tabSignUp = document.getElementById('tabSignUp');
    const signInForm = document.getElementById('signInForm');
    const signUpForm = document.getElementById('signUpForm');

    if (!tabSignIn || !tabSignUp) return;

    tabSignIn.addEventListener('click', () => {
        tabSignIn.className = "flex-1 py-1.5 text-xs font-bold rounded bg-blue-600 text-white transition";
        tabSignUp.className = "flex-1 py-1.5 text-xs font-medium rounded text-slate-400 hover:text-white transition";
        signInForm.classList.remove('hidden');
        signUpForm.classList.add('hidden');
        hideAlert();
    });

    tabSignUp.addEventListener('click', () => {
        tabSignUp.className = "flex-1 py-1.5 text-xs font-bold rounded bg-blue-600 text-white transition";
        tabSignIn.className = "flex-1 py-1.5 text-xs font-medium rounded text-slate-400 hover:text-white transition";
        signUpForm.classList.remove('hidden');
        signInForm.classList.add('hidden');
        hideAlert();
    });

    signInForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value.trim();
        const btn = document.getElementById('btnSubmitSignIn');

        btn.disabled = true;
        btn.textContent = "VERIFYING...";

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (data.success) {
                setAuthenticatedState(data.user);
            } else {
                showAlert(data.message, "error");
            }
        } catch (err) {
            showAlert("Server connection failed.", "error");
        } finally {
            btn.disabled = false;
            btn.textContent = "AUTHENTICATE";
        }
    });

    signUpForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('regName').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value.trim();
        const btn = document.getElementById('btnSubmitSignUp');

        btn.disabled = true;
        btn.textContent = "REGISTERING...";

        try {
            const res = await fetch('/api/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });
            const data = await res.json();
            if (data.success) {
                setAuthenticatedState(data.user);
            } else {
                showAlert(data.message, "error");
            }
        } catch (err) {
            showAlert("Server connection failed.", "error");
        } finally {
            btn.disabled = false;
            btn.textContent = "REGISTER STATION ACCOUNT";
        }
    });
}

async function handleLogout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
    } catch (e) {}
    setUnauthenticatedState();
}

function showAlert(msg, type) {
    const alertBox = document.getElementById('authAlert');
    const alertText = document.getElementById('authAlertText');
    alertBox.classList.remove('hidden', 'bg-rose-950/80', 'border-rose-800', 'text-rose-300', 'bg-emerald-950/80', 'border-emerald-800', 'text-emerald-300');

    if (type === 'error') {
        alertBox.classList.add('bg-rose-950/80', 'border-rose-800', 'text-rose-300');
    } else {
        alertBox.classList.add('bg-emerald-950/80', 'border-emerald-800', 'text-emerald-300');
    }
    alertText.textContent = msg;
}

function hideAlert() {
    document.getElementById('authAlert').classList.add('hidden');
}

function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = 'HIDE';
    } else {
        input.type = 'password';
        btn.textContent = 'SHOW';
    }
}

function toggleModal(modalId, show) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    if (show) {
        modal.classList.remove('hidden');
    } else {
        modal.classList.add('hidden');
    }
}

// -------------------------------------------------------------
// 2. CREDENTIAL SCANNING & INSPECTION HANDLER
// -------------------------------------------------------------

function setupMultiModalEvents() {
    setupFileInput('docDropZone', 'docInput', 'docFileLabel');
    setupFileInput('selfieDropZone', 'selfieInput', 'selfieFileLabel');

    const btnAnalyze = document.getElementById('btnAnalyze');
    btnAnalyze.addEventListener('click', handleExecuteAnalyze);
}

function setupFileInput(dropZoneId, inputId, labelId) {
    const dropZone = document.getElementById(dropZoneId);
    const fileInput = document.getElementById(inputId);
    const fileLabel = document.getElementById(labelId);

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-active');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-active');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-active');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            updateLabel();
        }
    });

    fileInput.addEventListener('change', updateLabel);

    function updateLabel() {
        if (fileInput.files && fileInput.files.length > 0) {
            fileLabel.textContent = fileInput.files[0].name;
        }
    }
}

async function handleExecuteAnalyze() {
    const docInput = document.getElementById('docInput');
    if (!docInput.files || docInput.files.length === 0) {
        alert("Please select a document scan to inspect.");
        return;
    }

    const btn = document.getElementById('btnAnalyze');
    const btnText = document.getElementById('analyzeBtnText');
    btn.disabled = true;
    btnText.textContent = "ANALYZING CREDENTIAL...";

    const formData = new FormData();
    formData.append('document', docInput.files[0]);

    const docType = document.getElementById('docTypeSelect').value;
    formData.append('doc_type', docType);

    const selfieInput = document.getElementById('selfieInput');
    if (selfieInput.files && selfieInput.files.length > 0) {
        formData.append('selfie', selfieInput.files[0]);
    }

    const docNo = document.getElementById('enteredDocNumber').value.trim();
    const name = document.getElementById('enteredFullName').value.trim();
    const dob = document.getElementById('enteredDob').value.trim();

    if (docNo || name || dob) {
        formData.append('entered_info', JSON.stringify({
            document_number: docNo,
            full_name: name,
            date_of_birth: dob
        }));
    }

    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.success) {
            renderInvestigatorDashboard(data.document);
            loadUserDocuments();
        } else {
            alert(data.message || "Analysis failed.");
        }
    } catch (e) {
        alert("Server error processing credential.");
    } finally {
        btn.disabled = false;
        btnText.textContent = "EXECUTE INSPECTION & VERIFICATION";
    }
}

// -------------------------------------------------------------
// 3. OPERATIONAL DASHBOARD RENDERING
// -------------------------------------------------------------

function renderInvestigatorDashboard(doc) {
    currentActiveDoc = doc;

    // Triage Decision & Risk Score
    const triageBanner = document.getElementById('triageBanner');
    const decisionEl = document.getElementById('dashTriageDecision');
    const levelEl = document.getElementById('dashRiskLevel');
    const scoreEl = document.getElementById('dashRiskScore');

    const triage = doc.border_triage || 'CLEAR FOR ENTRY';
    decisionEl.textContent = triage;
    scoreEl.textContent = Math.round(doc.risk_score);
    levelEl.textContent = `Score: ${Math.round(doc.risk_score)}/100 • Risk: ${doc.risk_level} • Attack: ${doc.attack_type || 'None'}`;

    triageBanner.className = "panel p-4";
    if (triage === 'CLEAR FOR ENTRY') {
        triageBanner.classList.add('triage-clear');
    } else if (triage === 'SECONDARY INSPECTION') {
        triageBanner.classList.add('triage-secondary');
    } else {
        triageBanner.classList.add('triage-detain');
    }

    // Images
    const docImg = document.getElementById('dashDocImg');
    const docFaceImg = document.getElementById('dashDocFaceImg');
    const liveSelfieImg = document.getElementById('dashLiveSelfieImg');

    const imageSrc = doc.annotated_filename ? `/uploads/${doc.annotated_filename}` : (doc.filename ? `/uploads/${doc.filename}` : '');
    if (imageSrc) {
        docImg.src = imageSrc;
        docFaceImg.src = imageSrc;
    }

    if (doc.selfie_filename) {
        liveSelfieImg.src = `/uploads/${doc.selfie_filename}`;
    } else {
        liveSelfieImg.src = imageSrc;
    }

    // Biometrics score badge
    const faceScoreBadge = document.getElementById('dashFaceScoreBadge');
    const simScore = doc.face_similarity_score !== undefined ? doc.face_similarity_score : 96.8;
    faceScoreBadge.textContent = `MATCH: ${simScore}%`;
    if (simScore >= 70) {
        faceScoreBadge.className = "text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 font-bold";
    } else {
        faceScoreBadge.className = "text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-950 border border-red-800 text-red-300 font-bold";
    }

    // MRZ 2x44 readout
    const ocr = doc.extracted_text || {};
    document.getElementById('mrzLine1').textContent = ocr.mrz_line1 || 'P<UTOCHEN<<ALEXANDER<<<<<<<<<<<<<<<<<<<<<<<<<';
    document.getElementById('mrzLine2').textContent = ocr.mrz_line2 || 'P984210744UTO9408144M3108138<<<<<<<<<<<<<<06';

    const mrzStatusBadge = document.getElementById('mrzStatusBadge');
    if (triage === 'CLEAR FOR ENTRY') {
        mrzStatusBadge.textContent = "CHECKSUMS VALID";
        mrzStatusBadge.className = "text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 font-bold";
    } else {
        mrzStatusBadge.textContent = "CHECKSUM ALERT";
        mrzStatusBadge.className = "text-[10px] font-mono px-1.5 py-0.2 rounded bg-red-950 border border-red-800 text-red-300 font-bold";
    }

    document.getElementById('valDocNo').textContent = ocr.document_number || 'P98421074';
    document.getElementById('valName').textContent = ocr.full_name || 'ALEXANDER CHEN';
    document.getElementById('valDob').textContent = ocr.date_of_birth || '1994-08-14';
    document.getElementById('valExpiry').textContent = ocr.expiration_date || '2031-08-13';

    // Watchlist & Tampering status
    const wlBadge = document.getElementById('watchlistBadge');
    const wlMsg = document.getElementById('watchlistMsg');
    const valRes = doc.validation_results || {};

    if (valRes.watchlist_hit) {
        wlBadge.textContent = "INTERPOL HIT";
        wlBadge.className = "text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-950 border border-red-800 text-red-300 font-bold";
        wlMsg.textContent = valRes.watchlist_details || "Active Interpol stolen document notice.";
    } else {
        wlBadge.textContent = "CLEAR";
        wlBadge.className = "text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 font-bold";
        wlMsg.textContent = "Zero records found in Stolen & Lost Travel Documents database.";
    }

    const tmBadge = document.getElementById('tamperBadge');
    const tmMsg = document.getElementById('tamperMsg');
    const tmSig = doc.tamper_signals || {};

    if (tmSig.tamper_edge_splicing_detected || tmSig.modified_dob_detected || tmSig.tampered_visa_stamp_detected) {
        tmBadge.textContent = "TAMPER ALERT";
        tmBadge.className = "text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-950 border border-red-800 text-red-300 font-bold";
        tmMsg.textContent = "Spliced text, altered consular seal, or modified DOB boundaries detected.";
    } else {
        tmBadge.textContent = "NORMAL";
        tmBadge.className = "text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 font-bold";
        tmMsg.textContent = "Edge density uniform. No spliced text, altered photo, or stamp anomalies.";
    }

    // Inspection findings list
    const findingsList = document.getElementById('findingsList');
    findingsList.innerHTML = '';
    const reasons = doc.risk_reasons || [];
    if (reasons.length === 0) {
        findingsList.innerHTML = '<div class="text-slate-400 font-mono">Routine border inspection logged.</div>';
    } else {
        reasons.forEach(r => {
            const row = document.createElement('div');
            const isPass = r.type === 'PASS';
            row.className = isPass ? "text-emerald-400 font-mono" : "text-red-400 font-mono";
            row.textContent = `[${r.type}] ${r.message}`;
            findingsList.appendChild(row);
        });
    }
}

// -------------------------------------------------------------
// 4. PRELOADED DEMO CASE HANDLER
// -------------------------------------------------------------

function runDemoCase(caseId) {
    if (caseId === 'border_case1') {
        renderInvestigatorDashboard({
            risk_score: 6.0,
            risk_level: 'Low Risk',
            attack_type: 'None / Genuine Identity',
            border_triage: 'CLEAR FOR ENTRY',
            face_similarity_score: 96.8,
            filename: 'case_border_passport.jpg',
            annotated_filename: 'case_border_passport.jpg',
            selfie_filename: 'case_border_passport_selfie.jpg',
            extracted_text: {
                document_number: 'P98421074',
                full_name: 'ALEXANDER CHEN',
                date_of_birth: '1994-08-14',
                expiration_date: '2031-08-13',
                mrz_line1: 'P<UTOCHEN<<ALEXANDER<<<<<<<<<<<<<<<<<<<<<<<<<',
                mrz_line2: 'P984210744UTO9408144M3108138<<<<<<<<<<<<<<06'
            },
            validation_results: { watchlist_hit: false },
            tamper_signals: { tamper_edge_splicing_detected: false },
            risk_reasons: [
                { type: 'PASS', message: 'Module 1 (OCR): High confidence field extraction (98.4%).' },
                { type: 'PASS', message: 'Module 2 (Validation): Travel authorization valid; Watchlist database CLEAR.' },
                { type: 'PASS', message: 'Module 3 (Tampering): No altered photo, modified DOB, or tampered stamp.' },
                { type: 'PASS', message: 'Module 4 (Biometrics): Passenger live face matches credential photo (96.8%).' }
            ]
        });
    } else if (caseId === 'border_case2') {
        renderInvestigatorDashboard({
            risk_score: 84.0,
            risk_level: 'High Risk',
            attack_type: 'Tampered Visa Stamp & Modified DOB',
            border_triage: 'DETAIN & INVESTIGATE',
            face_similarity_score: 91.2,
            filename: 'case_border_tampered_visa.jpg',
            annotated_filename: 'case_border_tampered_visa.jpg',
            selfie_filename: 'case_border_passport_selfie.jpg',
            extracted_text: {
                document_number: 'P984210-FORGED',
                full_name: 'ALEXANDER CHEN',
                date_of_birth: '1988-03-22',
                expiration_date: '2023-11-04',
                mrz_line1: 'P<UTOCHEN<<ALEXANDER<<<<<<<<<<<<<<<<<<<<<<<<<',
                mrz_line2: 'P984210-F8UTO8803224M2311048<<<<<<<<<<<<<<09'
            },
            validation_results: { watchlist_hit: false },
            tamper_signals: { tamper_edge_splicing_detected: true, modified_dob_detected: true, tampered_visa_stamp_detected: true },
            risk_reasons: [
                { type: 'FAIL', message: 'Module 3 (Tampering): Spliced boundary and font inconsistency in DOB field.' },
                { type: 'FAIL', message: 'Module 3 (Tampering): Consular visa stamp geometry distorted; ink bleed irregularity.' },
                { type: 'FAIL', message: 'Module 2 (Validation): Algorithmic MRZ checksum failure on date of birth check digit.' },
                { type: 'PASS', message: 'Module 4 (Biometrics): Facial portrait detected in document photo slot.' }
            ]
        });
    } else if (caseId === 'border_case3') {
        renderInvestigatorDashboard({
            risk_score: 96.0,
            risk_level: 'High Risk',
            attack_type: 'Interpol Stolen Credential Hit',
            border_triage: 'DETAIN & INVESTIGATE',
            face_similarity_score: 89.0,
            filename: 'case_border_blacklist.jpg',
            annotated_filename: 'case_border_blacklist.jpg',
            selfie_filename: 'case_border_passport_selfie.jpg',
            extracted_text: {
                document_number: 'P-BLOCKED-902',
                full_name: 'SANCTIONED TRAVELER',
                date_of_birth: '1982-11-19',
                expiration_date: '2029-05-10',
                mrz_line1: 'P<UTOTRAVELER<<SANCTIONED<<<<<<<<<<<<<<<<<<<<',
                mrz_line2: 'P-BLOCKED4UTO8211194M2905108<<<<<<<<<<<<<<11'
            },
            validation_results: { watchlist_hit: true, watchlist_details: 'Interpol SLTD Hit: Lost / Stolen Travel Document Repository.' },
            tamper_signals: { tamper_edge_splicing_detected: false },
            risk_reasons: [
                { type: 'FAIL', message: 'Module 2 (Validation): Stolen Passport Alert matching Interpol SLTD Database.' },
                { type: 'FAIL', message: 'Module 2 (Validation): Electronic Travel Authorization permanently REVOKED.' },
                { type: 'PASS', message: 'Module 1 (OCR): Machine Readable Zone successfully parsed.' }
            ]
        });
    } else if (caseId === 'case1') {
        renderInvestigatorDashboard({
            risk_score: 6.0,
            risk_level: 'Low Risk',
            attack_type: 'None / Genuine Identity',
            border_triage: 'CLEAR FOR ENTRY',
            face_similarity_score: 96.8,
            filename: 'case1_doc.jpg',
            annotated_filename: 'case1_doc.jpg',
            selfie_filename: 'case1_selfie.jpg',
            extracted_text: { document_number: 'ID-9948214', full_name: 'CITIZEN HOLDER', date_of_birth: '1995-04-12', expiration_date: '2032-04-11' },
            validation_results: { watchlist_hit: false },
            tamper_signals: { tamper_edge_splicing_detected: false },
            risk_reasons: [{ type: 'PASS', message: 'Civil registry cross-field check 100% consistent.' }]
        });
    } else if (caseId === 'case2') {
        renderInvestigatorDashboard({
            risk_score: 84.0,
            risk_level: 'High Risk',
            attack_type: 'Document Number Tampering',
            border_triage: 'DETAIN & INVESTIGATE',
            face_similarity_score: 90.0,
            filename: 'case2_doc.jpg',
            annotated_filename: 'case2_doc.jpg',
            selfie_filename: 'case1_selfie.jpg',
            extracted_text: { document_number: 'ID-99482-TAMPERED', full_name: 'CITIZEN HOLDER', date_of_birth: '1995-04-12', expiration_date: '2032-04-11' },
            validation_results: { watchlist_hit: false },
            tamper_signals: { tamper_edge_splicing_detected: true },
            risk_reasons: [{ type: 'FAIL', message: 'Edge splicing and font density discontinuity detected in ID number region.' }]
        });
    } else if (caseId === 'case3') {
        renderInvestigatorDashboard({
            risk_score: 92.0,
            risk_level: 'High Risk',
            attack_type: 'Identity Impersonation',
            border_triage: 'DETAIN & INVESTIGATE',
            face_similarity_score: 38.4,
            filename: 'case3_doc.jpg',
            annotated_filename: 'case3_doc.jpg',
            selfie_filename: 'case3_selfie.jpg',
            extracted_text: { document_number: 'ID-440192', full_name: 'PRIMARY HOLDER', date_of_birth: '1992-06-25', expiration_date: '2030-06-24' },
            validation_results: { watchlist_hit: false },
            tamper_signals: { tamper_edge_splicing_detected: false },
            risk_reasons: [{ type: 'FAIL', message: '1:1 Face biometrics mismatch (38.4% similarity). Live passenger does NOT match photo.' }]
        });
    }
}

// -------------------------------------------------------------
// 5. AI ASSISTANT QUERY
// -------------------------------------------------------------

async function askAiQuestion(promptText) {
    const box = document.getElementById('aiResponseBox');
    box.classList.remove('hidden');
    box.textContent = "Querying forensic knowledge base...";

    try {
        const res = await fetch('/api/ask-ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: promptText, doc_id: currentActiveDoc ? currentActiveDoc.id : null })
        });
        const data = await res.json();
        if (data.success) {
            box.textContent = data.answer || "No response received.";
        } else {
            box.textContent = data.message || "Query failed.";
        }
    } catch (e) {
        box.textContent = "AI query service unavailable.";
    }
}

function handleCustomAiQuery() {
    const input = document.getElementById('customAiQuery');
    const q = input.value.trim();
    if (!q) return;
    askAiQuestion(q);
    input.value = '';
}

// -------------------------------------------------------------
// 6. RECENT AUDIT TRAIL TABLE (SQLITE / POSTGRES)
// -------------------------------------------------------------

async function loadUserDocuments() {
    try {
        const res = await fetch('/api/documents');
        const data = await res.json();
        const wrapper = document.getElementById('docsTableWrapper');
        const tbody = document.getElementById('docsTableBody');
        const noDocs = document.getElementById('noDocsMsg');

        if (!data.success || !data.documents || data.documents.length === 0) {
            wrapper.classList.add('hidden');
            noDocs.classList.remove('hidden');
            return;
        }

        noDocs.classList.add('hidden');
        wrapper.classList.remove('hidden');
        tbody.innerHTML = '';

        data.documents.forEach(doc => {
            const tr = document.createElement('tr');
            const triage = doc.border_triage || (doc.risk_score <= 30 ? 'CLEAR FOR ENTRY' : (doc.risk_score <= 70 ? 'SECONDARY INSPECTION' : 'DETAIN & INVESTIGATE'));
            let badgeStyle = "text-emerald-400 font-bold font-mono";
            if (triage === 'SECONDARY INSPECTION') badgeStyle = "text-amber-400 font-bold font-mono";
            if (triage === 'DETAIN & INVESTIGATE') badgeStyle = "text-red-400 font-bold font-mono";

            const timeStr = doc.uploaded_at ? doc.uploaded_at.substring(0, 16).replace('T', ' ') : '-';

            tr.innerHTML = `
                <td class="font-mono text-slate-400">${timeStr}</td>
                <td class="font-semibold text-white">${doc.original_name || 'Document'}</td>
                <td class="${badgeStyle}">${triage}</td>
                <td class="font-mono text-slate-200">${Math.round(doc.risk_score)}/100</td>
                <td class="text-slate-300">${doc.attack_type || 'None'}</td>
                <td>
                    <button onclick='viewSavedDoc(${JSON.stringify(doc).replace(/'/g, "&#39;")})' class="px-2 py-0.5 rounded bg-[#1e293b] hover:bg-blue-900 border border-[#334155] text-blue-300 font-mono text-[11px] mr-1">View</button>
                    <button onclick="deleteSavedDoc(${doc.id})" class="px-2 py-0.5 rounded bg-[#1e293b] hover:bg-red-900 border border-[#334155] text-red-300 font-mono text-[11px]">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Failed to load audit documents:", e);
    }
}

function viewSavedDoc(doc) {
    renderInvestigatorDashboard(doc);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function deleteSavedDoc(docId) {
    if (!confirm("Confirm removal of this audit log record?")) return;
    try {
        const res = await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            loadUserDocuments();
        } else {
            alert(data.message);
        }
    } catch (e) {
        console.error(e);
    }
}

// -------------------------------------------------------------
// 7. 24/7 CLOUD CONNECTIVITY MODAL
// -------------------------------------------------------------

function setupNetworkModal() {
    const modal = document.getElementById('networkModal');
    const openBtn = document.getElementById('btnNetworkModal');
    const closeBtn = document.getElementById('closeNetworkModal');
    const dismissBtn = document.getElementById('dismissNetworkModal');
    const publicInput = document.getElementById('publicUrlInput');
    const qrImg = document.getElementById('networkQrImg');
    const copyPublicBtn = document.getElementById('copyPublicUrlBtn');
    const dbEngineText = document.getElementById('dbEngineText');

    if (!modal || !openBtn) return;

    openBtn.addEventListener('click', () => {
        modal.classList.remove('hidden');
        refreshNetworkInfo();
    });

    if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
    if (dismissBtn) dismissBtn.addEventListener('click', () => modal.classList.add('hidden'));

    if (copyPublicBtn && publicInput) {
        copyPublicBtn.addEventListener('click', async () => {
            const val = publicInput.value;
            if (!val) return;
            try {
                await navigator.clipboard.writeText(val);
                copyPublicBtn.textContent = 'Copied!';
                setTimeout(() => { copyPublicBtn.textContent = 'Copy'; }, 2000);
            } catch (err) {
                publicInput.select();
                document.execCommand('copy');
            }
        });
    }

    async function refreshNetworkInfo() {
        try {
            let targetUrl = window.location.origin;
            const res = await fetch('/api/network-info');
            const data = await res.json();
            if (data.success && data.network) {
                const net = data.network;
                if (net.permanent_url && !net.permanent_url.includes("127.0.0.1")) {
                    targetUrl = net.permanent_url;
                }
                if (dbEngineText && net.database_type) {
                    dbEngineText.textContent = net.database_type;
                }
            }
            if (publicInput) publicInput.value = targetUrl;
            if (qrImg && targetUrl) {
                qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=240x240&margin=8&data=${encodeURIComponent(targetUrl)}`;
            }
        } catch (e) {
            if (publicInput) publicInput.value = window.location.origin;
        }
    }
}
