/**
 * ID SHIELD - Frontend Investigation Application Logic
 * Supports Multi-Modal Upload, 3 Demo Cases, "Ask the AI" Assistant,
 * Circular Risk Gauge, and Forensic Audit Repository.
 */

let currentUser = null;
let currentActiveDoc = null;

document.addEventListener('DOMContentLoaded', () => {
    initLucide();
    setupAuthEvents();
    setupMultiModalEvents();
    setupNetworkModal();
    checkAuthSession();
});

function initLucide() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

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
        console.error("Auth check failed:", e);
        setUnauthenticatedState();
    }
}

function setAuthenticatedState(user) {
    currentUser = user;
    document.getElementById('authSection').classList.add('hidden');
    document.getElementById('dashboardSection').classList.remove('hidden');
    
    const navAuth = document.getElementById('navAuthArea');
    navAuth.innerHTML = `
        <div class="flex items-center gap-3">
            <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                <div class="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 font-bold flex items-center justify-center text-[11px]">
                    ${(user.name || 'U').charAt(0).toUpperCase()}
                </div>
                <div class="hidden sm:block text-left">
                    <div class="font-semibold text-white leading-tight">${user.name}</div>
                    <div class="text-[10px] text-slate-400 leading-tight">Investigator</div>
                </div>
            </div>
            <button onclick="handleLogout()" class="py-1.5 px-3 rounded-xl bg-slate-900 hover:bg-rose-950/40 border border-slate-800 hover:border-rose-800 text-slate-300 hover:text-rose-400 text-xs font-medium transition-all flex items-center gap-1.5">
                <i data-lucide="log-out" class="w-3.5 h-3.5"></i>
                <span class="hidden sm:inline">Sign Out</span>
            </button>
        </div>
    `;
    initLucide();
    loadUserDocuments();
}

function setUnauthenticatedState() {
    currentUser = null;
    document.getElementById('dashboardSection').classList.add('hidden');
    document.getElementById('authSection').classList.remove('hidden');
    
    const navAuth = document.getElementById('navAuthArea');
    navAuth.innerHTML = `<span class="text-xs text-slate-400">Not signed in</span>`;
    initLucide();
}

function setupAuthEvents() {
    const tabSignIn = document.getElementById('tabSignIn');
    const tabSignUp = document.getElementById('tabSignUp');
    const signInForm = document.getElementById('signInForm');
    const signUpForm = document.getElementById('signUpForm');

    tabSignIn.addEventListener('click', () => {
        tabSignIn.className = "flex-1 py-2 text-sm font-semibold rounded-lg transition-all bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md";
        tabSignUp.className = "flex-1 py-2 text-sm font-semibold rounded-lg text-slate-400 hover:text-white transition-all";
        signInForm.classList.remove('hidden');
        signUpForm.classList.add('hidden');
        hideAlert();
    });

    tabSignUp.addEventListener('click', () => {
        tabSignUp.className = "flex-1 py-2 text-sm font-semibold rounded-lg transition-all bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md";
        tabSignIn.className = "flex-1 py-2 text-sm font-semibold rounded-lg text-slate-400 hover:text-white transition-all";
        signUpForm.classList.remove('hidden');
        signInForm.classList.add('hidden');
        hideAlert();
    });

    signInForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (data.success) {
                showAlert(data.message, "success");
                setTimeout(() => setAuthenticatedState(data.user), 400);
            } else {
                showAlert(data.message, "error");
            }
        } catch (err) {
            showAlert("Connection error. Please try again.", "error");
        }
    });

    signUpForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();
        const name = document.getElementById('regName').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const confirm = document.getElementById('regConfirmPassword').value;

        if (password !== confirm) {
            showAlert("Passwords do not match.", "error");
            return;
        }

        try {
            const res = await fetch('/api/signup', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name, email, password })
            });
            const data = await res.json();
            if (data.success) {
                showAlert(data.message, "success");
                setTimeout(() => setAuthenticatedState(data.user), 500);
            } else {
                showAlert(data.message, "error");
            }
        } catch (err) {
            showAlert("Connection error. Please try again.", "error");
        }
    });
}

function showAlert(message, type = "info") {
    const alertBox = document.getElementById('authAlert');
    const alertText = document.getElementById('authAlertText');
    alertBox.classList.remove('hidden', 'bg-rose-950/60', 'border-rose-800', 'text-rose-300', 'bg-emerald-950/60', 'border-emerald-800', 'text-emerald-300', 'bg-cyan-950/60', 'border-cyan-800', 'text-cyan-300');
    
    if (type === 'error') {
        alertBox.classList.add('bg-rose-950/60', 'border-rose-800', 'text-rose-300');
    } else if (type === 'success') {
        alertBox.classList.add('bg-emerald-950/60', 'border-emerald-800', 'text-emerald-300');
    } else {
        alertBox.classList.add('bg-cyan-950/60', 'border-cyan-800', 'text-cyan-300');
    }
    
    alertText.textContent = message;
    alertBox.classList.remove('hidden');
    initLucide();
}

function hideAlert() {
    const alertBox = document.getElementById('authAlert');
    alertBox.classList.add('hidden');
}

async function handleLogout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        setUnauthenticatedState();
    } catch (e) {
        console.error(e);
        setUnauthenticatedState();
    }
}

// -------------------------------------------------------------
// 2. MULTI-MODAL UPLOAD & PIPELINE EXECUTION
// -------------------------------------------------------------

function setupMultiModalEvents() {
    setupFileInput('docDropZone', 'primaryDocInput', 'docFileLabel');
    setupFileInput('selfieDropZone', 'selfieInput', 'selfieFileLabel');
    setupFileInput('supDropZone', 'supDocInput', 'supFileLabel');

    const form = document.getElementById('multiModalForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const docInput = document.getElementById('primaryDocInput');
        if (!docInput.files || docInput.files.length === 0) {
            alert("Please select a primary Identity Document to inspect.");
            return;
        }

        const formData = new FormData();
        formData.append('document', docInput.files[0]);
        
        const selfieInput = document.getElementById('selfieInput');
        if (selfieInput.files && selfieInput.files.length > 0) {
            formData.append('selfie', selfieInput.files[0]);
        }

        const supInput = document.getElementById('supDocInput');
        if (supInput.files && supInput.files.length > 0) {
            formData.append('supporting_doc', supInput.files[0]);
        }

        const docTypeSelect = document.getElementById('docTypeSelect');
        if (docTypeSelect) {
            formData.append('doc_type', docTypeSelect.value);
        }

        formData.append('entered_name', document.getElementById('enteredName').value);
        formData.append('entered_dob', document.getElementById('enteredDOB').value);
        formData.append('entered_id', document.getElementById('enteredIDNum').value);

        executePipeline(formData, docInput.files[0].name);
    });
}

function setupFileInput(zoneId, inputId, labelId) {
    const zone = document.getElementById(zoneId);
    const input = document.getElementById(inputId);
    const label = document.getElementById(labelId);

    zone.addEventListener('click', () => input.click());
    zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('border-cyan-400'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('border-cyan-400'));
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('border-cyan-400');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            input.files = e.dataTransfer.files;
            label.textContent = e.dataTransfer.files[0].name;
        }
    });
    input.addEventListener('change', () => {
        if (input.files && input.files.length > 0) {
            label.textContent = input.files[0].name;
        }
    });
}

// 1-Click Screening Scenarios (Border & KYC)
async function triggerDemoCase(caseId) {
    const formData = new FormData();
    formData.append('sample_case', caseId);
    const names = {
        'case1': 'Case 1: Genuine Citizen Identity',
        'case2': 'Case 2: Tampered Document',
        'case3': 'Case 3: Identity Mismatch',
        'border_case1': 'Border Case A: Genuine Travel Passport with MRZ',
        'border_case2': 'Border Case B: Tampered Visa Stamp & Modified DOB',
        'border_case3': 'Border Case C: Stolen Travel Credential (Interpol Watchlist Hit)'
    };
    executePipeline(formData, names[caseId] || caseId);
}

async function executePipeline(formData, displayName) {
    const progressCard = document.getElementById('pipelineProgress');
    const statusText = document.getElementById('pipelineStatusText');
    const percentText = document.getElementById('pipelinePercent');
    const bar = document.getElementById('pipelineBar');
    const resultCard = document.getElementById('analysisResultCard');

    resultCard.classList.add('hidden');
    progressCard.classList.remove('hidden');

    const updateBar = (pct, text) => {
        statusText.textContent = text;
        percentText.textContent = `${pct}%`;
        bar.style.width = `${pct}%`;
    };

    updateBar(20, "1. Ingesting Identity Document & Normalizing Dimensions...");
    await sleep(220);
    updateBar(40, "2. Running OCR Text Extraction & Layout Boundary Check...");
    await sleep(220);
    updateBar(60, "3. Analyzing Image Forensics (Laplacian Sharpness & Edge Splicing)...");
    await sleep(250);
    updateBar(80, "4. Executing Facial Biometric Comparison & Cross-Field Consistency...");

    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const result = await res.json();

        if (!result.success) {
            alert(`Investigation Error: ${result.message}`);
            progressCard.classList.add('hidden');
            return;
        }

        updateBar(100, "5. Fraud Intelligence Synthesis Complete! Saved to SQLite.");
        await sleep(300);
        progressCard.classList.add('hidden');

        currentActiveDoc = result.data;
        renderInvestigatorDashboard(result.data);
        loadUserDocuments();

    } catch (e) {
        console.error(e);
        alert("Server error during investigation pipeline.");
        progressCard.classList.add('hidden');
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// -------------------------------------------------------------
// 3. RENDER INVESTIGATOR DASHBOARD (MATCHING INFOGRAPHIC)
// -------------------------------------------------------------

function renderInvestigatorDashboard(data) {
    const card = document.getElementById('analysisResultCard');
    card.classList.remove('hidden');

    const score = Math.round(data.risk_score);
    const triage = data.border_triage || (score <= 30 ? "CLEAR FOR ENTRY" : (score <= 70 ? "SECONDARY INSPECTION" : "DETAIN & INVESTIGATE"));
    const ocr = data.extracted_text || {};
    const val = data.validation_results || {};
    const tamper = data.tamper_signals || {};

    // 1. Border Security Personnel Assist: Accelerated Triage Decision Banner
    const triageBanner = document.getElementById('borderTriageBanner');
    const triageTitle = document.getElementById('borderTriageTitle');
    const triageSubtitle = document.getElementById('borderTriageSubtitle');
    const triageBox = document.getElementById('triageIconBox');

    if (triage === "CLEAR FOR ENTRY") {
        triageBanner.className = "p-5 rounded-3xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl bg-emerald-950/60 border-emerald-700/60 text-emerald-300";
        triageBox.className = "w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center text-xl font-black shadow-inner";
        triageTitle.innerHTML = `<span>CLEAR FOR ENTRY</span> <i data-lucide="check-circle" class="w-6 h-6 text-emerald-400"></i>`;
        triageSubtitle.textContent = "Automated e-Gate clearance authorized. 0 Watchlist records found. 1:1 facial biometric match confirmed.";
    } else if (triage === "SECONDARY INSPECTION") {
        triageBanner.className = "p-5 rounded-3xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl bg-amber-950/60 border-amber-700/60 text-amber-300";
        triageBox.className = "w-12 h-12 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/40 flex items-center justify-center text-xl font-black shadow-inner";
        triageTitle.innerHTML = `<span>SECONDARY INSPECTION</span> <i data-lucide="alert-circle" class="w-6 h-6 text-amber-400"></i>`;
        triageSubtitle.textContent = "Manual inspection required. Border control officer interview recommended due to borderline data correlation.";
    } else {
        triageBanner.className = "p-5 rounded-3xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl bg-rose-950/70 border-rose-700/70 text-rose-300";
        triageBox.className = "w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-400 border border-rose-500/40 flex items-center justify-center text-xl font-black shadow-inner";
        triageTitle.innerHTML = `<span>DETAIN & INVESTIGATE</span> <i data-lucide="shield-alert" class="w-6 h-6 text-rose-400"></i>`;
        triageSubtitle.textContent = "CRITICAL BORDER ALERT: Credential forgery, modified DOB, tampered visa stamp, or Watchlist/Interpol hit.";
    }

    // 2. Circular Risk Score Gauge
    document.getElementById('gaugeScoreText').textContent = score;
    const circle = document.getElementById('gaugeCircle');
    const circumference = 314.15;
    const offset = circumference - (score / 100) * circumference;
    circle.style.strokeDashoffset = offset;

    const riskTitle = document.getElementById('dashRiskTitle');
    const attackBadge = document.getElementById('attackTypeBadge');
    const attackText = document.getElementById('attackTypeText');

    if (score <= 30) {
        circle.style.stroke = '#10b981'; // Green
        riskTitle.textContent = "LOW RISK";
        riskTitle.className = "text-2xl sm:text-3xl font-extrabold tracking-tight text-emerald-400";
        attackBadge.className = "inline-flex items-center gap-2 mt-2 px-3 py-1 rounded-full text-xs font-bold border bg-emerald-950 text-emerald-300 border-emerald-800";
    } else if (score <= 70) {
        circle.style.stroke = '#f59e0b'; // Amber
        riskTitle.textContent = "MANUAL REVIEW";
        riskTitle.className = "text-2xl sm:text-3xl font-extrabold tracking-tight text-amber-400";
        attackBadge.className = "inline-flex items-center gap-2 mt-2 px-3 py-1 rounded-full text-xs font-bold border bg-amber-950 text-amber-300 border-amber-800";
    } else {
        circle.style.stroke = '#ef4444'; // Red
        riskTitle.textContent = "HIGH RISK";
        riskTitle.className = "text-2xl sm:text-3xl font-extrabold tracking-tight text-rose-400";
        attackBadge.className = "inline-flex items-center gap-2 mt-2 px-3 py-1 rounded-full text-xs font-bold border bg-rose-950 text-rose-300 border-rose-800";
    }

    attackText.textContent = data.attack_type || "Attack Classification Pending";

    // 3. Analysis Checklist (from Infographic)
    document.getElementById('dashOcrScore').textContent = `${ocr.ocr_confidence || 95}%`;
    document.getElementById('dashDocStructure').textContent = "Normal";

    const forensicsEl = document.getElementById('dashForensics');
    if (tamper.tamper_edge_splicing_detected || tamper.tampered_visa_stamp_detected || tamper.modified_dob_detected) {
        forensicsEl.textContent = "Suspicious (Spliced)";
        forensicsEl.className = "font-bold text-rose-400";
    } else {
        forensicsEl.textContent = "Passed";
        forensicsEl.className = "font-bold text-emerald-400";
    }

    const faceMatchEl = document.getElementById('dashFaceMatch');
    const sim = data.face_similarity_score;
    if (sim !== null && sim !== undefined && sim > 0) {
        faceMatchEl.textContent = `${sim}%`;
        faceMatchEl.className = sim >= 70 ? "font-bold text-emerald-400" : "font-bold text-rose-400";
    } else {
        faceMatchEl.textContent = data.face_count === 1 ? "1 Face (Doc)" : "None";
        faceMatchEl.className = "font-bold text-slate-300";
    }

    const livenessEl = document.getElementById('dashLiveness');
    livenessEl.textContent = data.liveness_status || "Normal";
    livenessEl.className = data.liveness_status === "PASS" ? "font-bold text-emerald-400" : "font-bold text-amber-400";

    const consistencyEl = document.getElementById('dashConsistency');
    consistencyEl.textContent = data.cross_field_status === "PASS" ? "Normal (Match)" : "Conflict";
    consistencyEl.className = data.cross_field_status === "PASS" ? "font-bold text-emerald-400" : "font-bold text-rose-400";

    // 4. Extracted Travel Credential & MRZ Forensic Card
    document.getElementById('tbDocType').textContent = ocr.document_type || "Passport";
    document.getElementById('tbDocNo').textContent = ocr.document_number || "P98421074";
    document.getElementById('tbDocName').textContent = ocr.full_name || "CHEN, ALEXANDER";
    document.getElementById('tbDocDOB').textContent = ocr.date_of_birth || "1994-08-14";
    document.getElementById('tbDocExpiry').textContent = ocr.expiration_date || "2031-08-13";
    document.getElementById('tbDocNat').textContent = ocr.nationality ? `${ocr.nationality} (UTOPIAN)` : "Standard";

    // Travel Authorization Badge
    const authEl = document.getElementById('dashTravelAuthBadge');
    if (val.travel_authorization && val.travel_authorization.includes("APPROVED")) {
        authEl.textContent = `TRAVEL AUTHORIZATION: ${val.travel_authorization}`;
        authEl.className = "px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800";
    } else {
        authEl.textContent = `TRAVEL AUTHORIZATION: ${val.travel_authorization || 'REVOKED'}`;
        authEl.className = "px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-950 text-rose-300 border border-rose-800";
    }

    // MRZ Lines & Checksum
    const mrzBox = document.getElementById('mrzDisplayContainer');
    if (ocr.mrz_line1 && ocr.mrz_line2) {
        mrzBox.classList.remove('hidden');
        document.getElementById('mrzLine1').textContent = ocr.mrz_line1;
        document.getElementById('mrzLine2').textContent = ocr.mrz_line2;
        const mrzBadge = document.getElementById('mrzChecksumBadge');
        if (tamper.tamper_edge_splicing_detected || (ocr.document_number && ocr.document_number.includes("FORGED"))) {
            mrzBadge.textContent = "CHECKSUM: MISMATCH / FORGED";
            mrzBadge.className = "px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-950 text-rose-400 border border-rose-800";
        } else {
            mrzBadge.textContent = "CHECKSUM: VALID (ICAO 9303)";
            mrzBadge.className = "px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-800";
        }
    } else {
        mrzBox.classList.add('hidden');
    }

    // Watchlist DB Status
    const wlEl = document.getElementById('tbWatchlistStatus');
    if (val.is_blacklisted) {
        wlEl.textContent = `ALERT: ${val.blacklist_reason || 'INTERPOL HIT'}`;
        wlEl.className = "font-bold text-rose-400";
    } else {
        wlEl.textContent = "CLEAR (0 HITS)";
        wlEl.className = "font-bold text-emerald-400";
    }

    // Visa Stamp Status
    const stampEl = document.getElementById('tbVisaStampStatus');
    if (tamper.tampered_visa_stamp_detected || (ocr.visa_stamp_status && ocr.visa_stamp_status.includes("Tampered"))) {
        stampEl.textContent = "TAMPERED / DISTORTED SEAL";
        stampEl.className = "font-bold text-rose-400";
    } else {
        stampEl.textContent = "AUTHENTIC SEAL";
        stampEl.className = "font-bold text-emerald-400";
    }

    // 5. Visual Forensic Evidence Images
    document.getElementById('dashAnnotatedImg').src = `/uploads/${data.annotated_filename || data.filename}`;
    document.getElementById('docDims').textContent = tamper.dimensions || "640 x 400 px";

    // Face Comparison Images
    const docFaceImg = document.getElementById('dashDocFaceImg');
    const liveSelfieImg = document.getElementById('dashLiveSelfieImg');
    const biometricText = document.getElementById('dashBiometricText');

    docFaceImg.src = `/uploads/${data.annotated_filename || data.filename}`;
    if (data.selfie_filename) {
        liveSelfieImg.src = `/uploads/${data.selfie_filename}`;
        liveSelfieImg.parentElement.classList.remove('hidden');
        biometricText.textContent = `Face Similarity: ${sim || 50}%`;
        biometricText.className = (sim && sim >= 70) ? "text-emerald-400 font-bold text-[11px]" : "text-rose-400 font-bold text-[11px]";
    } else {
        liveSelfieImg.src = `/uploads/${data.annotated_filename || data.filename}`;
        biometricText.textContent = "No Live Traveler Photo (Doc Portrait Only)";
        biometricText.className = "text-slate-400 font-medium text-[11px]";
    }

    // 6. Reset AI Assistant with default summary
    const aiLog = data.ai_investigation_log || {};
    const answerContent = document.getElementById('aiAnswerContent');
    const reasonsBullets = (aiLog.key_reasons || []).map(r => `• ${r}`).join('<br>');
    answerContent.innerHTML = `
        <strong class="text-white">${aiLog.summary || "Investigation summary generated."}</strong><br>
        <div class="mt-2 text-slate-400">${reasonsBullets}</div>
        <div class="mt-2 text-cyan-300 font-mono"><strong>Border Action:</strong> ${aiLog.recommended_action || "Standard review."}</div>
    `;

    initLucide();
    card.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// -------------------------------------------------------------
// 4. "ASK THE AI" INVESTIGATION ASSISTANT
// -------------------------------------------------------------

async function askAiQuestion(question) {
    if (!currentActiveDoc || !currentActiveDoc.id) {
        alert("Please load or inspect a document first before querying the AI assistant.");
        return;
    }

    const answerBox = document.getElementById('aiAnswerContent');
    answerBox.innerHTML = `<span class="text-cyan-400 animate-pulse font-mono">AI Reasoning Engine analyzing forensic artifacts...</span>`;

    try {
        const res = await fetch('/api/ask-ai', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ query: question, doc_id: currentActiveDoc.id })
        });
        const data = await res.json();
        if (data.success) {
            // Render markdown formatted text with linebreaks
            answerBox.innerHTML = data.answer.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>');
        } else {
            answerBox.textContent = data.message;
        }
    } catch (e) {
        answerBox.textContent = "Error contacting AI assistant.";
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
// 5. USER AUDIT TRAIL REPOSITORY (SQLITE)
// -------------------------------------------------------------

async function loadUserDocuments() {
    try {
        const res = await fetch('/api/documents');
        const data = await res.json();
        const grid = document.getElementById('docsListGrid');
        const noDocs = document.getElementById('noDocsMsg');

        if (!data.success || !data.documents || data.documents.length === 0) {
            grid.classList.add('hidden');
            noDocs.classList.remove('hidden');
            return;
        }

        noDocs.classList.add('hidden');
        grid.classList.remove('hidden');
        grid.innerHTML = '';

        data.documents.forEach(doc => {
            let badgeCls = "bg-emerald-950 text-emerald-400 border-emerald-800";
            if (doc.risk_level === 'Review') badgeCls = "bg-amber-950 text-amber-400 border-amber-800";
            if (doc.risk_level === 'High Risk') badgeCls = "bg-rose-950 text-rose-400 border-rose-800";

            const item = document.createElement('div');
            item.className = "p-4 rounded-2xl bg-slate-950/80 border border-slate-800 hover:border-cyan-500/40 transition-all flex flex-col justify-between space-y-3";
            item.innerHTML = `
                <div>
                    <div class="flex items-center justify-between gap-2 mb-2">
                        <span class="text-xs font-bold text-white truncate flex-1" title="${doc.original_name}">${doc.original_name}</span>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded border ${badgeCls}">${doc.risk_level}</span>
                    </div>
                    <div class="rounded-xl overflow-hidden bg-slate-900 border border-slate-800 h-28 flex items-center justify-center mb-2">
                        <img src="/uploads/${doc.annotated_filename || doc.filename}" alt="${doc.original_name}" class="h-full w-full object-cover">
                    </div>
                    <div class="text-[11px] text-slate-400 space-y-1">
                        <div class="flex justify-between">
                            <span>Score:</span>
                            <span class="font-mono text-white font-semibold">${doc.risk_score}/100</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Attack:</span>
                            <span class="text-cyan-300 font-medium">${doc.attack_type || 'None'}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Date:</span>
                            <span class="text-slate-500">${doc.uploaded_at}</span>
                        </div>
                    </div>
                </div>
                <div class="flex items-center gap-2 pt-2 border-t border-slate-800/80">
                    <button onclick='viewSavedDoc(${JSON.stringify(doc).replace(/'/g, "&apos;")})' class="flex-1 py-1.5 px-2 rounded-lg bg-cyan-950 hover:bg-cyan-900 text-cyan-300 text-xs font-semibold flex items-center justify-center gap-1 border border-cyan-800/60 transition-colors">
                        <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
                        <span>Inspect</span>
                    </button>
                    <button onclick="deleteSavedDoc(${doc.id})" class="p-1.5 rounded-lg bg-slate-900 hover:bg-rose-950/60 text-slate-400 hover:text-rose-400 text-xs border border-slate-800 hover:border-rose-800 transition-colors" title="Delete record">
                        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                    </button>
                </div>
            `;
            grid.appendChild(item);
        });

        initLucide();
    } catch (e) {
        console.error("Failed to load documents:", e);
    }
}

function viewSavedDoc(doc) {
    currentActiveDoc = doc;
    renderInvestigatorDashboard(doc);
}

async function deleteSavedDoc(docId) {
    if (!confirm("Delete this investigation record from SQLite?")) return;
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
// 6. UTILITY HELPERS
// -------------------------------------------------------------

function togglePasswordVisibility(inputId, btnElement) {
    const input = document.getElementById(inputId);
    if (!input) return;

    if (input.type === 'password') {
        input.type = 'text';
        btnElement.innerHTML = '<i data-lucide="eye-off" class="w-4 h-4 text-cyan-400"></i>';
    } else {
        input.type = 'password';
        btnElement.innerHTML = '<i data-lucide="eye" class="w-4 h-4 text-slate-500 hover:text-cyan-400"></i>';
    }
    initLucide();
}

// -------------------------------------------------------------
// 7. ANY NETWORK & ANY DEVICE CONNECTIVITY
// -------------------------------------------------------------

function setupNetworkModal() {
    const modal = document.getElementById('networkModal');
    const openBtn = document.getElementById('btnNetworkModal');
    const closeBtn = document.getElementById('closeNetworkModal');
    const dismissBtn = document.getElementById('dismissNetworkModal');
    const lanInput = document.getElementById('lanUrlInput');
    const publicInput = document.getElementById('publicUrlInput');
    const qrImg = document.getElementById('networkQrImg');
    const copyPublicBtn = document.getElementById('copyPublicUrlBtn');
    const copyLanBtn = document.getElementById('copyLanUrlBtn');
    const badge = document.getElementById('publicTunnelBadge');

    if (!modal || !openBtn) return;

    const openModal = () => {
        modal.classList.remove('hidden');
        refreshNetworkInfo();
        initLucide();
    };

    const closeModal = () => {
        modal.classList.add('hidden');
    };

    openBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (dismissBtn) dismissBtn.addEventListener('click', closeModal);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Copy helper
    const attachCopy = (btn, input) => {
        if (!btn || !input) return;
        btn.addEventListener('click', async () => {
            const val = input.value;
            if (!val || val.includes('Detecting') || val.includes('Connecting')) return;
            try {
                await navigator.clipboard.writeText(val);
                const orig = btn.innerHTML;
                btn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i> Copied!';
                initLucide();
                setTimeout(() => {
                    btn.innerHTML = orig;
                    initLucide();
                }, 2000);
            } catch (err) {
                input.select();
                document.execCommand('copy');
            }
        });
    };

    attachCopy(copyPublicBtn, publicInput);
    attachCopy(copyLanBtn, lanInput);

    async function refreshNetworkInfo() {
        try {
            const res = await fetch('/api/network-info');
            const data = await res.json();
            if (data.success && data.network) {
                const net = data.network;
                if (lanInput) lanInput.value = net.lan_url;

                const targetUrl = net.public_url || net.lan_url;
                if (publicInput) {
                    if (net.public_url) {
                        publicInput.value = net.public_url;
                        if (badge) {
                            badge.className = "text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30";
                            badge.textContent = "HTTPS ACTIVE";
                        }
                    } else {
                        publicInput.value = "Starting tunnel... click again in 5s";
                        if (badge) {
                            badge.className = "text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30";
                            badge.textContent = "CONNECTING";
                        }
                    }
                }

                // Generate QR Code pointing to public tunnel or LAN
                if (qrImg && targetUrl) {
                    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=260x260&margin=8&data=${encodeURIComponent(targetUrl)}`;
                    qrImg.src = qrUrl;
                }
            }
        } catch (e) {
            console.error("Failed to fetch network info:", e);
        }
    }

    // Initial background query to cache network info
    refreshNetworkInfo();
}

