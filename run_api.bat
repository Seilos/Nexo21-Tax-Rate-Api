@echo off
setlocal enabledelayedexpansion
title API BCV - DolarVzla Backend
echo ======================================================
echo INICIANDO MICROSERVICIO: API BCV
echo ======================================================
echo.

set "VENV_PATH=%~dp0..\..\venv"
set "PYTHON_EXE=%VENV_PATH%\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
    echo [OK] Entorno virtual detectado.
    echo [INFO] Iniciando API en el puerto 8081...
    echo.
    cd /d "%~dp0"
    "%PYTHON_EXE%" manage.py runserver 8081
) else (
    echo [CRITICO] No se encuentra el entorno virtual compartido en: %VENV_PATH%
)

echo.
pause
