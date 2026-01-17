@echo off
chcp 65001 >nul
title Ubik2CR - Ejecutando
color 0A

cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════
echo   UBIK2CR - EJECUTANDO APLICACION
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Crear venv si no existe
if not exist "venv\" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
)

REM Activar venv con CMD (no PowerShell)
echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo [INFO] Verificando dependencias...
pip install -r requirements.txt --quiet 2>nul

REM Configurar Flask
set FLASK_APP=main.py

REM Inicializar DB si es necesario
if not exist "migrations\" (
    echo [INFO] Inicializando base de datos...
    flask db init >nul 2>&1
    flask db migrate -m "Initial migration" >nul 2>&1
    flask db upgrade >nul 2>&1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   INICIANDO APLICACION...
echo ═══════════════════════════════════════════════════════════
echo.
echo   Abre tu navegador en: http://localhost:5000
echo.
echo   IMPORTANTE: Deja esta ventana ABIERTA
echo   Para detener: Presiona Ctrl+C
echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM Ejecutar aplicación
python main.py

pause
