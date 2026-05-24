AURA MedAI 🧬⚡
Futuristic AI-Powered Medical Diagnostic Dashboard

AURA MedAI is an advanced full-stack healthcare analytics and diagnostic platform that combines Machine Learning, predictive risk analysis, interactive dashboards, and a futuristic cyberpunk-inspired UI to simulate intelligent clinical diagnostics.

The platform evaluates patient vitals and predicts the probability of major medical conditions including:

🩸 Diabetes
❤️ Heart Disease
🧪 Kidney Disease

Built using Flask + Scikit-Learn + Vanilla JavaScript, the project demonstrates seamless integration between Machine Learning models and a dynamic real-time frontend dashboard.

🌐 Live Demo
[https://dashboard-l2.onrender.com/](https://dashboard-l2.onrender.com/)

🚀 Deployment

AURA MedAI Live Dashboard


✨ Key Features
🖥️ Global Dashboard

The landing dashboard provides a real-time overview of the healthcare analytics system.

Includes:
Total Patient Evaluations
Average Risk Percentage
Composite Health Score
AI Medical Bulletins
Real-Time Activity Timeline
Radar Risk Visualization
📊 Interactive Charts

Powered using Chart.js

Chronological patient timeline graphs
Radar charts for disease risk comparison
Live dashboard synchronization


🧠 Symptom Analyzer

An intelligent frontend-based symptom correlation engine.

Users can:

Enter symptoms manually
Select common health symptoms
Get disease likelihood estimation
Example Symptoms
Chest Pain
Fatigue
High Sugar
Frequent Urination
Shortness of Breath

The system uses a weighted symptom correlation algorithm to estimate which disease category is most likely related to the entered symptoms.

🔬 Predictive Health Scans
🩸 Diabetes Diagnostic Scan

Evaluates:

Glucose
BMI
Insulin
HbA1c
Blood Pressure

❤️ Cardiac Health Scan

Evaluates:

Cholesterol
Maximum Heart Rate
ST Depression (Oldpeak)
Chest Pain Type
Exercise Angina
🧪 Kidney Disease Scan

Evaluates:

Serum Creatinine
Blood Urea
Specific Gravity
Albumin
Blood Sugar
📈 AI Diagnostic Results

After prediction, the system generates:

🎯 Risk Percentage
💚 Health Score
⚠️ Emergency Warnings
🥗 AI Diet Recommendations
🏃 Exercise Suggestions
📊 SVG Circular Gauges
📌 Personalized Interventions
📄 PDF Medical Reports

Using html2pdf.js, users can instantly generate downloadable medical reports containing:

Patient vitals
Prediction percentages
AI recommendations
Emergency warnings
Health summaries
🗂️ Diagnostic History Logs

Every scan is securely stored locally using:

data/history.json
Features
View previous diagnostic records
Delete individual records
Clear complete history
Automatic chart synchronization
🤖 AI Clinical Assistant

Built-in educational medical chatbot capable of explaining:

Medical terminology
Lab reports
Vitals meaning
Lifestyle guidance
Basic healthcare awareness
Example Queries
“What is Serum Creatinine?”
“What causes high glucose?”
“How to reduce cholesterol?”
🛠️ Technical Architecture

The application follows a modern Client-Server Architecture.

⚙️ Backend Architecture
🐍 Python + Flask

Flask handles:

API routing
Prediction endpoints
Data processing
Frontend rendering
🤖 Machine Learning

Built using:

Scikit-Learn
RandomForestClassifier
NumPy
Pandas
🧪 Synthetic Dataset Generation

The train_models.py script automatically generates realistic synthetic healthcare datasets using probability distributions.

Includes:
Disease probability simulation
Feature importance calculation
Risk balancing
Dataset normalization
📊 Model Training

Three independent ML models are trained:

Disease	Algorithm	Accuracy
Diabetes	Random Forest	~94%
Heart Disease	Random Forest	High Accuracy
Kidney Disease	Random Forest	~99%
🔄 Data Preprocessing

Uses:

StandardScaler

to normalize patient vitals before prediction.

💾 Model Serialization

Models and scalers are saved using:

joblib

allowing Flask to load pre-trained models instantly at server startup.

🎨 Frontend Architecture
🌌 UI Design

Built using:

HTML5
CSS3
Vanilla JavaScript
Design Style
Cyberpunk aesthetic
Glassmorphism
Neon glow effects
Holographic animations
Smooth transitions
📱 Responsive Layout

Implemented using:

CSS Grid
Flexbox
Media Queries

Compatible with:

Desktop
Tablets
Mobile devices
⚡ Frontend Logic

The app.js file manages:

Form handling
API communication
Dynamic rendering
Tab switching
Chart updates
Gauge animations
🔄 Full Prediction Workflow
Step 1 — User Input

The user enters patient vitals using sliders and form inputs.

Step 2 — Frontend Transport

JavaScript captures the form and sends an asynchronous POST request using:

fetch()

to the Flask API endpoint.

Step 3 — Backend Processing

Flask receives the JSON payload and:

Loads the correct scaler
Normalizes patient data
Routes data to the ML model
Step 4 — AI Prediction

The Random Forest model calculates:

predict_proba()

which returns the disease risk probability.

Step 5 — Medical Logic Engine

Custom rule-based algorithms detect:

Emergency conditions
Dangerous thresholds
High-risk vitals

and generate personalized AI advice.

Step 6 — Data Persistence

The diagnostic result is saved into:

history.json
Step 7 — Frontend Rendering

JavaScript dynamically updates:

Circular gauges
Risk percentages
Dashboard charts
Medical warnings
AI recommendations

without reloading the page.


🚀 Installation Guide
1️⃣ Clone Repository
git clone https://github.com/your-username/AURA-MedAI.git
cd AURA-MedAI
2️⃣ Create Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
Linux / Mac
python3 -m venv venv
source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Train Models
python train_models.py
5️⃣ Start Flask Server
python app.py

🌟 Highlights for Presentation
Why This Project Stands Out

✅ Full-Stack Machine Learning Integration
✅ Real-Time Interactive Dashboard
✅ AI Risk Prediction System
✅ Dynamic Data Visualization
✅ PDF Report Generation
✅ Responsive Cyberpunk UI
✅ Practical Healthcare Simulation
✅ Flask API + JavaScript Communication
✅ Persistent Diagnostic History

🔮 Future Improvements
Real hospital API integration
Real patient datasets
Deep Learning models
Multi-language support
Voice-enabled AI assistant
Cloud database integration
Doctor authentication system
Secure patient login

📜 License
This project is licensed under the MIT License.

👨‍💻 Developer

Built with ❤️ using:

Python
Flask
Machine Learning
JavaScript
Chart.js
Cyberpunk UI Design

⭐ Support

If you like this project:

⭐ Star the repository
🍴 Fork the project
🛠️ Contribute improvements
📢 Share the project
