@echo off
title TEAM ZERODAY - ISRO SIH26166 Lunar Correspondence Platform
echo ================================================================
echo   TEAM ZERODAY // ISRO SIH26166 LUNAR CORRESPONDENCE PLATFORM   
echo ================================================================

cd /d "%~dp0"

echo.
echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
if exist ".venv\Scripts\uvicorn.exe" (
	start "Lunar CV Backend" cmd /k ".venv\Scripts\uvicorn.exe backend.main:app --app-dir . --host 127.0.0.1 --port 8000 --reload"
) else (
	start "Lunar CV Backend" cmd /k "python -m uvicorn backend.main:app --app-dir . --host 127.0.0.1 --port 8000 --reload"
)

timeout /t 3 /nobreak >nul

echo.
echo [2/2] Launching Next.js Mission Dashboard on http://localhost:3000 ...
cd frontend
npm run dev
