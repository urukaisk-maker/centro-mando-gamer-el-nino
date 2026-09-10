@echo off
cd /d "%~dp0"
taskkill /f /im python.exe >nul 2>&1
start "" pythonw server.py
timeout /t 2 /nobreak > nul
start "" http://localhost:8080/01_EL_NINO_LAUNCHER/index.html
exit
