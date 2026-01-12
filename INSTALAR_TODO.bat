@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════
echo   INSTALADOR AUTOMÁTICO - UBIK2CR
echo ═══════════════════════════════════════════════════════════
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python no está instalado
    echo.
    echo Necesitas instalar Python primero:
    echo.
    echo 1. Abre tu navegador
    echo 2. Ve a: https://www.python.org/downloads/
    echo 3. Haz clic en "Download Python"
    echo 4. Cuando termine, haz doble clic en el archivo descargado
    echo 5. IMPORTANTE: Marca la casilla "Add Python to PATH"
    echo 6. Haz clic en "Install Now"
    echo 7. Espera a que termine
    echo 8. Cierra esta ventana y vuelve a ejecutar este archivo
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python encontrado
echo.

REM Crear entorno virtual
echo [2/6] Creando entorno virtual...
if not exist "venv\" (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Error al crear entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual ya existe
)
echo.

REM Activar entorno virtual
echo [3/6] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Error al activar entorno virtual
    pause
    exit /b 1
)
echo ✅ Entorno virtual activado
echo.

REM Instalar dependencias
echo [4/6] Instalando dependencias (esto puede tardar varios minutos)...
if not exist "venv\Lib\site-packages\flask" (
    pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error al instalar dependencias
        pause
        exit /b 1
    )
    echo ✅ Dependencias instaladas
) else (
    echo ✅ Dependencias ya están instaladas
)
echo.

REM Inicializar base de datos
echo [5/6] Inicializando base de datos...
if not exist "migrations\" (
    flask db init >nul 2>&1
    flask db migrate -m "Initial migration" >nul 2>&1
    flask db upgrade >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Advertencia: Hubo un problema con la base de datos
        echo    (Puede que ya esté inicializada, no es grave)
    ) else (
        echo ✅ Base de datos inicializada
    )
) else (
    echo ✅ Base de datos ya está inicializada
)
echo.

REM Crear archivo .env básico si no existe
if not exist ".env" (
    echo [6/6] Creando archivo de configuración...
    (
        echo SESSION_SECRET=dev-secret-key-cambiar-en-produccion
        echo ADMIN_USER=admin
        echo ADMIN_PASS=admin123
        echo PORT=5000
    ) > .env
    echo ✅ Archivo de configuración creado
) else (
    echo [6/6] Archivo de configuración ya existe
)
echo.

echo ═══════════════════════════════════════════════════════════
echo   ✅ ¡TODO LISTO!
echo ═══════════════════════════════════════════════════════════
echo.
echo Ahora puedes ejecutar EJECUTAR.bat para iniciar la aplicación
echo O escribe en esta ventana: python main.py
echo.
pause

