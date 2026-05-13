@echo off
echo Starting FakeGuard AI Backend...
echo API will be available at: http://localhost:8000
echo API Docs at: http://localhost:8000/docs
echo.
cd /d %~dp0backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
