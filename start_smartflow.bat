@echo off
title SmartFlow Starter

start "SmartFlow Backend" cmd /k "cd /d D:\smartflow\backend && call .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
start "SmartFlow Frontend" cmd /k "cd /d D:\smartflow\frontend && npm run dev"

echo.
echo SmartFlow is starting...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
