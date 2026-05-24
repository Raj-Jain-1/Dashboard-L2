document.addEventListener("DOMContentLoaded", () => {
    // Clock in Sidebar
    updateClock();
    setInterval(updateClock, 1000);

    // Global State
    let historyData = [];
    let timelineChart = null;
    let radarChart = null;
    const selectedSymptoms = new Set();

    // Elements
    const navItems = document.querySelectorAll(".sidebar-nav .nav-item");
    const sections = document.querySelectorAll(".content-section");
    const pageTitle = document.getElementById("page-title");
    
    // Tab switching
    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const tabId = item.getAttribute("data-tab");
            
            navItems.forEach(nav => nav.classList.remove("active"));
            sections.forEach(sec => sec.classList.remove("active"));
            
            item.classList.add("active");
            document.getElementById(`tab-${tabId}`).classList.add("active");
            
            pageTitle.innerText = item.textContent.trim().toUpperCase();

            // Refresh charts if dashboard tab is active
            if (tabId === "dashboard") {
                initCharts();
            }
        });
    });

    // Range Slider Bubble Sync
    const sliders = document.querySelectorAll(".neon-slider");
    sliders.forEach(slider => {
        const valSpan = document.getElementById(`val-${slider.id}`);
        slider.addEventListener("input", () => {
            valSpan.innerText = slider.value;
        });
    });

    // Medical Scan Tabs Selection
    const scanTabs = document.querySelectorAll(".scan-nav .scan-tab-btn");
    const scanForms = document.querySelectorAll(".scan-form");
    const formTitle = document.getElementById("scan-form-title");
    
    scanTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const scanType = tab.getAttribute("data-scan");
            
            scanTabs.forEach(t => t.classList.remove("active"));
            scanForms.forEach(f => f.classList.add("hidden"));
            
            tab.classList.add("active");
            document.getElementById(`form-${scanType}`).classList.remove("hidden");
            
            formTitle.innerText = `${scanType.replace("_", " ").toUpperCase()} RISK SCANNER`;
        });
    });

    // Submit Prediction Forms
    scanForms.forEach(form => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const disease = form.id.replace("form-", "");
            const patientName = document.getElementById("patient-name-global").value.trim() || "Anonymous";
            
            // Gather form parameters
            const formDataObj = {};
            const formData = new FormData(form);
            formData.forEach((value, key) => {
                formDataObj[key] = parseFloat(value);
            });

            // Loading screen simulation or feedback
            const submitBtn = form.querySelector("button[type='submit']");
            const originalBtnHtml = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> CALCULATING CLASSIFICATION VALUES...`;

            try {
                const response = await fetch("/api/predict", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: jsonStringify({
                        patient_name: patientName,
                        disease: disease,
                        data: formDataObj
                    })
                });

                const result = await response.json();
                
                if (result.status === "success") {
                    renderPredictionResult(result.data);
                    
                    // Add diagnostic log entry
                    addConsoleLog(`[${new Date().toLocaleTimeString()}] Diagnosis processed for ${patientName}: ${disease} risk calculated at ${result.data.risk_percentage}%`);
                    
                    // Fetch latest history to update charts
                    await fetchHistory();
                } else {
                    alert(`Prediction Error: ${result.message}`);
                }
            } catch (err) {
                console.error("Fetch prediction failed:", err);
                alert("Could not reach predictions server. Make sure the Flask engine is running.");
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnHtml;
            }
        });
    });

    // Render Prediction Result on Cards
    function renderPredictionResult(record) {
        document.getElementById("no-results-view").classList.add("hidden");
        document.getElementById("results-view").classList.remove("hidden");

        // Risk Gauge and Labels
        const riskPct = record.risk_percentage;
        const riskClass = record.risk_level.toUpperCase() + " RISK";
        
        document.getElementById("result-risk-val").innerText = `${riskPct}%`;
        document.getElementById("result-risk-classification").innerText = riskClass;

        // Health Index
        const healthScore = record.health_score;
        document.getElementById("result-health-val").innerText = healthScore;

        // Animate SVG Gauges
        updateSvgGauge("risk-gauge-fill", riskPct);
        updateSvgGauge("health-gauge-fill", healthScore);

        // Styling indicators based on risk level
        const riskValText = document.getElementById("result-risk-val");
        const statusTag = document.getElementById("result-status-tag");
        
        // Remove old styles
        statusTag.className = "card-tag";
        riskValText.className = "gauge-num";

        if (riskPct >= 70) {
            statusTag.classList.add("text-red");
            statusTag.innerText = "CRITICAL";
            riskValText.classList.add("text-red");
        } else if (riskPct >= 30) {
            statusTag.classList.add("text-orange");
            statusTag.innerText = "MONITOR";
            riskValText.classList.add("text-orange");
        } else {
            statusTag.classList.add("text-green");
            statusTag.innerText = "STABLE";
            riskValText.classList.add("text-green");
        }

        // Warnings Panel
        const warningsBox = document.getElementById("result-warnings-container");
        warningsBox.innerHTML = "";
        
        if (record.warnings && record.warnings.length > 0) {
            warningsBox.classList.remove("hidden");
            record.warnings.forEach(warning => {
                const card = document.createElement("div");
                card.className = "warning-card";
                card.innerHTML = `
                    <i class="fa-solid fa-triangle-exclamation warning-blink"></i>
                    <p>${warning}</p>
                `;
                warningsBox.appendChild(card);
            });
            
            // Set global emergency warning banner
            const banner = document.getElementById("emergency-banner");
            const bannerText = document.getElementById("emergency-banner-text");
            bannerText.innerText = `EMERGENCY STATUS: ${record.warnings[0]}`;
            banner.classList.remove("hidden");
        } else {
            warningsBox.classList.add("hidden");
        }

        // Suggestions Panel
        const suggestionsList = document.getElementById("result-suggestions-list");
        suggestionsList.innerHTML = "";
        
        record.suggestions.forEach(sugg => {
            const item = document.createElement("li");
            item.className = `suggestion-item suggest-${sugg.type}`;
            item.innerHTML = sugg.text;
            suggestionsList.appendChild(item);
        });

        // Setup PDF download listener with current record data
        const downloadBtn = document.getElementById("download-pdf-btn");
        downloadBtn.onclick = () => generatePDF(record);
    }

    function updateSvgGauge(elementId, val) {
        const fillCircle = document.getElementById(elementId);
        // Radius of circle is 40, circumference is 2 * pi * r = 251.2
        const circ = 251.2;
        const offset = circ - (val / 100) * circ;
        fillCircle.style.strokeDashoffset = offset;
    }

    // PDF Report Generator
    function generatePDF(record) {
        const dateStr = new Date(record.timestamp).toLocaleString();
        
        // Populate PDF template details
        document.getElementById("pdf-report-id").innerText = `REPORT ID: ${record.id}`;
        document.getElementById("pdf-report-date").innerText = `DATE: ${dateStr}`;
        document.getElementById("pdf-patient-name").innerText = record.patient_name;
        document.getElementById("pdf-scan-type").innerText = `${record.disease.replace("_", " ").toUpperCase()} SCAN`;
        document.getElementById("pdf-risk-pct").innerText = `${record.risk_percentage}%`;
        document.getElementById("pdf-risk-class").innerText = record.risk_level.toUpperCase() + " RISK";
        document.getElementById("pdf-health-score").innerText = record.health_score;

        // Custom styling for PDF values based on classification
        const riskPctPdf = document.getElementById("pdf-risk-pct");
        const riskClassPdf = document.getElementById("pdf-risk-class");
        if (record.risk_percentage >= 70) {
            riskPctPdf.style.color = "#d9534f";
            riskClassPdf.style.color = "#d9534f";
        } else if (record.risk_percentage >= 30) {
            riskPctPdf.style.color = "#f0ad4e";
            riskClassPdf.style.color = "#f0ad4e";
        } else {
            riskPctPdf.style.color = "#5cb85c";
            riskClassPdf.style.color = "#5cb85c";
        }

        // Vitals Table
        const vitalsTable = document.getElementById("pdf-vitals-table");
        vitalsTable.innerHTML = "";
        
        let tr = null;
        let counter = 0;
        
        for (const [key, value] of Object.entries(record.inputs)) {
            if (counter % 2 === 0) {
                tr = document.createElement("tr");
                vitalsTable.appendChild(tr);
            }
            
            const labelTd = document.createElement("td");
            labelTd.style.padding = "6px 10px";
            labelTd.style.fontWeight = "bold";
            labelTd.style.borderBottom = "1px solid #eee";
            labelTd.innerText = key + ":";
            
            const valTd = document.createElement("td");
            valTd.style.padding = "6px 10px";
            valTd.style.borderBottom = "1px solid #eee";
            valTd.innerText = value;
            
            tr.appendChild(labelTd);
            tr.appendChild(valTd);
            counter++;
        }

        // Warnings Section
        const pdfWarningsSection = document.getElementById("pdf-warnings-section");
        const pdfWarningsList = document.getElementById("pdf-warnings-list");
        pdfWarningsList.innerHTML = "";
        
        if (record.warnings && record.warnings.length > 0) {
            pdfWarningsSection.style.display = "block";
            record.warnings.forEach(warning => {
                const item = document.createElement("div");
                item.style.marginBottom = "6px";
                item.innerHTML = `⚠️ <strong>${warning}</strong>`;
                pdfWarningsList.appendChild(item);
            });
        } else {
            pdfWarningsSection.style.display = "none";
        }

        // Suggestions Section
        const pdfSuggestions = document.getElementById("pdf-suggestions-list");
        pdfSuggestions.innerHTML = "";
        
        record.suggestions.forEach(sugg => {
            const li = document.createElement("li");
            li.style.marginBottom = "8px";
            li.innerHTML = sugg.text;
            pdfSuggestions.appendChild(li);
        });

        // Trigger download
        const element = document.getElementById("pdf-report-template");
        element.style.display = "block"; // Make visible temporarily for capturing
        
        const opt = {
            margin:       10,
            filename:     `AURA_MedAI_Report_${record.patient_name.replace(/\s+/g, '_')}_${record.disease}.pdf`,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };
        
        html2pdf().from(element.firstElementChild).set(opt).save().then(() => {
            element.style.display = "none"; // Hide again
        });
    }

    // Diagnostics Logs Helper
    function addConsoleLog(text) {
        const consoleLogs = document.querySelector(".logs-body");
        if (consoleLogs) {
            const line = document.createElement("div");
            line.className = "log-line";
            line.innerHTML = text;
            consoleLogs.appendChild(line);
            consoleLogs.scrollTop = consoleLogs.scrollHeight;
        }
    }

    // Symptom search UI logic
    const symptomInput = document.getElementById("symptom-input");
    const symptomsTags = document.getElementById("symptoms-tags");
    const suggestionPills = document.querySelectorAll(".symptom-pill");
    const analyzeBtn = document.getElementById("analyze-symptoms-btn");
    const symptomResultPanel = document.getElementById("symptom-result-panel");
    const correlationContainer = document.getElementById("correlation-results-container");

    symptomInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && symptomInput.value.trim()) {
            addSymptomTag(symptomInput.value.trim());
            symptomInput.value = "";
        }
    });

    suggestionPills.forEach(pill => {
        pill.addEventListener("click", () => {
            addSymptomTag(pill.innerText);
        });
    });

    function addSymptomTag(text) {
        const cleanText = text.toLowerCase().trim();
        if (selectedSymptoms.has(cleanText)) return;
        
        selectedSymptoms.add(cleanText);
        
        const tag = document.createElement("div");
        tag.className = "tag-item";
        tag.innerHTML = `
            <span>${cleanText}</span>
            <i class="fa-solid fa-xmark"></i>
        `;
        
        tag.querySelector("i").addEventListener("click", () => {
            selectedSymptoms.delete(cleanText);
            tag.remove();
        });
        
        symptomsTags.appendChild(tag);
    }

    // Analyze Symptom Profile correlations
    analyzeBtn.addEventListener("click", () => {
        if (selectedSymptoms.size === 0) {
            alert("Please input or click some symptoms first to analyze.");
            return;
        }

        symptomResultPanel.classList.remove("hidden");
        correlationContainer.innerHTML = "";

        // Rules mapping symptoms to disease correlations
        const diseaseCorrelations = {
            "Diabetes Panel": 0,
            "Cardiovascular Panel": 0,
            "Nephrology Panel": 0
        };

        const symptomRules = {
            "frequent urination": { "Diabetes Panel": 65, "Nephrology Panel": 40 },
            "excessive thirst": { "Diabetes Panel": 75 },
            "chest pain": { "Cardiovascular Panel": 90 },
            "shortness of breath": { "Cardiovascular Panel": 60, "Nephrology Panel": 25 },
            "foamy urine": { "Nephrology Panel": 85 },
            "swollen ankles": { "Nephrology Panel": 70, "Cardiovascular Panel": 30 },
            "fatigue": { "Diabetes Panel": 20, "Cardiovascular Panel": 20, "Nephrology Panel": 25 },
            "blurred vision": { "Diabetes Panel": 45 },
            "weight loss": { "Diabetes Panel": 40 },
            "headache": { "Cardiovascular Panel": 30, "Nephrology Panel": 20 },
            "nausea": { "Nephrology Panel": 40, "Diabetes Panel": 10 }
        };

        selectedSymptoms.forEach(symptom => {
            // Check direct match
            if (symptomRules[symptom]) {
                for (const [disease, weight] of Object.entries(symptomRules[symptom])) {
                    diseaseCorrelations[disease] = Math.max(diseaseCorrelations[disease], weight);
                }
            } else {
                // Check substring match
                for (const [ruleName, targets] of Object.entries(symptomRules)) {
                    if (symptom.includes(ruleName) || ruleName.includes(symptom)) {
                        for (const [disease, weight] of Object.entries(targets)) {
                            diseaseCorrelations[disease] = Math.max(diseaseCorrelations[disease], Math.round(weight * 0.7));
                        }
                    }
                }
            }
        });

        // Render bars
        for (const [disease, val] of Object.entries(diseaseCorrelations)) {
            const finalVal = Math.min(100, val || 5); // Default min 5% if symptoms entered but no match
            let barColor = "fill-cyan";
            if (disease.includes("Cardio")) barColor = "fill-red";
            if (disease.includes("Nephro")) barColor = "fill-green";

            const barGroup = document.createElement("div");
            barGroup.className = "correlation-bar-group";
            barGroup.innerHTML = `
                <div class="bar-label-row">
                    <span class="disease-name">${disease}</span>
                    <span class="font-mono text-cyan">${finalVal}%</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill ${barColor}" style="width: ${finalVal}%"></div>
                </div>
            `;
            correlationContainer.appendChild(barGroup);
        }

        addConsoleLog(`[${new Date().toLocaleTimeString()}] Symptom profile scan complete for: ${Array.from(selectedSymptoms).join(", ")}`);
    });

    // History log fetching & deletion
    async function fetchHistory() {
        try {
            const response = await fetch("/api/history");
            const result = await response.json();
            
            if (result.status === "success") {
                historyData = result.data;
                updateHistoryUI();
                initCharts();
            }
        } catch (err) {
            console.error("Error fetching history:", err);
        }
    }

    function updateHistoryUI() {
        const tbody = document.getElementById("history-table-body");
        tbody.innerHTML = "";

        // Update overall metrics count
        document.getElementById("stat-evaluations").innerText = historyData.length;
        
        let totalRisk = 0;
        let totalAdvice = 0;
        const diseaseRisks = { diabetes: [], heart_disease: [], kidney_disease: [] };
        
        if (historyData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center">No assessments found. Run a scan to populate history logs.</td></tr>`;
            document.getElementById("stat-health-score").innerText = "--";
            document.getElementById("stat-avg-risk").innerText = "0%";
            document.getElementById("stat-recommendations").innerText = "0";
            return;
        }

        historyData.forEach(item => {
            totalRisk += item.risk_percentage;
            totalAdvice += item.suggestions.length;
            diseaseRisks[item.disease].push(item.risk_percentage);
            
            const dateStr = new Date(item.timestamp).toLocaleString();
            const diseaseLabel = item.disease.replace("_", " ").toUpperCase();
            
            let badgeClass = "text-green";
            if (item.risk_percentage >= 70) badgeClass = "text-red";
            else if (item.risk_percentage >= 30) badgeClass = "text-orange";

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td class="font-mono">${dateStr}</td>
                <td>${item.patient_name}</td>
                <td><span class="card-tag">${diseaseLabel}</span></td>
                <td class="font-mono ${badgeClass}"><strong>${item.risk_percentage}%</strong></td>
                <td><span class="${badgeClass}">${item.risk_level.toUpperCase()}</span></td>
                <td class="font-mono text-green">${item.health_score}</td>
                <td>
                    <button class="action-icon-btn delete-btn" data-id="${item.id}" title="Delete diagnostic record">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Set average metrics
        const avgRisk = Math.round(totalRisk / historyData.length);
        document.getElementById("stat-avg-risk").innerText = `${avgRisk}%`;
        document.getElementById("stat-recommendations").innerText = totalAdvice;

        // Calculate active patient's current composite health score (from last available values of all run scans)
        const activePatient = document.getElementById("patient-name-global").value.trim() || "Anonymous";
        const patientHistory = historyData.filter(h => h.patient_name.toLowerCase() === activePatient.toLowerCase());
        
        if (patientHistory.length > 0) {
            // Find latest run for each scan type
            const latestScans = {};
            patientHistory.forEach(h => {
                if (!latestScans[h.disease]) {
                    latestScans[h.disease] = h.risk_percentage;
                }
            });
            
            // Calculate average risk from latest scans
            let scoreSum = 0;
            let scoreCount = 0;
            for (const [key, value] of Object.entries(latestScans)) {
                scoreSum += value;
                scoreCount++;
            }
            
            const avgLatestRisk = scoreSum / scoreCount;
            const healthScore = Math.max(0, Math.min(100, Math.round(100 - (avgLatestRisk * 0.8))));
            document.getElementById("stat-health-score").innerText = healthScore;
        } else {
            document.getElementById("stat-health-score").innerText = "--";
        }

        // Add event listeners for delete buttons
        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const recordId = btn.getAttribute("data-id");
                if (confirm("Are you sure you want to delete this diagnostics record?")) {
                    try {
                        const response = await fetch("/api/history/" + recordId, { method: "DELETE" });
                        const result = await response.json();
                        if (result.status === "success") {
                            historyData = historyData.filter(h => h.id !== recordId);
                            addConsoleLog(`[${new Date().toLocaleTimeString()}] Diagnostics log entry deleted`);
                            updateHistoryUI();
                            initCharts();
                        } else {
                            alert("Failed to delete record: " + result.message);
                        }
                    } catch (err) {
                        console.error("Delete failed:", err);
                        alert("Could not communicate with the server to delete record.");
                    }
                }
            });
        });
    }

    // Clear history button
    document.getElementById("clear-history-btn").addEventListener("click", async () => {
        if (confirm("CRITICAL WARNING: This will permanently wipe all diagnostic log files. Proceed?")) {
            try {
                const response = await fetch("/api/history/clear", { method: "POST" });
                const result = await response.json();
                if (result.status === "success") {
                    historyData = [];
                    updateHistoryUI();
                    initCharts();
                    addConsoleLog(`[${new Date().toLocaleTimeString()}] Diagnostic database cleared`);
                }
            } catch (err) {
                console.error("Clear history failed:", err);
            }
        }
    });

    // Chart.js initialization
    function initCharts() {
        // Destroy existing charts to avoid layout memory leaks
        if (timelineChart) timelineChart.destroy();
        if (radarChart) radarChart.destroy();

        const ctxTimeline = document.getElementById("timelineChart").getContext("2d");
        const ctxRadar = document.getElementById("radarChart").getContext("2d");

        // Format timeline data: reverse history to show chronological order
        const chronologicalHistory = [...historyData].reverse();
        const dates = chronologicalHistory.map(h => new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        const diabetesTimeline = chronologicalHistory.map(h => h.disease === "diabetes" ? h.risk_percentage : null);
        const heartTimeline = chronologicalHistory.map(h => h.disease === "heart_disease" ? h.risk_percentage : null);
        const kidneyTimeline = chronologicalHistory.map(h => h.disease === "kidney_disease" ? h.risk_percentage : null);

        // Chart styling colors
        const cyanColor = "#00f0ff";
        const redColor = "#ff3131";
        const greenColor = "#39ff14";

        timelineChart = new Chart(ctxTimeline, {
            type: 'line',
            data: {
                labels: dates.length > 0 ? dates : ["--:--"],
                datasets: [
                    {
                        label: 'Diabetes Risk',
                        data: diabetesTimeline,
                        borderColor: redColor,
                        backgroundColor: 'rgba(255, 49, 49, 0.05)',
                        borderWidth: 2,
                        tension: 0.3,
                        pointBackgroundColor: redColor,
                        spanGaps: true
                    },
                    {
                        label: 'Cardiac Risk',
                        data: heartTimeline,
                        borderColor: cyanColor,
                        backgroundColor: 'rgba(0, 240, 255, 0.05)',
                        borderWidth: 2,
                        tension: 0.3,
                        pointBackgroundColor: cyanColor,
                        spanGaps: true
                    },
                    {
                        label: 'Nephrology Risk',
                        data: kidneyTimeline,
                        borderColor: greenColor,
                        backgroundColor: 'rgba(57, 255, 20, 0.05)',
                        borderWidth: 2,
                        tension: 0.3,
                        pointBackgroundColor: greenColor,
                        spanGaps: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#e2e8f0', font: { family: 'Outfit' } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#8395a7', font: { family: 'Share Tech Mono' } }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#8395a7', font: { family: 'Share Tech Mono' } }
                    }
                }
            }
        });

        // Radar chart: showing latest risk value of each disease for active patient
        const latestRisks = { diabetes: null, heart_disease: null, kidney_disease: null };
        historyData.forEach(h => {
            if (latestRisks[h.disease] === null) {
                latestRisks[h.disease] = h.risk_percentage;
            }
        });
        
        const d_risk = latestRisks.diabetes || 0;
        const h_risk = latestRisks.heart_disease || 0;
        const k_risk = latestRisks.kidney_disease || 0;

        radarChart = new Chart(ctxRadar, {
            type: 'radar',
            data: {
                labels: ['Diabetes', 'Cardiac', 'Nephrology'],
                datasets: [{
                    label: 'Latest Assessment Risks (%)',
                    data: [d_risk, h_risk, k_risk],
                    backgroundColor: 'rgba(0, 240, 255, 0.2)',
                    borderColor: cyanColor,
                    borderWidth: 2,
                    pointBackgroundColor: cyanColor,
                    pointHoverBackgroundColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.05)' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        pointLabels: { color: '#e2e8f0', font: { family: 'Outfit', size: 11 } },
                        ticks: { display: false, stepSize: 20 },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }

    // AI Chatbot Interface
    const chatInput = document.getElementById("chat-input-field");
    const chatSendBtn = document.getElementById("chat-send-btn");
    const chatDialogueBox = document.getElementById("chat-dialogue-box");
    const quickTopicChips = document.querySelectorAll(".chat-quick-topics .chip");

    chatSendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    quickTopicChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-query");
            chatInput.value = query;
            sendMessage();
        });
    });

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        chatInput.value = "";
        
        // Append user bubble
        appendChatBubble("user", text);

        // Scroll to bottom
        chatDialogueBox.scrollTop = chatDialogueBox.scrollHeight;

        // Typing indicator simulator
        const typingId = "typing-" + Math.random().toString(36).substr(2, 9);
        const typingBubble = document.createElement("div");
        typingBubble.className = "message assistant";
        typingBubble.id = typingId;
        typingBubble.innerHTML = `
            <div class="message-meta font-mono">AURA MedAI // COGNITIVE_SYS</div>
            <div class="message-text"><i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing clinical metrics and generating suggestions...</div>
        `;
        chatDialogueBox.appendChild(typingBubble);
        chatDialogueBox.scrollTop = chatDialogueBox.scrollHeight;

        try {
            const response = await fetch("/api/ai_chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: jsonStringify({ message: text })
            });

            const result = await response.json();
            
            // Remove typing indicator
            document.getElementById(typingId).remove();

            if (result.status === "success") {
                appendChatBubble("assistant", result.message);
            } else {
                appendChatBubble("assistant", "An error occurred during communication: " + result.message);
            }
        } catch (err) {
            console.error("Chat fetch failed:", err);
            document.getElementById(typingId).remove();
            appendChatBubble("assistant", "Error: Dialogue engine offline. Please ensure local server is running.");
        }
        
        chatDialogueBox.scrollTop = chatDialogueBox.scrollHeight;
    }

    function appendChatBubble(sender, text) {
        const bubble = document.createElement("div");
        bubble.className = `message ${sender}`;
        
        const meta = sender === "user" ? "ACTIVE PATIENT // terminal" : "AURA MedAI // COGNITIVE_SYS";
        
        // Quick format markdown bold and headers for the response
        let formattedText = text
            .replace(/### (.*?)\n/g, "<h4>$1</h4>")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/-\s(.*?)\n/g, "<li>$1</li>")
            .replace(/\n\n/g, "<br><br>");

        // Wrap list items
        if (formattedText.includes("<li>")) {
            // Very simple list tag wrapper replacement
            formattedText = formattedText.replace(/(<li>.*?<\/li>)/gs, "<ul>$1</ul>");
        }

        bubble.innerHTML = `
            <div class="message-meta font-mono">${meta}</div>
            <div class="message-text">${formattedText}</div>
        `;
        chatDialogueBox.appendChild(bubble);
    }

    // Helper functions
    function updateClock() {
        const clockEl = document.getElementById("sidebar-clock");
        if (clockEl) {
            const now = new Date();
            clockEl.innerText = now.toTimeString().split(' ')[0] + " // " + now.toLocaleDateString();
        }
    }

    function jsonStringify(obj) {
        return JSON.stringify(obj);
    }

    // Load history on start
    fetchHistory();
});
