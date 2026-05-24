import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# Ensure models directory exists
os.makedirs("models", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Set random seed for reproducibility
np.random.seed(42)

def generate_and_train_diabetes():
    print("Generating Diabetes Dataset...")
    n_samples = 1500
    
    age = np.random.uniform(20, 80, n_samples)
    bmi = np.random.uniform(15, 45, n_samples)
    glucose = np.random.uniform(70, 260, n_samples)
    bp = np.random.uniform(60, 130, n_samples)
    insulin = np.random.uniform(15, 300, n_samples)
    hba1c = np.random.uniform(4.0, 9.5, n_samples)
    
    # Calculate probability of diabetes based on risk factors
    z = -10.5 + 0.045 * glucose + 0.12 * bmi + 0.02 * age + 0.9 * (hba1c - 5.5) + 0.015 * bp
    prob = 1 / (1 + np.exp(-z))
    target = np.random.binomial(1, prob)
    
    df = pd.DataFrame({
        'Age': age,
        'BMI': bmi,
        'Glucose': glucose,
        'BloodPressure': bp,
        'Insulin': insulin,
        'HbA1c': hba1c,
        'Diabetes': target
    })
    
    # Save synthetic dataset
    df.to_csv("data/diabetes_data.csv", index=False)
    
    X = df.drop('Diabetes', axis=1)
    y = df['Diabetes']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    accuracy = model.score(X_test_scaled, y_test)
    print(f"Diabetes Model Accuracy: {accuracy:.4f}")
    
    # Save model, scaler, and features list
    joblib.dump(model, "models/diabetes_model.joblib")
    joblib.dump(scaler, "models/diabetes_scaler.joblib")
    joblib.dump(list(X.columns), "models/diabetes_features.joblib")
    
    importances = dict(zip(X.columns, model.feature_importances_))
    print("Diabetes Feature Importances:", importances)
    print("---")

def generate_and_train_heart_disease():
    print("Generating Heart Disease Dataset...")
    n_samples = 1500
    
    age = np.random.uniform(30, 80, n_samples)
    sex = np.random.binomial(1, 0.6, n_samples)  # 60% male
    cp = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.4, 0.2, 0.3, 0.1])  # chest pain type
    trestbps = np.random.uniform(90, 180, n_samples)
    chol = np.random.uniform(150, 400, n_samples)
    thalach = np.random.uniform(80, 200, n_samples)  # max heart rate
    exang = np.random.binomial(1, 0.3, n_samples)  # exercise induced angina
    oldpeak = np.random.uniform(0.0, 5.0, n_samples)  # ST depression
    
    # Calculate probability of heart disease based on risk factors
    z = -7.5 + 0.03 * age + 0.6 * sex + 0.9 * cp + 0.015 * trestbps + 0.006 * chol - 0.025 * thalach + 1.2 * exang + 0.7 * oldpeak
    prob = 1 / (1 + np.exp(-z))
    target = np.random.binomial(1, prob)
    
    df = pd.DataFrame({
        'Age': age,
        'Sex': sex,
        'ChestPainType': cp,
        'RestingBP': trestbps,
        'Cholesterol': chol,
        'MaxHR': thalach,
        'ExerciseAngina': exang,
        'STDepression': oldpeak,
        'HeartDisease': target
    })
    
    df.to_csv("data/heart_disease_data.csv", index=False)
    
    X = df.drop('HeartDisease', axis=1)
    y = df['HeartDisease']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    accuracy = model.score(X_test_scaled, y_test)
    print(f"Heart Disease Model Accuracy: {accuracy:.4f}")
    
    joblib.dump(model, "models/heart_disease_model.joblib")
    joblib.dump(scaler, "models/heart_disease_scaler.joblib")
    joblib.dump(list(X.columns), "models/heart_disease_features.joblib")
    
    importances = dict(zip(X.columns, model.feature_importances_))
    print("Heart Disease Feature Importances:", importances)
    print("---")

def generate_and_train_kidney_disease():
    print("Generating Kidney Disease Dataset...")
    n_samples = 1500
    
    age = np.random.uniform(15, 80, n_samples)
    bp = np.random.uniform(50, 140, n_samples)
    sg = np.random.choice([1.005, 1.010, 1.015, 1.020, 1.025], size=n_samples, p=[0.1, 0.15, 0.2, 0.35, 0.2])  # specific gravity
    al = np.random.choice([0, 1, 2, 3, 4, 5], size=n_samples, p=[0.5, 0.15, 0.15, 0.1, 0.06, 0.04])  # albumin
    bs = np.random.uniform(70, 250, n_samples)  # blood sugar
    bu = np.random.uniform(10, 180, n_samples)  # blood urea
    sc = np.random.uniform(0.4, 15.0, n_samples)  # serum creatinine
    
    # Calculate probability of kidney disease
    # specific gravity is good when high, so lower sg = higher risk
    z = -3.5 + 0.015 * age + 0.012 * bp - 12.0 * (sg - 1.018) + 1.2 * al + 0.008 * bs + 0.012 * bu + 1.1 * sc
    prob = 1 / (1 + np.exp(-z))
    target = np.random.binomial(1, prob)
    
    df = pd.DataFrame({
        'Age': age,
        'BloodPressure': bp,
        'SpecificGravity': sg,
        'Albumin': al,
        'BloodSugar': bs,
        'BloodUrea': bu,
        'SerumCreatinine': sc,
        'KidneyDisease': target
    })
    
    df.to_csv("data/kidney_disease_data.csv", index=False)
    
    X = df.drop('KidneyDisease', axis=1)
    y = df['KidneyDisease']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    accuracy = model.score(X_test_scaled, y_test)
    print(f"Kidney Disease Model Accuracy: {accuracy:.4f}")
    
    joblib.dump(model, "models/kidney_disease_model.joblib")
    joblib.dump(scaler, "models/kidney_disease_scaler.joblib")
    joblib.dump(list(X.columns), "models/kidney_disease_features.joblib")
    
    importances = dict(zip(X.columns, model.feature_importances_))
    print("Kidney Disease Feature Importances:", importances)
    print("---")

if __name__ == "__main__":
    generate_and_train_diabetes()
    generate_and_train_heart_disease()
    generate_and_train_kidney_disease()
    print("All models trained and saved successfully.")
