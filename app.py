import os
import json
from datetime import datetime
import numpy as np
import joblib
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Paths
MODELS_DIR = "models"
HISTORY_FILE = os.path.join("data", "history.json")

# Ensure history directory exists
os.makedirs("data", exist_ok=True)
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

# Global variables for models and scalers
models = {}
scalers = {}
features_lists = {}

def load_ml_models():
    """Load trained models and scalers if they exist."""
    diseases = ["diabetes", "heart_disease", "kidney_disease"]
    for disease in diseases:
        model_path = os.path.join(MODELS_DIR, f"{disease}_model.joblib")
        scaler_path = os.path.join(MODELS_DIR, f"{disease}_scaler.joblib")
        features_path = os.path.join(MODELS_DIR, f"{disease}_features.joblib")
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                models[disease] = joblib.load(model_path)
                scalers[disease] = joblib.load(scaler_path)
                features_lists[disease] = joblib.load(features_path)
                print(f"Successfully loaded model and scaler for {disease}.")
            except Exception as e:
                print(f"Error loading {disease} model: {str(e)}")
        else:
            print(f"Model or scaler for {disease} not found at {model_path} / {scaler_path}.")

# Initial load
load_ml_models()

def generate_suggestions(disease, data, risk_pct):
    """Generate medical recommendations and health suggestions based on feature inputs."""
    suggestions = []
    
    # Generic suggestion if risk is moderate or high
    if risk_pct >= 70:
        suggestions.append({
            "type": "critical",
            "text": "HIGH RISK: Schedule an appointment with your healthcare provider immediately for a comprehensive evaluation."
        })
    elif risk_pct >= 30:
        suggestions.append({
            "type": "warning",
            "text": "MODERATE RISK: We recommend reviewing these metrics with a doctor during your next visit."
        })
    else:
        suggestions.append({
            "type": "info",
            "text": "LOW RISK: Keep maintaining a healthy lifestyle, balanced diet, and regular exercise."
        })

    if disease == "diabetes":
        glucose = float(data.get("Glucose", 0))
        bmi = float(data.get("BMI", 0))
        hba1c = float(data.get("HbA1c", 0))
        bp = float(data.get("BloodPressure", 0))
        
        if glucose > 125:
            suggestions.append({
                "type": "diet",
                "text": f"Your Glucose level ({glucose} mg/dL) is high. Reduce consumption of refined sugars and simple carbohydrates."
            })
        if hba1c > 6.0:
            suggestions.append({
                "type": "medical",
                "text": f"HbA1c of {hba1c}% indicates prediabetic or diabetic range. Consult an endocrinologist for custom glycemic control plans."
            })
        if bmi > 25.0:
            suggestions.append({
                "type": "exercise",
                "text": f"BMI of {bmi:.1f} is above optimal range. Aim for 150 minutes of moderate cardiovascular exercise per week."
            })
        if bp > 130:
            suggestions.append({
                "type": "medical",
                "text": f"Blood pressure ({bp} mmHg) is elevated. Monitor blood pressure daily and restrict daily sodium intake to under 2,000 mg."
            })

    elif disease == "heart_disease":
        bp = float(data.get("RestingBP", 0))
        chol = float(data.get("Cholesterol", 0))
        exang = int(data.get("ExerciseAngina", 0))
        oldpeak = float(data.get("STDepression", 0))
        
        if bp > 130:
            suggestions.append({
                "type": "medical",
                "text": f"Resting Blood Pressure ({bp} mmHg) is high. Practice stress-reduction techniques and restrict high-sodium foods."
            })
        if chol > 200:
            suggestions.append({
                "type": "diet",
                "text": f"Cholesterol level ({chol} mg/dL) is elevated. Increase consumption of soluble fibers (oats, beans) and omega-3 fatty acids."
            })
        if exang == 1:
            suggestions.append({
                "type": "exercise",
                "text": "You experience chest tightness during exercise (angina). Avoid sudden intense workouts; consult a cardiologist first."
            })
        if oldpeak > 1.5:
            suggestions.append({
                "type": "medical",
                "text": f"ST Depression of {oldpeak} during stress tests is a key indicator of cardiac ischemia. Further cardiovascular diagnostic tests are highly advised."
            })

    elif disease == "kidney_disease":
        sg = float(data.get("SpecificGravity", 1.020))
        al = int(data.get("Albumin", 0))
        sc = float(data.get("SerumCreatinine", 0))
        bu = float(data.get("BloodUrea", 0))
        
        if al > 0:
            suggestions.append({
                "type": "medical",
                "text": f"Albumin protein detected in urine (Grade {al}). This indicates potential filtration barrier disruption in the kidneys. Seek nephrology consult."
            })
        if sc > 1.2:
            suggestions.append({
                "type": "medical",
                "text": f"Serum Creatinine ({sc} mg/dL) is elevated, pointing to decreased glomerular filtration rate (GFR). Avoid NSAID painkillers like ibuprofen which can strain kidneys."
            })
        if sg < 1.015:
            suggestions.append({
                "type": "info",
                "text": f"Urine Specific Gravity is low ({sg}). This can signal diluted urine or impaired renal concentrating ability."
            })
        if bu > 40:
            suggestions.append({
                "type": "diet",
                "text": f"Blood Urea level ({bu} mg/dL) is elevated. Avoid excessively high protein diets to reduce nitrogenous load on kidney clearance."
            })

    return suggestions

def detect_emergencies(disease, data):
    """Detect critical thresholds and generate emergency warnings."""
    warnings = []
    
    if disease == "diabetes":
        glucose = float(data.get("Glucose", 0))
        bp = float(data.get("BloodPressure", 0))
        if glucose >= 250:
            warnings.append("CRITICAL GLUCOSE: Glucose level is dangerously high (>= 250 mg/dL). Risk of diabetic ketoacidosis (DKA) or hyperosmolar hyperglycemic state (HHS). Seek immediate medical help.")
        if bp >= 180:
            warnings.append("HYPERTENSIVE EMERGENCY: Blood pressure is dangerously high (>= 180 mmHg). Risk of stroke or organ damage. Seek emergency care immediately.")

    elif disease == "heart_disease":
        bp = float(data.get("RestingBP", 0))
        chol = float(data.get("Cholesterol", 0))
        oldpeak = float(data.get("STDepression", 0))
        if bp >= 180:
            warnings.append("HYPERTENSIVE EMERGENCY: Resting blood pressure is in crisis range (>= 180 mmHg). Seek emergency medical assistance.")
        if oldpeak >= 3.5:
            warnings.append("ACUTE ISCHEMIA WARNING: Significant ST Depression detected (>= 3.5), suggesting severe restriction of cardiac blood supply. Seek immediate cardiac screening.")
        if chol >= 320:
            warnings.append("SEVERE HYPERCHOLESTEROLEMIA: Cholesterol level exceeds 320 mg/dL. High risk for immediate coronary events. Consult a cardiovascular specialist.")

    elif disease == "kidney_disease":
        sc = float(data.get("SerumCreatinine", 0))
        bp = float(data.get("BloodPressure", 0))
        if sc >= 4.0:
            warnings.append(f"ACUTE KIDNEY STRESS: Serum Creatinine level is critically high ({sc} mg/dL). Severe kidney injury or end-stage renal disease (ESRD) risk. Immediate clinical evaluation is required.")
        if bp >= 180:
            warnings.append("HYPERTENSIVE CRISIS: Blood pressure is dangerously elevated (>= 180 mmHg) which directly damages kidney vessels. Seek emergency support.")

    return warnings

def calculate_overall_health_score(risk_scores):
    """Calculate a composite health index score (0-100) based on multiple risk predictions."""
    # Base health score starts at 100
    # Each high-risk disease reduces the health score
    # Formula: Health Index = 100 - average(risk_scores)
    if not risk_scores:
        return 100
    avg_risk = sum(risk_scores.values()) / len(risk_scores)
    health_score = max(0, min(100, round(100 - (avg_risk * 0.8))))
    return health_score

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/predict", methods=["POST"])
def predict():
    # If models are not loaded, try to load them first
    if not models:
        load_ml_models()
        if not models:
            return jsonify({
                "status": "error",
                "message": "Machine learning models are not yet trained. Please run `train_models.py` first."
            }), 503

    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({"status": "error", "message": "Missing JSON request payload"}), 400

        patient_name = req_data.get("patient_name", "Anonymous")
        disease = req_data.get("disease")
        form_data = req_data.get("data")

        if not disease or disease not in models:
            return jsonify({"status": "error", "message": f"Unsupported or missing disease: {disease}"}), 400

        # Extract features in correct order
        model = models[disease]
        scaler = scalers[disease]
        features = features_lists[disease]

        input_array = []
        for feature in features:
            if feature not in form_data:
                return jsonify({"status": "error", "message": f"Missing required feature: {feature}"}), 400
            input_array.append(float(form_data[feature]))

        # Scale inputs and predict
        import pandas as pd
        input_df = pd.DataFrame([input_array], columns=features)
        scaled_input = scaler.transform(input_df)
        prob = model.predict_proba(scaled_input)[0][1] # Probability of positive class (disease)
        
        risk_pct = round(float(prob) * 100, 1)
        
        if risk_pct >= 70:
            risk_level = "High"
        elif risk_pct >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Generate custom guidelines and warning alerts
        suggestions = generate_suggestions(disease, form_data, risk_pct)
        warnings = detect_emergencies(disease, form_data)

        # Get all predictions for this patient from history to compute composite health score
        # (For simple calculations, we will just use the current prediction if no others exist)
        health_score = calculate_overall_health_score({disease: risk_pct})

        # Save to history
        record = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S") + f"-{np.random.randint(1000, 9999)}",
            "patient_name": patient_name,
            "disease": disease,
            "timestamp": datetime.now().isoformat(),
            "inputs": form_data,
            "risk_percentage": risk_pct,
            "risk_level": risk_level,
            "health_score": health_score,
            "suggestions": suggestions,
            "warnings": warnings
        }

        with open(HISTORY_FILE, "r+") as f:
            history = json.load(f)
            history.insert(0, record)
            f.seek(0)
            json.dump(history, f, indent=4)
            f.truncate()

        return jsonify({
            "status": "success",
            "data": record
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Prediction failed: {str(e)}"}), 500

@app.route("/api/history", methods=["GET"])
def get_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        return jsonify({"status": "success", "data": history})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/history/<record_id>", methods=["DELETE"])
def delete_history_record(record_id):
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        
        new_history = [r for r in history if r.get("id") != record_id]
        
        with open(HISTORY_FILE, "w") as f:
            json.dump(new_history, f, indent=4)
            
        return jsonify({"status": "success", "message": "Record deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)
        return jsonify({"status": "success", "message": "History cleared successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/ai_chat", methods=["POST"])
def ai_chat():
    try:
        req_data = request.get_json()
        user_message = req_data.get("message", "").lower()
        
        # Simple intelligent keyword matching
        response = ""
        if any(w in user_message for w in ["hello", "hi", "hey", "greetings"]):
            response = (
                "### Hello, I am AURA MedAI. 🤖\n\n"
                "I am your automated medical assistant. I can analyze risk metrics for **Diabetes**, "
                "**Heart Disease**, and **Kidney Disease**. How can I assist you with your health analysis today?\n\n"
                "*Disclaimer: AI suggestions are for educational purposes. Consult a physician for diagnostic advice.*"
            )
        elif any(w in user_message for w in ["diabetes", "sugar", "glucose", "insulin", "hba1c"]):
            response = (
                "### Understanding Diabetes Risks 🩸\n\n"
                "Diabetes is heavily linked to insulin resistance and glucose accumulation in the bloodstream. Key markers include:\n"
                "- **HbA1c**: Reflects average blood sugar over 3 months. Normal is <5.7%, Prediabetes is 5.7%-6.4%, Diabetes is >=6.5%.\n"
                "- **Fasting Glucose**: Ideally should be under 100 mg/dL.\n"
                "- **BMI**: Excessive body weight increases insulin resistance.\n\n"
                "**Actionable Suggestions**:\n"
                "1. **Diet**: Prioritize low glycemic index foods, leafy greens, and fibers. Avoid soft drinks and sugary pastries.\n"
                "2. **Exercise**: Participate in aerobic training (brisk walking, swimming) for 30 minutes daily to improve muscle insulin sensitivity.\n"
                "3. **Regular Monitoring**: Track your fasting glucose levels weekly if you are in the prediabetic range."
            )
        elif any(w in user_message for w in ["heart", "cardio", "bp", "cholesterol", "angina", "chest pain"]):
            response = (
                "### Cardiovascular Health Insights ❤️\n\n"
                "Coronary artery disease and heart attacks are often preceded by arterial plaque buildup and high blood pressure:\n"
                "- **Cholesterol**: LDL ('bad' cholesterol) causes arterial plaque. Total cholesterol should ideally remain below 200 mg/dL.\n"
                "- **Resting BP**: Normal is <120/80 mmHg. Levels >= 130 mmHg reflect stage 1 hypertension.\n"
                "- **Exercise Angina**: Chest pain during exertion represents standard warning signs of reduced cardiac blood flow.\n\n"
                "**Actionable Suggestions**:\n"
                "1. **Sodium Control**: Restrict sodium to less than 1,500 - 2,000 mg per day to manage high blood pressure.\n"
                "2. **Healthy Fats**: Replace saturated and trans fats with monounsaturated oils (olive oil, avocados) and consume fish.\n"
                "3. **Stress Relief**: Implement breathing exercises, yoga, or meditation to lower heart rate and calm autonomic stress."
            )
        elif any(w in user_message for w in ["kidney", "renal", "creatinine", "albumin", "urine", "urea"]):
            response = (
                "### Renal Function Analysis 🧪\n\n"
                "Kidney damage (Chronic Kidney Disease) impairs blood filtration. Crucial indicators include:\n"
                "- **Serum Creatinine**: A metabolic waste product. High values (> 1.2 mg/dL) show reduced glomerular filtration.\n"
                "- **Albuminuria**: Albumin in urine indicates damage to the glomerulus filters, which shouldn't normally leak proteins.\n"
                "- **Specific Gravity**: Evaluates the kidney's capacity to concentrate urine.\n\n"
                "**Actionable Suggestions**:\n"
                "1. **Hydration**: Drink adequate water (2-3 liters/day) to support kidney filtration, unless on a fluid restriction diet.\n"
                "2. **Pain Relievers Warning**: Minimize consumption of NSAID pain relief medication (e.g. Ibuprofen, Naproxen) as they are nephrotoxic.\n"
                "3. **Blood Pressure Management**: Tight BP control (<130/80) is the absolute best way to prevent progressive kidney scarring."
            )
        elif any(w in user_message for w in ["diet", "food", "nutrition", "eat"]):
            response = (
                "### General Dietary Guidelines 🥗\n\n"
                "A balanced, health-oriented eating structure reduces risks across all three fields:\n"
                "- **Hydration**: Choose water instead of sugary beverages.\n"
                "- **Fiber**: Increase intake of vegetables, whole grains, and legumes. Fiber helps control blood sugar and lower cholesterol.\n"
                "- **Portion Control**: Focus on calorie density to maintain a healthy BMI.\n"
                "- **Healthy Fats**: Focus on olive oil, nuts, and fish over red meats."
            )
        elif any(w in user_message for w in ["exercise", "workout", "fitness", "run", "walk"]):
            response = (
                "### Exercise Recommendations 🏃‍♂️\n\n"
                "Physical exercise improves cardiac stroke volume, lowers insulin resistance, and manages weight:\n"
                "- **Aerobic activity**: 150 minutes of moderate activity (e.g., fast walking, cycling) per week.\n"
                "- **Strength training**: 2 days per week to build muscle tissue, which absorbs glucose from the bloodstream.\n"
                "- **Safety First**: If you experience chest tightness, dizziness, or severe shortness of breath, stop exercising and consult a doctor immediately."
            )
        else:
            response = (
                "### AURA MedAI Clinical Assistant\n\n"
                "I detected your query but do not have a specific medical mapping for those exact terms. "
                "I can advise you on: \n"
                "- **Diabetes risks** (glucose, insulin, BMI)\n"
                "- **Cardiovascular risks** (cholesterol, blood pressure, angina)\n"
                "- **Kidney functions** (creatinine, albumin,specific gravity)\n"
                "- **General wellness advice** (diet, exercise)\n\n"
                "Could you please specify which of these health aspects you would like to discuss?"
            )
            
        return jsonify({
            "status": "success",
            "message": response
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
