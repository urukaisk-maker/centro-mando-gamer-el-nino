@echo off
chcp 65001 >nul
title Detener - El Nino
color 0B

echo ========================================
echo   Deteniendo Centro de Mando
echo ========================================
echo.

REM Cerrar servidor
taskkill /F /IM pythonw.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 echo Servidor (pythonw) detenido
taskkill /F /IM python.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 echo Servidor (python) detenido

echo.
echo Listo. Servidor detenido.
timeout /t 2 /nobreak >nul
exit /b 0
