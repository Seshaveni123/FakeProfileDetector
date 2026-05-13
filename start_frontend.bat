@echo off
echo Starting FakeGuard AI Frontend...
echo UI will be available at: http://localhost:5173
echo.
cd /d %~dp0frontend
npm run dev
