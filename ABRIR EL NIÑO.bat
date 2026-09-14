@echo off
chcp 65001 >nul
title Centro de Mando Gamer - El Nino
color 0B

REM ==========================================
REM  INICIAR CENTRO DE MANDO GAMER - EL NINO
REM ==========================================

REM Ir siempre al directorio del script
cd /d "%~dp0" || (
    echo ERROR: no puedo acceder al directorio del disco
    pause
    exit /b 1
)

echo ========================================
echo   Centro de Mando Gamer - El Nino
echo ========================================
echo.

REM Verificar que existe el servidor
if not exist "server.py" (
    echo ERROR: no encuentro server.py en esta carpeta
    pause
    exit /b 1
)

REM Buscar Python (portable primero, luego del sistema)
set PYTHON=
if exist "python_portable\pythonw.exe" (
    set PYTHON=python_portable\pythonw.exe
    set PYTHON_EXE=python_portable\python.exe
    echo Python portable detectado
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON=python
        set PYTHON_EXE=python
        echo Python del sistema detectado
    )
)

if "%PYTHON%"=="" (
    echo ERROR: no encuentro Python ni portable ni instalado
    echo.
    echo Opciones:
    echo 1. Instala Python desde python.org
    echo 2. Copia Python portable a python_portable\
    pause
    exit /b 1
)

REM Cerrar servidor anterior si esta corriendo
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
timeout /t 1 /nobreak >nul

REM Arrancar servidor en segundo plano
echo Arrancando servidor...
start "" /B "%PYTHON%" "server.py"

REM Esperar a que arranque (maximo 5 segundos)
set INTENTOS=0
:esperar
timeout /t 1 /nobreak >nul
set /a INTENTOS+=1
curl -s -o nul --max-time 1 http://localhost:8080/01_EL_NINO_LAUNCHER/index.html 2>nul
if %ERRORLEVEL% EQU 0 goto listo
if %INTENTOS% LSS 5 goto esperar

echo ADVERTENCIA: el servidor tarda mas de lo esperado
echo Revisa si tienes algun programa usando el puerto 8080
goto abrir

:listo
echo Servidor listo.

:abrir
echo Abriendo el navegador...
start "" "http://localhost:8080/01_EL_NINO_LAUNCHER/index.html"

echo.
echo ========================================
echo   Listo. Disfruta, Mario.
echo ========================================
echo.
echo Puedes cerrar esta ventana.
timeout /t 3 /nobreak >nul
exit /b 0
