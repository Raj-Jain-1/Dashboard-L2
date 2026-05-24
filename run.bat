@echo off
title AURA MedAI Platform Launcher
:menu
cls
echo ===========================================================
echo             AURA MedAI PLATFORM LAUNCHER
echo ===========================================================
echo [1] Launch Futuristic Web Dashboard (Flask + Neon UI)
echo [2] Launch Alternative Dashboard (Streamlit)
echo [3] Re-train Scikit-Learn ML Models
echo [4] Install Missing Dependencies (pip)
echo [5] Exit
echo ===========================================================
set /p choice="Select an option (1-5): "

if "%choice%"=="1" (
    echo [SYS] Starting Flask server on http://localhost:5000 ...
    python app.py
    pause
    goto menu
)
if "%choice%"=="2" (
    echo [SYS] Starting Streamlit dashboard ...
    streamlit run app_streamlit.py
    pause
    goto menu
)
if "%choice%"=="3" (
    echo [SYS] Running Model Training Script ...
    python train_models.py
    echo [SYS] Done.
    pause
    goto menu
)
if "%choice%"=="4" (
    echo [SYS] Installing requirements ...
    pip install -r requirements.txt
    pause
    goto menu
)
if "%choice%"=="5" (
    echo [SYS] Exiting platform...
    exit
)

echo [SYS] Invalid selection, try again.
pause
goto menu
