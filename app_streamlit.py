import os
import json
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import joblib
from fpdf import FPDF

# Page Configuration
st.set_page_config(
    page_title="AURA MedAI // Disease Predictor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Neon Blue/Green Theme
st.markdown("""
<style>
    /* Dark Futuristic Style */
    .stApp {
        background-color: #070b14;
        color: #e2e8f0;
    }
    
    /* Neon headings */
    h1, h2, h3 {
        color: #00f0ff !important;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
        font-family: 'Outfit', sans-serif;
    }
    
    .stButton>button {
        background-color: transparent !important;
        color: #00f0ff !important;
        border: 1px solid #00f0ff !important;
        border-radius: 8px !important;
        box-shadow: 0 0 8px rgba(0, 240, 255, 0.1) !important;
        transition: all 0.3s ease !important;
        font-weight: bold !important;
    }
    
    .stButton>button:hover {
        background-color: #00f0ff !important;
        color: #070b14 !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.6) !important;
    }
    
    .stProgress > div > div > div > div {
        background-color: #39ff14 !important;
    }
    
    /* Info/Success metrics cards */
    div[data-testid="stMetricValue"] {
        color: #39ff14 !important;
        font-family: 'Share Tech Mono', monospace;
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.4);
    }
    
    .emergency-card {
        background-color: rgba(255, 49, 49, 0.12);
        border: 1px solid #ff3131;
        border-radius: 8px;
        padding: 15px;
        color: #ffcccc;
        margin-bottom: 20px;
        box-shadow: 0 0 12px rgba(255, 49, 49, 0.4);
    }
    
    .suggestion-box {
        background-color: rgba(13, 22, 42, 0.6);
        border-left: 4px solid #00f0ff;
        padding: 12px;
        border-radius: 0px 8px 8px 0px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Load Models
MODELS_DIR = "models"
HISTORY_FILE = os.path.join("data", "history.json")

@st.cache_resource
def load_models():
    models = {}
    scalers = {}
    features = {}
    diseases = ["diabetes", "heart_disease", "kidney_disease"]
    
    for d in diseases:
        m_path = os.path.join(MODELS_DIR, f"{d}_model.joblib")
        s_path = os.path.join(MODELS_DIR, f"{d}_scaler.joblib")
        f_path = os.path.join(MODELS_DIR, f"{d}_features.joblib")
        
        if os.path.exists(m_path) and os.path.exists(s_path):
            models[d] = joblib.load(m_path)
            scalers[d] = joblib.load(s_path)
            features[d] = joblib.load(f_path)
            
    return models, scalers, features

models, scalers, features_lists = load_models()

# Setup Local History database
if not os.path.exists("data"):
    os.makedirs("data", exist_ok=True)
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

def get_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# Sidebar System details
st.sidebar.markdown("### 🤖 AURA MedAI // SYSTEM")
st.sidebar.markdown(f"**SYS_STATUS**: `ONLINE`  \n**MED-NET**: `SECURE`  \n**TIME**: `{datetime.now().strftime('%H:%M:%S')}`")

patient_name = st.sidebar.text_input("Active Patient Profile:", value="John Doe")

# Generate Suggestions
def generate_suggestions(disease, data, risk_pct):
    suggestions = []
    if risk_pct >= 70:
        suggestions.append("HIGH RISK: Consult with your doctor immediately for comprehensive medical evaluation.")
    elif risk_pct >= 30:
        suggestions.append("MODERATE RISK: Review these levels with your doctor during your next physical checkup.")
    else:
        suggestions.append("LOW RISK: Continue maintaining a healthy diet and balanced fitness routine.")
        
    if disease == "diabetes":
        glucose = float(data.get("Glucose", 0))
        bmi = float(data.get("BMI", 0))
        hba1c = float(data.get("HbA1c", 0))
        if glucose > 125:
            suggestions.append(f"Glucose level ({glucose} mg/dL) is high. We recommend reducing carb/sugar consumption.")
        if hba1c > 6.0:
            suggestions.append(f"HbA1c level ({hba1c}%) is elevated. Consult an endocrinologist for custom glycemic control.")
        if bmi > 25.0:
            suggestions.append(f"BMI of {bmi:.1f} is high. Aim for at least 150 minutes of aerobic exercise weekly.")
            
    elif disease == "heart_disease":
        bp = float(data.get("RestingBP", 0))
        chol = float(data.get("Cholesterol", 0))
        if bp > 130:
            suggestions.append(f"Blood pressure ({bp} mmHg) is high. Restrict dietary sodium and practice stress management.")
        if chol > 200:
            suggestions.append(f"Cholesterol ({chol} mg/dL) is high. Increase soluble dietary fiber intake and consult your cardiologist.")
            
    elif disease == "kidney_disease":
        al = int(data.get("Albumin", 0))
        sc = float(data.get("SerumCreatinine", 0))
        if al > 0:
            suggestions.append(f"Albumin detected in urine (Grade {al}). Nephrology screening is highly advised.")
        if sc > 1.2:
            suggestions.append(f"Serum Creatinine ({sc} mg/dL) is high. Limit high-sodium foods and avoid nephrotoxic NSAID medications.")
            
    return suggestions

# Emergency warnings
def detect_emergencies(disease, data):
    warnings = []
    if disease == "diabetes":
        glucose = float(data.get("Glucose", 0))
        bp = float(data.get("BloodPressure", 0))
        if glucose >= 250:
            warnings.append("CRITICAL GLUCOSE: Glucose level is dangerously high (>= 250 mg/dL). Risk of Diabetic Ketoacidosis (DKA). Seek urgent medical help.")
        if bp >= 180:
            warnings.append("HYPERTENSIVE DISASTER: Blood pressure is dangerously high (>= 180 mmHg). Seek emergency medical assistance.")
            
    elif disease == "heart_disease":
        bp = float(data.get("RestingBP", 0))
        oldpeak = float(data.get("STDepression", 0))
        if bp >= 180:
            warnings.append("HYPERTENSIVE EMERGENCY: Resting blood pressure is critical (>= 180 mmHg). Seek emergency clinical aid.")
        if oldpeak >= 3.5:
            warnings.append("ACUTE ISCHEMIA WARNING: Significant ST Depression detected (>= 3.5), suggesting restriction of cardiac blood supply. Seek immediate screening.")
            
    elif disease == "kidney_disease":
        sc = float(data.get("SerumCreatinine", 0))
        bp = float(data.get("BloodPressure", 0))
        if sc >= 4.0:
            warnings.append(f"ACUTE RENAL THREAT: Serum Creatinine is critically high ({sc} mg/dL). Risk of severe kidney injury or failure. Seek clinical evaluation.")
        if bp >= 180:
            warnings.append("HYPERTENSIVE CRISIS: Blood pressure is dangerously elevated (>= 180 mmHg). Direct kidney vessel strain risk.")
            
    return warnings

# Create PDF report
def build_pdf_report(record):
    pdf = FPDF()
    pdf.add_page()
    
    # Title Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 86, 179)
    pdf.cell(0, 15, "AURA MedAI - CLINICAL REPORT", ln=True, align="L")
    pdf.set_draw_color(0, 86, 179)
    pdf.line(10, 25, 200, 25)
    
    pdf.ln(10)
    
    # Patient Dossier
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 8, "PATIENT ASSESSMENT DOSSIER", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(90, 6, f"Patient Name: {record['patient_name']}", border=0)
    pdf.cell(90, 6, f"Date/Time: {datetime.fromisoformat(record['timestamp']).strftime('%Y-%m-%d %H:%M')}", border=0, ln=True)
    pdf.cell(90, 6, f"Diagnostic Scan: {record['disease'].replace('_', ' ').upper()}", border=0)
    pdf.cell(90, 6, f"Secure Reference ID: {record['id']}", border=0, ln=True)
    
    pdf.ln(8)
    
    # Risk Results
    pdf.rect(10, 62, 190, 28)
    pdf.set_xy(15, 65)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(90, 6, "CLASSIFIED DIAGNOSTIC RISK SCORE", ln=False)
    pdf.cell(90, 6, "COMPOSITE HEALTH SCORE", ln=True)
    
    pdf.set_xy(15, 72)
    pdf.set_font("Helvetica", "B", 18)
    if record['risk_percentage'] >= 70:
        pdf.set_text_color(217, 83, 79)
    elif record['risk_percentage'] >= 30:
        pdf.set_text_color(240, 173, 78)
    else:
        pdf.set_text_color(92, 184, 92)
    pdf.cell(90, 8, f"{record['risk_percentage']}% ({record['risk_level'].upper()} RISK)", ln=False)
    
    pdf.set_text_color(92, 184, 92)
    pdf.cell(90, 8, f"{record['health_score']} / 100", ln=True)
    
    pdf.set_text_color(51, 51, 51)
    pdf.ln(12)
    
    # Vital inputs
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "VITAL INDICATORS RECORDED", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for k, v in record['inputs'].items():
        pdf.cell(90, 6, f" - {k}: {v}", border=0, ln=True)
        
    pdf.ln(8)
    
    # Warnings
    if record['warnings']:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(217, 83, 79)
        pdf.cell(0, 8, "EMERGENCY WARNING TRIGGERS", ln=True)
        pdf.set_font("Helvetica", "B", 10)
        for w in record['warnings']:
            pdf.multi_cell(0, 6, f"!! {w}")
        pdf.ln(6)
        
    # Suggestions
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 86, 179)
    pdf.cell(0, 8, "AI-GENERATED HEALTH INTERVENTIONS", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(51, 51, 51)
    for s in record['suggestions']:
        pdf.multi_cell(0, 6, f" * {s}")
        
    # PDF footer disclaimer
    pdf.set_y(260)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 4, "Disclaimer: This document is generated automatically by AURA MedAI. For screening purposes only.", ln=True, align="C")
    pdf.cell(0, 4, "Always consult a medical professional for formal medical diagnostics.", ln=True, align="C")
    
    return pdf.output()

# Layout Navigation tabs
tab_dash, tab_scan, tab_hist, tab_ai = st.tabs([
    "📊 Real-time Dashboard", 
    "🩺 Diagnostic Scanners", 
    "📂 Diagnostic Logs", 
    "💬 Clinical AI Assistant"
])

# TAB 1: DASHBOARD
with tab_dash:
    st.title("AURA MedAI Predictive Dashboard")
    history = get_history()
    
    # Metrics Row
    m_evals, m_health, m_avg_risk, m_advice = st.columns(4)
    m_evals.metric("Total Evaluations Conducted", len(history))
    
    if history:
        avg_risk = int(np.mean([h['risk_percentage'] for h in history]))
        m_avg_risk.metric("Average Risk Level", f"{avg_risk}%")
        
        advice_count = sum([len(h['suggestions']) for h in history])
        m_advice.metric("AI Recommendations Issued", advice_count)
        
        # Calculate active patient composite health
        pat_history = [h for h in history if h['patient_name'].lower() == patient_name.lower()]
        if pat_history:
            latest_risks = {}
            for h in pat_history:
                if h['disease'] not in latest_risks:
                    latest_risks[h['disease']] = h['risk_percentage']
            score = max(0, min(100, round(100 - (np.mean(list(latest_risks.values())) * 0.8))))
            m_health.metric("Composite Health Index", score)
        else:
            m_health.metric("Composite Health Index", "--")
    else:
        m_avg_risk.metric("Average Risk Level", "0%")
        m_advice.metric("AI Recommendations Issued", 0)
        m_health.metric("Composite Health Index", "--")
        
    st.write("---")
    
    col_chart_left, col_chart_right = st.columns([2, 1])
    
    with col_chart_left:
        st.markdown("### Patient Assessment Timeline")
        if history:
            chron_hist = history[::-1]
            dates = [datetime.fromisoformat(h['timestamp']).strftime('%H:%M') for h in chron_hist]
            
            fig = go.Figure()
            
            for disease, color, name in [
                ("diabetes", "#ff3131", "Diabetes"),
                ("heart_disease", "#00f0ff", "Cardiac"),
                ("kidney_disease", "#39ff14", "Nephrology")
            ]:
                d_risks = [h['risk_percentage'] if h['disease'] == disease else None for h in chron_hist]
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=d_risks,
                    mode='lines+markers',
                    name=name,
                    line=dict(color=color, width=2),
                    connectgaps=True
                ))
                
            fig.update_layout(
                plot_bgcolor='#070b14',
                paper_bgcolor='#070b14',
                font_color='#e2e8f0',
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', range=[0, 100])
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timeline records available yet. Run a diagnostic scan.")
            
    with col_chart_right:
        st.markdown("### Risk Balance Index")
        if history:
            latest_risks = {"diabetes": 0, "heart_disease": 0, "kidney_disease": 0}
            for h in history:
                if not latest_risks[h['disease']]:
                    latest_risks[h['disease']] = h['risk_percentage']
            
            categories = ['Diabetes', 'Cardiac', 'Nephrology']
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=[latestRisks['diabetes'], latestRisks['heart_disease'], latestRisks['kidney_disease']],
                theta=categories,
                fill='toself',
                fillcolor='rgba(0, 240, 255, 0.15)',
                line=dict(color='#00f0ff', width=2)
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor='#070b14',
                    radialaxis=dict(visible=False, range=[0, 100]),
                    angularaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)', linecolor='rgba(255,255,255,0.05)')
                ),
                paper_bgcolor='#070b14',
                font_color='#e2e8f0',
                margin=dict(l=30, r=30, t=30, b=30)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("Radar diagnostic mapping unavailable.")

# TAB 2: DIAGNOSTIC SCANNERS
with tab_scan:
    if not models:
        st.error("⚠️ Machine Learning Models are not trained! Please run the training script.")
    else:
        st.markdown("### Clinical Parameters Input")
        
        disease_selector = st.selectbox("Select Target Pathology Scan:", [
            ("Diabetes Prediction Model", "diabetes"),
            ("Cardiovascular Disease Model", "heart_disease"),
            ("Chronic Kidney Disease Model", "kidney_disease")
        ], format_func=lambda x: x[0])
        
        disease_type = disease_selector[1]
        
        col_form, col_res = st.columns([1.2, 0.8])
        
        form_data = {}
        with col_form:
            st.markdown(f"#### Form: {disease_selector[0]}")
            with st.form("vital_inputs_form"):
                if disease_type == "diabetes":
                    form_data["Age"] = st.slider("Patient Age (Years)", 20, 80, 45)
                    form_data["BMI"] = st.slider("BMI (Body Mass Index)", 15.0, 50.0, 26.5, 0.1)
                    form_data["Glucose"] = st.slider("Fasting Glucose Level (mg/dL)", 70, 250, 110)
                    form_data["BloodPressure"] = st.slider("Diastolic Blood Pressure (mmHg)", 60, 140, 80)
                    form_data["Insulin"] = st.slider("Serum Insulin Level (μIU/mL)", 15, 300, 85)
                    form_data["HbA1c"] = st.slider("HbA1c Level (%)", 4.0, 9.5, 5.6, 0.1)
                    
                elif disease_type == "heart_disease":
                    form_data["Age"] = st.slider("Patient Age (Years)", 30, 80, 55)
                    sex_opt = st.selectbox("Sex", ["Male", "Female"])
                    form_data["Sex"] = 1.0 if sex_opt == "Male" else 0.0
                    
                    cp_opt = st.selectbox("Chest Pain Type", [
                        "Typical Angina (0)", 
                        "Atypical Angina (1)", 
                        "Non-anginal Pain (2)", 
                        "Asymptomatic (3)"
                    ])
                    form_data["ChestPainType"] = float(cp_opt.split("(")[1].split(")")[0])
                    
                    form_data["RestingBP"] = st.slider("Resting Blood Pressure (mmHg)", 90, 180, 120)
                    form_data["Cholesterol"] = st.slider("Serum Cholesterol (mg/dL)", 150, 400, 220)
                    form_data["MaxHR"] = st.slider("Max Heart Rate Achieved (bpm)", 80, 200, 150)
                    
                    ex_ang = st.selectbox("Exercise Induced Angina", ["No (0)", "Yes (1)"])
                    form_data["ExerciseAngina"] = 1.0 if "Yes" in ex_ang else 0.0
                    
                    form_data["STDepression"] = st.slider("ST Depression (Oldpeak)", 0.0, 5.0, 1.2, 0.1)
                    
                elif disease_type == "kidney_disease":
                    form_data["Age"] = st.slider("Patient Age (Years)", 15, 80, 50)
                    form_data["BloodPressure"] = st.slider("Resting Blood Pressure (mmHg)", 50, 140, 80)
                    
                    sg_opt = st.selectbox("Urine Specific Gravity", [
                        "1.025 (Optimal)", "1.020 (Normal)", "1.015 (Sub-optimal)", "1.010 (Impaired)", "1.005 (Severe)"
                    ])
                    form_data["SpecificGravity"] = float(sg_opt.split(" ")[0])
                    
                    al_opt = st.selectbox("Urine Albumin Level", ["0 (Normal)", "1 (Trace)", "2 (Mild)", "3 (Moderate)", "4 (Heavy)", "5 (Severe)"])
                    form_data["Albumin"] = float(al_opt.split(" ")[0])
                    
                    form_data["BloodSugar"] = st.slider("Blood Sugar (mg/dL)", 70, 250, 95)
                    form_data["BloodUrea"] = st.slider("Blood Urea (mg/dL)", 10, 180, 35)
                    form_data["SerumCreatinine"] = st.slider("Serum Creatinine (mg/dL)", 0.4, 15.0, 0.9, 0.1)
                    
                submit_scan = st.form_submit_state = st.form_submit_button("Initiate MedAI Predictor Model")
                
        with col_res:
            st.markdown("#### Diagnosis Outputs")
            if submit_scan:
                # Load correct model/scaler
                model = models[disease_type]
                scaler = scalers[disease_type]
                feats = features_lists[disease_type]
                
                input_vals = [float(form_data[f]) for f in feats]
                input_df = pd.DataFrame([input_vals], columns=feats)
                scaled_input = scaler.transform(input_df)
                
                prob = model.predict_proba(scaled_input)[0][1]
                risk_pct = round(float(prob) * 100, 1)
                
                risk_level = "Low"
                if risk_pct >= 70:
                    risk_level = "High"
                elif risk_pct >= 30:
                    risk_level = "Medium"
                    
                suggestions = generate_suggestions(disease_type, form_data, risk_pct)
                warnings = detect_emergencies(disease_type, form_data)
                
                # Composite Health Score
                health_score = max(0, min(100, round(100 - (risk_pct * 0.8))))
                
                # Save Record
                record = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S") + "-ST",
                    "patient_name": patient_name,
                    "disease": disease_type,
                    "timestamp": datetime.now().isoformat(),
                    "inputs": form_data,
                    "risk_percentage": risk_pct,
                    "risk_level": risk_level,
                    "health_score": health_score,
                    "suggestions": [{"type": "info", "text": s} for s in suggestions],
                    "warnings": warnings
                }
                
                # Append to history
                current_hist = get_history()
                current_hist.insert(0, record)
                save_history(current_hist)
                
                # Display results
                # Radial Plotly Gauge for Risk Percentage
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = risk_pct,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"{risk_level.upper()} RISK ASSESSMENT", 'font': {'size': 14, 'color': '#00f0ff'}},
                    number = {'suffix': '%', 'font': {'color': '#ff3131' if risk_level == "High" else ('#ff9f1c' if risk_level == "Medium" else '#39ff14')}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickcolor': '#e2e8f0'},
                        'bar': {'color': "#ff3131" if risk_level == "High" else ('#ff9f1c' if risk_level == "Medium" else '#39ff14')},
                        'bgcolor': "#070b14",
                        'bordercolor': "rgba(0, 240, 255, 0.2)",
                        'steps': [
                            {'range': [0, 30], 'color': 'rgba(57, 255, 20, 0.05)'},
                            {'range': [30, 70], 'color': 'rgba(255, 159, 28, 0.05)'},
                            {'range': [70, 100], 'color': 'rgba(255, 49, 49, 0.05)'}
                        ]
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor='#070b14',
                    font_color='#e2e8f0',
                    height=200,
                    margin=dict(l=10, r=10, t=40, b=10)
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # Warnings Alert Box
                if warnings:
                    for w in warnings:
                        st.markdown(f'<div class="emergency-card">⚠️ <strong>EMERGENCY ALERT</strong>: {w}</div>', unsafe_allow_html=True)
                
                # Health suggestions
                st.markdown("##### 🧠 AI Health Interventions")
                for s in suggestions:
                    st.markdown(f'<div class="suggestion-box">💡 {s}</div>', unsafe_allow_html=True)
                    
                # PDF report download
                pdf_bytes = build_pdf_report(record)
                st.download_button(
                    label="📥 Download Clinical Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"AURA_Report_{patient_name}_{disease_type}.pdf",
                    mime="application/pdf"
                )
            else:
                st.info("Set patient vitals on the left, then click 'Initiate MedAI Predictor' to calculate results.")

# TAB 3: DIAGNOSTIC LOGS
with tab_hist:
    st.markdown("### Persistent Medical Logs")
    history = get_history()
    
    if not history:
        st.info("No diagnostic scan history log found in the system.")
    else:
        st.write("Current patient database snapshot:")
        df_records = []
        for h in history:
            df_records.append({
                "Timestamp": datetime.fromisoformat(h['timestamp']).strftime('%Y-%m-%d %H:%M'),
                "Patient": h['patient_name'],
                "Scan": h['disease'].replace("_", " ").upper(),
                "Risk Percentage": f"{h['risk_percentage']}%",
                "Risk Classification": h['risk_level'].upper(),
                "Health Score": h['health_score']
            })
        st.dataframe(pd.DataFrame(df_records), use_container_width=True)
        
        # Clear Logs Button
        if st.button("Permanently Wipe Database Logs"):
            save_history([])
            st.success("Database logs wiped successfully. Please refresh the page.")

# TAB 4: CLINICAL ASSISTANT
with tab_ai:
    st.markdown("### Holographic AI Assistant Terminal")
    
    # Initialize message list
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello, I am the AURA MedAI advisor. How can I assist you with disease prediction vitals, cardiovascular, or renal risk parameters today?"}
        ]
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask AURA... (e.g. how do I lower my diabetes risk?)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Mock responsive logic
        user_lower = prompt.lower()
        response = ""
        if any(w in user_lower for w in ["diabetes", "sugar", "glucose", "insulin"]):
            response = """
            ### Diabetes Information
            Diabetes mellitus is a chronic metabolic disease with elevated glucose levels.
            - **Primary Target**: Fasting glucose (< 100 mg/dL normal, > 125 mg/dL diabetic).
            - **Key Management**:
              1. Restrict carbohydrate intake.
              2. Conduct regular exercise to lower insulin resistance.
              3. Track HbA1c values quarterly.
            """
        elif any(w in user_lower for w in ["heart", "cardio", "bp", "angina", "cholesterol"]):
            response = """
            ### Cardiovascular Information
            Heart disease covers conditions like heart failure and coronary blockages.
            - **Key Indicators**: Rest BP (> 130 mmHg indicates hypertension), Cholesterol (> 200 mg/dL is high).
            - **Key Management**:
              1. Restrict salt intake to lower blood pressure.
              2. Avoid trans fats; eat olive oil and fish.
              3. Introduce moderate cardio routines (30m daily).
            """
        elif any(w in user_lower for w in ["kidney", "renal", "creatinine", "albumin"]):
            response = """
            ### Renal Function Information
            Kidney health is assessed by blood filtration performance.
            - **Key Indicators**: Serum Creatinine (> 1.2 mg/dL shows reduced GFR filtration), Albumin in urine (Grade > 0 shows filter leakage).
            - **Key Management**:
              1. Stay well hydrated (2.5L water daily).
              2. Avoid NSAID painkillers like ibuprofen.
              3. Tight BP control is the single best way to protect kidney vessels.
            """
        else:
            response = """
            I am AURA MedAI. I can discuss diabetes parameters, heart disease factors, kidney filtration levels, and healthy dietary habits. Could you please clarify your request?
            """
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
