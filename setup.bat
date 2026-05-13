@echo off
echo ================================================
echo  FakeGuard AI — Full Setup Script
echo  Platform-Aware Fake Profile Detection System
echo ================================================
echo.

REM Step 1: Install Python dependencies
echo [1/4] Installing Python dependencies...
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo.

REM Step 2: Train ML models
echo [2/3] Training platform-specific ML models using real datasets...
python ml\train_models.py
if errorlevel 1 (
    echo ERROR: Failed to train models
    pause
    exit /b 1
)
echo.

REM Step 3: Install frontend dependencies
echo [3/3] Installing frontend dependencies...
cd frontend
call npm install
cd ..
echo.

echo ================================================
echo  Setup Complete!
echo ================================================
echo.
echo To start the application:
echo   1. Backend:  cd backend ^& uvicorn app:app --reload --port 8000
echo   2. Frontend: cd frontend ^& npm run dev
echo.
echo Or use the start scripts:
echo   start_backend.bat
echo   start_frontend.bat
echo.
pause
