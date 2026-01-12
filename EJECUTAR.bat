@echo off
echo ========================================
echo   INICIANDO UBIK2CR
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo.
    echo Por favor:
    echo 1. Instala Python desde https://www.python.org/downloads/
    echo 2. Durante la instalacion, marca "Add Python to PATH"
    echo 3. Reinicia esta ventana
    pause
    exit /b 1
)

echo Python encontrado!
echo.

REM Verificar si existe el entorno virtual
if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR al crear entorno virtual
        pause
        exit /b 1
    )
    echo Entorno virtual creado!
    echo.
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar si las dependencias están instaladas
if not exist "venv\Lib\site-packages\flask" (
    echo Instalando dependencias (esto puede tardar unos minutos)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR al instalar dependencias
        pause
        exit /b 1
    )
    echo Dependencias instaladas!
    echo.
)

REM Verificar si la base de datos está inicializada
if not exist "migrations\" (
    echo Inicializando base de datos...
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    echo Base de datos inicializada!
    echo.
)

echo ========================================
echo   INICIANDO LA APLICACION...
echo ========================================
echo.
echo La aplicacion estara disponible en: http://localhost:5000
echo.
echo IMPORTANTE: NO CIERRES ESTA VENTANA
echo Para detener la aplicacion, presiona Ctrl+C
echo.
echo ========================================
echo.

REM Ejecutar la aplicación
python main.py

pause

