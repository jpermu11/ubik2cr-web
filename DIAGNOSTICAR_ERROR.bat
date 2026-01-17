@echo off
chcp 65001 >nul
echo ========================================
echo   DIAGNOSTICAR PROBLEMA - Ubik2CR
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo.
    echo Por favor instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    python --version
    echo ✅ Python encontrado
)
echo.

echo [2/5] Verificando entorno virtual...
if not exist "venv\" (
    echo ⚠️  Entorno virtual no existe - creándolo...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Error al crear entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual existe
)
echo.

echo [3/5] Activando entorno virtual e instalando dependencias...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Advertencia: Error al instalar dependencias
    echo    Intentando instalar de nuevo...
    pip install -r requirements.txt
) else (
    echo ✅ Dependencias instaladas
)
echo.

echo [4/5] Verificando base de datos...
if not exist "migrations\" (
    echo ⚠️  Migraciones no inicializadas - inicializando...
    set FLASK_APP=main.py
    flask db init >nul 2>&1
    flask db migrate -m "Initial migration" >nul 2>&1
    flask db upgrade >nul 2>&1
    echo ✅ Base de datos inicializada
) else (
    echo ✅ Migraciones encontradas
)
echo.

echo [5/5] Intentando iniciar la aplicación...
echo.
echo ========================================
echo   EJECUTANDO LA APLICACIÓN...
echo ========================================
echo.
echo La aplicación debería estar disponible en:
echo   http://localhost:5000
echo.
echo IMPORTANTE: Mantén esta ventana abierta
echo Si ves errores aquí abajo, cópialos y compártelos
echo.
echo ========================================
echo.

set FLASK_APP=main.py
python main.py

pause
