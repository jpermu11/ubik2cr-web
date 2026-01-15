@echo off
echo ========================================
echo  Iniciando Ubik2CR en modo local
echo ========================================
echo.

REM Activar entorno virtual
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Creando entorno virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Instalar dependencias
echo.
echo Instalando dependencias...
pip install -r requirements.txt

REM Verificar archivo .env
if not exist .env (
    echo.
    echo ADVERTENCIA: No se encontro archivo .env
    echo Creando .env con valores por defecto...
    (
        echo SECRET_KEY=clave-secreta-local-cambiar-en-produccion
        echo DATABASE_URL=sqlite:///local.db
        echo MAINTENANCE_MODE=false
        echo ADMIN_USER=admin
        echo ADMIN_PASSWORD=admin123
    ) > .env
    echo.
    echo Archivo .env creado. Por favor, revisalo y ajusta los valores.
    echo.
    pause
)

REM Inicializar base de datos
echo.
echo Inicializando base de datos...
flask db upgrade

REM Correr aplicación
echo.
echo ========================================
echo  Aplicacion iniciada!
echo  Abri en tu navegador: http://localhost:5000
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python main.py

pause
